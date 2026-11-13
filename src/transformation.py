"""Training-only derived datasets and matrix."""
import numpy as np


def transform(root, cfg, data):
    train, items = data['train'], data['items']
    user_stats = train.groupby('user_id').agg(activity_count=('rating','size'), average_rating=('rating','mean'), last_interaction=('timestamp','max')).reset_index()
    item_stats = train.groupby('item_id').agg(activity_count=('rating','size'), average_rating=('rating','mean')).reset_index()
    positives = train[train.rating >= cfg['positive_rating']].groupby('item_id').size()
    item_stats['positive_count'] = item_stats.item_id.map(positives).fillna(0).astype(int)
    user_ids, item_ids = data['users'].user_id.tolist(), items.item_id.tolist()
    matrix = train.pivot_table(index='user_id', columns='item_id', values='rating', aggfunc='mean').reindex(index=user_ids,columns=item_ids).fillna(0)
    np.savez_compressed(root/'data/processed/interaction_matrix.npz', ratings=matrix.to_numpy(), user_ids=user_ids, item_ids=item_ids)
    user_stats.to_csv(root/'data/processed/user_activity.csv', index=False)
    item_stats.to_csv(root/'data/processed/item_popularity.csv', index=False)
    return {**data, 'user_stats':user_stats, 'item_stats':item_stats}
