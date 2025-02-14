from pathlib import Path

from mako.lookup import TemplateLookup  # type: ignore


class BaseMakoPromptBuilder:
    def __init__(self, templates_dir: str | Path, template_name: str):
        self.templates_dir = Path(templates_dir)
        self.template_name = template_name

        if not self.templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {templates_dir}")

        template_path = self.templates_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        self.lookup = TemplateLookup(directories=[str(self.templates_dir)], input_encoding="utf-8")
