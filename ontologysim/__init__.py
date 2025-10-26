import os
from pathlib import Path

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as version_file:
    version = version_file.read().strip()

__version__ = version


def get_default_config_file_paths() -> dict[str, Path]:
    return {
        "production": (
            Path(__file__).parent
            / "Flask"
            / "Assets"
            / "DefaultFiles"
            / "production_config_lvl3.ini"
        ).resolve(),
        "owl": (
            Path(__file__).parent
            / "Flask"
            / "Assets"
            / "DefaultFiles"
            / "owl_config.ini"
        ).resolve(),
        "controller": (
            Path(__file__).parent
            / "Flask"
            / "Assets"
            / "DefaultFiles"
            / "controller_config.ini"
        ).resolve(),
        "logger": (
            Path(__file__).parent
            / "Flask"
            / "Assets"
            / "DefaultFiles"
            / "logger_config_lvl3.ini"
        ).resolve(),
    }
