from pathlib import Path

_this_file = Path(__file__).resolve()

DIR_REPO = _this_file.parent.resolve()

DIR_TASK = (DIR_REPO / "task_folder").resolve()
DIR_TASK_EVENTS = (DIR_TASK / "event").resolve()
DIR_TASK_SCHEMA = (DIR_TASK / "schema").resolve()
