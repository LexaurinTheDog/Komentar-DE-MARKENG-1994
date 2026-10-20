from pathlib import Path
from urllib.request import Request,urlopen
from datetime import datetime,timezone
import json,hashlib,zipfile,io,xml.etree.ElementTree as E,shutil,subprocess
from html.parser import HTMLParser
W=Path(__file__).resolve().parent;D=W/'sources/review-p152-p164'
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,s):self.parts.append(s)
items=[('boss.pdf','https://juris.bundesgerichtshof.de/cgi-bin/rechtsprechung/document.py?Art=en&Blank=1.pdf&Datum=2005-7-21&Gericht=bgh&anz=31&nr=34261&pos=22','pdf'),('stgb-2.html','https://www.gesetze-im-internet.de/stgb/__2.html','html'),('owig-4.html','https://www.gesetze-im-internet.de/owig_1968/__4.html','html'),('egbgb-229-6.html','https://www.gesetze-im-internet.de/bgbeg/art_229__6.html','html')]
f=json.loads((D/'fetches.json').read_text())
for name,url,kind in items:
 now=datetime.now(timezone.utc).isoformat()
 try:
  with urlopen(Request(url,headers={'User-Agent':'OpenCommentary-review/1.0'}),timeout=45) as r:body=r.read();status=r.status;ct=r.headers.get('Content-Type');final=r.url
  p=D/name;p.write_bytes(body);assert status==200
  if kind=='pdf':
   assert body.startswith(b'%PDF-') and b'%%EOF' in body[-2048:]
   subprocess.run(['pdftotext','-layout',str(p),str(p.with_suffix('.txt'))],check=True);assert 'I ZR 312/02' in p.with_suffix('.txt').read_text();check='PDF magic/EOF checked, pdftotext parsed, expected docket present'
  else:
   assert b'<html' in body[:2000].lower() and len(body)>1000
   h=Text();h.feed(body.decode('iso-8859-1'));p.with_suffix('.txt').write_text('\n'.join(s.strip() for s in h.parts if s.strip()));check='HTML signature checked; text extracted for targeted reference reading'
  f.append(dict(url=url,final_url=final,accessed_at=now,http_status=status,content_type=ct,path=str(p.relative_to(W)),sha256=hashlib.sha256(body).hexdigest(),format_validation=check))
  (D/'fetches.json').write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n');print(name,status,len(body),flush=True)
 except Exception as e:
  with (D/'fetch-errors.jsonl').open('a') as o:o.write(json.dumps(dict(url=url,accessed_at=now,error=str(e)))+'\n')
  print(name,type(e).__name__,str(e),flush=True)
