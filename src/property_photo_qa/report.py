import html
import json

def render(report):
    esc=lambda s:html.escape(str(s),quote=True)
    cards=[]
    for row in report['images']:
        thumb=row.get('thumbnail')
        image=f'<img src="{thumb}" alt="Local thumbnail">' if thumb else '<div class="missing">Preview unavailable</div>'
        cards.append(f'<article data-property="{esc(row["property_id"])}" data-flagged="{str(bool(row["flags"])).lower()}">{image}<h3>{esc(row["path"])}</h3><p>{esc(row["property_id"])}</p><p>{row.get("width") or "?"} × {row.get("height") or "?"}</p><p class="flags">{esc(", ".join(row["flags"]) or "No configured flags")}</p></article>')
    scope=report.get('review_scope')
    excluded_html=''
    if scope is not None:
        excluded_html='<section><h2>Explicit review scope</h2><p>'+esc(scope['notice'])+'</p><p>'+str(scope['audited_images'])+' audited of '+str(scope['discovered_images'])+' discovered images.</p><ul>'+''.join('<li>'+esc(x['path'])+' — '+esc(x['property_id'])+': '+esc(x['reason'])+'</li>' for x in scope['excluded_images'])+'</ul></section>'
    pairs=''.join(f'<tr><td>{esc(p["left"])}</td><td>{esc(p["right"])}</td><td>{esc(p["kind"])}</td><td>{p["hash_distance"]}</td><td>{p["cross_property"]}</td></tr>' for p in report['pairs'])
    properties=''.join(f'<option>{esc(p)}</option>' for p in sorted({r['property_id'] for r in report['images']}))
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Property Photo QA</title><style>
body{font:16px system-ui;background:#f2f5f6;color:#163339;margin:0}header,main{max-width:1200px;margin:auto;padding:24px}header{background:#163339;color:white;border-radius:0 0 24px 24px}h1{margin:8px 0}.stats{display:flex;gap:24px;flex-wrap:wrap}.stats b{font-size:28px;display:block}.controls{display:flex;gap:20px;padding:20px 0;flex-wrap:wrap}select,input{font:inherit;padding:8px}.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px}article{padding:16px;border-radius:14px;background:white;border:1px solid #d7e2e3}article img{width:100%;height:160px;object-fit:contain;background:#edf1f1}h3{font-size:15px;overflow-wrap:anywhere}.flags{color:#8a3a12;font-size:14px}.missing{height:160px;background:#fbe9df;display:grid;place-content:center}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:10px;border-bottom:1px solid #cad7d8;text-align:left;overflow-wrap:anywhere}.table{overflow:auto}footer{font-size:14px;margin-top:25px}article[hidden]{display:none}</style>
<header><p>LOCAL MEDIA PREFLIGHT</p><h1>Property Photo QA</h1><p>Review configured issues before publishing your property catalogue.</p><div class="stats">'''+''.join(f'<div><b>{value}</b>{esc(key.replace("_"," "))}</div>' for key,value in report['summary'].items())+'''</div></header><main><p>Source images were not changed or uploaded. Visual similarity is a review candidate, not proof of duplication, ownership or misuse. GPS coordinates are never included in this report.</p><div class="controls"><label>Property <select id="property"><option value="">All properties</option>'''+properties+'''</select></label><label><input id="flagged" type="checkbox"> Flagged images only</label><span id="visible" aria-live="polite"></span></div><section class="cards">'''+''.join(cards)+'''</section>'''+excluded_html+'''<h2>Duplicate and similarity review</h2><div class="table"><table><thead><tr><th>Image A</th><th>Image B</th><th>Reason</th><th>Distance</th><th>Different properties</th></tr></thead><tbody>'''+pairs+'''</tbody></table></div><footer>Developed by <a href="https://novasia.estate/">NovAsia Estate</a>. This report may contain private thumbnails and paths. Share it only with authorised reviewers.</footer></main><script>
const property=document.querySelector('#property'),flagged=document.querySelector('#flagged');function filter(){let shown=0;document.querySelectorAll('article').forEach(card=>{card.hidden=!!((property.value&&card.dataset.property!==property.value)||(flagged.checked&&card.dataset.flagged!=='true'));if(!card.hidden)shown++});document.querySelector('#visible').textContent=shown+' images shown'}property.addEventListener('change',filter);flagged.addEventListener('change',filter);filter();</script></html>'''

def write_reports(report,output):
    output.mkdir(parents=True,exist_ok=True)
    (output/'report.html').write_text(render(report),encoding='utf-8')
    machine={**report,'images':[{k:v for k,v in r.items() if k!='thumbnail'} for r in report['images']]}
    (output/'report.json').write_text(json.dumps(machine,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
