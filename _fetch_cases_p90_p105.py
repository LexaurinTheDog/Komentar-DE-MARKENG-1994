from pathlib import Path
from urllib.request import Request,urlopen
from datetime import datetime,timezone
import zipfile,io,hashlib,json,xml.etree.ElementTree as E,shutil
W=Path(__file__).resolve().parent;D=W/'sources/review-p90-p105'
fetches=json.loads((D/'fetches.json').read_text())
for name,doc,docket in [('wasser','JURE119007542','24 W (pat) 33/09'),('hohenlohe','KORE311442021','I ZR 163/19')]:
 url=f'https://www.rechtsprechung-im-internet.de/jportal/docs/bsjrs/jb-{doc}.zip';now=datetime.now(timezone.utc).isoformat()
 with urlopen(Request(url,headers={'User-Agent':'OpenCommentary-bounded-review/1.0'}),timeout=40) as r:body=r.read();st=r.status;typ=r.headers.get('Content-Type');final=r.url
 assert st==200;z=zipfile.ZipFile(io.BytesIO(body));assert z.testzip() is None
 ns=[n for n in z.namelist() if n.endswith('.xml')];assert len(ns)==1;raw=z.read(ns[0]);root=E.fromstring(raw);assert root.findtext('aktenzeichen')==docket
 p=D/(name+'.zip');p.write_bytes(body);p.with_suffix('.xml').write_bytes(raw)
 shutil.copyfile(Path('/Volumes/LaCie/law-intake/eu/de/rii')/('rii-'+doc.lower()+'.md'),D/(name+'-local.md'))
 # Create readable official text including paragraph numbers, not third-party summaries.
 p.with_suffix('.txt').write_text('\n'.join(''.join(x.itertext()) for tag in ['tenor','tatbestand','entscheidungsgruende','gruende'] for x in root.findall('.//'+tag+'//p')))
 fetches.append(dict(url=url,final_url=final,accessed_at=now,http_status=st,content_type=typ,path=str(p.relative_to(W)),sha256=hashlib.sha256(body).hexdigest(),xml_path=str(p.with_suffix('.xml').relative_to(W)),xml_sha256=hashlib.sha256(raw).hexdigest(),format_validation='ZIP CRC checked; unique XML parsed; docket verified',captured_body_sha256_verified=True))
 print(name,st,len(body),flush=True)
(D/'fetches.json').write_text(json.dumps(fetches,ensure_ascii=False,indent=2)+'\n')
