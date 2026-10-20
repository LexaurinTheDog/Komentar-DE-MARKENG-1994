from pathlib import Path
from urllib.request import Request,urlopen
from datetime import datetime,timezone
from html.parser import HTMLParser
import zipfile,io,hashlib,json,xml.etree.ElementTree as E,shutil,re
W=Path(__file__).resolve().parent;D=W/'sources/review-p35-p54'
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,data):self.parts.append(data)
fetches=json.loads((D/'fetches.json').read_text())
urls=[('nivea.zip','https://www.rechtsprechung-im-internet.de/jportal/docs/bsjrs/jb-KORE301012015.zip'),('patg-81.html','https://www.gesetze-im-internet.de/patg/__81.html')]+[(f'zpo-{n}.html',f'https://www.gesetze-im-internet.de/zpo/__{n}.html') for n in [325,66,67,68,69,70,71,72,73,74,76]]
for name,url in urls:
 if any(f['path']==str((D/name).relative_to(W)) for f in fetches):continue
 now=datetime.now(timezone.utc).isoformat()
 with urlopen(Request(url,headers={'User-Agent':'OpenCommentary-bounded-review/1.0'}),timeout=40) as r:body=r.read();st=r.status;typ=r.headers.get('Content-Type');final=r.url
 assert st==200;p=D/name;p.write_bytes(body)
 if name.endswith('.zip'):
  z=zipfile.ZipFile(io.BytesIO(body));assert z.testzip() is None
  ns=[x for x in z.namelist() if x.endswith('.xml')];assert len(ns)==1
  raw=z.read(ns[0]);root=E.fromstring(raw);assert root.findtext('aktenzeichen')=='I ZB 65/13';p.with_suffix('.xml').write_bytes(raw)
  check='ZIP CRC validated; single XML with docket I ZB 65/13 parsed'
 else:
  assert b'<html' in body[:2000].lower() and b'jurAbsatz' in body
  parser=Text();parser.feed(body.decode('iso-8859-1'));p.with_suffix('.txt').write_text('\n'.join(x.strip() for x in parser.parts if x.strip()))
  check='Official HTML signature and jurAbsatz statutory text checked; readable extract preserved'
 fetches.append(dict(url=url,final_url=final,accessed_at=now,http_status=st,content_type=typ,path=str(p.relative_to(W)),sha256=hashlib.sha256(body).hexdigest(),format_validation=check,captured_body_sha256_verified=True))
 (D/'fetches.json').write_text(json.dumps(fetches,ensure_ascii=False,indent=2)+'\n')
 print(name,st,len(body),flush=True)
shutil.copyfile('/Volumes/LaCie/law-intake/eu/de/rii/rii-kore301012015.md',D/'nivea-local.md')
