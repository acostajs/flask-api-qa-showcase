from tui.employees_tab import format_availability


def test_format_availability_empty() -> None:
    """Test format_availability with empty or invalid input."""
    assert format_availability({}) == "Not set"
    assert format_availability(None) == "Not set"
    assert format_availability("not a dict") == "Not set"


def test_format_availability_valid_dict() -> None:
    """Test format_availability with valid dictionary input."""
    avail = {
        "monday": {"start": "09:00", "end": "17:00"},
        "Wednesday": "10am-6pm",
        "thursday": "Off",
    }
    expected = "Mon: 09:00 - 17:00\nWed: 10am-6pm"
    assert format_availability(avail) == expected
