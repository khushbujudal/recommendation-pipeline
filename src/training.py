"""Train two rankers. JSON artifacts are safe to inspect and reload."""
import json
import numpy as np
from src.features import user_profile


def train_models(root, cfg, data):
    f = data['item_features'].sort_values('item_id')
    scores = f.positive_count.to_numpy(dtype=float)
    scores /= max(scores.max(), 1)
    common = {'item_ids':f.item_id.astype(int).tolist(), 'popularity':scores.tolist(),
              'item_categories':f.category.tolist(), 'categories':data['categories']}
    baseline = {**common, 'kind':'popularity'}
    personalized = {**common, 'kind':'content', 'weight':cfg['personalization_weight']}
    for name, model in [('popularity',baseline), ('personalized',personalized)]:
        (root/'models'/f'{name}.json').write_text(json.dumps(model,indent=2))
    return {'popularity':baseline, 'personalized':personalized}


def recommend(model, profiles, user_id, seen, k):
    ids = np.array(model['item_ids'])
    scores = np.array(model['popularity'], dtype=float)
    if model['kind'] == 'content':
        profile = user_profile(user_id, profiles, model['categories'])
        affinities = dict(zip(model['categories'], profile))
        scores = model['weight']*np.array([affinities[c] for c in model['item_categories']]) + (1-model['weight'])*scores
    candidates = [(int(i),float(s)) for i,s in zip(ids,scores) if int(i) not in seen]
    return [i for i,s in sorted(candidates,key=lambda x:(-x[1],x[0]))[:k]]
