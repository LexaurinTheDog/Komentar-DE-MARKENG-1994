from pathlib import Path
from datetime import datetime,timezone
import json,shutil,hashlib
W=Path(__file__).resolve().parent;O=Path(json.loads((W/'meta.json').read_text())['repo_dir'])
assert O==Path('/Volumes/LaCie/open-commentary/de/Komentar-DE-MARKENG-1994')
# Source manifest is a reproducible inventory, excluding itself to avoid recursive hashes.
files=[dict(path=str(p.relative_to(W)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted((W/'sources').rglob('*')) if p.is_file() and p.name!='manifest.json']
(W/'sources/manifest.json').write_text(json.dumps(dict(created_at=datetime.now(timezone.utc).isoformat(),primary_statute='markeng.xml',canonical_statute='canonical.md',files=files),ensure_ascii=False,indent=2)+'\n')
for name in ['README.md','REVIEW.md','SOURCES.md','review-result.json','preflight-result.json','status.json','validation.json','quality-report.json','completeness-independent.json','_review_p134a_p151_preflight.py','_review_p134a_p151_checkpoint.py','_fetch_review_p134a_p151.py','_revise_p134a_p151.py','_docs_review_p134a_p151.py','_sync_review_p134a_p151.py']:
 shutil.copyfile(W/name,O/name)
for directory in ['sources','cases','commentary']:shutil.copytree(W/directory,O/directory,dirs_exist_ok=True)
