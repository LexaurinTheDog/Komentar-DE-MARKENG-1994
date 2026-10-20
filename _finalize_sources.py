#!/usr/bin/env python3
"""Capture and validate official final-assembly source responses without changing intake."""
from pathlib import Path
from urllib.request import Request, urlopen
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import hashlib, io, json, zipfile, subprocess
import xml.etree.ElementTree as ET

W = Path(__file__).resolve().parent
assert W == Path('/Volumes/LaCie/open-commentary/_work/de/Komentar-DE-MARKENG-1994')
D = W/'sources/finalization-2026-10-20'
D.mkdir(exist_ok=True)
sha = lambda data: hashlib.sha256(data).hexdigest()
targets = [
    ('index.html', 'https://www.gesetze-im-internet.de/markeng/', 'html'),
    ('markeng.zip', 'https://www.gesetze-im-internet.de/markeng/xml.zip', 'zip'),
    ('amendment-2026-152.pdf', 'https://www.recht.bund.de/bgbl/1/2026/152/regelungstext.pdf?__blob=publicationFile&v=1', 'pdf'),
    ('amendment-2026-9.pdf', 'https://www.recht.bund.de/bgbl/1/2026/9/regelungstext.pdf?__blob=publicationFile&v=1', 'pdf')]

def fetch(item):
    name, url, kind = item
    rec = dict(url=url, accessed_at=datetime.now(timezone.utc).isoformat(), path=str((D/name).relative_to(W)))
    try:
        with urlopen(Request(url, headers={'User-Agent': 'OpenCommentary-source-verification/1.0'}), timeout=25) as response:
            body = response.read()
            rec.update(http_status=response.status, content_type=response.headers.get('Content-Type'), final_url=response.url)
        (D/name).write_bytes(body)
        rec.update(sha256=sha(body), bytes=len(body))
        assert rec['http_status'] == 200
        if kind == 'zip':
            assert body.startswith(b'PK')
            z = zipfile.ZipFile(io.BytesIO(body))
            assert z.testzip() is None
            members = [x for x in z.namelist() if x.endswith('.xml')]
            assert len(members) == 1
            raw = z.read(members[0])
            root = ET.fromstring(raw)
            assert root.tag == 'dokumente'
            assert root.findtext('norm/metadaten/jurabk') == 'MarkenG'
            assert root.findtext('norm/metadaten/amtabk') == 'MarkenG'
            assert root.findtext('norm/metadaten/standangabe/standkommentar') == 'Zuletzt geändert durch Art. 14 G v. 20.5.2026 I Nr. 152'
            (D/'markeng.xml').write_bytes(raw)
            assert raw == (W/'sources/markeng.xml').read_bytes(), 'Official version changed; effective-version selection must be revisited'
            rec.update(extracted_xml_path=str((D/'markeng.xml').relative_to(W)), extracted_xml_sha256=sha(raw), agrees_with_canonical_xml=True)
            rec['format_validation'] = 'ZIP magic, CRC, single XML, parsed root, jurabk and amtabk verified'
        elif kind == 'pdf':
            assert body.startswith(b'%PDF-') and b'%%EOF' in body[-2048:]
            subprocess.run(['pdftotext', '-layout', str(D/name), str((D/name).with_suffix('.txt'))], check=True)
            text = (D/name).with_suffix('.txt').read_text()
            if '152' in name:
                assert 'Artikel 14' in text and 'Artikel 18' in text and '1. Oktober 2026' in text
            else:
                assert 'Artikel 5' in text and 'Artikel 16' in text and '15. Januar 2026' in text
                assert 'Dieses Gesetz tritt am Tag nach der Verkündung in Kraft.' in text
            assert body == (W/'sources'/name).read_bytes(), 'Promulgation snapshot differs'
            rec.update(agrees_with_preserved_promulgation=True, format_validation='PDF magic/EOF, pdftotext readability, amending and commencement articles verified')
        else:
            assert b'<html' in body[:2000].lower() and b'MarkenG' in body
            assert b'xml.zip' in body and b'BJNR308210994' in body
            rec['format_validation'] = 'HTML signature, expected act and official XML/full-text links verified; version is checked in XML, not inferred from index'
        rec['valid'] = True
    except Exception as exc:
        rec.update(valid=False, error=f'{type(exc).__name__}: {exc}')
    return rec

with ThreadPoolExecutor(max_workers=4) as pool:
    records = list(pool.map(fetch, targets))
(D/'fetches.json').write_text(json.dumps(records, ensure_ascii=False, indent=2)+'\n')
assert all(x['valid'] for x in records), records
v = json.loads((W/'sources/verification.json').read_text())
for rec in records:
    v['fetches'] = [x for x in v['fetches'] if x['path'] != rec['path']] + [rec]
v['last_verified_at'] = max(x['accessed_at'] for x in records)
v['final_assembly_recheck'] = dict(decisive_date='2026-10-19', fetches='sources/finalization-2026-10-20/fetches.json', canonical_xml_unchanged=True, promulgation_pdfs_unchanged=True, purpose='Technical source and version-evidence recheck; no new substantive second pass', web_tool_attempt='Official index open through web tool timed out; successful direct official response bodies preserved here.')
(W/'sources/verification.json').write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n')
print(json.dumps([dict(path=x['path'], status=x.get('http_status'), valid=x['valid']) for x in records]))
