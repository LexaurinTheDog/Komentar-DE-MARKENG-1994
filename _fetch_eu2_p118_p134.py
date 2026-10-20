from pathlib import Path
from urllib.request import Request,urlopen
from datetime import datetime,timezone
import json,hashlib,zipfile,io,xml.etree.ElementTree as E,subprocess,shutil
from html.parser import HTMLParser
W=Path(__file__).resolve().parent;D=W/'sources/review-p118-p134'
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,s):self.parts.append(s)
items=[('umv-eli.pdf','https://eur-lex.europa.eu/eli/reg/2017/1001/2025-12-01/deu/pdf','pdf'),('craft-eli.pdf','https://eur-lex.europa.eu/eli/reg/2023/2411/oj/deu/pdf','pdf'),('geneva-eli.pdf','https://eur-lex.europa.eu/eli/reg/2019/1753/2025-12-01/deu/pdf','pdf'),('peek-encoded.pdf','https://eur-lex.europa.eu/legal-content/DE/TXT/PDF/?uri=CELEX%3A62017CJ0148&from=DE','pdf')]
f=json.loads((D/'fetches.json').read_text())
for name,url,kind in items:
 if any(x['path']==str((D/name).relative_to(W)) for x in f):continue
 now=datetime.now(timezone.utc).isoformat()
 try:
  with urlopen(Request(url,headers={'User-Agent':'OpenCommentary-review/1.0'}),timeout=45) as r:body=r.read();status=r.status;ct=r.headers.get('Content-Type');final=r.url
  p=D/name;p.write_bytes(body);assert status==200
  if kind=='zip':
   z=zipfile.ZipFile(io.BytesIO(body));assert z.testzip() is None;ns=[x for x in z.namelist() if x.endswith('.xml')];assert len(ns)==1
   raw=z.read(ns[0]);root=E.fromstring(raw);p.with_suffix('.xml').write_bytes(raw);check='ZIP CRC validated, unique XML parsed, docket '+str(root.findtext('aktenzeichen'))
   p.with_suffix('.txt').write_text('\n\n'.join(''.join(x.itertext()).strip() for tag in ['tenor','tatbestand','entscheidungsgruende'] for x in root.findall(tag+'/div')))
  elif kind=='pdf':
   assert body.startswith(b'%PDF-') and b'%%EOF' in body[-2048:];subprocess.run(['pdftotext','-layout',str(p),str(p.with_suffix('.txt'))],check=True);assert p.with_suffix('.txt').stat().st_size>1000;check='PDF signature/EOF checked; actual text extracted'
  else:
   assert b'<html' in body[:2000].lower() and len(body)>3000
   h=Text();h.feed(body.decode('iso-8859-1' if 'gesetze-im-internet' in url else 'utf-8'));p.with_suffix('.txt').write_text('\n'.join(s.strip() for s in h.parts if s.strip()));check='HTML parsed, extracted text retained; content checked before reliance'
  f.append(dict(url=url,final_url=final,accessed_at=now,http_status=status,content_type=ct,path=str(p.relative_to(W)),sha256=hashlib.sha256(body).hexdigest(),format_validation=check));(D/'fetches.json').write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n');print(name,status,len(body),flush=True)
 except Exception as e:
  with (D/'fetch-errors.jsonl').open('a') as h:h.write(json.dumps(dict(url=url,at=now,error=str(e)))+'\n')
  print(name,'ERROR',str(e),flush=True)
for slug,doc in [('himalaya','KORE303842016'),('senioritaet','KORE300632019'),('patentanwaltskosten','KORE310532023')]:
 shutil.copyfile(Path('/Volumes/LaCie/law-intake/eu/de/rii')/('rii-'+doc.lower()+'.md'),D/(slug+'-local.md'))
