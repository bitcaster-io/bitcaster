import json
from datetime import date
from unittest import mock

import pytest
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

    # Mock Occurrence objects
    occurrence_mock_data = [
        {"day": date(2023, 1, 1), "status": Occurrence.Status.PROCESSED.value, "count": 5},
        {"day": date(2023, 1, 1), "status": Occurrence.Status.FAILED.value, "count": 2},
        {"day": date(2023, 1, 2), "status": Occurrence.Status.PROCESSED.value, "count": 3},
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
        assert chart_data["labels"][0] == "Jan 01"
        assert len(chart_data["datasets"]) == len(Occurrence.Status)

        # Check data for PROCESSED status
        processed_data = next((ds for ds in chart_data["datasets"] if ds["label"] == "Processed"), None)
        assert processed_data["data"][0] == 5
        assert processed_data["data"][1] == 3  # Jan 02 has PROCESSED with count 3

        # Check data for FAILED status
        failed_data = next((ds for ds in chart_data["datasets"] if ds["label"] == "Failed"), None)
        assert failed_data["data"][0] == 2
        assert failed_data["data"][1] == 0

        # Check data for NEW status (should be all zeros as not in mock data)
        new_data = next((ds for ds in chart_data["datasets"] if ds["label"] == "New"), None)
        assert all(d == 0 for d in new_data["data"])


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
        assert chart_data["labels"]
        for ds in chart_data["datasets"]:
            assert all(d == 0 for d in ds["data"])
