from pathlib import Path

BASE_DIR = Path.home() / ".dpnael-dashboard"
BACKUP_DIR = BASE_DIR / "backups"

PRIMARY_COLOR = "#D126F7"
ICON_CONTAINER = "📦"
ICON_IMAGE = "🖼️"

BACKUP_DIR.mkdir(parents=True, exist_ok=True)