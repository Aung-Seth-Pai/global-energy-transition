from pathlib import Path
import os

def get_paths(project_root: Path | None = None):
    if project_root is None:
        project_root = Path(__file__).resolve().parents[2]

    data_dir = project_root / "data"
    return {
        "PROJECT_ROOT": project_root,
        "DATA_DIR": data_dir,
        "RAW_DATA_DIR": data_dir / "raw",
        "PROCESSED_DATA_DIR": data_dir / "processed",
        "NOTEBOOKS_DIR": project_root / "notebooks",
        "LOGS_DIR": project_root / "logs",
    }
