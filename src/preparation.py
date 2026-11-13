"""Normalize metadata and perform a global chronological split."""
import pandas as pd


def prepare(root, cfg, clean):
    clean['items']['category'] = clean['items']['category'].str.strip().str.lower()
    clean['items']['title'] = clean['items']['title'].str.strip()
    clean['users']['age_group'] = clean['users']['age_group'].str.strip()
    events = clean['interactions'].sort_values(['timestamp','user_id','item_id']).reset_index(drop=True)
    cutoff = events.timestamp.quantile(cfg['train_fraction'], interpolation='nearest')
    train = events[events.timestamp <= cutoff].copy()
    test = events[events.timestamp > cutoff].copy()
    if train.empty or test.empty: raise ValueError('Empty temporal partition')
    assert train.timestamp.max() < test.timestamp.min()
    for name, data in [('train', train), ('test', test), ('users',clean['users']), ('items',clean['items'])]:
        data.to_csv(root/'data/processed'/f'{name}.csv', index=False)
    return {**clean, 'train':train, 'test':test, 'cutoff':cutoff}
