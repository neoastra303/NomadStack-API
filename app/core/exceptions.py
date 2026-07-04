class NomadStackError(Exception):
    pass


class CityNotFoundError(NomadStackError):
    def __init__(self, city: str):
        self.city = city
        super().__init__(f"City not found: {city}")


class ServiceUnavailableError(NomadStackError):
    def __init__(self, service: str):
        self.service = service
        super().__init__(f"Service unavailable: {service}")
