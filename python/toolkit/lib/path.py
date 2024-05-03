from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from s3path import S3Path


def parse_path(path: str) -> Path:
    """Parse a `str` and create either an S3Path or Path

    Args:
        path(str):  The string to parse into a Path.

    Returns:
        Path: The Path return value.
    """
    url = urlparse(path)
    if url.scheme == "s3":
        return S3Path(f"/{url.netloc}/{url.path}")
    else:
        return Path(url.path).resolve()


def parse_optional_path(opt_path: str) -> Optional[Path]:
    """Parse an `str` and create either an Optional[S3Path] or Optional[Path]

    Args:
        opt_path(str): The string to parse into an optional Path.

    Returns:
        Optional[Path]: The optional Path return value.
    """
    return None if not opt_path else parse_path(opt_path)
