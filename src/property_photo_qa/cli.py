import argparse, json
from pathlib import Path
from .audit import audit
from .report import write_reports

def main():
    p=argparse.ArgumentParser(description='Offline property photography preflight; does not edit or upload source images.')
    p.add_argument('root',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--mapping',type=Path);p.add_argument('--min-width',type=int,default=1200);p.add_argument('--min-height',type=int,default=800)
    p.add_argument('--near-threshold',type=int,default=4);p.add_argument('--max-files',type=int,default=1000)
    p.add_argument("--exclude-reviewed",type=Path,help="JSON object mapping reviewed property IDs to reasons; requires image mapping")
    args=p.parse_args()
    try:
        exclusions=None
        if args.exclude_reviewed is not None:
            if args.exclude_reviewed.stat().st_size > 100000:raise ValueError('exclusion file exceeds100KB')
            exclusions=json.loads(args.exclude_reviewed.read_text(encoding='utf-8'))
        result=audit(args.root,exclude_properties=exclusions,mapping=args.mapping,min_width=args.min_width,min_height=args.min_height,near_threshold=args.near_threshold,max_files=args.max_files)
        write_reports(result,args.out);print(result['summary'])
        if exclusions is not None:print('Review scope:',result['review_scope']['audited_images'],'audited;',len(result['review_scope']['excluded_images']),'explicitly excluded. Exit status covers audited images only.')
        return 1 if result['summary']['flagged'] else 0
    except (ValueError,OSError) as error:p.error(str(error))

if __name__=='__main__':raise SystemExit(main())
