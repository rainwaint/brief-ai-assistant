"""Configuration loading for evaluation criteria."""

from __future__ import annotations

from pathlib import Path

import yaml

from brief_evaluator.models import CriteriaConfig
from brief_evaluator.protocols import CriteriaProvider


class YamlCriteriaProvider(CriteriaProvider):
    """Loads criteria from a YAML configuration file."""

    def __init__(self, config_path: Path | None = None) -> None:
        self._config_path = config_path or self.default_config_path()

    @staticmethod
    def default_config_path() -> Path:
        """Return the default criteria.yaml path relative to project root."""
        return Path(__file__).resolve().parents[2] / "config" / "criteria.yaml"

    def load(self) -> CriteriaConfig:
        """Load criteria from the configured path."""
        return self.load_from_path(self._config_path)

    def load_from_path(self, path: Path) -> CriteriaConfig:
        """Load and validate criteria from a YAML file."""
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        return CriteriaConfig.model_validate(data)
