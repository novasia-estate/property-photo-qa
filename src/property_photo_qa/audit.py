import csv
from pathlib import Path
from .images import inspect_image
from .scope import review_exclusions
EXTENSIONS={'.jpg','.jpeg','.png','.webp','.tif','.tiff'}

def load_mapping(path):
    if path is None:return {}
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if not {'relative_path','property_id'}<=set(reader.fieldnames or []):raise ValueError('Mapping requires relative_path,property_id')
        result={}
        for row in reader:
            name=row['relative_path']
            if name in result:raise ValueError('Duplicate mapping path: '+name)
            if not row['property_id'].strip():raise ValueError('Empty property ID')
            result[name]=row['property_id']
        return result

def audit(root, *, mapping=None, min_width=1200, min_height=800, near_threshold=4, max_files=1000, max_bytes=30_000_000, exclude_properties=None):
    root=Path(root).resolve(strict=True)
    if not root.is_dir():raise ValueError('Root must be a directory')
    if min_width<1 or min_height<1 or max_files<1 or max_bytes<1 or not 0<=near_threshold<=16:raise ValueError('Invalid audit limits')
    mapped=load_mapping(mapping)
    paths=sorted(p for p in root.rglob('*') if p.is_file() and p.suffix.lower() in EXTENSIONS)
    if len(paths)>max_files:raise ValueError(f'{len(paths)} images exceeds the explicit {max_files}-file limit')
    identities={p.relative_to(root).as_posix():mapped.get(p.relative_to(root).as_posix(),'unassigned') for p in paths}
    exclusions=review_exclusions(exclude_properties,set(identities.values()))
    if 'unassigned' in exclusions:raise ValueError('Map images to explicit property IDs before excluding them')
    excluded=[{'path':name,'property_id':gid,'reason':exclusions[gid]} for name,gid in identities.items() if gid in exclusions]
    rows=[]
    for p in paths:
        relative=p.relative_to(root).as_posix()
        if identities[relative] in exclusions:continue
        row={'path':relative,'property_id':mapped.get(relative,'unassigned'),'flags':[]}
        if not p.resolve().is_relative_to(root):row['flags']=['symlink_outside_root']
        else:
            try:row.update(inspect_image(p,min_width=min_width,min_height=min_height,max_bytes=max_bytes))
            except OSError:row['flags']=['unreadable_file']
        rows.append(row)
    pairs=[]
    for i,a in enumerate(rows):
        for b in rows[i+1:]:
            if a.get('sha256') and a.get('sha256')==b.get('sha256'):
                kind='exact_duplicate';distance=0
            elif a.get('dhash') and b.get('dhash'):
                distance=(int(a['dhash'],16)^int(b['dhash'],16)).bit_count()
                if distance>near_threshold:continue
                kind='visual_candidate'
            else:continue
            pairs.append({'left':a['path'],'right':b['path'],'kind':kind,'hash_distance':distance,
                          'cross_property':a['property_id']!=b['property_id'] and 'unassigned' not in [a['property_id'],b['property_id']]})
            for row in [a,b]:
                if kind not in row['flags']:row['flags'].append(kind)
    report = {'version':'1.2.0','limits':{'min_width':min_width,'min_height':min_height,'near_threshold':near_threshold,'max_files':max_files,'max_bytes':max_bytes},
            'images':rows,'pairs':pairs,'unused_mapping_paths':sorted(set(mapped)-set(identities)),
            'summary':{'images':len(rows),'flagged':sum(bool(r['flags']) for r in rows),'exact_pairs':sum(p['kind']=='exact_duplicate' for p in pairs),'visual_candidates':sum(p['kind']=='visual_candidate' for p in pairs)}}

    if exclude_properties is not None:
        report['review_scope']={'discovered_images':len(paths),'audited_images':len(rows),'excluded_images':excluded,
                                'notice':'Excluded images were not inspected or compared; no all-catalogue clearance is implied.'}
    return report
