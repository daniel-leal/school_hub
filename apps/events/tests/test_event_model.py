import pytest

from apps.events.models import Event


def test_event_type_choices_contain_only_three_types():
    choice_values = [value for value, _ in Event.EventType.choices]
    assert set(choice_values) == {"payment", "potluck", "presence"}
    assert "mixed" not in choice_values


def test_event_type_has_no_mixed_attribute():
    assert not hasattr(Event.EventType, "MIXED")


def test_event_model_has_no_is_payment_event_property():
    assert not hasattr(Event, "is_payment_event")


def test_event_model_has_no_is_potluck_event_property():
    assert not hasattr(Event, "is_potluck_event")


@pytest.mark.parametrize(
    "event_type,expected",
    [
        (Event.EventType.POTLUCK, True),
        (Event.EventType.PRESENCE, True),
        (Event.EventType.PAYMENT, False),
    ],
)
def test_requires_participation(event_type, expected):
    event = Event.__new__(Event)
    event.event_type = event_type
    assert event.requires_participation is expected
