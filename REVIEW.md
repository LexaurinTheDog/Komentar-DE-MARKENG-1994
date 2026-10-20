# Zusammengeführter Prüfstand des Entwurfs

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
| § 1 – § 18 | 20 | 12 / 8 | 2026-10-20T11:46:41.061403+00:00 | [Einzelbericht 1](sources/finalization-2026-10-20/batch-01.json) |
| § 19 – § 34 | 20 | 13 / 7 | 2026-10-20T11:56:45.844744+00:00 | [Einzelbericht 2](sources/finalization-2026-10-20/batch-02.json) |
| § 35 – § 54 | 20 | 12 / 8 | 2026-10-20T12:07:22.295047+00:00 | [Einzelbericht 3](sources/finalization-2026-10-20/batch-03.json) |
| § 55 – § 71 | 20 | 10 / 10 | 2026-10-20T12:19:02.393169+00:00 | [Einzelbericht 4](sources/finalization-2026-10-20/batch-04.json) |
| § 72 – § 89a | 20 | 13 / 7 | 2026-10-20T12:29:21.772171+00:00 | [Einzelbericht 5](sources/finalization-2026-10-20/batch-05.json) |
| § 90 – § 105 | 20 | 13 / 7 | 2026-10-20T12:40:55.523475+00:00 | [Einzelbericht 6](sources/finalization-2026-10-20/batch-06.json) |
| § 106 – § 117 | 20 | 16 / 4 | 2026-10-20T12:55:46.972535+00:00 | [Einzelbericht 7](sources/finalization-2026-10-20/batch-07.json) |
| § 118 – § 134 | 20 | 14 / 6 | 2026-10-20T13:10:27.229615+00:00 | [Einzelbericht 8](sources/finalization-2026-10-20/batch-08.json) |
| § 134a – § 151 | 20 | 12 / 8 | 2026-10-20T13:21:28.931865+00:00 | [Einzelbericht 9](sources/finalization-2026-10-20/batch-09.json) |
| § 152 – § 164 | 11 | 6 / 5 | 2026-10-20T13:34:04.536049+00:00 | [Einzelbericht 10](sources/finalization-2026-10-20/batch-10.json) |

Die [historische Bearbeitungsdokumentation](REVIEW-batches.md) ist unverändert erhalten. Darin genannte Restzahlen und begrenzte Prüfumfänge beschreiben den jeweiligen damaligen Arbeitsstand. Die Aggregation ergibt 191 dokumentierte Teilprüfungen, 121 korrigierte und 70 beibehaltene Einheiten. Der jetzige technische Abgleich bestätigt die Unverändertheit der Texte seit diesen Prüfungen, ohne die materielle Bewertung zu wiederholen.

## Rechtsprechungsnachweise

Die folgenden 19 vorhandenen Fallkarten verweisen auf gesicherte amtliche XML-/ZIP-Texte und gelesene örtliche Korpusfassungen. Die jeweiligen Teilreviews dokumentieren Volltextlektüre, genaue Randnummern, tragende Aussagen, Parteivortrag, offene Fragen und Grenzen älterer Gesetzesfassungen. Die Fallkarten und Quellensnapshots wurden bei der Zusammenstellung unverändert übernommen. Es erfolgte keine neue Volltextlektüre und keine erschöpfende spätere Rechtsprechungsrecherche.

- BGH, 2023-01-12, I ZR 86/22: [Fallkarte](cases/bgh-dachser.md).
- BGH, 2025-05-07, I ZR 143/24: [Fallkarte](cases/bgh-werktitel.md).
- BGH, 2022-10-13, I ZB 59/19: [Fallkarte](cases/bgh-patentanwaltskosten.md).
- BGH, 2015-10-21, I ZR 51/12: [Fallkarte](cases/bgh-davidoff.md).
- BGH, 2015-07-09, I ZB 65/13: [Fallkarte](cases/bgh-nivea.md).
- BPatG, 2011-01-11, 24 W (pat) 46/09: [Fallkarte](cases/bpatg-kostenruecknahme.md).
- BPatG, 2010-11-23, 24 W (pat) 111/10: [Fallkarte](cases/bpatg-gebuehrenruecknahme.md).
- BGH, 2013-04-11, I ZB 93/11: [Fallkarte](cases/bgh-gehoer-schriftverfahren.md).
- BGH, 2010-07-01, I ZA 14/10: [Fallkarte](cases/bgh-vkh-nebenentscheidung.md).
- BPatG, 2010-10-26, 24 W (pat) 33/09: [Fallkarte](cases/bpatg-wasser-bewegt-uns.md).
- BGH, 2021-07-29, I ZR 163/19: [Fallkarte](cases/bgh-hohenloher-landschwein.md).
- BPatG, 2024-12-16, 26 W (pat) 31/20: [Fallkarte](cases/bpatg-bio-mineralwasser.md).
- BPatG, 2026-05-06, 26 W (pat) 579/20: [Fallkarte](cases/bpatg-ggn.md).
- BPatG, 2020-05-08, 26 W (pat) 549/17: [Fallkarte](cases/bpatg-fritz-frize.md).
- BGH, 2016-03-31, I ZR 86/13: [Fallkarte](cases/bgh-himalaya-salz.md).
- BGH, 2018-11-08, I ZR 126/15: [Fallkarte](cases/bgh-puc-ii.md).
- BGH, 2021-04-21, 3 StR 225/20: [Fallkarte](cases/bgh-gemeinschaftsmarke-strafbarkeit.md).
- BPatG, 2023-02-06, 29 W (pat) 514/20: [Fallkarte](cases/bpatg-kragenweite-uebergang.md).
- BPatG, 2023-04-17, 26 W (pat) 27/18: [Fallkarte](cases/bpatg-goeler-uebergang.md).

## Technische Kontrollen und Grenzen

Die [Validierung](validation.json), der [Vollständigkeitsbericht](completeness-independent.json), der [Qualitätsbericht](quality-report.json) und der [Zusammenstellungsbericht](finalization-result.json) enthalten die tatsächlichen maschinenlesbaren Ergebnisse. Der strenge Validator verlangt vollständige Wortlautübereinstimmung und einen lokalen Git-Commit im sauberen OUTPUT. Zusätzlich werden alle Roh-XML-Kennungen und Zeichen, alle Kommentarblöcke, lokale Verweise in Buchseiten und Fallkarten sowie exakte wiederholte Absätze und lange Sätze kontrolliert. Mindestlänge und fehlerfreie Links beweisen keine juristische Qualität. Die amtlichen HTML-Snapshots werden nicht als vollständig lokal navigierbare Websites ausgegeben.

Die Grenzen der einzelnen Teilprüfungen bleiben in den vollständigen Berichten erhalten: selektive Rechtsprechung; keine vollständige Rekonstruktion aller historischen Fassungen, unionsrechtlichen und internationalen Akte oder fremdgesetzlichen Regelungssysteme; kein lückenloser Audit sämtlicher Bundesgesetzblätter. Fehlgeschlagene Firecrawl-, EUR-Lex- und vermeintliche PDF-Abrufe werden nicht als erfolgreiche Volltextbelege behandelt. Bei der Zusammenstellung konnten die amtlichen Hauptquellen direkt abgerufen werden. Der Web-Tool-Abruf des amtlichen Index lief in einen Timeout; der direkte HTTP-Abruf wurde gesichert. Eine anfängliche technische Erwartung eines Fassungsdatums auf der Inhaltsverzeichnisseite war unzutreffend; die Versionsprüfung verwendet das amtliche XML und die Verkündungstexte. Der [erste Prüflauf](sources/finalization-2026-10-20/initial-validation-attempt.json) bleibt erhalten.

Dieser Bericht schließt ausschließlich den beauftragten Zusammenstellungs- und technischen Validierungsauftrag ab. Er ist keine neue materielle Ganzbuchprüfung, kein externes juristisches Gutachten und keine Veröffentlichungsfreigabe. Es wurde ausschließlich lokal gearbeitet; kein Push und keine externe Übermittlung erfolgten.

Ein technischer Metadatenfehler im zentralen Abruflog wurde berichtigt: Die WIPO-Indexseite und der Vertragstext waren dort noch mit früheren Abrufangaben beziehungsweise einer überholten Wrapper-Beschreibung erfasst. Das bereits vorhandene abschließende Batch-Abruflog stimmt mit den tatsächlichen Antwortkörpern überein und wurde als Metadatenquelle übernommen. [Vorher-/Nachher-Protokoll](sources/finalization-2026-10-20/verification-metadata-repairs.json) nennt beide tatsächlichen Abrufzeitpunkte und Hashes. Der frühere Index-Antwortkörper ist nicht mehr vorhanden und wird nicht als erhaltener Beleg ausgegeben; der spätere Index und der tatsächliche vollständige Vertragstext bleiben gesichert. Die Kommentierung und Fallkarten wurden dadurch nicht geändert.
