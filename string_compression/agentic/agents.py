from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import Field

from .evaluator import CandidateEvaluator
from .models import (
    CandidateBatch,
    CandidateSpec,
    StrategyRun,
    StrictModel,
    UsageRecord,
)
from .sandbox import SQLValidationError, run_profile_query


DEFAULT_MODEL = "gpt-5.6-terra"
PROMPT_VERSION = "agentic-string-compression-v1"

SYSTEM_INSTRUCTIONS = """You discover lossless string-column compression strategies for tabular data.

Return executable DuckDB SQL candidates, not general advice. Each candidate has two queries:
- compression_sql reads only from `source`, returns exactly one row per input row, preserves
  `__virtual_row_id`, and may remove target columns or add declared residual columns.
- reconstruction_sql reads only from `compressed` and returns every original column plus
  `__virtual_row_id` with exactly the original values and NULLs.

Every column created by compression_sql must be listed in residual_columns, and no declared
residual may be absent. Reference columns must remain in the compressed output. You may use
pure deterministic DuckDB scalar string, URL, regular-expression, list, conditional, and cast
operations. You may use SELECT queries and CTEs. Do not use files, network access, extensions,
DDL, DML, random values, clocks, sequences, or user-defined functions.

Prefer compact formulas with constant literals. For imperfect formulas, add explicit error
strings and indicators so reconstruction remains exact. Never claim that a sampled pattern is
universally true: the local evaluator is authoritative. Propose at most five materially distinct
candidates. Keep identifiers concise and use double quotes for column names.
"""


class ProfileSQLArguments(StrictModel):
    sql: str = Field(min_length=1, max_length=20_000)


class EvaluateCandidateArguments(StrictModel):
    candidate: CandidateSpec


class SubmitCandidatesArguments(StrictModel):
    candidates: list[CandidateSpec] = Field(max_length=5)


def _function_tool(
    name: str, description: str, model: type[StrictModel]
) -> dict[str, Any]:
    return {
        "type": "function",
        "name": name,
        "description": description,
        "parameters": model.model_json_schema(),
        "strict": True,
    }


TOOLS = [
    _function_tool(
        "run_profile_sql",
        "Run one read-only DuckDB SELECT over the discovery sample relation named source. "
        "The result is limited to 100 rows, 20 columns, and 64 KB.",
        ProfileSQLArguments,
    ),
    _function_tool(
        "evaluate_candidate",
        "Validate a complete candidate on the discovery sample and return exactness, "
        "counterexamples, and Snappy size feedback.",
        EvaluateCandidateArguments,
    ),
    _function_tool(
        "submit_candidates",
        "Finish the run by submitting up to five final candidates.",
        SubmitCandidatesArguments,
    ),
]


def build_discovery_prompt(profile: dict[str, Any]) -> str:
    return (
        f"Prompt version: {PROMPT_VERSION}\n"
        "Find useful string reconstruction candidates for this sampled table. "
        "The profile includes DuckDB types, aggregate statistics, and truncated example rows. "
        "Do not target __virtual_row_id.\n\n"
        + json.dumps(profile, ensure_ascii=False, indent=2)
    )


def _payload(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", exclude_none=True)
    return vars(value)


def _response_usage(response: Any, elapsed_seconds: float) -> UsageRecord:
    usage = getattr(response, "usage", None)
    if usage is None:
        return UsageRecord(
            response_id=getattr(response, "id", None), elapsed_seconds=elapsed_seconds
        )
    if hasattr(usage, "model_dump"):
        usage = usage.model_dump()
    elif not isinstance(usage, dict):
        usage = vars(usage)
    return UsageRecord(
        response_id=getattr(response, "id", None),
        input_tokens=int(usage.get("input_tokens", 0) or 0),
        output_tokens=int(usage.get("output_tokens", 0) or 0),
        total_tokens=int(usage.get("total_tokens", 0) or 0),
        elapsed_seconds=elapsed_seconds,
    )


def _parsed_batch(response: Any) -> CandidateBatch:
    parsed = getattr(response, "output_parsed", None)
    if isinstance(parsed, CandidateBatch):
        return parsed
    if parsed is not None:
        return CandidateBatch.model_validate(parsed)
    output_text = getattr(response, "output_text", None)
    if not output_text:
        raise ValueError("OpenAI response did not contain structured candidate output")
    return CandidateBatch.model_validate_json(output_text)


class OpenAIAgent:
    def __init__(
        self,
        *,
        client: Any | None = None,
        model: str | None = None,
        max_turns: int = 8,
        max_tool_calls: int = 12,
    ) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        load_dotenv(repo_root / ".env", override=False)
        self.model = model or os.getenv("VIRTUAL_OPENAI_MODEL", DEFAULT_MODEL)
        self.max_turns = max_turns
        self.max_tool_calls = max_tool_calls
        self.client = client
        if self.client is None and os.getenv("OPENAI_API_KEY"):
            self.client = OpenAI()

    @property
    def available(self) -> bool:
        return self.client is not None

    def _skip(self, strategy: str) -> StrategyRun:
        return StrategyRun(
            strategy=strategy,
            model=self.model,
            status="skipped",
            reason="OPENAI_API_KEY is not configured",
        )

    def _structured_call(self, prompt: str) -> tuple[CandidateBatch, UsageRecord]:
        started = time.monotonic()
        response = self.client.responses.parse(
            model=self.model,
            instructions=SYSTEM_INSTRUCTIONS,
            input=prompt,
            text_format=CandidateBatch,
            reasoning={"effort": "medium"},
            max_output_tokens=12_000,
            store=False,
        )
        elapsed = time.monotonic() - started
        return _parsed_batch(response), _response_usage(response, elapsed)

    def run_single(self, profile: dict[str, Any]) -> StrategyRun:
        if not self.available:
            return self._skip("single")
        started = time.monotonic()
        try:
            batch, usage = self._structured_call(build_discovery_prompt(profile))
            return StrategyRun(
                strategy="single",
                model=self.model,
                candidates=batch.candidates,
                usage=[usage],
                calls=1,
                elapsed_seconds=time.monotonic() - started,
                lineage={
                    candidate.id: {"stage": "initial"} for candidate in batch.candidates
                },
            )
        except Exception as exc:
            return StrategyRun(
                strategy="single",
                model=self.model,
                status="error",
                reason=f"{type(exc).__name__}: {exc}",
                calls=1,
                elapsed_seconds=time.monotonic() - started,
            )

    def run_two_stage(
        self, profile: dict[str, Any], evaluator: CandidateEvaluator
    ) -> StrategyRun:
        if not self.available:
            return self._skip("two_stage")
        started = time.monotonic()
        usage_records: list[UsageRecord] = []
        try:
            initial, usage = self._structured_call(build_discovery_prompt(profile))
            usage_records.append(usage)
            feedback = []
            for candidate in initial.candidates:
                evaluation = evaluator.evaluate(candidate, split="discovery")
                feedback.append(
                    {
                        "candidate": candidate.model_dump(mode="json"),
                        "evaluation": evaluation.model_dump(mode="json"),
                    }
                )
            repair_prompt = (
                build_discovery_prompt(profile)
                + "\n\nThe first-stage candidates were evaluated locally. Return the best valid "
                "candidates unchanged and repair or replace failed candidates. The evaluator is "
                "authoritative.\n\n"
                + json.dumps(feedback, ensure_ascii=False, indent=2)
            )
            repaired, usage = self._structured_call(repair_prompt)
            usage_records.append(usage)
            lineage = {
                candidate.id: {
                    "stage": "repair",
                    "initial_candidate_ids": [item.id for item in initial.candidates],
                }
                for candidate in repaired.candidates
            }
            return StrategyRun(
                strategy="two_stage",
                model=self.model,
                candidates=repaired.candidates,
                usage=usage_records,
                calls=2,
                elapsed_seconds=time.monotonic() - started,
                lineage=lineage,
            )
        except Exception as exc:
            return StrategyRun(
                strategy="two_stage",
                model=self.model,
                status="error",
                reason=f"{type(exc).__name__}: {exc}",
                usage=usage_records,
                calls=len(usage_records) + 1,
                elapsed_seconds=time.monotonic() - started,
            )

    def run_tool_loop(
        self, profile: dict[str, Any], evaluator: CandidateEvaluator
    ) -> StrategyRun:
        if not self.available:
            return self._skip("tool_loop")
        started = time.monotonic()
        conversation: list[dict[str, Any]] = [
            {"role": "user", "content": build_discovery_prompt(profile)}
        ]
        usage_records: list[UsageRecord] = []
        tool_call_count = 0
        submitted: list[CandidateSpec] | None = None
        try:
            for _turn in range(self.max_turns):
                call_started = time.monotonic()
                response = self.client.responses.create(
                    model=self.model,
                    instructions=SYSTEM_INSTRUCTIONS,
                    input=conversation,
                    tools=TOOLS,
                    tool_choice="auto",
                    parallel_tool_calls=False,
                    reasoning={"effort": "medium"},
                    max_output_tokens=12_000,
                    max_tool_calls=self.max_tool_calls,
                    store=False,
                )
                usage_records.append(
                    _response_usage(response, time.monotonic() - call_started)
                )
                output_items = list(getattr(response, "output", []) or [])
                conversation.extend(_payload(item) for item in output_items)
                function_calls = [
                    item
                    for item in output_items
                    if getattr(item, "type", None) == "function_call"
                    or _payload(item).get("type") == "function_call"
                ]
                if not function_calls:
                    output_text = getattr(response, "output_text", "")
                    if output_text:
                        try:
                            submitted = CandidateBatch.model_validate_json(
                                output_text
                            ).candidates
                        except Exception:
                            pass
                    break

                for item in function_calls:
                    if tool_call_count >= self.max_tool_calls:
                        break
                    tool_call_count += 1
                    payload = _payload(item)
                    call_id = payload.get("call_id") or getattr(item, "call_id", None)
                    name = payload.get("name") or getattr(item, "name", None)
                    raw_arguments = payload.get("arguments") or getattr(
                        item, "arguments", "{}"
                    )
                    if name == "run_profile_sql":
                        try:
                            arguments = ProfileSQLArguments.model_validate_json(
                                raw_arguments
                            )
                            result = run_profile_query(
                                evaluator.samples.discovery, arguments.sql
                            )
                            tool_result = {
                                "ok": result.ok,
                                "columns": result.columns,
                                "rows": result.rows,
                                "error": result.error,
                                "elapsed_seconds": result.elapsed_seconds,
                            }
                        except (SQLValidationError, ValueError) as exc:
                            tool_result = {"ok": False, "error": str(exc)}
                    elif name == "evaluate_candidate":
                        try:
                            arguments = EvaluateCandidateArguments.model_validate_json(
                                raw_arguments
                            )
                            evaluation = evaluator.evaluate(
                                arguments.candidate, split="discovery"
                            )
                            tool_result = evaluation.model_dump(mode="json")
                        except Exception as exc:
                            tool_result = {
                                "ok": False,
                                "error": f"{type(exc).__name__}: {exc}",
                            }
                    elif name == "submit_candidates":
                        arguments = SubmitCandidatesArguments.model_validate_json(
                            raw_arguments
                        )
                        submitted = arguments.candidates
                        tool_result = {"ok": True, "accepted": len(submitted)}
                    else:
                        tool_result = {"ok": False, "error": f"unknown tool {name!r}"}

                    conversation.append(
                        {
                            "type": "function_call_output",
                            "call_id": call_id,
                            "output": json.dumps(tool_result, ensure_ascii=False),
                        }
                    )
                    if submitted is not None:
                        break
                if submitted is not None or tool_call_count >= self.max_tool_calls:
                    break

            if submitted is None:
                raise ValueError("tool loop ended without submit_candidates")
            return StrategyRun(
                strategy="tool_loop",
                model=self.model,
                candidates=submitted,
                usage=usage_records,
                calls=len(usage_records),
                tool_calls=tool_call_count,
                elapsed_seconds=time.monotonic() - started,
                lineage={
                    candidate.id: {"stage": "tool_loop"} for candidate in submitted
                },
            )
        except Exception as exc:
            return StrategyRun(
                strategy="tool_loop",
                model=self.model,
                status="error",
                reason=f"{type(exc).__name__}: {exc}",
                usage=usage_records,
                calls=len(usage_records),
                tool_calls=tool_call_count,
                elapsed_seconds=time.monotonic() - started,
            )

    def run(
        self,
        strategy: str,
        profile: dict[str, Any],
        evaluator: CandidateEvaluator,
    ) -> StrategyRun:
        normalized = strategy.replace("-", "_")
        if normalized == "single":
            return self.run_single(profile)
        if normalized == "two_stage":
            return self.run_two_stage(profile, evaluator)
        if normalized == "tool_loop":
            return self.run_tool_loop(profile, evaluator)
        raise ValueError(f"unknown strategy {strategy!r}")
