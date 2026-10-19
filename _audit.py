#!/usr/bin/env python3
"""Independent raw-XML coverage/character audit and local output QA. Does not import _parse."""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,re,hashlib,collections,sys,difflib,datetime
W=Path(__file__).resolve().parent
R=ET.parse(W/'sources/markeng.xml').getroot()
U=[json.loads(s) for s in (W/'units.jsonl').read_text().splitlines() if s.strip()]
expected=[];raw={};struct=[];other=[]
compact=lambda s:re.sub(r'\s+','',s)
for n in R.findall('norm'):
 label=n.findtext('metadaten/enbez') or ''
 if n.find('metadaten/gliederungseinheit') is not None:struct.append(n.attrib['doknr']);continue
 if label.startswith('(XXXX)'):
  assert label=='(XXXX) §§ 161 bis 163'
  expected.extend(['p161','p162','p163']);raw.update({f'p{x}':'(weggefallen)' for x in range(161,164)});continue
 m=re.fullmatch(r'§ (\d+[a-z]?)',label)
 if m:
  ident='p'+m[1];expected.append(ident);e=n.find('textdaten/text/Content');raw[ident]=''.join(e.itertext()) if e is not None else '';continue
 other.append(dict(doknr=n.attrib['doknr'],label=label or 'Act metadata and introductory footnotes'))
ids=[u['id'] for u in U];mismatch=[]
for u in U:
 if compact(u['text'])!=compact(raw.get(u['id'],'')):mismatch.append(u['id'])
# All commentary markers, including duplicates (the builder dictionary alone can conceal them).
markers=[];comments={}
for p in sorted((W/'commentary').glob('*.md')):
 for m in re.finditer(r'(?m)^=== (\S+)\s*\n(.*?)(?=^=== |\Z)',p.read_text(),re.S|re.M):markers.append(m[1]);comments[m[1]]=m[2].strip()
duplicates=[k for k,v in collections.Counter(markers).items() if v>1]
paras=collections.defaultdict(list)
for ident,s in comments.items():
 for p in re.split(r'\n\s*\n',s):
  if len(p)>150:paras[p].append(ident)
repeated=[v for k,v in paras.items() if len(set(v))>1]
# Repeated long exact sentences signal template reuse, but findings are reported rather than hidden.
sentences=collections.defaultdict(set)
for ident,s in comments.items():
 for p in re.split(r'(?<=[.!?])\s+',s):
  if len(p)>100:sentences[p].add(ident)
rs=[dict(sentence=k,ids=sorted(v)) for k,v in sentences.items() if len(v)>1]
report=dict(checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),expected_basis='Independent enumeration of all raw operative XML metadata; no parser import and no copying parsed ids',xml_sha256=hashlib.sha256((W/'sources/markeng.xml').read_bytes()).hexdigest(),expected_ids=expected,parsed_ids=ids,expected_count=len(expected),parsed_count=len(ids),missing=sorted(set(expected)-set(ids)),unexpected=sorted(set(ids)-set(expected)),duplicates=[k for k,v in collections.Counter(ids).items() if v>1],xml_character_mismatch=mismatch,comparison='Exact character sequence after removing whitespace only; grouped repeal §§ 161–163 explicitly expanded',structural_record_count=len(struct),other_records=other,annex_disposition=[dict(label=n.findtext('metadaten/enbez'),handling='Operative annex included') for n in R if 'Anlage' in (n.findtext('metadaten/enbez') or '')] or ['No annex metadata record in complete official XML; no annex entry in official contents'],repealed_slots=[dict(id=u['id'],text=u['text']) for u in U if 'weggefallen' in u['title']],commented_count=len(comments),missing_commentary=sorted(set(ids)-set(comments)),extra_commentary=sorted(set(comments)-set(ids)),duplicate_commentary=duplicates,commentary_characters=sum(map(len,comments.values())),repeated_paragraphs=repeated,repeated_long_sentences=rs)
report['ok']=not any(report[k] for k in ['missing','unexpected','duplicates','xml_character_mismatch','missing_commentary','extra_commentary','duplicate_commentary','repeated_paragraphs'])
(W/'completeness-independent.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
# Compare preserved intake provision text, never rewrite intake.
s=(W/'sources/intake-2026-10-02.md').read_text();hs=list(re.finditer(r'(?m)^#{2,4} (.+)$',s));old={}
for i,h in enumerate(hs):
 m=re.match(r'§ (\d+[a-z]?) ',h[1])
 if m:
  tail=s[h.end():hs[i+1].start() if i+1<len(hs) else len(s)]
  body=tail if tail.startswith('\n\n') else tail.split('\n\n',1)[1]
  old['p'+m[1]]=body.split('\nFußnote:')[0].strip()
changes=[]
for u in U:
 if u['id'] in old and compact(old[u['id']])!=compact(u['text']):changes.append(u['id'])
change=dict(original_intake_path='/Volumes/LaCie/law-intake/eu/de/gesetze/gii-markeng.md',preserved_intake='sources/intake-2026-10-02.md',original_sha256=hashlib.sha256((W/'sources/intake-2026-10-02.md').read_bytes()).hexdigest(),current_xml_sha256=report['xml_sha256'],comparison='All 190 individually headed intake provisions compared after removing whitespace only; three grouped repeal slots separately accounted for',compared_individual_units=len(old),changed_individual_units=changes,grouped_repeal_disposition='Original grouped §§ 161–163 retained as three explicit empty slots, no substantive insertion',statutory_change_since_intake=bool(changes),format_changes=['XML list and paragraph boundaries preserved in canonical Markdown','Official structure separated from operative text','Grouped repeal expanded for individual coverage'],version_note='Both intake and current XML list Art. 14 G v. 20.5.2026 I Nr. 152; commencement independently checked in BGBl. Art. 18(1): 1 October 2026. Earlier Art. 5 G v. 11.1.2026 I Nr. 9 effective 16 January 2026.')
(W/'sources/change-map.json').write_text(json.dumps(change,ensure_ascii=False,indent=2)+'\n')
# Output links in authored pages (raw source snapshots are evidence, not authored navigation).
meta=json.loads((W/'meta.json').read_text());out=Path(meta['repo_dir']);broken=[];links=0
if out.exists():
 for p in list(out.glob('*.md'))+list((out/'cases').glob('*.md')):
  for dest in re.findall(r'\]\(([^)]+)\)',p.read_text()):
   dest=dest.split('#')[0]
   if not dest or re.match(r'[a-z]+:',dest):continue
   links+=1
   if not (p.parent/dest).exists():broken.append(dict(file=str(p.relative_to(out)),target=dest))
quality=dict(units=len(U),commentary_chars=report['commentary_characters'],minimum_commentary_chars=min(map(len,comments.values())),below_700=[dict(id=i,chars=len(s)) for i,s in comments.items() if len(s)<700],exact_repeated_paragraphs=repeated,repeated_long_sentences=rs,checked_output_links=links,broken_local_links=broken,placeholder_matches=[])
for i,s in comments.items():
 if re.search(r'\b(TODO|FIXME|TBD)\b|lorem ipsum',s,re.I):quality['placeholder_matches'].append(i)
(W/'quality-report.json').write_text(json.dumps(quality,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(completeness_ok=report['ok'],units=len(U),character_mismatches=mismatch,commented=len(comments),repeated_paragraphs=repeated,repeated_sentences=len(rs),intake_changed=changes,broken_links=broken),ensure_ascii=False))
sys.exit(0 if report['ok'] and not broken and not quality['placeholder_matches'] else 1)
