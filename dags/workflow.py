"""Fail-fast scheduled Python workflow; each stage runs after its dependencies."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.ingestion import ingest
from src.validation import validate
from src.preparation import prepare
from src.transformation import transform
from src.features import build_features
from src.training import train_models
from src.evaluation import evaluate
from src.tracking import track


def run(config):
    cfg = json.loads(config.read_text())
    if not (0 < cfg['train_fraction'] < 1) or cfg['k'] < 1: raise ValueError('Invalid split or K')
    for folder in ['data/raw','data/errors','data/processed','data/features','models','reports','experiments']:
        (ROOT/folder).mkdir(parents=True, exist_ok=True)
    state = {'started_at':datetime.now(timezone.utc).isoformat(),'status':'running','tasks':[]}
    path = ROOT/'reports/workflow_run.json'
    def task(name, fn):
        start = time.perf_counter()
        try:
            result = fn()
            state['tasks'].append({'task':name,'status':'success','seconds':round(time.perf_counter()-start,4)})
            print(f'[SUCCESS] {name}',flush=True)
            return result
        except Exception as exc:
            state['status'] = 'failed'
            state['tasks'].append({'task':name,'status':'failed','error':str(exc)})
            raise
        finally:
            path.write_text(json.dumps(state,indent=2))
    raw = task('01 ingestion',lambda:ingest(ROOT,cfg))
    data = task('02 validation',lambda:validate(ROOT,cfg,raw))
    data = task('03 preparation and time split',lambda:prepare(ROOT,cfg,data))
    data = task('04 transformation',lambda:transform(ROOT,cfg,data))
    data = task('05 feature management',lambda:build_features(ROOT,cfg,data))
    models = task('06 model training',lambda:train_models(ROOT,cfg,data))
    results = task('07 model evaluation',lambda:evaluate(ROOT,cfg,data,models))
    run_id = task('08 experiment tracking',lambda:track(ROOT,cfg,results))
    state.update(status='success',finished_at=datetime.now(timezone.utc).isoformat(),run_id=run_id,
                 cutoff=data['cutoff'].isoformat(),train_rows=len(data['train']),test_rows=len(data['test']))
    path.write_text(json.dumps(state,indent=2))
    print(results.to_string(index=False),flush=True)
    print(f'WORKFLOW SUCCESS | run_id={run_id}',flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config',type=Path,default=ROOT/'configs/pipeline.json')
    run(parser.parse_args().config)
