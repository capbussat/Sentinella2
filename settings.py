# settings.py

from pathlib import Path
import yaml

SETTINGS_YAML_FILE = "/etc/sentinella/settings.yaml"

class Settings:
    def __init__(self, filename=SETTINGS_YAML_FILE):
        self.filename = Path(filename)
        self.data = self._load()

    def _load(self):
        if not self.filename.exists():
            raise FileNotFoundError(
                f"No s'ha trobat el fitxer de configuració: {self.filename}"
            )

        with open(self.filename, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @property
    def settings(self):
        return self.data.get("settings", {})

    @property
    def buttons(self):
        return self.data.get("buttons", [])

    def reload(self):
        """Recarrega la configuració des del fitxer."""
        self.data = self._load()


# Global instance
settings = Settings()
print("Settings loaded")


