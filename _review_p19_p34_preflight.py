#!/usr/bin/env python3
"""Fresh official-source checks for the bounded p19–p34 second pass."""
from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone
import hashlib, json, io, zipfile, re, collections, subprocess, sys
import xml.etree.ElementTree as ET

W = Path(__file__).resolve().parent
D = W/'sources/review-p19-p34'
D.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, obj): p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')
targets = [
 ('index.html', 'https://www.gesetze-im-internet.de/markeng/', 'html'),
 ('markeng.zip', 'https://www.gesetze-im-internet.de/markeng/xml.zip', 'statute'),
 ('amendment-2026-152.pdf', 'https://www.recht.bund.de/bgbl/1/2026/152/regelungstext.pdf?__blob=publicationFile&v=1', 'pdf'),
 ('amendment-2026-9.pdf', 'https://www.recht.bund.de/bgbl/1/2026/9/regelungstext.pdf?__blob=publicationFile&v=1', 'pdf')]
fetches = []
for filename, url, kind in targets:
 if '--reuse' in sys.argv:
  continue
 now = datetime.now(timezone.utc).isoformat()
 with urlopen(Request(url, headers={'User-Agent':'OpenCommentary-bounded-review/1.0'}), timeout=45) as r:
  body = r.read(); status = r.status; content_type = r.headers.get('Content-Type'); final_url = r.url
 p = D/filename; p.write_bytes(body)
 assert status == 200
 if kind in ('statute','case'):
  z = zipfile.ZipFile(io.BytesIO(body)); assert z.testzip() is None
  names = [n for n in z.namelist() if n.lower().endswith('.xml')]; assert len(names) == 1
  raw = z.read(names[0]); root = ET.fromstring(raw)
  xp = p.with_suffix('.xml'); xp.write_bytes(raw)
  assert sha(xp) == sha(W/'sources'/xp.name), 'Source changed: reselect effective version before reviewing'
  if kind == 'statute':
   assert root.tag == 'dokumente' and root.findtext('norm/metadaten/jurabk') == 'MarkenG'
   assert root.findtext('norm/metadaten/amtabk') == 'MarkenG'
  else:
   expected = 'I ZR 143/24' if filename.startswith('werktitel') else 'I ZR 86/22'
   assert expected in ''.join(root.itertext())
  validation = 'ZIP CRC checked; unique XML member parsed; identity and bytes compared with preserved official XML'
 elif kind == 'pdf':
  assert body.startswith(b'%PDF-') and b'%%EOF' in body[-2048:]
  subprocess.run(['pdftotext','-layout',str(p),str(p.with_suffix('.txt'))],check=True)
  assert sha(p) == sha(W/'sources'/filename)
  validation = 'PDF magic/EOF checked; text extracted; byte-identical to earlier promulgation snapshot'
 else:
  assert b'<html' in body[:2000].lower() and b'Marken' in body
  validation = 'HTML signature and expected title checked'
 fetches.append(dict(url=url,final_url=final_url,accessed_at=now,http_status=status,content_type=content_type,path=str(p.relative_to(W)),sha256=sha(p),format_validation=validation,captured_body_sha256_verified=True))
 print(filename, status, len(body), flush=True)
if '--reuse' in sys.argv:
 fetches = json.loads((D/'fetches.json').read_text())
 for f in fetches:
  assert sha(W/f['path']) == f['sha256']
else:
 save(D/'fetches.json',fetches)

root = ET.parse(D/'markeng.xml').getroot(); norms = root.findall('norm')
header = norms[0]; stand = header.findtext('metadaten/standangabe/standkommentar')
assert stand == 'Zuletzt geändert durch Art. 14 G v. 20.5.2026 I Nr. 152'
labels = [n.findtext('metadaten/enbez') for n in norms if n.findtext('metadaten/enbez') not in (None,'Inhaltsübersicht')]
assert len(labels) == len(set(labels)) == 191
assert len({n.attrib['doknr'] for n in norms}) == len(norms) == 224
annexes = [label for label in labels if re.search('Anlage|Anhang',label)]
assert not annexes
assert header.find('textdaten/text/Content') is None
assert header.find('textdaten/fussnoten/Content') is not None
a = (D/'amendment-2026-152.txt').read_text(); b = (D/'amendment-2026-9.txt').read_text()
assert '1. Oktober 2026' in a and 'Artikel 18' in a
assert 'Dieses Gesetz tritt am Tag nach der Verkündung in Kraft.' in b and '15. Januar 2026' in b
# Inspect the actual MarkenG amending articles separately from other statutes.
art14 = re.search(r'^\s*Artikel 14\s+Änderung des Markengesetzes(.*?)^\s*Artikel 15\s*$',a,re.S|re.M)[1]
art5 = re.search(r'^\s*Artikel 5\s+Änderung des Markengesetzes(.*?)^\s*Artikel 6\s*$',b,re.S|re.M)[1]
assert '§ 81' in art14 and '§ 82' in art14
assert not re.search(r'§\s*(?:[1-9]|1[0-8])[a-z]?\b',art14)
assert 'In § 4 Nummer 3' in art5 and '§ 6a' in art5 and '5. § 14 wird' in art5 and '6. In § 14a Absatz 2' in art5
save(D/'version-excerpts.json',dict(article_14_2026_152=art14,article_5_2026_9=art5,assigned_changes_2026_9={'p22':'Absatz 1 Nummer 2 neu gefasst (Art. 5 Nr. 7)','p26':'Absatz 5 Bezug auf Tag, ab dem kein Widerspruch mehr möglich war (Art. 5 Nr. 8)'},assigned_changes_2026_152=[],latest_commencement='2026-10-01',preceding_commencement='2026-01-16',decisive_date='2026-10-19',note='Technical build timestamp is not commencement proof; actual promulgation clauses read. Changes already incorporated in October intake.'))
# Verify the actual assigned 2026 changes and the limited external BGB references.
assert '7. § 22 Absatz 1 Nummer 2' in art5 and '8. In § 26 Absatz 5' in art5
bgb = ET.parse(D/'bgb.xml').getroot()
bgb_stand = [e.text for e in bgb.findall('norm/metadaten/standangabe/standkommentar')]
assert any('23.7.2026 I Nr. 226' in t for t in bgb_stand)
refs = []
for label in ['§ 195','§ 199','§ 811','§ 852']:
 ns = [n for n in bgb.findall('norm') if n.findtext('metadaten/enbez') == label]
 assert len(ns) == 1
 refs.append(dict(label=label,doknr=ns[0].attrib['doknr'],text=''.join(ns[0].find('textdaten/text/Content').itertext()),official_notes=''.join(ns[0].find('textdaten/fussnoten').itertext())))
t = (D/'bgb-amendment-2026-226.txt').read_text()
art6 = re.search(r'^\s*Artikel 6\s+Änderung des Bürgerlichen Gesetzbuches(.*?)^\s*Artikel 7\s*$',t,re.S|re.M)[1]
assert not re.search(r'§\s*(?:195|199|811|852)\b',art6)
assert 'Dieses Gesetz tritt vorbehaltlich der Absätze 2 bis 4 am Tag nach der Verkündung in Kraft.' in t
assert '28. Juli 2026' in t
save(D/'bgb-reference-check.json',dict(decisive_date='2026-10-19',checked_at=datetime.now(timezone.utc).isoformat(),current_xml_stand=bgb_stand,selected_references=refs,latest_amending_article=art6,latest_amendment_effective_from='2026-07-29',latest_amendment_affects_selected_references=False,method='Official XML current consolidation with unique selected records; current HTML pages read; latest BGB amending article and actual commencement clause read. No alternate/future version in the selected records.',limitation='No full BGB historical reconstruction or exhaustive pipeline audit.'))
subprocess.run(['python3','-I',str(W/'_audit.py')],check=True)
coverage = json.loads((W/'completeness-independent.json').read_text()); assert coverage['ok']
now = datetime.now(timezone.utc).isoformat()
verification = json.loads((W/'sources/verification.json').read_text())
verification['fetches'] += [f for f in fetches if f['path'] not in {x['path'] for x in verification['fetches']}]
verification['last_verified_at'] = now
verification['bounded_review_p19_p34'] = dict(verified_at=now,evidence='sources/review-p19-p34/fetches.json',version_excerpts='sources/review-p19-p34/version-excerpts.json',bgb_reference_check='sources/review-p19-p34/bgb-reference-check.json',decisive_date='2026-10-19',official_xml_unchanged=True,search_log='sources/review-p19-p34-amendments-search.json',firecrawl_extraction='sources/review-p19-p34-index-firecrawl.md',limit='Current consolidation plus selective later-amendment search; no exhaustive BGBl pipeline audit.')
save(W/'sources/verification.json',verification)
# Retain the earlier full preflight; add this fresh bounded-review confirmation.
preflight = json.loads((W/'preflight-result.json').read_text())
preflight['bounded_review_p19_p34_recheck'] = dict(complete=True,decisive_date='2026-10-19',official_url=targets[0][1],verified_at=now,version_evidence='sources/review-p19-p34/version-excerpts.json',fetches='sources/review-p19-p34/fetches.json',historical_versions_checked=dict(duplicate_labels=[],duplicate_doknr=[],method='Single current consolidation; fresh identical XML; both 2026 amendment articles and commencement clauses checked; no historical text concatenation.'),annexes_checked=dict(raw_records=224,operative_annexes=[],disposition='No operative annex in raw XML or contents; no separate Eingangsformel; introductory official notes preserved.'),coverage=dict(expected=191,parsed=191,missing=coverage['missing'],extra=coverage['unexpected'],xml_character_mismatch=coverage['xml_character_mismatch']),unresolved_blockers=[])
save(W/'preflight-result.json',preflight)
