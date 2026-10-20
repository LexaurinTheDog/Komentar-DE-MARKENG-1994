#!/usr/bin/env python3
"""Assemble the existing reviewed manuscript; never rewrite commentary or reassert review execution."""
from pathlib import Path
from datetime import datetime, timezone
import collections, hashlib, json, re, shutil, subprocess, sys

W = Path(__file__).resolve().parent
assert W == Path('/Volumes/LaCie/open-commentary/_work/de/Komentar-DE-MARKENG-1994')
O = Path('/Volumes/LaCie/open-commentary/de/Komentar-DE-MARKENG-1994')
TOOLS = Path('/Volumes/LaCie/open-commentary/_tools')
D = W/'sources/finalization-2026-10-20'
D.mkdir(exist_ok=True)
now = datetime.now(timezone.utc).isoformat()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
hashtext = lambda t: hashlib.sha256(t.encode()).hexdigest()
def load(p): return json.loads(p.read_text())
def save(p, obj): p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')

for name in ['README.md', 'REVIEW.md', 'review-result.json', 'status.json', 'preflight-result.json']:
    dest = D/('prior-'+name)
    if not dest.exists(): shutil.copyfile(W/name, dest)
if not (W/'REVIEW-batches.md').exists():
    (W/'REVIEW-batches.md').write_text('# Historische Teilprüfungen\n\nDie folgenden Einträge sind unveränderte chronologische Arbeitsstände. Angaben über damals noch offene Einheiten gelten für den jeweiligen Zeitpunkt. Den zusammengeführten Stand dokumentiert [REVIEW.md](REVIEW.md). Die elf zuletzt geprüften Einheiten sind im [damaligen Einzelbericht](sources/finalization-2026-10-20/prior-review-result.json) nachgewiesen.\n\n'+(D/'prior-REVIEW.md').read_text())

units = [json.loads(s) for s in (W/'units.jsonl').read_text().splitlines() if s.strip()]
U = {u['id']: u for u in units}
comments = {}
for p in sorted((W/'commentary').glob('*.md')):
    for m in re.finditer(r'^=== (\S+)\s*\n(.*?)(?=^=== |\Z)', p.read_text(), re.M|re.S):
        assert m[1] not in comments
        comments[m[1]] = m[2].strip()
ledger = load(W/'batch-review-ledger.json')
all_ids, findings, batch_rows, batches = [], {}, [], []
for k, b in ledger['batches'].items():
    r = b['review']
    assert b['complete'] and r['complete'] and not r['unresolved_blockers']
    assert b['ids'] == r['reviewed_ids'] and len(b['ids']) == r['units_reviewed']
    assert {x['id'] for x in r['findings']} == set(b['ids'])
    ref = f'sources/finalization-2026-10-20/batch-{len(batches)+1:02d}.json'
    save(W/ref, b)
    corrected = 0
    for f in r['findings']:
        ident = f['id']
        assert ident not in findings
        assert f['commentary_after_sha256'] == hashtext(comments[ident]), ('Changed after review', ident)
        assert f.get('statutory_text_sha256', f.get('statutory_sha256')) == hashtext(U[ident]['text'])
        assert f.get('source_xml_doknr', f.get('official_doknr')) == U[ident]['xml_doknr']
        assert f.get('resolved', True) and f.get('statutory_wording_agreement', True)
        outcome = f.get('outcome', f.get('disposition'))
        assert outcome in ['retained', 'corrected']
        corrected += outcome == 'corrected'
        findings[ident] = dict(f, batch_key=k, batch_evidence=ref, review_execution='Inherited from completed bounded second-pass ledger; not rerun during final assembly')
    all_ids += b['ids']
    batches.append(dict(key=k, ids=b['ids'], count=len(b['ids']), corrected=corrected, retained=len(b['ids'])-corrected, reviewed_at=r['reviewed_at'], evidence=ref, evidence_sha256=sha(W/ref)))
    batch_rows.append(f"| {U[b['ids'][0]]['label']} – {U[b['ids'][-1]]['label']} | {len(b['ids'])} | {corrected} / {len(b['ids'])-corrected} | {r['reviewed_at']} | [Einzelbericht {len(batches)}]({ref}) |")
assert len(all_ids) == len(set(all_ids)) == len(U) == len(comments) == 191
assert set(all_ids) == set(U) == set(comments)
baseline = D/'commentary-baseline-hashes.json'
current_hashes = {i:hashtext(comments[i]) for i in U}
if baseline.exists(): assert load(baseline) == current_hashes
else: save(baseline, current_hashes)

verification = load(W/'sources/verification.json')
fetches = load(D/'fetches.json')
assert all(x['valid'] and x['http_status'] == 200 and sha(W/x['path']) == x['sha256'] for x in fetches)
assert verification['final_assembly_recheck']['canonical_xml_unchanged']
# Two discovery/treaty entries in the central log predated the final batch-local
# captures. Use that contemporaneous log, not invented retrieval times or hashes.
repairs_path = D/'verification-metadata-repairs.json'
repairs = load(repairs_path) if repairs_path.exists() else []
for ix, old in enumerate(verification['fetches']):
    if old['path'] not in ['sources/review-p106-p117/wipo-current.html', 'sources/review-p106-p117/wipo-protocol-wrapper.html']:
        continue
    local_log = W/'sources/review-p106-p117/fetches.json'
    actual = next(x for x in load(local_log) if x.get('path') == old['path'])
    assert actual['http_status'] == 200 and actual['sha256'] == sha(W/actual['path']) and actual['url'] == old['url']
    if old.get('accessed_at') != actual['accessed_at'] or old.get('format_validation') != actual['format_validation']:
        repairs.append(dict(path=old['path'], previous_metadata=old, corrected_metadata=actual, evidence=str(local_log.relative_to(W)), reason='Central log retained an earlier retrieval and obsolete wrapper description; batch-local final capture record matches preserved body', earlier_body_still_available=old['sha256'] == actual['sha256']))
        verification['fetches'][ix] = actual
save(repairs_path, repairs)
verification['finalization_metadata_repairs'] = str(repairs_path.relative_to(W))
save(W/'sources/verification.json', verification)
for x in verification['fetches']:
    assert sha(W/x['path']) == x['sha256'], x['path']
shutil.copyfile(TOOLS/'LICENSE', W/'LICENSE')

prior_readme = (D/'prior-README.md').read_text().split('\n\n')
# Keep the detailed original source/version and rights paragraphs; replace obsolete batch-status paragraphs.
readme = '\n\n'.join(prior_readme[:6])
readme += '''

Zusammenstellung vom **20. Oktober 2026**: Alle 191 vorhandenen Kommentarblöcke sind mit Wortlaut und amtlicher Gliederung in 13 Kapitel eingebaut. Die frühere künstliche Aufteilung der amtlichen Sammelaufhebung §§ 161–163 ist bereits im Parser berichtigt; die Erläuterungen aller drei Nummern bleiben erhalten. Keine Kommentierung wurde bei der Zusammenstellung neu geschrieben oder gekürzt.

Das [Review-Ledger](batch-review-ledger.json) dokumentiert zehn abgeschlossene, abgegrenzte Zweitprüfungen für zusammen 191 eindeutige Einheiten. Für jede Einheit wurden der gespeicherte Kommentar-Hash, der Gesetzestext-Hash und die amtliche XML-Kennung mit dem jetzigen Bestand abgeglichen. Alle stimmen überein; die Teilberichte enthalten keine offenen Blocker. [REVIEW.md](REVIEW.md) fasst sie mit Einzelbefunden zusammen, [REVIEW-batches.md](REVIEW-batches.md) bewahrt die zeitliche Dokumentation. Die jetzige Zusammenstellung wiederholt diese materiellen Prüfungen nicht und ist keine neue unabhängige Ganzbuchfreigabe.

Neunzehn selektiv ausgewählte Entscheidungen sind als [Fallkarten in REVIEW](REVIEW.md#rechtsprechungsnachweise) mit amtlichen Volltextbelegen, genauen Randnummern, Kontext und Grenzen nachgewiesen. Ihre vollständige Lektüre ist in den jeweiligen Teilreviews dokumentiert; sie wurde bei dieser technischen Zusammenstellung nicht erneut vorgenommen. Weitere in den Entscheidungen zitierte Urteile und Literatur gelten damit nicht als eigenständig geprüft. Die Auswahl ist keine vollständige Rechtsprechungsübersicht.

Der [Prüfbericht](finalization-result.json) dokumentiert die erneuten Kontrollen: strikter Validator, separater Roh-XML-Abgleich sämtlicher 224 Datensätze, vollständige Kommentarzuordnung, unveränderter Inhalt seit dem jeweiligen Review, lokale Buchlinks und exakte Textwiederholungen. Die amtlichen XML-/ZIP- und Verkündungsquellen wurden am 20. Oktober 2026 nochmals erfolgreich abgerufen und formatgeprüft; [Antwortkörper und Abrufprotokoll](sources/finalization-2026-10-20/fetches.json) sind erhalten. Der Rechtsstand bleibt der 19. Oktober 2026. Mindestlänge und Textgleichheit sind keine juristische Qualitätszertifizierung.

**Zusammengestellter, technisch geprüfter Entwurf.** Die abgegrenzten Teilreviews sind vollständig im Ledger nachgewiesen; eine externe fachliche Freigabe oder eine neue materielle Ganzbuchprüfung wird nicht behauptet. Die Recherche bleibt selektiv. Historische Fassungen, fremdgesetzliche Regelungssysteme, unionsrechtliche Ausführungsakte und spätere Rechtsprechung sind nicht lückenlos eigenständig rekonstruiert. Für konkrete Altverfahren bleiben zusätzliche historische Quellen erforderlich. Ein lückenloser Gesetzgebungsmonitor wird nicht behauptet. Bereitstellung wie besehen; der Text ersetzt keine fallbezogene Rechtsberatung.

'''+prior_readme[-1]+'\n'
(W/'README.md').write_text(readme)

limits = [
    'Assigned task is final assembly and technical validation only. No new substantive unit review or independent whole-book approval was performed; no whole-book completion certification.',
    'Ledger proves recorded bounded review coverage and matching final hashes, not legal errorlessness or external professional approval.',
    'Case law remains selective: 19 inherited case cards with full-text review recorded in their bounded reviews, no fresh full-text rereading or exhaustive later-case audit during final assembly.',
    'Historical laws, every external or EU reference and implementing regulation have not been comprehensively reconstructed; concrete historical double tests need separate historical sources.',
    'Current official consolidation and both relevant 2026 promulgation/commencement sources are preserved; later-amendment search is selective, not an exhaustive BGBl pipeline audit.',
    'Earlier failed Firecrawl/EUR-Lex/PDF requests remain documented and are not valid source evidence. Fresh direct official HTTP captures succeeded. An initial finalization index assertion wrongly expected a version date on the table of contents; it was corrected to check the version in XML, with the failed attempt retained.',
    'Central WIPO discovery-index/treaty retrieval metadata was synchronized to the already preserved final batch-local captures. The earlier discovery-index response body is no longer available; its obsolete metadata is archived, not claimed as a retained source. The actual final index body and treaty full text both match their contemporaneous batch-local hashes.'
]
case_sources = load(D/'prior-status.json')['case_law_sources']
assert len(case_sources) == len(list((W/'cases').glob('*.md'))) == 19
case_rows = []
for c in case_sources:
    date = c['date']
    if len(date) == 8 and date.isdigit(): date = f'{date[:4]}-{date[4:6]}-{date[6:]}'
    case_rows.append(f"- {c['court']}, {date}, {c['docket']}: [Fallkarte]({c['card']}).")
review = '''# Zusammengeführter Prüfstand des Entwurfs

Am 20. Oktober 2026 wurden die vorhandenen Buchteile, Quellen und Prüfberichte technisch zusammengestellt. Die Kommentierung blieb vollständig unverändert. Der Auftrag umfasst die Zusammenstellung aus dem Ledger und technische Fehlerbehebung. Die materiellen Teilprüfungen wurden hier nicht wiederholt; die nachstehende Abdeckung ist eine überprüfte Aggregation ihrer Nachweise, keine Selbstzertifizierung als unabhängiger Zweitprüfer oder externe fachliche Freigabe.

## Rechtsstand und Quellen

Entscheidender Rechtsstand ist der Bearbeitungsbeginn **19. Oktober 2026**. [Gesetze im Internet](https://www.gesetze-im-internet.de/markeng/) weist Artikel 14 des Gesetzes vom 20. Mai 2026, BGBl. 2026 I Nr. 152, als letzte Änderung aus. Der [Verkündungstext](sources/finalization-2026-10-20/amendment-2026-152.txt) belegt die Änderungen der §§ 81 und 82 und in Artikel 18 Absatz 1 ihr Inkrafttreten am 1. Oktober 2026; die Ausnahmen der Absätze 2–4 betreffen andere Artikel. [BGBl. 2026 I Nr. 9](sources/finalization-2026-10-20/amendment-2026-9.txt), Artikel 5 und 16, belegt die vorausgehende MarkenG-Änderung seit 16. Januar 2026 nach Verkündung am 15. Januar 2026. Die aktuellen Quellen wurden am **20. Oktober 2026** erneut mit HTTP 200 abgerufen. Beide PDFs und die XML stimmen bytegenau mit den bisherigen Nachweisen überein. [Abrufzeiten, URLs, Formate und SHA-256](sources/verification.json) sowie [neue Originalantworten](sources/finalization-2026-10-20/fetches.json) sind erhalten. Technische Build- oder Abrufdaten wurden nicht als Inkrafttretensbeweis verwendet.

## Abdeckung und Zusammenstellung

Die amtliche XML enthält 224 Datensätze: 191 Vorschriftendatensätze, 31 Gliederungssätze, Kopfsatz und Inhaltsübersicht. 191 Einheiten decken 193 Paragraphennummern einschließlich Buchstabenparagraphen und ausdrücklicher Wegfälle ab. Die Gruppe `(XXXX) §§ 161 bis 163` ist amtlich ein Datensatz mit leerem operativem Textfeld und dem Metadaten-Titel „(weggefallen)“. Sie bleibt als `p161-163` erhalten, mit allen drei vorhandenen Erläuterungen. § 164 hat das amtliche Textfeld „-“. Die frühere künstliche Aufteilung der Gruppe ist behoben und im [Änderungsnachweis](sources/change-map.json) mit den früheren Dateien dokumentiert.

Jeder Rohdatensatz ist im [separaten XML-Abgleich](completeness-independent.json) disponiert. Es gibt keine fehlende, zusätzliche oder doppelte amtliche Kennung, keine Zeichenabweichung nach Entfernung ausschließlich von Weißraum und keine nicht zugeordnete Kommentierung. Operative Anlagen und eine gesonderte operative Eingangsformel sind nicht vorhanden. Die [einleitenden amtlichen Fußnoten](sources/introductory-notes.md) bleiben erhalten. Der Parser, die amtliche Inhaltsübersicht und der getrennte XML-Prüfer sind eigenständige technische Kontrollwege; diese methodische Trennung ist keine personelle Unabhängigkeit.

## Nachweise der abgegrenzten Zweitprüfungen

Das [unveränderte Ledger](batch-review-ledger.json) enthält zehn abgeschlossene Teilprüfungen ohne verzeichnete offene Blocker. Ihre 191 Kennungen bilden genau den jetzigen gesetzlichen Korpus, ohne Überschneidung. Für sämtliche 191 Einheiten stimmen der jeweilige Nachher-Hash des Kommentars, der Gesetzestext-Hash und die amtliche XML-Kennung mit dem Buchbestand überein. Der [zusammengeführte maschinenlesbare Bericht](review-result.json) behält jeden tatsächlichen Einzelbefund samt Herkunft bei. Die Aussagen über vollständige Lektüre in diesen Berichten stammen aus den jeweiligen Teilprüfungen; im jetzigen Auftrag wurden keine Einheiten erneut materiell geprüft.

| Bereich | Einheiten | Korrigiert / beibehalten | Dokumentierter UTC-Abschluss | Nachweis |
| --- | ---: | ---: | --- | --- |
'''+ '\n'.join(batch_rows)+'''

Die [historische Bearbeitungsdokumentation](REVIEW-batches.md) ist unverändert erhalten. Darin genannte Restzahlen und begrenzte Prüfumfänge beschreiben den jeweiligen damaligen Arbeitsstand. Die Aggregation ergibt 191 dokumentierte Teilprüfungen, 121 korrigierte und 70 beibehaltene Einheiten. Der jetzige technische Abgleich bestätigt die Unverändertheit der Texte seit diesen Prüfungen, ohne die materielle Bewertung zu wiederholen.

## Rechtsprechungsnachweise

Die folgenden 19 vorhandenen Fallkarten verweisen auf gesicherte amtliche XML-/ZIP-Texte und gelesene örtliche Korpusfassungen. Die jeweiligen Teilreviews dokumentieren Volltextlektüre, genaue Randnummern, tragende Aussagen, Parteivortrag, offene Fragen und Grenzen älterer Gesetzesfassungen. Die Fallkarten und Quellensnapshots wurden bei der Zusammenstellung unverändert übernommen. Es erfolgte keine neue Volltextlektüre und keine erschöpfende spätere Rechtsprechungsrecherche.

'''+ '\n'.join(case_rows)+'''

## Technische Kontrollen und Grenzen

Die [Validierung](validation.json), der [Vollständigkeitsbericht](completeness-independent.json), der [Qualitätsbericht](quality-report.json) und der [Zusammenstellungsbericht](finalization-result.json) enthalten die tatsächlichen maschinenlesbaren Ergebnisse. Der strenge Validator verlangt vollständige Wortlautübereinstimmung und einen lokalen Git-Commit im sauberen OUTPUT. Zusätzlich werden alle Roh-XML-Kennungen und Zeichen, alle Kommentarblöcke, lokale Verweise in Buchseiten und Fallkarten sowie exakte wiederholte Absätze und lange Sätze kontrolliert. Mindestlänge und fehlerfreie Links beweisen keine juristische Qualität. Die amtlichen HTML-Snapshots werden nicht als vollständig lokal navigierbare Websites ausgegeben.

Die Grenzen der einzelnen Teilprüfungen bleiben in den vollständigen Berichten erhalten: selektive Rechtsprechung; keine vollständige Rekonstruktion aller historischen Fassungen, unionsrechtlichen und internationalen Akte oder fremdgesetzlichen Regelungssysteme; kein lückenloser Audit sämtlicher Bundesgesetzblätter. Fehlgeschlagene Firecrawl-, EUR-Lex- und vermeintliche PDF-Abrufe werden nicht als erfolgreiche Volltextbelege behandelt. Bei der Zusammenstellung konnten die amtlichen Hauptquellen direkt abgerufen werden. Der Web-Tool-Abruf des amtlichen Index lief in einen Timeout; der direkte HTTP-Abruf wurde gesichert. Eine anfängliche technische Erwartung eines Fassungsdatums auf der Inhaltsverzeichnisseite war unzutreffend; die Versionsprüfung verwendet das amtliche XML und die Verkündungstexte. Der [erste Prüflauf](sources/finalization-2026-10-20/initial-validation-attempt.json) bleibt erhalten.

Dieser Bericht schließt ausschließlich den beauftragten Zusammenstellungs- und technischen Validierungsauftrag ab. Er ist keine neue materielle Ganzbuchprüfung, kein externes juristisches Gutachten und keine Veröffentlichungsfreigabe. Es wurde ausschließlich lokal gearbeitet; kein Push und keine externe Übermittlung erfolgten.
'''
review += '\nEin technischer Metadatenfehler im zentralen Abruflog wurde berichtigt: Die WIPO-Indexseite und der Vertragstext waren dort noch mit früheren Abrufangaben beziehungsweise einer überholten Wrapper-Beschreibung erfasst. Das bereits vorhandene abschließende Batch-Abruflog stimmt mit den tatsächlichen Antwortkörpern überein und wurde als Metadatenquelle übernommen. [Vorher-/Nachher-Protokoll](sources/finalization-2026-10-20/verification-metadata-repairs.json) nennt beide tatsächlichen Abrufzeitpunkte und Hashes. Der frühere Index-Antwortkörper ist nicht mehr vorhanden und wird nicht als erhaltener Beleg ausgegeben; der spätere Index und der tatsächliche vollständige Vertragstext bleiben gesichert. Die Kommentierung und Fallkarten wurden dadurch nicht geändert.\n'
assert sum(x['corrected'] for x in batches) == 121
(W/'REVIEW.md').write_text(review)

sources = (W/'SOURCES.md').read_text()
sources = sources.replace('[genaue Kennungen und Befunde](review-result.json)', '[genaue Kennungen und Befunde](sources/finalization-2026-10-20/prior-review-result.json)')
if '## Technische Zusammenstellung aus dem Review-Ledger' not in sources:
    sources += '''\n\n## Technische Zusammenstellung aus dem Review-Ledger\n\nAm 20. Oktober 2026 wurden alle vorhandenen Teile und Belege aus dem [Ledger](batch-review-ledger.json) zusammengeführt. [REVIEW.md](REVIEW.md) enthält die zehn einzeln verlinkten Teilberichte und alle 19 Fallkarten; [REVIEW-batches.md](REVIEW-batches.md) bewahrt die chronologische Dokumentation. [review-result.json](review-result.json) aggregiert die ursprünglichen Einzelbefunde, ohne eine neue materielle Prüfung zu behaupten. Die zuvor auf §§ 152–164 begrenzte letzte Root-Berichtsdatei bleibt [unverändert erhalten](sources/finalization-2026-10-20/prior-review-result.json).\n\nNeue amtliche HTTP-Abrufe: [Index, ZIP/XML und beide Verkündungs-PDFs](sources/finalization-2026-10-20/fetches.json). Version und tatsächliches Inkrafttreten sind in der XML beziehungsweise in den Verkündungstexten überprüfbar. [_finalize_sources.py](_finalize_sources.py) dokumentiert Format- und Hashprüfung. [_finalize.py](_finalize.py) reproduziert die Ledger-Zuordnung, den Abgleich sämtlicher Nachher-Hashes, Zusammenstellung und Quellenmanifest. [finalization-result.json](finalization-result.json) hält die technischen Ergebnisse und ihre Grenzen fest. Das vollständige Quellenmanifest umfasst auch frühere Antwortkörper und fehlgeschlagene Rechercheversuche; ein Dateimanifest erklärt einen verworfenen Antwortkörper nicht zur gültigen Autorität.\n'''
(W/'SOURCES.md').write_text(sources)

validated = '--validated' in sys.argv
validation = load(W/'validation.json') if validated else None
coverage = load(W/'completeness-independent.json')
quality = load(W/'quality-report.json')
if validated:
    assert validation['ok'] and validation['verbatim_ratio'] == 1.0 and validation['commentary_chars'] == sum(map(len, comments.values()))
    assert coverage['ok'] and not coverage['xml_character_mismatch']
    assert not quality['broken_local_links'] and not quality['placeholder_matches'] and not quality['repeated_long_sentences']
preflight = load(W/'preflight-result.json')
preflight.update(task='source_preflight_with_final_assembly_recheck', verified_at=verification['last_verified_at'], verification_date='2026-10-20', final_assembly_recheck=verification['final_assembly_recheck'])
preflight['technical_validation'] = validation
preflight['limitations'] = limits[3:5] + ['No new substantive second pass during final assembly; existing completed bounded reviews are aggregated separately.']
save(W/'preflight-result.json', preflight)

review_result = dict(complete=validated, task='finalize_from_batch_review_ledger', decisive_date='2026-10-19', assembled_at=now, units_reviewed=191, reviewed_ids=list(U), units_reviewed_in_this_finalize=0, review_basis='191 inherited completed bounded reviews; exact current text hashes verified, no new substantive review execution', ledger='batch-review-ledger.json', ledger_sha256=sha(W/'batch-review-ledger.json'), batches=batches, unresolved_blockers=[], findings=[findings[i] for i in U], limitations=limits, whole_book_complete=False, independent_whole_book_approval=False, technical_validation=validation, technical_validation_pending=not validated)
save(W/'review-result.json', review_result)
final = dict(complete=validated, task='bounded_finalize', assembled_at=now, decisive_date='2026-10-19', total_units=191, completed_commentary_units=191, ledger_reviewed_units=191, new_substantive_reviews=0, chapters=13, all_reviewed_commentary_hashes_match=True, all_reviewed_statutory_hashes_match=True, all_official_doknr_match=True, commentary_unchanged_from_finalization_baseline=True, baseline_hashes=str(baseline.relative_to(W)), source_checks='sources/verification.json', ledger='batch-review-ledger.json', ledger_sha256=sha(W/'batch-review-ledger.json'), validation=validation, completeness=dict(ok=coverage['ok'], expected=coverage['expected_count'], parsed=coverage['parsed_count'], missing=coverage['missing'], extra=coverage['unexpected'], duplicate_ids=coverage['duplicates'], xml_character_mismatch=coverage['xml_character_mismatch']), quality=dict(checked_output_links=quality['checked_output_links'], broken_links=quality['broken_local_links'], repeated_paragraphs=quality['exact_repeated_paragraphs'], repeated_long_sentences=quality['repeated_long_sentences'], placeholder_matches=quality['placeholder_matches']), unresolved_blockers=[], limitations=limits, whole_book_completion_claimed=False, publication='local only; no push or external submission')
save(W/'finalization-result.json', final)
status = load(D/'prior-status.json')
status.update(stage='drafted_technical_validation' if validated else 'final_assembly_validation_pending', task_scope='Bounded final assembly from completed review ledger; no new substantive review', updated_at=now, completed_at=now if validated else None, total_units=191, completed_units=191, commentary_characters=sum(map(len, comments.values())), units_reviewed=0, reviewed_ids=[], cumulative_reviewed_units=191, cumulative_reviewed_ids=list(U), remaining_second_pass_units=0, whole_book_review_complete=False, independent_second_pass='191 recorded bounded reviews aggregated with exact hash agreement; zero new substantive unit reviews in final assembly', validation_result=validation, remaining_limitations=limits, unresolved_blockers=[], finalization_result='finalization-result.json', finalization_complete=validated, review_result='review-result.json', review_completed_at=None, completed_units_basis='All existing commentary blocks built; scope completeness is not whole-book legal approval', case_law_provenance='Nineteen inherited cards; full-text reading recorded in bounded reviews, not repeated during final assembly', quality_checks=final['quality'])
status['source_checks']['latest_verification'] = verification['last_verified_at']
save(W/'status.json', status)

# Copy only manuscript/evidence files, never production runtime logs, locks or assignments.
root_files = ['README.md', 'REVIEW.md', 'REVIEW-batches.md', 'SOURCES.md', 'LICENSE', 'meta.json', 'units.jsonl', 'batch-review-ledger.json', 'review-result.json', 'preflight-result.json', 'status.json', 'validation.json', 'quality-report.json', 'completeness.json', 'completeness-independent.json', 'finalization-result.json']
root_files += [p.name for p in W.glob('_*.py')]
manifest = [dict(path=str(p.relative_to(W)), bytes=p.stat().st_size, sha256=sha(p)) for p in sorted((W/'sources').rglob('*')) if p.is_file() and p.name != 'manifest.json']
save(W/'sources/manifest.json', dict(created_at=now, primary_statute='markeng.xml', canonical_statute='canonical.md', files=manifest))
O.mkdir(exist_ok=True)
for name in root_files: shutil.copyfile(W/name, O/name)
for dirname in ['sources', 'cases', 'commentary']: shutil.copytree(W/dirname, O/dirname, dirs_exist_ok=True)
print(json.dumps(dict(assembled=True, technical_validation_recorded=validated, units=191, reviewed_ledger_units=len(all_ids), commentary_unchanged=True, copied_source_files=len(manifest)), ensure_ascii=False))
