class DXFFileError(Exception):
    """Base class for exceptions in this module."""

    pass


class InvalidDXFFileError(DXFFileError):
    """Exception raised for invalid DXF file structure."""

    def __init__(self, message: str):
        super().__init__(message)


class DXFEntityError(DXFFileError):
    """Exception raised for errors in DXF entities."""

    pass
