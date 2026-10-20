#!/usr/bin/env python3
"""Persist the expressly bounded review findings and reproducible scope checks."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, subprocess, sys
import xml.etree.ElementTree as ET

W = Path(__file__).resolve().parent
BASELINE = '30a204fc011a3f6d6d276f9cc79a12051b64f7f2'
IDS = ['p1','p2','p3','p4','p5','p6','p6a','p7','p8','p9','p10','p11','p12','p13','p14','p14a','p15','p16','p17','p18']
def save(p, o): p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def sha_text(t): return hashlib.sha256(t.encode()).hexdigest()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def blocks(text): return {m[1]:m[2].strip() for m in re.finditer(r'^=== (\S+)\s*\n(.*?)(?=^=== |\Z)',text,re.S|re.M)}

# These are the substantive reading findings, not findings inferred from length.
NOTES = {
 'p1': ('retained', 'Drei Schutzgegenstände, verschiedene Entstehungs- und Anspruchsgrundlagen sowie das Verpackungsbeispiel gegen Wortlaut und §§ 4, 5, 14, 15, 126, 128 geprüft; keine materielle Korrektur erforderlich.'),
 'p2': ('corrected', 'Konkurrenzöffnung auf den Schutz derselben Kennzeichen präzisiert; das bisher nur benachbarte Porträtbeispiel durch eine mögliche kumulative Marken-/Urheberrechtsverletzung desselben Bildzeichens ersetzt. § 2 bleibt ohne eigene Anspruchsgrundlage; §§ 13 und 19d abgeglichen.'),
 'p3': ('retained', 'Abs. 1 abstrakte Markenfähigkeit von § 8 getrennt; Abs. 2 alle drei Ausschlüsse, ausschließliche Merkmalsgestaltung und fehlende Heilung durch Verkehrsdurchsetzung geprüft. Funktionales Griffbeispiel und Grenzen sind zutreffend.'),
 'p4': ('retained', 'Alle drei Erwerbswege, bloße Anmeldung gegenüber Eintragung, Verkehrsgeltungsnachweis, räumliche Reichweite und § 12 geprüft. Die erweiterte PVÜ-Zitierung aus Art. 5 Nr. 3 des Gesetzes 2026 I Nr. 9 ist im mechanischen Wortlaut enthalten; keine materielle Kommentarkorrektur erforderlich.'),
 'p5': ('corrected', 'Drei Absätze und unterschiedliche Kennzeichenfunktionen geprüft. Digitale Bezeichnungen nicht pauschal als Werktitel behandelt; Verkehrsgeltung für Zeichen nach Abs. 2 Satz 2 nicht auf jeden Titel übertragen. BGH I ZR 143/24, insbesondere Rn. 17–27, volltextgeprüft und Verweis präzisiert.'),
 'p6': ('retained', 'Bedingter Anwendungsbereich in Abs. 1, Anmeldung/ausländische und Ausstellungspriorität in Abs. 2, Erwerbstag in Abs. 3 und Taggleichheit in Abs. 4 geprüft. Keine Verwechslung von Eintragungsdatum, Gründungsdatum und Rechtserwerb.'),
 'p6a': ('corrected', 'Alle drei Zeichenkategorien und Einbeziehung des gesetzlichen PVÜ-Verweises konkretisiert; private Gütesiegel nicht pauschal amtlichen Zeichen gleichgestellt. Neues Verbot seit 16. Januar 2026 anhand Art. 5 Nr. 4 und Art. 16 des verkündeten Gesetzes 2026 I Nr. 9 geprüft und ergänzt. § 145 Abs. 1 Nr. 1 abgeglichen.'),
 'p7': ('corrected', 'Alle drei Inhaberkategorien, Rechtsfähigkeit und Vertretung sowie Sonderregeln §§ 98 und 106b geprüft. Ungenauen Ausdruck Verbandsmarke durch gesetzliche Kollektivmarke ersetzt; materieller Rest zutreffend.'),
 'p8': ('corrected', 'Zuvor zu knappe Sammeldarstellung durch einzelne Abgrenzungen der 14 Hindernisse erweitert. Darstellbarkeit, drei unterschiedliche Grundhindernisse, spezielle Herkunfts-/Wein-/Spezialitäten-/Sortenregeln, Bösgläubigkeit, Zeitpunkt der Verkehrsdurchsetzung und unterschiedliche Ausnahmen des Abs. 4 geprüft und erklärt. § 37 Abs. 3 und § 50 abgeglichen.'),
 'p9': ('corrected', 'Drei Kollisionsmodelle, Eintragung älterer Anmeldung und beidseitige Klassenneutralität geprüft. Nach § 51 Abs. 3 erforderliche Bekanntheit schon am Rangtag der jüngeren Marke ergänzt; Benutzungs- und Bestandsprüfung terminologisch präzisiert.'),
 'p10': ('corrected', 'Materieller Schutz, Inlandsnotorietät, Rang und Ermächtigung geprüft. Engere Amtsprüfung des § 37 Abs. 4 ergänzt: amtsbekannte Notorietät und § 9 Abs. 1 Nr. 1 oder 2, nicht schon Nr. 3. Registerfreiheit nicht mit genereller Amtszurückweisung gleichgesetzt.'),
 'p11': ('retained', 'Agenten-/Vertreterbeziehung, Zuordnung der Marke, fehlende Zustimmung und Rechtfertigungsvorbehalt gegen Wortlaut geprüft. Vertriebsbeispiel und Trennung von Löschung und Übertragung nach § 17 zutreffend; kein frei erfundenes Sonderverhältnis unterstellt.'),
 'p12': ('retained', 'Beide älteren Rechtsarten, Erwerb vor Rangtag und bundesweite Untersagungsbefugnis einzeln geprüft. Lokaler Altgebrauch wird zutreffend nicht mit bundesweitem Löschungsgrund gleichgesetzt; Gasthausbeispiel bleibt als offener Prüfungsfall erkennbar.'),
 'p13': ('retained', 'Abs. 1 ältere sonstige Rechte, Abgrenzung §§ 9–12, bundesweite Reichweite; Abs. 2 alle sechs Rechtsgruppen sowie Bild-/Urheberrechtsbeispiel geprüft. Keine Entstehung fremder Rechte durch § 13 behauptet; Checkliste sachbezogen.'),
 'p14': ('corrected', 'Sämtliche sieben Absätze geprüft. Benutzungsbezug, Markenfunktionen, Klassenneutralität, alle Handlungstypen und Vorbereitungsgefahr konkretisiert. Unterlassung ohne Verschulden, Schadensbemessung ohne Mehrfachentschädigung und Verschulden des Mitarbeiters bei Abs. 7 erklärt. DACHSER vollständig gelesen; unterstellte Bekanntheit und Einzelfallabwägung getrennt.'),
 'p14a': ('corrected', 'Inhaberschaft geschäftlicher Bezeichnungen und für derartige Waren eingetragene Marke ausdrücklich erläutert. Drittstaaten-/Transitfall, strenger Identitätsmaßstab, fehlende Zustimmung und Gegenbeweis durch zollrechtlichen Anmelder/Besitzer im bezeichneten Verfahren geprüft. Erforderlichen Nachweis nicht mit bloßer Exportabsicht gleichgesetzt; § 150 abgeglichen.'),
 'p15': ('corrected', 'Alle sechs Absätze geprüft; Wiederholungs-/Erstbegehungsgefahr und Verschuldenszurechnung präzisiert. BGH I ZR 143/24 vollständig gelesen; Werkidentität, Herkunftstäuschung, Aufgabe älterer nicht tragender Annahme, kumulative grundsätzlich unabhängige Voraussetzungen und fehlende Prozentquote ergänzt.'),
 'p16': ('corrected', 'Registerstatus, Gattungseindruck, Anspruch gegen Verleger und alle drei Absätze geprüft. Keine Pflicht zur eigens herzustellenden Neuauflage oder Rückruf aus Abs. 2 abgeleitet; entsprechende Datenbankanwendung ohne erfundene Änderungsfrist erläutert. § 49 Abs. 2 Nr. 1 verlangt zusätzliche Voraussetzungen; kein automatischer Verfall durch Lexikoneintrag.'),
 'p17': ('retained', 'Übertragung von Anmeldung oder Registerrecht, gesonderte Benutzungszustimmung bei eingetragener Agentenmarke, schuldhafter Schadensersatz, betriebliche Zurechnung und Rechtfertigung in Abs. 3 geprüft. Fiktive Weisung zur Fremdanmeldung trägt die Unterscheidung; keine Korrektur erforderlich.'),
 'p18': ('corrected', 'Vernichtung von Waren im Besitz oder Eigentum gegenüber Materialien/Geräten nur im Eigentum geprüft. Rückruf/endgültige Entfernung, fehlendes Verschuldenserfordernis und Verhältnismäßigkeit einschließlich Drittinteressen ergänzt. Etikettenbeispiel wird fallabhängig geprüft; kein automatischer Vernichtungsanspruch gegen beliebige Anlagen.')
}

current = {}; before = {}
baseline_path = W/'sources/review-p1-p18/commentary-baseline.json'
saved_baseline = json.loads(baseline_path.read_text()) if baseline_path.exists() else None
if saved_baseline:
 assert saved_baseline['work_baseline_commit'] == BASELINE
 before = saved_baseline['commentary']
for p in sorted((W/'commentary').glob('*.md')):
 current.update(blocks(p.read_text()))
 if not saved_baseline:
  old = subprocess.check_output(['git','-C',str(W),'show',BASELINE+':'+str(p.relative_to(W))],text=True)
  before.update(blocks(old))
if not saved_baseline:
 save(baseline_path,dict(work_baseline_commit=BASELINE,commentary=before))
assert current.keys() == before.keys()
assert set(IDS) == set(NOTES) and len(IDS) == 20
changed = [i for i in current if current[i] != before[i]]
assert set(changed) <= set(IDS), changed
assert len(changed) == 12
for i in IDS: assert (i in changed) == (NOTES[i][0] == 'corrected')
units = {u['id']:u for u in map(json.loads,(W/'units.jsonl').read_text().splitlines())}
norms = {n.attrib['doknr']:n for n in ET.parse(W/'sources/markeng.xml').getroot().findall('norm')}
compact = lambda s: re.sub(r'\s+','',s)
findings = []
for i in IDS:
 u = units[i]; n = norms[u['xml_doknr']]
 assert compact(u['text']) == compact(''.join(n.find('textdaten/text/Content').itertext()))
 findings.append(dict(id=i,label=u['label'],outcome=NOTES[i][0],finding=NOTES[i][1],resolved=True,source_xml_doknr=u['xml_doknr'],statutory_text_sha256=sha_text(u['text']),commentary_before_sha256=sha_text(before[i]),commentary_after_sha256=sha_text(current[i])))

case_checks=[]
for name, docket, scope, end in [('werktitel','I ZR 143/24',['p5','p15'],39),('dachser','I ZR 86/22',['p14'],46)]:
 r=ET.parse(W/'sources'/f'{name}.xml').getroot(); local=compact((W/'sources'/f'{name}-local.md').read_text()); count=0
 for tag in ['tenor','tatbestand','entscheidungsgruende']:
  for e in r.findall('.//'+tag+'//p'):
   t=''.join(e.itertext()).strip()
   if t:
    assert compact(t) in local, t[:120]
    count+=1
 case_checks.append(dict(docket=docket,court='BGH',date=r.findtext('entsch-datum'),ecli=r.findtext('ecli'),full_text_read=True,read_scope=f'Tenor, Rn. 1–{end}'+('; Berichtigungsbeschluss 12.07.2023' if name=='dachser' else ''),supported_reviewed_ids=scope,official_xml=f'sources/{name}.xml',fresh_xml=f'sources/review-p1-p18/{name}.xml',official_xml_sha256=sha(W/'sources'/f'{name}.xml'),corpus_path=f'sources/{name}-local.md',nonempty_official_paragraphs_compared=count,missing_from_read_corpus=0))

now=datetime.now(timezone.utc).isoformat()
limitations=[
 'Complete means this exact 20-unit assignment only; the remaining 171 commentary units have not received this second pass.',
 'Selective case law: the two existing relevant BGH decisions were read and verified again; no exhaustive new case-law survey for every unit.',
 'No new substantive review of the Patentanwaltskosten case card or commentary outside the assigned IDs.',
 'No complete reconstruction of historical statutes or separate consolidation of all cross-referenced EU, treaty and domestic rules; those are not reproduced from memory.',
 'Current official consolidation, both 2026 amending articles and commencement clauses checked; supplementary search is not an exhaustive BGBl pipeline audit.',
 'No external lawyer approval or legal errorlessness certification; technical tests are separate from the recorded substantive reading.'
]
technical=None
if '--validated' in sys.argv:
 technical=json.loads((W/'validation.json').read_text()); assert technical['ok'] and technical['verbatim_ratio']==1.0
coverage=json.loads((W/'completeness-independent.json').read_text());assert coverage['ok']
quality=json.loads((W/'quality-report.json').read_text());assert not quality['broken_local_links'] and not quality['exact_repeated_paragraphs']
result=dict(complete=True,task='bounded_independent_second_pass',units_reviewed=20,reviewed_ids=IDS,decisive_date='2026-10-19',reviewed_at=now,unresolved_blockers=[],findings=findings,limitations=limitations,changed_ids=changed,retained_ids=[i for i in IDS if i not in changed],whole_book_complete=False,work_baseline_commit=BASELINE,baseline_evidence=str(baseline_path.relative_to(W)),baseline_evidence_sha256=sha(baseline_path),unchanged_unassigned_units=171,unassigned_commentary_unchanged=True,case_checks=case_checks,source_preflight='preflight-result.json',source_verification='sources/verification.json',technical_validation=technical,technical_validation_pending=technical is None,completeness=dict(expected=coverage['expected_count'],parsed=coverage['parsed_count'],missing=coverage['missing'],extra=coverage['unexpected'],xml_character_mismatch=coverage['xml_character_mismatch'],repeated_paragraphs=coverage['repeated_paragraphs']),quality=dict(broken_links=quality['broken_local_links'],repeated_long_sentences=quality['repeated_long_sentences'],placeholder_matches=quality['placeholder_matches']))
save(W/'review-result.json',result)
status=json.loads((W/'status.json').read_text())
status.update(stage='bounded_second_pass_complete',task_scope='Exactly p1–p18 including p6a and p14a; no whole-book review completion.',reviewed_ids=IDS,units_reviewed=20,review_result='review-result.json',review_completed_at=now,whole_book_review_complete=False,independent_second_pass='completed for assigned 20 units; remaining 171 pending',updated_at=now,remaining_limitations=limitations,unresolved_blockers=[])
status['source_checks']['latest_verification']=now
status['commentary_characters']=sum(map(len,current.values()))
status['case_law_provenance']='I ZR 143/24 and I ZR 86/22 fully reread and official XML freshly verified for this batch; Patentanwaltskosten card preserved without renewed substantive review.'
status['quality_checks'].update(output_local_links=quality['checked_output_links'],broken_links=quality['broken_local_links'],repeated_paragraphs=quality['exact_repeated_paragraphs'],repeated_long_sentences=quality['repeated_long_sentences'],other_commentary_blocks='All 171 unassigned unit commentaries unchanged against work baseline '+BASELINE)
status['quality_checks'].pop('unchanged_ordinary_units',None)
status['quality_checks'].update(unchanged_commentary_units=179,retained_reviewed_units=8,corrected_reviewed_units=12)
if technical is not None:status['validation_result']=technical
save(W/'status.json',status)
log=json.loads((W/'sources/search-log.json').read_text())
log['bounded_review_p1_p18']=dict(checked_at=now,search_evidence='sources/review-p1-p18-search.json',firecrawl='sources/review-p1-p18-index-firecrawl.md',fresh_fetches='sources/review-p1-p18/fetches.json',queries=['site:gesetze-im-internet.de/markeng/ "Stand" "2026"','site:recht.bund.de "Markengesetz" "2026" "Oktober"'],result='Current consolidation corroborated; returned results did not evidence a later MarkenG amendment. Search absence is not exhaustive proof.',case_checks=case_checks,unreviewed_case_card='cases/bgh-patentanwaltskosten.md')
save(W/'sources/search-log.json',log)
manifest=dict(created_at=now,primary_statute='markeng.xml',canonical_statute='canonical.md',files=[dict(path=str(p.relative_to(W)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted((W/'sources').rglob('*')) if p.is_file() and p.name!='manifest.json'])
save(W/'sources/manifest.json',manifest)
print(json.dumps(dict(review_complete=True,units_reviewed=20,corrected=len(changed),retained=20-len(changed),unassigned_unchanged=171,technical_validation_pending=technical is None)))
