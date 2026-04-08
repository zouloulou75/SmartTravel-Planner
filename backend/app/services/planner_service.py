from __future__ import annotations

from datetime import UTC, datetime
import json
import re
from typing import Any
from uuid import uuid4

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import PlannerRun
from app.repositories.examples import fetch_prompt_examples, fetch_reference_match
from app.repositories.runs import save_planner_run
from app.schemas.trip import DayPlan, TripPlanRequest, TripPlanResponse


class PlannerService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def plan_trip(
        self,
        payload: TripPlanRequest,
        *,
        pipeline_run_id: str | None = None,
        persist: bool = True,
    ) -> TripPlanResponse:
        if not self.settings.groq_api_key:
            raise HTTPException(status_code=503, detail="GROQ_API_KEY is not configured.")

        prompt_examples = fetch_prompt_examples(
            self.db,
            org=payload.org,
            dest=payload.dest,
            days=payload.days,
            budget=payload.budget,
            limit=3,
        )
        reference_example = fetch_reference_match(self.db, payload.org, payload.dest)
        dataset_match = reference_example is not None
        prompt = self._build_prompt(payload, prompt_examples, reference_example)
        raw_response = self._call_groq(prompt)
        parsed = self._parse_llm_response(raw_response, payload)

        run_id = str(uuid4())
        created_at = None
        if persist:
            run = PlannerRun(
                id=run_id,
                pipeline_run_id=pipeline_run_id,
                org=payload.org,
                dest=payload.dest,
                days=payload.days,
                budget=payload.budget,
                people_number=payload.people_number,
                constraint_text=payload.constraint_text,
                query=payload.query,
                poi_ids_json=payload.poi_ids,
                dataset_match=dataset_match,
                provider="groq",
                model=self.settings.groq_model,
                prompt_text=prompt,
                raw_response=raw_response,
                summary_json=parsed["summary"],
                itinerary_json=parsed["itinerary"],
            )
            saved = save_planner_run(self.db, run)
            run_id = saved.id
            created_at = saved.created_at

        itinerary = [DayPlan(**item) for item in parsed["itinerary"]]
        return TripPlanResponse(
            run_id=run_id,
            summary=parsed["summary"],
            itinerary=itinerary,
            provider="groq",
            model=self.settings.groq_model,
            dataset_match=dataset_match,
            created_at=created_at or parsed["created_at"],
        )

    def _build_prompt(self, payload: TripPlanRequest, prompt_examples, reference_example) -> str:
        example_blocks = []
        for example in prompt_examples:
            normalized = self._normalize_example_plan(example.annotated_plan_json)
            example_blocks.append(
                "EXAMPLE INPUT:\n"
                f"Origin: {example.org}\n"
                f"Destination: {example.dest}\n"
                f"Days: {example.days}\n"
                f"Budget: {example.budget}\n"
                f"Query: {example.query}\n\n"
                "EXAMPLE OUTPUT:\n"
                f"{json.dumps(normalized, ensure_ascii=False, indent=2)}"
            )

        reference_block = ""
        if reference_example is not None and reference_example.reference_information_json:
            reference_block = (
                "\nREFERENCE INFORMATION:\n"
                f"{json.dumps(reference_example.reference_information_json, ensure_ascii=False)[:6000]}\n"
            )

        poi_block = ""
        if payload.poi_ids:
            poi_block = f"\nRECOMMENDED POI IDS: {payload.poi_ids}\n"

        return (
            "You are TravelAI, an expert travel planner.\n"
            "Return ONLY valid JSON with the exact structure:\n"
            '{'
            '"summary": {"org": "...", "dest": "...", "days": 0, "people_number": 0, '
            '"budget": 0, "query": "...", "constraint_text": "..."}, '
            '"itinerary": ['
            '{"day": 1, "city": "...", "transport": "...", "breakfast": "...", '
            '"lunch": "...", "dinner": "...", "attraction": "...", "accommodation": "..."}'
            "]}\n\n"
            "Rules:\n"
            f"- Create exactly {payload.days} itinerary days.\n"
            f"- Respect the total budget of {payload.budget}.\n"
            "- Do not add markdown, code fences, or commentary.\n"
            "- If information is uncertain, keep the plan realistic and concise.\n"
            + ("\n\n" + "\n\n".join(example_blocks) if example_blocks else "")
            + reference_block
            + poi_block
            + "\nCURRENT REQUEST:\n"
            f"Origin: {payload.org}\n"
            f"Destination: {payload.dest}\n"
            f"Days: {payload.days}\n"
            f"People: {payload.people_number}\n"
            f"Budget: {payload.budget}\n"
            f"Constraints: {payload.constraint_text or 'none'}\n"
            f"Query: {payload.query}\n"
        )

    def _call_groq(self, prompt: str) -> str:
        try:
            response = httpx.post(
                self.settings.groq_api_url,
                headers={
                    "Authorization": f"Bearer {self.settings.groq_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.settings.groq_model,
                    "temperature": 0.2,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1800,
                },
                timeout=self.settings.groq_timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            return payload["choices"][0]["message"]["content"]
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=502, detail=f"Groq request failed: {exc}") from exc
        except (KeyError, IndexError, TypeError) as exc:
            raise HTTPException(status_code=502, detail="Unexpected Groq response format.") from exc

    def _parse_llm_response(self, raw_response: str, payload: TripPlanRequest) -> dict[str, Any]:
        cleaned = re.sub(r"^```json|^```|```$", "", raw_response.strip(), flags=re.MULTILINE).strip()
        start_index = cleaned.find("{")
        end_index = cleaned.rfind("}")
        if start_index == -1 or end_index == -1:
            raise HTTPException(status_code=502, detail="LLM returned a non-JSON response.")

        try:
            parsed = json.loads(cleaned[start_index : end_index + 1])
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=502, detail="Failed to parse LLM JSON output.") from exc

        summary = parsed.get("summary") or {}
        summary.setdefault("org", payload.org)
        summary.setdefault("dest", payload.dest)
        summary.setdefault("days", payload.days)
        summary.setdefault("people_number", payload.people_number)
        summary.setdefault("budget", payload.budget)
        summary.setdefault("query", payload.query)
        summary.setdefault("constraint_text", payload.constraint_text)

        itinerary = self._normalize_itinerary(parsed.get("itinerary") or [], payload)
        return {
            "summary": summary,
            "itinerary": itinerary,
            "created_at": datetime.now(UTC).replace(tzinfo=None),
        }

    def _normalize_itinerary(self, itinerary: list[Any], payload: TripPlanRequest) -> list[dict[str, Any]]:
        normalized = []
        for index, item in enumerate(itinerary):
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "day": int(item.get("day") or item.get("days") or index + 1),
                    "city": str(item.get("city") or item.get("current_city") or payload.dest),
                    "transport": str(item.get("transport") or item.get("transportation") or "-"),
                    "breakfast": str(item.get("breakfast") or "-"),
                    "lunch": str(item.get("lunch") or "-"),
                    "dinner": str(item.get("dinner") or "-"),
                    "attraction": str(item.get("attraction") or "-"),
                    "accommodation": str(item.get("accommodation") or "-"),
                }
            )
            if len(normalized) >= payload.days:
                break

        while len(normalized) < payload.days:
            next_day = len(normalized) + 1
            normalized.append(
                {
                    "day": next_day,
                    "city": payload.dest,
                    "transport": "-",
                    "breakfast": "-",
                    "lunch": "-",
                    "dinner": "-",
                    "attraction": "-",
                    "accommodation": "-",
                }
            )
        return normalized

    def _normalize_example_plan(self, plan: Any) -> dict[str, Any]:
        if not isinstance(plan, list) or len(plan) < 2:
            return {"summary": {}, "itinerary": []}

        summary = plan[0] if isinstance(plan[0], dict) else {}
        itinerary_source = plan[1] if isinstance(plan[1], list) else []
        normalized = []
        for index, day in enumerate(itinerary_source):
            if not isinstance(day, dict) or not day:
                continue
            normalized.append(
                {
                    "day": int(day.get("day") or day.get("days") or index + 1),
                    "city": day.get("city") or day.get("current_city") or "-",
                    "transport": day.get("transport") or day.get("transportation") or "-",
                    "breakfast": day.get("breakfast") or "-",
                    "lunch": day.get("lunch") or "-",
                    "dinner": day.get("dinner") or "-",
                    "attraction": day.get("attraction") or "-",
                    "accommodation": day.get("accommodation") or "-",
                }
            )
        return {"summary": summary, "itinerary": normalized}
