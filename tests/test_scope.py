import tempfile,unittest,importlib
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from property_photo_qa import audit
from property_photo_qa.report import render,write_reports

class PhotoScopeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        Image.new('RGB',(1600,1000),'navy').save(self.root/'a.png');(self.root/'b.png').write_bytes((self.root/'a.png').read_bytes())
        self.mapping=self.root/'mapping.csv';self.mapping.write_text('relative_path,property_id\na.png,A\nb.png,B\n',encoding='utf-8')
    def tearDown(self):self.tmp.cleanup()
    def test_excluded_property_not_decoded_or_paired(self):
        from property_photo_qa.audit import inspect_image
        with patch.object(importlib.import_module('property_photo_qa.audit'),'inspect_image',wraps=inspect_image) as inspect:
            r=audit(self.root,mapping=self.mapping,exclude_properties={'A':'Reviewed'})
        self.assertEqual(inspect.call_count,1);self.assertEqual(r['summary']['exact_pairs'],0);self.assertEqual([x['path'] for x in r['images']],['b.png']);self.assertEqual(r['unused_mapping_paths'],[])
        self.assertEqual(r['review_scope']['excluded_images'],[{'path':'a.png','property_id':'A','reason':'Reviewed'}])
    def test_unknown_unassigned_and_bad_reasons_fail(self):
        for value in [{'absent':'Checked'},{'A':''},{'A':False},['A']]:
            with self.subTest(value=value),self.assertRaises(ValueError):audit(self.root,mapping=self.mapping,exclude_properties=value)
        with self.assertRaises(ValueError):audit(self.root,exclude_properties={'unassigned':'Checked'})
    def test_discovery_limit_cannot_be_bypassed_by_excluding(self):
        with self.assertRaises(ValueError):audit(self.root,mapping=self.mapping,max_files=1,exclude_properties={'A':'Checked','B':'Checked'})
    def test_all_excluded_remains_explicit_and_escaped_in_reports(self):
        r=audit(self.root,mapping=self.mapping,exclude_properties={'A':'<script>bad</script>','B':'Checked'})
        self.assertEqual(r['summary']['images'],0);self.assertEqual(r['review_scope']['discovered_images'],2)
        h=render(r);self.assertIn('0 audited of 2',h);self.assertNotIn('<script>bad</script>',h);self.assertIn('&lt;script&gt;',h)
        write_reports(r,self.root/'report');self.assertIn('excluded_images',(self.root/'report/report.json').read_text())
    def test_legacy_pairs_and_report_without_policy(self):
        r=audit(self.root,mapping=self.mapping);self.assertEqual(r['summary']['exact_pairs'],1);self.assertNotIn('review_scope',r)
