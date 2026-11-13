"""Run with python -m unittest discover -s tests -v."""
import json
import math
from pathlib import Path
import unittest
import pandas as pd
from src.evaluation import ranking_metrics
from src.validation import validate_frame
from src.training import recommend

ROOT = Path(__file__).resolve().parents[1]

class PipelineTests(unittest.TestCase):
    def test_metrics_known_example(self):
        p,r,n = ranking_metrics([1,9,2],{1,2,3},3)
        self.assertAlmostEqual(p,2/3)
        self.assertAlmostEqual(r,2/3)
        self.assertAlmostEqual(n,1.5/(1+1/math.log2(3)+.5))

    def test_validation_rejects_types_integrity_dates_and_duplicates(self):
        users = pd.DataFrame({'user_id':[1]})
        items = pd.DataFrame({'item_id':[1]})
        df = pd.DataFrame([[1,1,4,'2024-01-01'],[1,1,4,'2024-01-01'],[1,1,8,'2024-02-01'],
                           [2,1,4,'2024-02-01'],[1,1,'oops','invalid'],[1.5,1,4,'2030-01-01'],
                           [None,1,4,'2024-04-01']],columns=['user_id','item_id','rating','timestamp'])
        clean,bad = validate_frame(df,'interactions','2025-01-01T00:00:00Z',users,items)
        self.assertEqual(len(clean),1)
        self.assertEqual(len(bad),6)
        for reason in ['duplicate','invalid_rating','unknown_user','incorrect_type_rating','invalid_timestamp','missing_value','incorrect_type_user_id']:
            self.assertTrue(bad.error_reasons.str.contains(reason).any(),reason)

    def test_artifacts_temporal_split_and_train_only_features(self):
        train = pd.read_csv(ROOT/'data/processed/train.csv')
        test = pd.read_csv(ROOT/'data/processed/test.csv')
        self.assertLess(pd.to_datetime(train.timestamp,utc=True).max(),pd.to_datetime(test.timestamp,utc=True).min())
        features = pd.read_csv(ROOT/'data/features/users.csv').set_index('user_id')
        pd.testing.assert_series_equal(features.activity_count.sort_index(),train.groupby('user_id').size().sort_index(),check_names=False)
        items = pd.read_csv(ROOT/'data/features/items.csv').set_index('item_id')
        self.assertEqual(items.activity_count.sum(),len(train))

    def test_reload_seen_filter_and_cold_start(self):
        profiles = pd.read_csv(ROOT/'data/features/user_category_profiles.csv',index_col='user_id')
        model = json.loads((ROOT/'models/personalized.json').read_text())
        seen = {1,2,3,4}
        recs = recommend(model,profiles,1,seen,10)
        self.assertEqual(len(recs),10)
        self.assertTrue(set(recs).isdisjoint(seen))
        self.assertEqual(len(set(recs)),10)
        cold = recommend(model,profiles,999999,set(),10)
        baseline = json.loads((ROOT/'models/popularity.json').read_text())
        self.assertEqual(cold,recommend(baseline,profiles,999999,set(),10))

if __name__ == '__main__': unittest.main()
