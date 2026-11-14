from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("PyVideoKit-GUI")
except PackageNotFoundError:
    __version__ = "unknown"
