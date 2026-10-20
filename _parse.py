#!/usr/bin/env python3
"""Reproduce canonical text and units from the preserved GII XML; no manual statute edits."""
from pathlib import Path
import xml.etree.ElementTree as E
import re,json,hashlib,collections
W=Path(__file__).resolve().parent
R=E.parse(W/'sources/markeng.xml').getroot()
def clean(t):return re.sub(r'[ \t\r\f\v]+',' ',t).strip()
def render(e):
 if e is None:return ''
 s=e.text or ''
 for c in e:
  if c.tag=='BR':s+='\n'
  elif c.tag=='DL':s+='\n'+render(c)+'\n'
  elif c.tag=='DT':s+='\n'+render(c)+' '
  elif c.tag in ('P','row'):s+='\n\n'+render(c)+'\n\n'
  elif c.tag=='entry':s+=render(c)+' | '
  else:s+=render(c)
  s+=c.tail or ''
 return s

def txt(e):return '\n'.join(clean(l) for l in render(e).strip().splitlines()).strip()
# Legal thematic chapters, preserving official hierarchy inside each chapter.
ranges=[(13,'grundlagen','Grundlagen und Eintragungshindernisse'),(19,'verletzung','Schutzinhalt und Rechtsdurchsetzung'),(31,'schranken-vermoegen','Schranken und Vermögensverkehr'),(47,'eintragung','Eintragung, Widerspruch und Verlängerung'),(55,'bestand','Verfall und Nichtigkeit'),(65,'amt','Verfahren vor dem Deutschen Patent- und Markenamt'),(82,'patentgericht','Verfahren vor dem Bundespatentgericht'),(96,'rechtsmittel','Rechtsbeschwerde und gemeinsame Verfahrensregeln'),(106,'kollektiv-gewaehrleistung','Kollektiv- und Gewährleistungsmarken'),(125,'international','Internationale Registrierungen und Unionsmarken'),(139,'herkunft','Geografische Herkunftsangaben'),(151,'durchsetzung','Kennzeichenstreitsachen, Sanktionen und Zoll'),(164,'uebergang','Übergangsrecht')]
units=[]; canonical=[]; hierarchy=[]; disposition=[]
for n in R.findall('norm'):
 m=n.find('metadaten');g=m.find('gliederungseinheit');en=m.findtext('enbez') or ''
 if g is not None:
  key=g.findtext('gliederungskennzahl'); depth=len(key)//3
  h=clean((g.findtext('gliederungsbez') or '')+' — '+(g.findtext('gliederungstitel') or '').replace('\n',' '))
  hierarchy=hierarchy[:depth-1]+[h];canonical.append('## '+h)
  disposition.append(dict(record=n.attrib['doknr'],type='structural_heading',heading=h,handling='Retained in structure, not an operative provision.'))
  assert not txt(n.find('textdaten/text/Content')),n.attrib['doknr']
  continue
 body=txt(n.find('textdaten/text/Content')); notes=txt(n.find('textdaten/fussnoten/Content'))
 if en=='Inhaltsübersicht':
  disposition.append({'record':n.attrib['doknr'],'type':'official_contents','handling':'Independently checked against operative records; not a separate statutory unit.'});continue
 if not en:
  assert not body,('Unclassified unnumbered operative text',n.attrib['doknr'])
  if notes:canonical.append(notes)
  disposition.append(dict(record=n.attrib['doknr'],type='act_header',handling='No text/Content or separate Eingangsformel; official introductory footnotes retained in canonical text and sources/introductory-notes.md.',notes=notes))
  (W/'sources/introductory-notes.md').write_text('# Amtliche einleitende Fußnoten\n\n'+notes+'\n')
  continue
 if en.startswith('(XXXX)'):
  title=m.findtext('titel') or ''; assert '161 bis 163' in en+title
  assert not body and title=='(weggefallen)'
  labels=[en];body=clean(title)
  disposition.append({'record':n.attrib['doknr'],'type':'grouped_repeal','official_label':en,'unit_id':'p161-163','covered_numbers':['161','162','163'],'text_origin':'metadaten/titel; text/Content is empty','handling':'One official record retained; (XXXX) is the source technical label, not statutory wording.'})
 else: labels=[en]
 for label in labels:
  if en.startswith('(XXXX)'):num=161;ident='p161-163'
  else:
   match=re.fullmatch(r'§ (\d+)([a-z]?)',label); assert match,label
   num=int(match[1]); ident='p'+match[1]+match[2]
  chapter=next(i+1 for i,(end,_,__) in enumerate(ranges) if num<=end)
  # 106a-h belong with certification marks, already chapter 9.
  title=clean((m.findtext('titel') or '').replace('\n',' ')) if not en.startswith('(XXXX)') else '(weggefallen)'
  if not body and title=='(weggefallen)':body='(weggefallen)'
  assert body,(label,title)
  u=dict(id=ident,label=label,title=title,chapter=chapter,structure=list(hierarchy),text=body,notes=[notes] if notes else [],xml_doknr=n.attrib['doknr'])
  if en.startswith('(XXXX)'):u.update(covered_numbers=['161','162','163'],text_origin='metadaten/titel (empty text/Content)')
  units.append(u);canonical.extend(['### '+label+' — '+title,body]+([notes] if notes else []))
(W/'units.jsonl').write_text(''.join(json.dumps(u,ensure_ascii=False)+'\n' for u in units))
(W/'sources/canonical.md').write_text('\n\n'.join(canonical)+'\n')
meta=dict(cc='de',lang='de',repo='Komentar-DE-MARKENG-1994',repo_dir='/Volumes/LaCie/open-commentary/de/Komentar-DE-MARKENG-1994',title='Kommentar zum Markengesetz',source_path=str(W/'sources/canonical.md'),intro_file='00-einleitung.md',intro_desc='Einleitung und Methode',labels=dict(text='Wortlaut der Vorschrift',chapter='Kommentarkapitel',notes='Amtliche Fußnote'),chapters=[dict(n=i+1,slug=s,title=t) for i,(_,s,t) in enumerate(ranges)])
(W/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
# Secondary coverage evidence from official contents; operative metadata supplies the
# grouped repeal and empty § 164, which the contents table omits.
toc=R.findall('norm')[1]
expected=[]
for ent in toc.findall('.//entry'):
 s=clean(''.join(ent.itertext()))
 if re.fullmatch(r'§\s*\d+[a-z]?',s):expected.append('p'+re.sub(r'§\s*','',s))
grouped=[n for n in R.findall('norm') if (n.findtext('metadaten/enbez') or '').startswith('(XXXX)')]
assert len(grouped)==1 and grouped[0].findtext('metadaten/enbez')=='(XXXX) §§ 161 bis 163'
expected.append('p161-163')
# The official contents omits the operative empty record § 164; audit it independently.
assert any(n.findtext('metadaten/enbez')=='§ 164' for n in R.findall('norm'))
expected.append('p164') if 'p164' not in expected else None
ids=[u['id'] for u in units]
report=dict(xml_sha256=hashlib.sha256((W/'sources/markeng.xml').read_bytes()).hexdigest(),expected_basis='Official XML Inhaltsübersicht entry nodes plus the grouped §§ 161–163 and empty § 164 operative metadata records omitted by that table; source grouping preserved.',expected_ids=expected,parsed_ids=ids,expected_count=len(expected),parsed_count=len(ids),covered_paragraph_numbers=sum(len(u.get('covered_numbers',[u['id']])) for u in units),missing=sorted(set(expected)-set(ids)),unexpected=sorted(set(ids)-set(expected)),duplicates=[k for k,v in collections.Counter(ids).items() if v>1],record_disposition=disposition,annex_disposition='No operative annex record exists in the complete preserved XML or official contents. The XML contents ends at § 160; the grouped §§ 161–163 and § 164 follow as operative metadata records.',empty_repealed=[u['id'] for u in units if 'weggefallen' in u['title'] or u['text']=='(weggefallen)'])
report['ok']=not(report['missing'] or report['unexpected'] or report['duplicates'])
(W/'completeness.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['expected_ids','parsed_ids','non_provision_records']},ensure_ascii=False))
