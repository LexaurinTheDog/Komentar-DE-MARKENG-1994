"""Copy the bounded-review manuscript and evidence into its exclusive output."""
from pathlib import Path
import shutil,json
W=Path(__file__).resolve().parent;O=Path(json.loads((W/'meta.json').read_text())['repo_dir'])
assert O==Path('/Volumes/LaCie/open-commentary/de/Komentar-DE-MARKENG-1994')
for name in ['README.md','REVIEW.md','SOURCES.md','review-result.json','preflight-result.json','status.json','validation.json','quality-report.json','completeness-independent.json','_review_p55_p71_preflight.py','_review_p55_p71_checkpoint.py','_fetch_review_p55_p71.py','_revise_p55_p71.py','_sync_review_p55_p71.py']:
 shutil.copyfile(W/name,O/name)
for directory in ['sources','cases','commentary']:shutil.copytree(W/directory,O/directory,dirs_exist_ok=True)
