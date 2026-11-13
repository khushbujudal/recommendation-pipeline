"""Validate all entities, quarantine errors and preserve reason codes."""
import json
import pandas as pd


def validate_frame(df, entity, as_of, users=None, items=None):
    df = df.copy()
    required = {'users':['user_id','age_group'], 'items':['item_id','title','category'],
                'interactions':['user_id','item_id','rating','timestamp']}[entity]
    absent = set(required) - set(df.columns)
    if absent:
        raise ValueError(f'{entity}: missing columns {sorted(absent)}')
    reasons = [[] for _ in range(len(df))]
    def flag(mask, code):
        for i, value in enumerate(mask):
            if value: reasons[i].append(code)
    flag(df[required].isna().any(axis=1), 'missing_value')
    for col in [c for c in ['user_id','item_id','rating'] if c in required]:
        numeric = pd.to_numeric(df[col], errors='coerce')
        flag(numeric.isna() | (numeric % 1 != 0), 'incorrect_type_' + col)
        df[col] = numeric
        if col.endswith('_id'): flag(numeric.le(0), 'invalid_' + col)
    if entity == 'interactions':
        flag(~df.rating.between(1,5), 'invalid_rating')
        timestamps = pd.to_datetime(df.timestamp, errors='coerce', utc=True, format='mixed')
        flag(timestamps.isna() | (timestamps > pd.Timestamp(as_of)), 'invalid_timestamp')
        df.timestamp = timestamps
        flag(~df.user_id.isin(users.user_id), 'unknown_user')
        flag(~df.item_id.isin(items.item_id), 'unknown_item')
        keys = ['user_id','item_id','timestamp']
    else:
        keys = [required[0]]
        for col in required[1:]:
            flag(df[col].fillna('').astype(str).str.strip().eq(''), 'empty_' + col)
    flag(df.duplicated(keys, keep='first'), 'duplicate')
    good = [not r for r in reasons]
    errors = df.loc[[not v for v in good]].copy()
    errors['error_reasons'] = [';'.join(r) for r in reasons if r]
    clean = df.loc[good].copy()
    for col in ['user_id','item_id','rating']:
        if col in clean: clean[col] = clean[col].astype(int)
    return clean, errors


def validate(root, cfg, raw):
    clean, report = {}, {}
    for entity in ['users','items','interactions']:
        clean[entity], errors = validate_frame(raw[entity], entity, cfg['as_of'], clean.get('users'), clean.get('items'))
        errors.to_csv(root/'data/errors'/f'{entity}.csv', index=False)
        report[entity] = {'input':len(raw[entity]), 'accepted':len(clean[entity]), 'rejected':len(errors),
                          'reasons': errors.error_reasons.astype(str).str.split(';').explode().value_counts().to_dict()}
    (root/'reports/validation.json').write_text(json.dumps(report, indent=2))
    if any(clean[x].empty for x in clean): raise ValueError('Validation left an empty entity')
    return clean
