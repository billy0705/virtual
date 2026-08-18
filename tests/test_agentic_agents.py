import json
from types import SimpleNamespace

import pandas as pd
import pytest
from pydantic import ValidationError

from string_compression.agentic.agents import OpenAIAgent
from string_compression.agentic.evaluator import CandidateEvaluator
from string_compression.agentic.models import CandidateBatch, CandidateSpec
from string_compression.agentic.profiler import profile_dataframe, split_dataset


def duplicate_candidate(candidate_id="duplicate"):
    return CandidateSpec(
        id=candidate_id,
        summary="Drop duplicate target.",
        target_columns=["target"],
        reference_columns=["source_text"],
        residual_columns=[],
        compression_sql='SELECT * EXCLUDE ("target") FROM source',
        reconstruction_sql='SELECT *, "source_text" AS "target" FROM compressed',
    )


def test_row_id_can_be_declared_as_a_reference_but_not_overwritten():
    candidate = duplicate_candidate()
    candidate.reference_columns.append("__virtual_row_id")
    assert CandidateSpec.model_validate(candidate.model_dump()) == candidate

    data = candidate.model_dump()
    data["target_columns"] = ["__virtual_row_id"]
    data["reference_columns"] = ["source_text"]
    with pytest.raises(ValidationError, match="cannot be a target or residual"):
        CandidateSpec.model_validate(data)


def response(*, parsed=None, output=None, response_id="response"):
    return SimpleNamespace(
        id=response_id,
        output_parsed=parsed,
        output=output or [],
        output_text="",
        usage=SimpleNamespace(input_tokens=10, output_tokens=5, total_tokens=15),
    )


class FakeResponses:
    def __init__(self, parsed_responses=None, created_responses=None):
        self.parsed_responses = list(parsed_responses or [])
        self.created_responses = list(created_responses or [])
        self.parse_kwargs = []
        self.create_kwargs = []

    def parse(self, **kwargs):
        self.parse_kwargs.append(kwargs)
        return self.parsed_responses.pop(0)

    def create(self, **kwargs):
        self.create_kwargs.append(kwargs)
        return self.created_responses.pop(0)


class FakeClient:
    def __init__(self, responses):
        self.responses = responses


def fixture_context():
    values = ["value-" + "x" * 200 + str(index) for index in range(200)]
    samples = split_dataset(pd.DataFrame({"source_text": values, "target": values}))
    return profile_dataframe(samples.discovery), CandidateEvaluator(samples)


def test_single_and_two_stage_use_structured_responses():
    profile, evaluator = fixture_context()
    initial = duplicate_candidate("initial")
    repaired = duplicate_candidate("repaired")
    fake = FakeResponses(
        parsed_responses=[
            response(parsed=CandidateBatch(candidates=[initial]), response_id="one"),
            response(parsed=CandidateBatch(candidates=[initial]), response_id="two"),
            response(parsed=CandidateBatch(candidates=[repaired]), response_id="three"),
        ]
    )
    agent = OpenAIAgent(client=FakeClient(fake), model="test-model")

    single = agent.run_single(profile)
    two_stage = agent.run_two_stage(profile, evaluator)

    assert [item.id for item in single.candidates] == ["initial"]
    assert [item.id for item in two_stage.candidates] == ["repaired"]
    assert single.calls == 1
    assert two_stage.calls == 2
    assert sum(item.total_tokens for item in single.usage) == 15
    assert sum(item.total_tokens for item in two_stage.usage) == 30
    assert all(call["store"] is False for call in fake.parse_kwargs)


def test_tool_loop_profiles_evaluates_and_submits():
    profile, evaluator = fixture_context()
    candidate = duplicate_candidate()
    evaluate_call = SimpleNamespace(
        type="function_call",
        call_id="call-1",
        name="evaluate_candidate",
        arguments=json.dumps({"candidate": candidate.model_dump(mode="json")}),
    )
    submit_call = SimpleNamespace(
        type="function_call",
        call_id="call-2",
        name="submit_candidates",
        arguments=json.dumps({"candidates": [candidate.model_dump(mode="json")]}),
    )
    fake = FakeResponses(
        created_responses=[
            response(output=[evaluate_call], response_id="one"),
            response(output=[submit_call], response_id="two"),
        ]
    )
    agent = OpenAIAgent(client=FakeClient(fake), model="test-model")
    result = agent.run_tool_loop(profile, evaluator)

    assert result.status == "completed"
    assert [item.id for item in result.candidates] == ["duplicate"]
    assert result.calls == 2
    assert result.tool_calls == 2
    assert all(call["store"] is False for call in fake.create_kwargs)


def test_tool_loop_enforces_turn_and_tool_call_limits():
    profile, evaluator = fixture_context()
    calls = [
        SimpleNamespace(
            type="function_call",
            call_id=f"call-{index}",
            name="run_profile_sql",
            arguments=json.dumps({"sql": "SELECT 1 AS value FROM source"}),
        )
        for index in range(3)
    ]
    fake = FakeResponses(created_responses=[response(output=calls)])
    agent = OpenAIAgent(
        client=FakeClient(fake), model="test-model", max_turns=8, max_tool_calls=2
    )
    result = agent.run_tool_loop(profile, evaluator)

    assert result.status == "error"
    assert result.calls == 1
    assert result.tool_calls == 2
    assert "without submit_candidates" in result.reason
