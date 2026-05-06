from datetime import date

import pytest
from unittest import mock

from django.test import RequestFactory

from bitcaster.models import Occurrence
from bitcaster.web.dashboard.components.tracker import ErrorTrackerComponent


@pytest.fixture
def mock_cache_manager():
    with mock.patch("bitcaster.web.dashboard.components.tracker.CacheManager") as mock_class:
        yield mock_class


@pytest.fixture
def mock_get_dates():
    with mock.patch("bitcaster.web.dashboard.components.tracker.get_dates") as mock_func:
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 31)
        mock_func.return_value = (start_date, end_date)
        yield mock_func


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def component(request_factory):
    request = request_factory.get("/dashboard/")
    return ErrorTrackerComponent(request)


def test_get_context_data_with_cache_hit(component, mock_cache_manager):
    cached_data = [{"color": "bg-green-700", "tooltip": 5}]
    mock_cache_manager.return_value.retrieve.return_value = cached_data

    context = component.get_context_data()

    mock_cache_manager.return_value.retrieve.assert_called_once_with("dashboard:tracker")
    assert context == {"data": cached_data}


def test_get_context_data_with_cache_miss_and_occurrences(component, mock_cache_manager, mock_get_dates):
    mock_cache_manager.return_value.retrieve.return_value = None  # Cache miss

    # Mock Occurrence objects
    occurrence_mock_data = [
        {"status": Occurrence.Status.PROCESSED.value, "count": 5},
        {"status": Occurrence.Status.FAILED.value, "count": 2},
        {"status": Occurrence.Status.NEW.value, "count": 1},
    ]

    with mock.patch("bitcaster.models.Occurrence.objects") as mock_occurrence_objects:
        mock_qs = mock.MagicMock()
        mock_occurrence_objects.filter.return_value = mock_qs
        mock_qs.values.return_value = mock_qs
        mock_qs.annotate.return_value = occurrence_mock_data

        context = component.get_context_data()

        mock_cache_manager.return_value.retrieve.assert_called_once()
        expected_data_for_store = [
            {"color": "bg-green-700", "tooltip": 5},
            {"color": "bg-green-700", "tooltip": 5},
            {"color": "bg-green-700", "tooltip": 5},
            {"color": "bg-green-700", "tooltip": 5},
            {"color": "bg-green-700", "tooltip": 5},
            {"color": "bg-red-700", "tooltip": 2},
            {"color": "bg-red-700", "tooltip": 2},
            {"color": "bg-gray-700", "tooltip": 1},
        ]
        mock_cache_manager.return_value.store.assert_called_once_with("dashboard:tracker", expected_data_for_store)

        assert "data" in context
        assert len(context["data"]) == 8
        assert context["data"] == expected_data_for_store


def test_get_context_data_with_cache_miss_no_occurrences(component, mock_cache_manager, mock_get_dates):
    mock_cache_manager.return_value.retrieve.return_value = None  # Cache miss

    with mock.patch("bitcaster.models.Occurrence.objects") as mock_occurrence_objects:
        mock_qs = mock.MagicMock()
        mock_occurrence_objects.filter.return_value = mock_qs
        mock_qs.values.return_value = mock_qs
        mock_qs.annotate.return_value = []  # No occurrences

        context = component.get_context_data()

        mock_cache_manager.return_value.retrieve.assert_called_once()
        mock_cache_manager.return_value.store.assert_called_once_with("dashboard:tracker", [])

        assert "data" in context
        assert context["data"] == []
