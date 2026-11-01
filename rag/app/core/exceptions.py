"""Custom application exceptions and error structures."""

from typing import Any, Dict, Optional


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class AuthenticationException(AppException):
    """Raised when an internal service request fails token verification."""

    def __init__(self, message: str = "Invalid or missing internal service token"):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401,
        )


class ConfigurationException(AppException):
    """Raised when essential configuration or credentials are missing."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR",
            status_code=500,
        )


class ProviderException(AppException):
    """Raised when an external model or embedding provider fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="PROVIDER_ERROR",
            status_code=502,
            details=details,
        )


class UnsupportedMediaTypeException(AppException):
    """Raised when an uploaded file type is unsupported."""

    def __init__(self, message: str = "Unsupported document format. Allowed types: PDF, TXT."):
        super().__init__(
            message=message,
            code="UNSUPPORTED_MEDIA_TYPE",
            status_code=415,
        )


class PayloadTooLargeException(AppException):
    """Raised when an uploaded file exceeds the allowed size limit."""

    def __init__(self, message: str = "File size exceeds the allowed limit (max 20MB)."):
        super().__init__(
            message=message,
            code="FILE_TOO_LARGE",
            status_code=413,
        )


class EmptyDocumentException(AppException):
    """Raised when an ingested document contains no extractable text."""

    def __init__(self, message: str = "The document is empty or contains no extractable text."):
        super().__init__(
            message=message,
            code="EMPTY_DOCUMENT",
            status_code=400,
        )


class CorruptedDocumentException(AppException):
    """Raised when a document cannot be opened or parsed due to corruption."""

    def __init__(self, message: str = "Document is corrupted or cannot be parsed."):
        super().__init__(
            message=message,
            code="CORRUPTED_DOCUMENT",
            status_code=400,
        )


class DocumentExtractionException(AppException):
    """Raised when an unexpected error occurs during document text extraction."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="EXTRACTION_ERROR",
            status_code=422,
            details=details,
        )
