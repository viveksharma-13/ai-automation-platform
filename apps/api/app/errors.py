from fastapi import HTTPException, status


class AppError(HTTPException):
    def __init__(self, status_code: int, detail: str, code: str = "error") -> None:
        super().__init__(status_code=status_code, detail={"code": code, "message": detail})
        self.code = code


class NotFoundError(AppError):
    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, "not_found")


class UnauthorizedError(AppError):
    def __init__(self, detail: str = "Not authenticated") -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, "unauthorized")


class ForbiddenError(AppError):
    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail, "forbidden")


class ConflictError(AppError):
    def __init__(self, detail: str = "Conflict") -> None:
        super().__init__(status.HTTP_409_CONFLICT, detail, "conflict")


class ValidationAppError(AppError):
    def __init__(self, detail: str) -> None:
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, detail, "validation_error")
