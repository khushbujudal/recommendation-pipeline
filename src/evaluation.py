"""Full-catalog evaluation with binary held-out relevance and seen filtering."""
import json
import math
import numpy as np
import pandas as pd
from src.training import recommend


def ranking_metrics(recs, relevant, k):
    hits = [int(item in relevant) for item in recs]
    precision = sum(hits)/k
    recall = sum(hits)/len(relevant) if relevant else 0.
    dcg = sum(h/math.log2(i+2) for i,h in enumerate(hits))
    ideal = sum(1/math.log2(i+2) for i in range(min(k,len(relevant))))
    return precision, recall, dcg/ideal if ideal else 0.


def evaluate(root, cfg, data, models):
    seen = data['train'].groupby('user_id').item_id.apply(set).to_dict()
    eligible = data['test'][data['test'].rating >= cfg['positive_rating']].groupby('user_id').item_id.apply(set).to_dict()
    categories = data['items'].set_index('item_id').category.to_dict()
    records, examples = [], []
    for name, model in models.items():
        metrics, union, diversities = [], set(), []
        for uid, relevant in sorted(eligible.items()):
            relevant = relevant - seen.get(uid,set())
            if not relevant: continue
            recs = recommend(model,data['profiles'],uid,seen.get(uid,set()),cfg['k'])
            metrics.append(ranking_metrics(recs,relevant,cfg['k']))
            union.update(recs)
            pairs = [(a,b) for i,a in enumerate(recs) for b in recs[i+1:]]
            diversities.append(np.mean([categories[a] != categories[b] for a,b in pairs]) if pairs else 0.)
            examples.append({'model':name,'user_id':int(uid),'recommended':recs,'relevant':sorted(int(x) for x in relevant)})
        if not metrics: raise ValueError('No evaluable users')
        avg = np.mean(metrics, axis=0)
        records.append({'model':name, 'precision_at_k':avg[0], 'recall_at_k':avg[1], 'ndcg_at_k':avg[2],
                        'coverage':len(union)/len(categories), 'diversity':float(np.mean(diversities)), 'evaluated_users':len(metrics)})
    results = pd.DataFrame(records)
    results.to_csv(root/'reports/evaluation.csv',index=False)
    (root/'reports/recommendations.json').write_text(json.dumps(examples,indent=2))
    return results
