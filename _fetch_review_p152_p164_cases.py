from pathlib import Path
from urllib.request import Request,urlopen
from datetime import datetime,timezone
import json,hashlib,zipfile,io,xml.etree.ElementTree as E,shutil
W=Path(__file__).resolve().parent;D=W/'sources/review-p152-p164'
f=json.loads((D/'fetches.json').read_text())
for slug,doc,docket in [('kragenweite','JURE239030841','29 W (pat) 514/20'),('goeler','JURE239030940','26 W (pat) 27/18')]:
 url='https://www.rechtsprechung-im-internet.de/jportal/docs/bsjrs/jb-'+doc+'.zip';now=datetime.now(timezone.utc).isoformat()
 with urlopen(Request(url,headers={'User-Agent':'OpenCommentary-review/1.0'}),timeout=45) as r:body=r.read();status=r.status;ct=r.headers.get('Content-Type');final=r.url
 p=D/(slug+'.zip');p.write_bytes(body);assert status==200
 z=zipfile.ZipFile(io.BytesIO(body));assert z.testzip() is None;ns=[x for x in z.namelist() if x.endswith('.xml')];assert len(ns)==1
 raw=z.read(ns[0]);root=E.fromstring(raw);assert docket==root.findtext('aktenzeichen');p.with_suffix('.xml').write_bytes(raw)
 p.with_suffix('.txt').write_text('\n\n'.join(''.join(x.itertext()).strip() for tag in ['tenor','tatbestand','entscheidungsgruende','gruende'] for x in root.findall(tag+'/div')))
 shutil.copyfile(Path('/Volumes/LaCie/law-intake/eu/de/rii')/('rii-'+doc.lower()+'.md'),D/(slug+'-local.md'))
 f.append(dict(url=url,final_url=final,accessed_at=now,http_status=status,content_type=ct,path=str(p.relative_to(W)),sha256=hashlib.sha256(body).hexdigest(),format_validation='ZIP CRC validated; unique XML parsed; expected docket '+docket));(D/'fetches.json').write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n');print(slug,status,len(body),flush=True)
