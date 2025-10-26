import logging
import os
from datetime import datetime
from pathlib import Path


class Logger:
    """Cache per-module loggers; each name gets its own logger object."""

    _loggers: dict[str, logging.Logger] = {}
    _logs_dir: Path | None = None  # computed once

    @classmethod
    def _resolve_logs_dir(cls) -> Path:
        if cls._logs_dir is not None:
            return cls._logs_dir

        env_log_dir = os.getenv("LOG_DIR")
        if env_log_dir:
            logs_dir = Path(env_log_dir).expanduser().resolve()
        else:
            # <project_root>/logs  assuming this file is at <root>/src/utils/logger.py
            current_file = Path(__file__).resolve()
            project_root = current_file.parents[2]  # .../src/utils/logger.py -> parents[2] == <root>
            if not (project_root / "src").is_dir():
                project_root = Path.cwd()
            logs_dir = project_root / "logs"

        logs_dir.mkdir(parents=True, exist_ok=True)
        cls._logs_dir = logs_dir
        return logs_dir

    @classmethod
    def get_logger(cls, name: str, level: int = logging.DEBUG) -> logging.Logger:
        # return cached logger per name
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.propagate = False  # don't bubble to root and duplicate

        if not logger.handlers:
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            logs_dir = cls._resolve_logs_dir()
            log_file = logs_dir / f"app_{datetime.now().strftime("%Y-%m-%d")}.log"

            file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            logger.debug(f"Logger initialized. Writing to: {log_file}")

        cls._loggers[name] = logger
        return logger
