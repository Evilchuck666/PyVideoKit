from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("PyVideoKit-CLI")
except PackageNotFoundError:
    __version__ = "unknown"
