"""Minimal local experiment tracker: immutable runs with hashes and artifacts."""
from datetime import datetime, timezone
import hashlib
import json
import platform
import shutil
import uuid
import numpy as np
import pandas as pd


def track(root, cfg, results):
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]
    dest = root/'experiments'/run_id
    dest.mkdir(parents=True)
    for name in ['popularity','personalized']:
        shutil.copy2(root/'models'/f'{name}.json',dest/f'{name}.json')
    shutil.copy2(root/'data/features/user_category_profiles.csv',dest/'user_category_profiles.csv')
    shutil.copy2(root/'reports/evaluation.csv',dest/'evaluation.csv')
    paths = sorted((root/'data/raw').glob('*.csv')) + sorted((root/'src').glob('*.py'))
    manifest = {'run_id':run_id,'parameters':cfg,'metrics':results.to_dict(orient='records'),
                'environment':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__},
                'sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    (dest/'run.json').write_text(json.dumps(manifest,indent=2))
    return run_id
