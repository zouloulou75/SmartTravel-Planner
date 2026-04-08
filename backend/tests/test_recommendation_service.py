from __future__ import annotations

from pathlib import Path

import joblib

from app.core.config import get_settings
from app.models import POIStat, RegionStat
from app.schemas.recommendation import RecommendationRequest
from app.services.recommendation_service import RecommendationService


class FakeModel:
    classes_ = [101, 202, 303]

    def predict_proba(self, _features):
        return [
            [0.2, 0.7, 0.1],
            [0.05, 0.85, 0.1],
            [0.8, 0.1, 0.1],
        ]


def test_recommendation_service_returns_ranked_poi_ids(
    db_session,
    monkeypatch,
    tmp_path: Path,
):
    artifact_path = tmp_path / 'artifact.joblib'
    joblib.dump(
        {
            'model': FakeModel(),
            'all_features': [
                'weather_label',
                'travel_mode_label',
                'census_division',
                'region_tier',
                'region_freq',
                'poi_freq',
                'month',
                'hour',
                'day_of_week',
            ],
            'candidate_pool_size': 3,
        },
        artifact_path,
    )

    monkeypatch.setenv('MODEL_ARTIFACT_PATH', str(artifact_path))
    get_settings.cache_clear()

    db_session.add_all(
        [
            POIStat(
                poi_id=101,
                poi_freq=500,
                popularity_rank=1,
                relative_score=1.0,
                state_name='California',
                census_division='Pacific',
                region_tier='Metropolis',
            ),
            POIStat(
                poi_id=202,
                poi_freq=450,
                popularity_rank=2,
                relative_score=0.9,
                state_name=None,
                census_division='Unknown',
                region_tier='Major City',
            ),
            POIStat(
                poi_id=303,
                poi_freq=400,
                popularity_rank=3,
                relative_score=0.8,
                state_name='Oregon',
                census_division='Pacific',
                region_tier='Mid-size City',
            ),
            RegionStat(
                census_division='Pacific',
                region_tier='Metropolis',
                region_freq_median=1200,
                sample_count=50,
            ),
        ]
    )
    db_session.commit()

    service = RecommendationService(db_session)
    response = service.recommend(
        RecommendationRequest(
            weather_label='Clear',
            travel_mode_label='car',
            census_division='Pacific',
            region_tier='Metropolis',
            hour=14,
            day_of_week=4,
            top_k=3,
        )
    )

    assert [item.poi_id for item in response.items] == [202, 101, 303]
    assert response.items[0].region_label == 'Pacific • Major City'
    assert response.context['region_freq'] == 1200
