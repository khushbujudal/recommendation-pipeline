"""Deterministic synthetic movie platform data, including deliberate errors."""
import numpy as np
import pandas as pd


def ingest(root, cfg):
    rng = np.random.default_rng(cfg['seed'])
    users = pd.DataFrame({'user_id': range(1, cfg['users'] + 1),
                          'age_group': rng.choice(['18-24', '25-34', '35-49', '50+'], cfg['users'])})
    categories = ['Action', 'Comedy', 'Drama', 'Fantasy', 'Mystery', 'Science Fiction']
    items = pd.DataFrame({'item_id': range(1, cfg['items'] + 1),
                          'title': [f'Synthetic Movie {i:03d}' for i in range(1, cfg['items'] + 1)],
                          'category': [categories[i % 6] for i in range(cfg['items'])]})
    rows = []
    for uid in users.user_id:
        preferred = int(rng.integers(0, 6))
        # Category preference plus a weaker shared item popularity effect.
        probs = np.where(np.arange(cfg['items']) % 6 == preferred, 5., 1.)
        probs *= np.linspace(1.5, 0.5, cfg['items'])
        selected = rng.choice(cfg['items'], cfg['interactions_per_user'], replace=False, p=probs/probs.sum())
        for item in selected:
            rating = int(np.clip(np.rint(rng.normal(4.6 if item % 6 == preferred else 2.8, .65)), 1, 5))
            ts = pd.Timestamp('2024-01-01', tz='UTC') + pd.Timedelta(days=int(rng.integers(0, 365)), seconds=int(rng.integers(0,86400)))
            rows.append([int(uid), int(item+1), rating, ts.isoformat()])
    interactions = pd.DataFrame(rows, columns=['user_id','item_id','rating','timestamp'])
    bad = pd.DataFrame([[None, 1, 4, '2024-03-01'], [1, 1, 'bad', '2024-03-01'],
                        [1, 2, 9, '2024-03-01'], [1, 3, 4, 'not-a-date'],
                        [9999, 1, 4, '2024-03-01'], [1, 9999, 4, '2024-03-01'],
                        [1, 4, 4, '2035-01-01']], columns=interactions.columns)
    interactions = pd.concat([interactions, interactions.iloc[:3], bad], ignore_index=True)
    for name, data in [('users', users), ('items', items), ('interactions', interactions)]:
        data.to_csv(root / 'data/raw' / f'{name}.csv', index=False)
    return {name: pd.read_csv(root / 'data/raw' / f'{name}.csv') for name in ['users', 'items', 'interactions']}
