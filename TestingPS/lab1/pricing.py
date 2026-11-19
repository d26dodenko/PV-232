"""Расчёт стоимости использования модели. Функция взята из GameForge."""

from __future__ import annotations

from decimal import ROUND_CEILING, Decimal
from typing import Any


def cost_bounds(usage: dict[str, int], pricing: dict[str, Any]) -> tuple[int, int]:
    """Per invocation, in nanodollars. Cached input is a subset, never added twice.

    When receipts omit cache-write counts, lower uses ordinary fresh input and
    upper treats all fresh input as cache writes. A Codex turn may contain several
    requests, so its aggregate cannot prove that any one request used long context.
    For that case lower uses short rates and upper uses long rates when possible.
    Reasoning tokens are already part of output_tokens.
    """
    for key in ("input_tokens", "cached_input_tokens", "output_tokens"):
        if type(usage.get(key)) is not int or usage[key] < 0:
            raise ValueError("Incomplete or invalid usage receipt")
    incoming, cached, output = (
        usage[k] for k in ("input_tokens", "cached_input_tokens", "output_tokens")
    )
    if cached > incoming:
        raise ValueError("Cached input exceeds total input")
    rates = {key: Decimal(value) for key, value in pricing["usd_per_million"].items()}
    long = incoming > pricing["long_context_threshold"]
    high_input = Decimal(pricing["long_input_multiplier"]) if long else Decimal(1)
    high_output = Decimal(pricing["long_output_multiplier"]) if long else Decimal(1)
    low_input = high_input if pricing["provider"] == "openai" else Decimal(1)
    low_output = high_output if pricing["provider"] == "openai" else Decimal(1)
    written = usage.get("cache_write_tokens")
    if written is not None and (type(written) is not int or not 0 <= written <= incoming - cached):
        raise ValueError("Invalid cache-write usage")
    # Missing cache-write detail is a price interval, never an invented zero.
    writes_low = written if written is not None else 0
    writes_high = written if written is not None else incoming - cached
    lower = (
        (incoming - cached - writes_low) * rates["input"]
        + cached * rates["cached_input"]
        + writes_low * rates["cache_write"]
    ) * low_input + output * rates["output"] * low_output
    upper = (
        (incoming - cached - writes_high) * rates["input"]
        + cached * rates["cached_input"]
        + writes_high * rates["cache_write"]
    ) * high_input + output * rates["output"] * high_output
    return (
        int((lower * 1000).to_integral_value(rounding=ROUND_CEILING)),
        int((upper * 1000).to_integral_value(rounding=ROUND_CEILING)),
    )
