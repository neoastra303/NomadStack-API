import pytest

from app.core.exceptions import CityNotFoundError, ServiceUnavailableError


def test_city_not_found_error():
    exc = CityNotFoundError("Atlantis")
    assert "Atlantis" in str(exc)
    assert exc.city == "Atlantis"


def test_service_unavailable_error():
    exc = ServiceUnavailableError("Weather Service")
    assert "Weather Service" in str(exc)
    assert exc.service == "Weather Service"


def test_exception_hierarchy():
    assert issubclass(CityNotFoundError, Exception)
    assert issubclass(ServiceUnavailableError, Exception)
