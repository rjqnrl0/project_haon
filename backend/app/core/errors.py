from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, code: str, detail: str, status_code: int = 500):
        self.code = code
        self.detail = detail
        self.status_code = status_code


class AuthError(AppError):
    def __init__(self, detail: str = "인증이 필요합니다", code: str = "AUTH_REQUIRED"):
        super().__init__(code=code, detail=detail, status_code=401)


class ForbiddenError(AppError):
    def __init__(self, detail: str = "권한이 없습니다"):
        super().__init__(code="FORBIDDEN", detail=detail, status_code=403)


class NotFoundError(AppError):
    def __init__(self, detail: str = "리소스를 찾을 수 없습니다"):
        super().__init__(code="NOT_FOUND", detail=detail, status_code=404)


class ValidationError(AppError):
    def __init__(self, detail: str = "입력값이 올바르지 않습니다"):
        super().__init__(code="VALIDATION_ERROR", detail=detail, status_code=422)


class FileTooLargeError(AppError):
    def __init__(self, detail: str = "파일 크기가 10MB를 초과합니다"):
        super().__init__(code="FILE_TOO_LARGE", detail=detail, status_code=413)


class FileTypeInvalidError(AppError):
    def __init__(self, detail: str = "지원하지 않는 파일 형식입니다"):
        super().__init__(code="FILE_TYPE_INVALID", detail=detail, status_code=415)


class TaskExpiredError(AppError):
    def __init__(self, detail: str = "만료된 작업입니다"):
        super().__init__(code="TASK_EXPIRED", detail=detail, status_code=410)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
    )
