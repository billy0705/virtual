import os
from pathlib import Path

import pandas as pd
import pytest
from dotenv import load_dotenv

from string_compression.agentic.agents import OpenAIAgent
from string_compression.agentic.datasets import (
    DatasetConfig,
    load_dataframe,
    resolve_dataset,
)
from string_compression.agentic.profiler import profile_dataframe, split_dataset


REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / ".env", override=False)
LIVE = os.getenv("RUN_AGENTIC_LIVE_TESTS") == "1"

pytestmark = pytest.mark.skipif(
    not LIVE,
    reason="set RUN_AGENTIC_LIVE_TESTS=1 to enable network and OpenAI integration tests",
)


@pytest.mark.parametrize("config_name", ["20231101.ab", "20231101.zh-classical"])
def test_bootstrap_small_wikipedia_configs(config_name):
    resolution = resolve_dataset(
        REPO_ROOT / "string_compression" / "config.json",
        DatasetConfig(
            dataset_id="wikimedia/wikipedia",
            config_name=config_name,
            details={},
        ),
        bootstrap_small=True,
    )
    assert resolution.path is not None, resolution.reason
    assert not load_dataframe(resolution.path, max_rows=10).empty


def test_live_openai_single_strategy():
    assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is required for the live test"
    values = ["shared-" + "x" * 200 + str(index) for index in range(100)]
    samples = split_dataset(pd.DataFrame({"source_text": values, "target": values}))
    agent = OpenAIAgent()
    result = agent.run_single(profile_dataframe(samples.discovery))
    assert result.status == "completed", result.reason
    assert result.calls == 1
