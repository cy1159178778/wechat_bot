from pathlib import Path

from packaging import version


__version__ = "0.7.4"


def need_init():
    file = Path(__file__).parent / "resource" / "ops_initialized"
    if not file.exists():
        return True
    with file.open("r", encoding="utf-8") as f:
        target = version.parse(f.read())
    source = version.parse(__version__)
    return target.major < source.major or target.minor < source.minor
