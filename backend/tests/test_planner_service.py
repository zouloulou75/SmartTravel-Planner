from __future__ import annotations

from app.schemas.trip import TripPlanRequest
from app.services.planner_service import PlannerService


def test_parse_llm_response_normalizes_missing_days(db_session):
    service = PlannerService(db_session)
    payload = TripPlanRequest(
        org='Tunis',
        dest='Rome',
        days=3,
        budget=1200,
        people_number=1,
        constraint_text='',
        query='Plan a cultural city break.',
    )

    parsed = service._parse_llm_response(
        '{"summary": {"org": "Tunis", "dest": "Rome"}, "itinerary": [{"day": 1, "city": "Rome", "transport": "Flight", "breakfast": "-", "lunch": "Cafe", "dinner": "Trattoria", "attraction": "Colosseum", "accommodation": "Boutique hotel"}]}',
        payload,
    )

    assert parsed['summary']['days'] == 3
    assert len(parsed['itinerary']) == 3
    assert parsed['itinerary'][0]['city'] == 'Rome'
    assert parsed['itinerary'][1]['city'] == 'Rome'
