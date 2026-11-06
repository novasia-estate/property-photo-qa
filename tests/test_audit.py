import tempfile,unittest,sys
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).parents[1]/'src'))
from property_photo_qa import audit
from property_photo_qa.report import render

class AuditTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def photo(self,name='one.png',size=(1600,1000)):
        p=self.root/name;Image.new('RGB',size,'navy').save(p);return p
    def test_valid_image_and_no_source_changes(self):
        p=self.photo();before=p.read_bytes();r=audit(self.root)
        self.assertEqual(r['summary']['images'],1);self.assertFalse(r['images'][0]['flags']);self.assertEqual(p.read_bytes(),before)
    def test_small_photo(self):
        self.photo(size=(20,20));self.assertIn('below_requested_resolution',audit(self.root)['images'][0]['flags'])
    def test_exact_duplicates(self):
        a=self.photo();(self.root/'copy.png').write_bytes(a.read_bytes());r=audit(self.root)
        self.assertEqual(r['summary']['exact_pairs'],1)
    def test_corrupt_image_is_retained(self):
        (self.root/'broken.jpg').write_bytes(b'not a photo');self.assertIn('unreadable_image',audit(self.root)['images'][0]['flags'])
    def test_configured_file_limit(self):
        self.photo();self.photo('two.png')
        with self.assertRaises(ValueError):audit(self.root,max_files=1)
    def test_large_file_not_decoded(self):
        self.photo();self.assertEqual(audit(self.root,max_bytes=1)['images'][0]['flags'],['file_size_limit'])
    def test_cross_property_pair(self):
        a=self.photo();(self.root/'two.png').write_bytes(a.read_bytes());m=self.root/'mapping.csv';m.write_text('relative_path,property_id\none.png,A\ntwo.png,B\n',encoding='utf-8')
        self.assertTrue(audit(self.root,mapping=m)['pairs'][0]['cross_property'])
    def test_duplicate_mapping_rejected(self):
        m=self.root/'mapping.csv';m.write_text('relative_path,property_id\na,A\na,B\n')
        with self.assertRaises(ValueError):audit(self.root,mapping=m)
    def test_report_escapes_property_labels(self):
        self.photo();m=self.root/'mapping.csv';m.write_text('relative_path,property_id\none.png,<script>bad</script>\n')
        text=render(audit(self.root,mapping=m));self.assertNotIn('<script>bad</script>',text);self.assertIn('&lt;script&gt;',text)
    def test_invalid_limits(self):
        with self.assertRaises(ValueError):audit(self.root,near_threshold=64)
    def test_gps_flag_without_coordinates_in_result(self):
        exif=Image.Exif();exif[34853]={1:'N',2:(1.0,2.0,3.0)}
        Image.new('RGB',(40,40)).save(self.root/'gps.jpg',exif=exif)
        row=audit(self.root)['images'][0];self.assertTrue(row['gps_present']);self.assertNotIn('latitude',row)
    def test_empty_folder(self):self.assertEqual(audit(self.root)['summary']['images'],0)

if __name__=='__main__':unittest.main()
