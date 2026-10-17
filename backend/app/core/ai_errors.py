class AIServiceError(Exception):
    """Safe, user-facing classification for unavailable or invalid AI results."""

    def __init__(self, message: str = "AI processing is temporarily unavailable"):
        super().__init__(message)
        self.message = message


class AIServiceUnavailable(AIServiceError):
    pass


class AIServiceInvalidResponse(AIServiceError):
    pass
