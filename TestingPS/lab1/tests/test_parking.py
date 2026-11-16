from services import ParkingFeeService
import pytest

@pytest.fixture
def service() -> ParkingFeeService:
    return ParkingFeeService()


@pytest.mark.parametrize(
    "minutes, is_resident",
    [
        pytest.param(0, False, id="TC-02_zero_minutes"),
        pytest.param(30, False, id="TC-03_free_upper_boundary"),
        pytest.param(30, True, id="TC-11_free_for_resident"),
    ],
)
def test_free_period(service, minutes, is_resident):
    assert service.calculate_fee(minutes, is_resident) == pytest.approx(0.0)


@pytest.mark.parametrize(
    "minutes, expected",
    [
        pytest.param(120, 200.0, id="TC-01_two_hours"),
        pytest.param(31, 100.0, id="TC-04_first_paid_minute"),
        pytest.param(60, 100.0, id="TC-05_exactly_one_hour"),
        pytest.param(61, 200.0, id="TC-06_second_hour_started"),
    ],
)
def test_paid_parking(service, minutes, expected):
    assert service.calculate_fee(minutes) == pytest.approx(expected)


@pytest.mark.parametrize(
    "minutes, expected",
    [
        pytest.param(600, 1000.0, id="TC-07_cap_reached_exactly"),
        pytest.param(601, 1000.0, id="TC-08_cap_applied"),
        pytest.param(1440, 1000.0, id="TC-09_max_duration"),
    ],
)
def test_daily_cap(service, minutes, expected):
    assert service.calculate_fee(minutes) == pytest.approx(expected)


@pytest.mark.parametrize(
    "minutes, expected",
    [
        pytest.param(120, 140.0, id="TC-10_resident_discount"),
        pytest.param(31, 70.0, id="TC-12_resident_first_paid_minute"),
        pytest.param(601, 700.0, id="TC-13_cap_applied_before_discount"),
    ],
)
def test_resident_discount(service, minutes, expected):
    assert service.calculate_fee(minutes, is_resident=True) == pytest.approx(expected)


@pytest.mark.parametrize(
    "minutes, message",
    [
        pytest.param(-1, "Minutes must be >= 0", id="TC-14_negative_minutes"),
        pytest.param(1441, "Minutes must be <= 1440", id="TC-15_more_than_day"),
    ],
)
def test_invalid_minutes(service, minutes, message):
    with pytest.raises(ValueError, match=message):
        service.calculate_fee(minutes)


def test_custom_configuration():
    custom = ParkingFeeService(
        free_minutes=10,
        hourly_rate=50,
        daily_cap=200,
        resident_coefficient=0.5,
        max_minutes=600,
    )

    assert custom.calculate_fee(10) == pytest.approx(0.0)
    assert custom.calculate_fee(11) == pytest.approx(50.0)
    assert custom.calculate_fee(300) == pytest.approx(200.0)
    assert custom.calculate_fee(11, is_resident=True) == pytest.approx(25.0)

    with pytest.raises(ValueError):
        custom.calculate_fee(601)
