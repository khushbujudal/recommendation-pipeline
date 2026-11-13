"""Reload persisted models and features to recommend without retraining."""
import argparse
import json
from pathlib import Path
import pandas as pd
from src.training import recommend

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--user-id',type=int,required=True)
    parser.add_argument('--model',choices=['popularity','personalized'],default='personalized')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    model = json.loads((root/'models'/f'{args.model}.json').read_text())
    profiles = pd.read_csv(root/'data/features/user_category_profiles.csv',index_col='user_id')
    train = pd.read_csv(root/'data/processed/train.csv')
    seen = set(train.loc[train.user_id == args.user_id,'item_id'])
    print(recommend(model,profiles,args.user_id,seen,10))
