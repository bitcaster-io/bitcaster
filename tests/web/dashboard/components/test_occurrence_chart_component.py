import json
from datetime import date

import pytest
from unittest import mock

from django.test import RequestFactory

from bitcaster.models import Occurrence
from bitcaster.web.dashboard.components.occurrences import OccurrenceChartComponent


@pytest.fixture
def mock_cache_manager():
    # Patch CacheManager where it's used/looked up by OccurrenceChartComponent
    with mock.patch("bitcaster.web.dashboard.components.occurrences.CacheManager") as mock_class:
        yield mock_class


@pytest.fixture
def mock_get_dates():
    with mock.patch("bitcaster.web.dashboard.components.occurrences.get_dates") as mock_func:
        # Revert to original 31-day range as component hardcodes range(31)
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
    return OccurrenceChartComponent(request)


def test_get_context_data_with_cache_hit(component, mock_cache_manager):
    cached_data = {"height": 220, "data": '{"labels": [], "datasets": []}'}
    # Configure the mock instance that will be returned when CacheManager is instantiated
    mock_cache_manager.return_value.retrieve.return_value = cached_data

    context = component.get_context_data()

    # Assertions should be on the mock instance
    mock_cache_manager.return_value.retrieve.assert_called_once_with("dashboard:cache:OccurrenceChartComponent")
    assert context == cached_data


def test_get_context_data_with_cache_miss_and_occurrences(component, mock_cache_manager, mock_get_dates):
    mock_cache_manager.return_value.retrieve.return_value = None  # Cache miss

    # Mock Occurrence objects - sparse data across the 31-day range
    occurrence_mock_data = [
        {"day": date(2023, 1, 1), "status": Occurrence.Status.PROCESSING.value, "count": 5},
        {"day": date(2023, 1, 1), "status": Occurrence.Status.FAILED.value, "count": 2},
        {"day": date(2023, 1, 1), "status": Occurrence.Status.NEW.value, "count": 1},
        {"day": date(2023, 1, 15), "status": Occurrence.Status.PROCESSING.value, "count": 10},
        {"day": date(2023, 1, 15), "status": Occurrence.Status.FAILED.value, "count": 6},
        {"day": date(2023, 1, 15), "status": Occurrence.Status.NEW.value, "count": 3},
        {"day": date(2023, 1, 31), "status": Occurrence.Status.PROCESSING.value, "count": 7},
        {"day": date(2023, 1, 31), "status": Occurrence.Status.FAILED.value, "count": 8},
        {"day": date(2023, 1, 31), "status": Occurrence.Status.NEW.value, "count": 4},
    ]

    with mock.patch("bitcaster.models.Occurrence.objects") as mock_occurrence_objects:
        mock_qs = mock.MagicMock()
        mock_occurrence_objects.filter.return_value = mock_qs
        mock_qs.annotate.return_value = mock_qs
        mock_qs.values.return_value = mock_qs
        mock_qs.annotate.return_value = mock_qs
        mock_qs.order_by.return_value = occurrence_mock_data

        context = component.get_context_data()

        mock_cache_manager.return_value.retrieve.assert_called_once()
        mock_cache_manager.return_value.store.assert_called_once()

        assert "height" in context
        assert "data" in context

        chart_data = json.loads(context["data"])
        assert len(chart_data["labels"]) == 31  # Now asserting 31 labels
        assert chart_data["labels"][0] == "Jan 01"
        assert chart_data["labels"][14] == "Jan 15"  # Index for Jan 15
        assert chart_data["labels"][30] == "Jan 31"  # Index for Jan 31

        # Check data for PROCESSED status
        processed_data = next((ds for ds in chart_data["datasets"] if ds["label"] == "Processed"), None)
        assert processed_data["data"][0] == 5
        assert processed_data["data"][14] == 10
        assert processed_data["data"][30] == 7
        assert all(processed_data["data"][i] == 0 for i in range(31) if i not in [0, 14, 30])

        # Check data for FAILED status
        failed_data = next((ds for ds in chart_data["datasets"] if ds["label"] == "Failed"), None)
        assert failed_data["data"][0] == 2
        assert failed_data["data"][14] == 6
        assert failed_data["data"][30] == 8
        assert all(failed_data["data"][i] == 0 for i in range(31) if i not in [0, 14, 30])

        # Check data for NEW status
        new_data = next((ds for ds in chart_data["datasets"] if ds["label"] == "New"), None)
        assert new_data["data"][0] == 1
        assert new_data["data"][14] == 3
        assert new_data["data"][30] == 4
        assert all(new_data["data"][i] == 0 for i in range(31) if i not in [0, 14, 30])


def test_get_context_data_with_cache_miss_no_occurrences(component, mock_cache_manager, mock_get_dates):
    mock_cache_manager.return_value.retrieve.return_value = None  # Cache miss

    with mock.patch("bitcaster.models.Occurrence.objects") as mock_occurrence_objects:
        mock_qs = mock.MagicMock()
        mock_occurrence_objects.filter.return_value = mock_qs
        mock_qs.annotate.return_value = mock_qs
        mock_qs.values.return_value = mock_qs
        mock_qs.annotate.return_value = mock_qs
        mock_qs.order_by.return_value = []  # No occurrences

        context = component.get_context_data()

        mock_cache_manager.return_value.retrieve.assert_called_once()
        mock_cache_manager.return_value.store.assert_called_once()

        chart_data = json.loads(context["data"])
        assert len(chart_data["labels"]) == 31  # Now asserting 31 labels
        for ds in chart_data["datasets"]:
            assert all(d == 0 for d in ds["data"])
