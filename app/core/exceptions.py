class AppError(Exception):
    """Base class for the application exceptions."""

class IngestionError(AppError):
    """Base class for ingestion-related errors."""

class UnsupportedSourceError(IngestionError):
    """Raised when the source type is not supported."""

class SourceFetchError(IngestionError):
    """Raised when a remote source cannot be fetched."""

class SourceParseError(IngestionError):
    """Raised when a fetched source cannot be parsed into usable text."""
