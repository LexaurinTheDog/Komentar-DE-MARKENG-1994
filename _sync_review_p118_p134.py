from pathlib import Path
import json,shutil
W=Path(__file__).resolve().parent;O=Path(json.loads((W/'meta.json').read_text())['repo_dir'])
assert O==Path('/Volumes/LaCie/open-commentary/de/Komentar-DE-MARKENG-1994')
for name in ['README.md','REVIEW.md','SOURCES.md','review-result.json','preflight-result.json','status.json','validation.json','quality-report.json','completeness-independent.json','_review_p118_p134_preflight.py','_review_p118_p134_checkpoint.py','_fetch_review_p118_p134.py','_fetch_eu_p118_p134.py','_fetch_eu2_p118_p134.py','_fetch_eu3_p118_p134.py','_revise_p118_p134.py','_docs_review_p118_p134.py','_sync_review_p118_p134.py']:
 shutil.copyfile(W/name,O/name)
for directory in ['sources','cases','commentary']:shutil.copytree(W/directory,O/directory,dirs_exist_ok=True)
