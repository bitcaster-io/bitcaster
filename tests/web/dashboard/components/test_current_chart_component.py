import json
from datetime import date, datetime
from unittest import mock

import pytest
from django.test import RequestFactory

from bitcaster.models import Occurrence
from bitcaster.web.dashboard.components.current import CurrentChartComponent


@pytest.fixture
def mock_cache_manager():
    with mock.patch("bitcaster.web.dashboard.components.current.CacheManager") as mock_class:
        yield mock_class


@pytest.fixture
def mock_get_dates():
    with mock.patch("bitcaster.web.dashboard.components.current.get_dates") as mock_func:
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
    return CurrentChartComponent(request)


def test_get_context_data_with_cache_hit(component, mock_cache_manager):
    cached_data = {"height": 220, "data": '{"labels": [], "datasets": []}'}
    mock_cache_manager.return_value.retrieve.return_value = cached_data

    context = component.get_context_data()

    mock_cache_manager.return_value.retrieve.assert_called_once_with(
        "dashboard:cache:CurrentChartComponent"  # Correct cache key
    )
    assert context == cached_data


def test_get_context_data_with_cache_miss_and_occurrences(component, mock_cache_manager, mock_get_dates):
    mock_cache_manager.return_value.retrieve.return_value = None  # Cache miss

    # Mock Occurrence objects
    occurrence_mock_data = [
        {"hour": datetime(2023, 1, 31, 10, 0), "status": Occurrence.Status.PROCESSED.value, "count": 5},
        {"hour": datetime(2023, 1, 31, 10, 0), "status": Occurrence.Status.FAILED.value, "count": 2},
        {"hour": datetime(2023, 1, 31, 12, 0), "status": Occurrence.Status.PROCESSED.value, "count": 3},
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
        mock_cache_manager.return_value.store.assert_called_once_with(
            "dashboard:cache:CurrentChartComponent",  # Correct cache key
            mock.ANY,
        )

        assert "height" in context
        assert "data" in context

        chart_data = json.loads(context["data"])
        assert len(chart_data["labels"]) == 24
        assert chart_data["labels"][10] == "10"
        assert len(chart_data["datasets"]) == len(Occurrence.Status)

        # Check data for PROCESSED status
        processed_data = next((ds for ds in chart_data["datasets"] if ds["label"] == "Processed"), None)
        assert processed_data["data"][10] == 5
        assert processed_data["data"][12] == 3
        assert processed_data["data"][11] == 0


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
        assert len(chart_data["labels"]) == 24
        for ds in chart_data["datasets"]:
            assert all(d == 0 for d in ds["data"])
