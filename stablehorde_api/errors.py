class StatusNotFound(BaseException):
    """Raise when status of generation is not found"""

class InvalidAPIKey(BaseException):
    pass

class ValidationError(BaseException):
    pass

class TooManyPrompts(BaseException):
    pass

class MaintenanceMode(BaseException):
    pass

class AvailableWorkerNotFound(BaseException):
    pass
