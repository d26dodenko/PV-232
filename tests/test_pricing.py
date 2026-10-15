"""Тесты расчёта стоимости. Номера кейсов указаны в отчёте."""

from copy import deepcopy

import pytest

from pricing import cost_bounds


@pytest.fixture
def pricing():
    """Основной набор тарифов для тестов."""
    return {
        "usd_per_million": {
            "input": "10",
            "cached_input": "1",
            "cache_write": "12.50",
            "output": "50",
        },
        "long_context_threshold": 272_000,
        "long_input_multiplier": "2",
        "long_output_multiplier": "1.5",
        "provider": "openai",
    }


def receipt(incoming, cached=0, output=0, **details):
    """Данные о количестве использованных токенов."""
    return {
        "input_tokens": incoming,
        "cached_input_tokens": cached,
        "output_tokens": output,
        "total_tokens": incoming + output,
        "calls": 1,
        **details,
    }


# Расчёт стоимости и граничные значения. Суммы указаны в нанодолларах.
@pytest.mark.parametrize(
    "usage, provider, expected",
    [
        pytest.param(receipt(100_000, 90_000, 1_000), "openai", (240_000_000, 265_000_000), id="TC-01_mixed_cache"),
        pytest.param(receipt(100_000, 100_000), "openai", (100_000_000, 100_000_000), id="TC-02_all_cached"),
        pytest.param(receipt(0), "openai", (0, 0), id="TC-03_zero_usage"),
        pytest.param(receipt(272_000, 0, 1_000), "openai", (2_770_000_000, 3_450_000_000), id="TC-04_at_threshold"),
        pytest.param(receipt(272_001, 0, 1_000), "openai", (5_515_020_000, 6_875_025_000), id="TC-05_above_threshold"),
        pytest.param(receipt(400_000), "codex", (4_000_000_000, 10_000_000_000), id="TC-06_aggregate_bounds"),
        pytest.param(receipt(0, 0, 1_000), "openai", (50_000_000, 50_000_000), id="TC-07_output_only"),
        pytest.param(receipt(100, 20, 10, cache_write_tokens=0), "openai", (1_320_000, 1_320_000), id="TC-08_known_zero_writes"),
        pytest.param(receipt(100, 20, 10, cache_write_tokens=30), "openai", (1_395_000, 1_395_000), id="TC-09_known_partial_writes"),
        pytest.param(receipt(100, 20, 10, cache_write_tokens=80), "openai", (1_520_000, 1_520_000), id="TC-10_maximum_writes"),
        pytest.param(receipt(100, 20, 10, cache_write_tokens=None), "openai", (1_320_000, 1_520_000), id="TC-11_unknown_writes"),
        pytest.param(receipt(400_000, 400_000), "openai", (800_000_000, 800_000_000), id="TC-12_long_cached_input"),
        pytest.param(receipt(400_000, 0, 1_000), "codex", (4_050_000_000, 10_075_000_000), id="TC-13_aggregate_output"),
        pytest.param(receipt(271_999, 0, 1_000), "openai", (2_769_990_000, 3_449_987_500), id="TC-14_below_threshold"),
    ],
)
def test_cost_bounds(usage, provider, expected, pricing):
    pricing["provider"] = provider
    actual = cost_bounds(usage, pricing)
    assert actual == expected
    assert isinstance(actual, tuple)
    assert all(type(value) is int for value in actual)


@pytest.mark.parametrize(
    "rates, usage, expected",
    [
        pytest.param(
            ("0.10", "0.01", "0.125", "0.50"), receipt(1), (100, 125),
            id="TC-15_small_rate",
        ),
        pytest.param(
            ("0.0004", "0.0001", "0.0011", "0.005"), receipt(1), (1, 2),
            id="TC-16_round_up",
        ),
        pytest.param(
            ("2", "0.10", "2.50", "10"), receipt(100, 20, 10, cache_write_tokens=30),
            (277_000, 277_000), id="TC-18_ledger_regression",
        ),
    ],
)
def test_other_fixed_rates(rates, usage, expected, pricing):
    # TC-15 взят из test_pricing.py; TC-18 — из test_financial_ledger.py.
    pricing["usd_per_million"] = dict(zip(("input", "cached_input", "cache_write", "output"), rates))
    assert cost_bounds(usage, pricing) == expected


def test_tc_17_independent_requests(pricing):
    # Два коротких запроса считаются отдельно, даже если их сумма больше порога.
    first = cost_bounds(receipt(200_000), pricing)
    second = cost_bounds(receipt(200_000), pricing)
    assert first == second == (2_000_000_000, 2_500_000_000)
    assert (first[0] + second[0], first[1] + second[1]) == (4_000_000_000, 5_000_000_000)
    assert cost_bounds(receipt(400_000), pricing) == (8_000_000_000, 10_000_000_000)


def test_tc_19_ignored_metadata(pricing):
    usage = receipt(100_000, 90_000, 1_000, total_tokens=999_999, calls=100, reasoning_tokens=500)
    assert cost_bounds(usage, pricing) == (240_000_000, 265_000_000)


def test_tc_20_inputs_unchanged(pricing):
    usage = receipt(100, 20, 10, cache_write_tokens=30)
    before = deepcopy((usage, pricing))
    assert cost_bounds(usage, pricing) == (1_395_000, 1_395_000)
    assert (usage, pricing) == before


REQUIRED_FIELDS = ("input_tokens", "cached_input_tokens", "output_tokens")
MISSING = object()


@pytest.mark.parametrize("field", REQUIRED_FIELDS)
@pytest.mark.parametrize(
    "value",
    [
        pytest.param(MISSING, id="TC-21_missing_field"),
        pytest.param(-1, id="TC-22_negative_counter"),
        pytest.param(True, id="TC-23_boolean_counter_true"),
        pytest.param(False, id="TC-23_boolean_counter_false"),
        pytest.param(1.5, id="TC-24_fractional_counter"),
        pytest.param("1", id="TC-25_string_counter"),
        pytest.param(None, id="TC-26_null_counter"),
    ],
)
def test_required_counters(field, value, pricing):
    usage = receipt(100, 20, 10)
    if value is MISSING:
        del usage[field]
    else:
        usage[field] = value
    with pytest.raises(ValueError, match="^Incomplete or invalid usage receipt$"):
        cost_bounds(usage, pricing)


@pytest.mark.parametrize(
    "usage, message",
    [
        pytest.param(receipt(1, 2), "Cached input exceeds total input", id="TC-27_cache_exceeds_input"),
        pytest.param(receipt(100, 20, 10, cache_write_tokens=-1), "Invalid cache-write usage", id="TC-28_negative_writes"),
        pytest.param(receipt(100, 20, 10, cache_write_tokens=81), "Invalid cache-write usage", id="TC-29_excessive_writes"),
    ],
)
def test_invalid_relationships(usage, message, pricing):
    with pytest.raises(ValueError, match=f"^{message}$"):
        cost_bounds(usage, pricing)


@pytest.mark.parametrize(
    "written",
    [
        pytest.param(True, id="TC-30_boolean_writes_true"),
        pytest.param(False, id="TC-30_boolean_writes_false"),
        pytest.param(1.0, id="TC-30_float_writes"),
        pytest.param("1", id="TC-30_string_writes"),
    ],
)
def test_cache_write_type(written, pricing):
    with pytest.raises(ValueError, match="^Invalid cache-write usage$"):
        cost_bounds(receipt(100, 20, 10, cache_write_tokens=written), pricing)


@pytest.mark.parametrize(
    "provider, expected",
    [
        pytest.param("openai", (6_525_000_000, 6_525_000_000), id="TC-31_known_writes_request"),
        pytest.param("codex", (3_275_000_000, 6_525_000_000), id="TC-31_known_writes_aggregate"),
    ],
)
def test_known_writes_keep_aggregate_uncertainty(provider, expected, pricing):
    pricing["provider"] = provider
    assert cost_bounds(receipt(400_000, 100_000, 1_000, cache_write_tokens=50_000), pricing) == expected
