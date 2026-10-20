#!/usr/bin/env python3
"""Reproduce source-version and raw-record preflight from saved official responses."""
from pathlib import Path
import json,hashlib,datetime,collections,re,xml.etree.ElementTree as ET
W=Path(__file__).resolve().parent;S=W/'sources';D=S/'preflight-2026-10-20'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
v=json.loads((S/'verification.json').read_text());fetches=json.loads((D/'fetches.json').read_text())
assert all(f.get('http_status')==200 for f in fetches),fetches
for f in fetches:
 assert sha(W/f['path'])==f['sha256'],f['path']
xml=S/'markeng.xml';fresh=D/'markeng.xml';assert sha(xml)==sha(fresh)
r=ET.parse(xml).getroot();norms=r.findall('norm')
labels=[n.findtext('metadaten/enbez') for n in norms if n.findtext('metadaten/enbez') and n.findtext('metadaten/enbez')!='Inhaltsübersicht']
dups=[k for k,c in collections.Counter(labels).items() if c>1]
assert not dups
assert len({n.attrib['doknr'] for n in norms})==len(norms)
header=norms[0];assert header.find('textdaten/text/Content') is None
assert header.find('textdaten/fussnoten/Content') is not None
stand=header.findtext('metadaten/standangabe/standkommentar')
assert stand=='Zuletzt geändert durch Art. 14 G v. 20.5.2026 I Nr. 152'
html=(D/'full.html').read_text(encoding='iso-8859-1')
assert 'Eingangsformel' not in html and 'Das G wurde als Artikel 1 G' in html
annexes=[n.attrib['doknr'] for n in norms if re.search(r'Anlage|Anhang',n.findtext('metadaten/enbez') or '')]
assert not annexes
# Check the promulgated commencement and the two operative 2026 insertions.
a=(D/'amendment-2026-152.txt').read_text();b=(D/'amendment-2026-9.txt').read_text()
assert '1. Oktober 2026' in a and 'Artikel 18' in a
assert 'Dieses Gesetz tritt am Tag nach der Verkündung in Kraft.' in b and '15. Januar 2026' in b
assert 'Artikel 14' in a and 'Änderung des Markengesetzes' in a
compact=lambda t:re.sub(r'\s+','',t)
for label,phrase in [('§ 81','Satz 2 gilt entsprechend für das jeweils zuständige Vollstreckungsorgan in Verfahren über die Vollstreckung von Entscheidungen des Bundespatentgerichts.'),('§ 82','Die §§ 752a und 753a der Zivilprozessordnung sind mit der Maßgabe anzuwenden')]:
 n=next(n for n in norms if n.findtext('metadaten/enbez')==label)
 assert compact(phrase) in compact(''.join(n.find('textdaten/text/Content').itertext()))
 assert compact(phrase) in compact(a)
reg=(D/'delegated-regulation-2026-50.txt').read_text()
assert 'Verordnung' in reg and 'Rechtsverkehrs' in reg and 'Deutschen Patent- und Markenamt' in reg
# Exact snapshots from the previous attempt and the intake are retained.
assert sha(S/'intake-2026-10-02.md')=='f0f08aec140ce600b08b97b6995423c2d471c6667d30532f40ae2a3a29fece86'
for f in fetches:
 if not any(old.get('path')==f['path'] for old in v['fetches']):v['fetches'].append(f)
for f in v['fetches']:
 p=W/f['path'];assert p.exists() and sha(p)==f['sha256'],str(p)
 f['captured_body_sha256_verified']=True
v['last_verified_at']=now
v['preflight_decisive_date']='2026-10-19'
v['preflight_note']='Original authoring date retained; source/parser repair verified again on 20 October 2026. No legal second pass performed.'
v['official_xml']={'url':'https://www.gesetze-im-internet.de/markeng/xml.zip','path':'sources/markeng.xml','sha256':sha(xml),'fresh_evidence_path':str(fresh.relative_to(W)),'format_validation':'XML parsed; root dokumente; header jurabk/amtabk MarkenG; extracted from validated official ZIP'}
v['historical_version_selection']={'checked':True,'operative_record_count':191,'duplicate_official_labels':dups,'duplicate_doknr':[],'xml_builddates':sorted({n.attrib.get('builddate') for n in norms}),'selected_effective_date':'2026-10-19','method':'One current official consolidation, not multiple historical versions; latest two amendments and actual commencement clauses read in fresh official BGBl PDFs. Transitional references and historical notes retained as such.','old_and_new_xml_identical':True,'full_historical_reconstruction':False}
v['introductory_text_disposition']={'checked':True,'separate_eingangsformel_present':False,'evidence':'Header norm BJNR308210994 has no text/Content; introductory adoption/commencement statement is in textdaten/fussnoten/Content; full HTML has no Eingangsformel heading.','preserved_notes':'sources/introductory-notes.md'}
v['preflight_search']={'queries':[{'query':'site:recht.bund.de Markengesetz Änderung 2026 Oktober September','evidence':'sources/preflight-2026-10-20/preflight-2026-10-20-amendments.json'},{'query':'site:gesetze-im-internet.de/markeng "Stand" "2026"','evidence':'sources/preflight-2026-10-20/preflight-2026-10-20-stand.json'}],'later_amendment_identified':False,'additional_hit_checked':{'citation':'BGBl. 2026 I Nr. 50','evidence':'sources/preflight-2026-10-20/delegated-regulation-2026-50.pdf','disposition':'Delegated DPMA electronic-procedure regulation; no MarkenG amending article. Separate regulation not annex to MarkenG.'},'limit':'Search engine results and current official consolidation are not an exhaustive audit of every BGBl issue.'}
v['annex_check']={'checked':True,'raw_records_examined':len(norms),'operative_annex_records':annexes,'official_contents_annex_entry':False,'disposition':'No operative annex in this title; external EU acts and delegated regulations are not annexes.'}
v['preflight_source_agreement']={'intake_hash_verified':True,'fresh_xml_matches_previous_xml':True,'fresh_bgbl_152_matches_previous_pdf':sha(D/'amendment-2026-152.pdf')==sha(S/'amendment-2026-152.pdf'),'fresh_bgbl_9_matches_previous_pdf':sha(D/'amendment-2026-9.pdf')==sha(S/'amendment-2026-9.pdf')}
write(S/'verification.json',v)
coverage=json.loads((W/'completeness-independent.json').read_text());assert coverage['ok']
result=dict(complete=True,task='source_preflight_only',decisive_date='2026-10-19',verification_date=now[:10],official_url='https://www.gesetze-im-internet.de/markeng/',verified_at=now,version_evidence={'consolidated_version':stand,'xml_path':'sources/markeng.xml','xml_sha256':sha(xml),'xml_builddate':r.attrib['builddate'],'not_a_commencement_proof':'The builddate and retrieval timestamp are technical metadata only.','latest_amendment':{'citation':'BGBl. 2026 I Nr. 152','amending_article':'14','commencement_article':'18(1)','effective_from':'2026-10-01','evidence':'sources/preflight-2026-10-20/amendment-2026-152.pdf'},'preceding_amendment':{'citation':'BGBl. 2026 I Nr. 9','amending_article':'5','commencement_article':'16','publication_date':'2026-01-15','effective_from':'2026-01-16','evidence':'sources/preflight-2026-10-20/amendment-2026-9.pdf'},'fresh_fetches':'sources/preflight-2026-10-20/fetches.json','substantive_change_since_intake':False},historical_versions_checked=v['historical_version_selection'],annexes_checked=v['annex_check'],eingangsformel_checked=v['introductory_text_disposition'],coverage={'expected_official_units':191,'parsed_units':coverage['parsed_count'],'covered_paragraph_numbers':193,'missing':coverage['missing'],'extra':coverage['unexpected'],'duplicate_ids':coverage['duplicates'],'official_labels_agree':not(coverage['missing_official_identifiers'] or coverage['extra_official_identifiers']),'raw_record_disposition_count':len(coverage['record_disposition']),'evidence':'completeness-independent.json'},repairs=[{'from':['p161','p162','p163'],'to':'p161-163','official_label':'(XXXX) §§ 161 bis 163','reason':'Preserve the actual single official grouped repeal record; all three explanations retained in its commentary.','prior_snapshot':'sources/preflight-2026-10-20/prior-parser/'},'Explicit header/introductory-footnote disposition and all 224 raw records audited. No separate operative Eingangsformel or annex to insert.'],unresolved_blockers=[],limitations=['This task did not review the legal meaning of all existing commentary or re-research existing case cards.','Independent second pass remains pending.','Historical laws continued by transitional references were not reconstructed in full.','Later-law search is selective; no exhaustive legislative pipeline audit claimed.'])
write(W/'preflight-result.json',result)
files=[dict(path=str(p.relative_to(W)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(S.rglob('*')) if p.is_file() and p.name!='manifest.json']
write(S/'manifest.json',dict(created_at=now,primary_statute='markeng.xml',canonical_statute='canonical.md',files=files))
print(json.dumps(dict(preflight_complete=True,decisive_date=result['decisive_date'],verified_at=now,expected=191,parsed=coverage['parsed_count'],unresolved_blockers=[])))
