"""Reusable feature store and shared training/inference profile function."""
import pandas as pd
import numpy as np


def user_profile(user_id, profile_table, categories):
    """Known users receive their train-only preference; cold users receive zero."""
    if user_id in profile_table.index:
        return profile_table.loc[user_id].reindex(categories).to_numpy(dtype=float)
    return np.zeros(len(categories))


def build_features(root, cfg, data):
    train, items = data['train'], data['items']
    categories = sorted(items.category.unique())
    joined = train.merge(items[['item_id','category']], on='item_id', validate='many_to_one')
    # Center ratings on neutral 3; mean by category prevents activity-count bias.
    joined['affinity'] = joined.rating - 3
    profiles = joined.pivot_table(index='user_id',columns='category',values='affinity',aggfunc='mean').reindex(columns=categories).fillna(0)
    users = data['users'].merge(data['user_stats'], how='left',on='user_id')
    users['days_since_last_interaction'] = (data['cutoff']-users.last_interaction).dt.total_seconds()/86400
    users['preferred_category'] = users.user_id.map(profiles.idxmax(axis=1)).fillna('unknown')
    users['activity_count'] = users.activity_count.fillna(0)
    users['average_rating'] = users.average_rating.fillna(train.rating.mean())
    item_features = items.merge(data['item_stats'],how='left',on='item_id').fillna({'activity_count':0,'positive_count':0,'average_rating':train.rating.mean()})
    users.to_csv(root/'data/features/users.csv',index=False)
    item_features.to_csv(root/'data/features/items.csv',index=False)
    profiles.to_csv(root/'data/features/user_category_profiles.csv')
    joined[['user_id','item_id','timestamp','affinity']].to_csv(root/'data/features/interactions.csv',index=False)
    return {**data, 'profiles':profiles, 'categories':categories, 'item_features':item_features}
