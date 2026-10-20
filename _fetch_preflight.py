#!/usr/bin/env python3
"""Capture official source bodies and validate their formats before use."""
from pathlib import Path
from urllib.request import Request, urlopen
import datetime, hashlib, json, zipfile, io, xml.etree.ElementTree as ET
W=Path(__file__).resolve().parent
D=W/'sources/preflight-2026-10-20';D.mkdir(exist_ok=True)
targets=[('index.html','https://www.gesetze-im-internet.de/markeng/','html'),('markeng.zip','https://www.gesetze-im-internet.de/markeng/xml.zip','zip'),('full.html','https://www.gesetze-im-internet.de/markeng/BJNR308210994.html','html'),('amendment-2026-152.pdf','https://www.recht.bund.de/bgbl/1/2026/152/regelungstext.pdf?__blob=publicationFile&v=1','pdf'),('amendment-2026-9.pdf','https://www.recht.bund.de/bgbl/1/2026/9/regelungstext.pdf?__blob=publicationFile&v=1','pdf')]
fetches=[]
for name,url,fmt in targets:
 now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 try:
  with urlopen(Request(url,headers={'User-Agent':'OpenCommentary-source-verification/1.0'}),timeout=45) as response:
   body=response.read();status=response.status;ct=response.headers.get('Content-Type');final=response.url
  p=D/name;p.write_bytes(body)
  if fmt=='zip':
   z=zipfile.ZipFile(io.BytesIO(body));assert z.testzip() is None
   names=[n for n in z.namelist() if n.endswith('.xml')];assert names==['BJNR308210994.xml'],names
   xml=z.read(names[0]);r=ET.fromstring(xml);assert r.tag=='dokumente'
   assert r.findtext('norm/metadaten/jurabk')=='MarkenG' and r.findtext('norm/metadaten/amtabk')=='MarkenG'
   (D/'markeng.xml').write_bytes(xml)
   validation='ZIP CRC verified; single BJNR308210994.xml parsed as dokumente; jurabk/amtabk MarkenG'
  elif fmt=='pdf':
   assert body.startswith(b'%PDF-') and b'%%EOF' in body[-2048:]
   validation='PDF magic and EOF checked; complete text extraction follows'
  else:
   assert b'<html' in body[:2000].lower() and b'Marken' in body
   validation='HTML signature and expected MarkenG title checked'
  fetches.append(dict(url=url,final_url=final,accessed_at=now,http_status=status,content_type=ct,sha256=hashlib.sha256(body).hexdigest(),path=str(p.relative_to(W)),format_validation=validation))
  print(name,status,len(body),fetches[-1]['sha256'],flush=True)
 except Exception as e:
  fetches.append(dict(url=url,accessed_at=now,error=str(e)));print(name,str(e),flush=True)
(D/'fetches.json').write_text(json.dumps(fetches,ensure_ascii=False,indent=2)+'\n')
