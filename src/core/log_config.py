import os
import logging
import subprocess
import socket
import time
import traceback
import json
from pathlib import Path
from contextvars import ContextVar
from pythonjsonlogger import jsonlogger

REQUEST_ID_CTX: ContextVar[str | None] = ContextVar("request_id", default=None)

_RESERVED_LOG_RECORD_KEYS = set(logging.makeLogRecord({}).__dict__.keys())


def set_request_id(request_id: str) -> object:
    return REQUEST_ID_CTX.set(request_id)


def reset_request_id(token: object) -> None:
    REQUEST_ID_CTX.reset(token)


def get_request_id() -> str | None:
    return REQUEST_ID_CTX.get()


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        request_id = get_request_id()
        if request_id:
            record.request_id = request_id
        return True


def _candidate_build_metadata_paths() -> list[Path]:
    module_root = Path(__file__).resolve().parents[2]
    cwd = Path.cwd().resolve()
    return [
        module_root / "build_metadata.json",
        cwd / "build_metadata.json",
        Path("/app/build_metadata.json"),
    ]


def _read_build_metadata() -> tuple[dict, Path | None]:
    for path in _candidate_build_metadata_paths():
        if not path.exists():
            continue
        try:
            with path.open("r", encoding="utf-8") as fp:
                data = json.load(fp)
            if isinstance(data, dict):
                return data, path
        except Exception:
            continue
    return {}, None


def _read_git_value(command: list[str]) -> str | None:
    try:
        return subprocess.check_output(command).decode("utf-8").strip()
    except Exception:
        return None


def _build_app_metadata() -> dict:
    build_meta, _ = _read_build_metadata()

    app_name = os.getenv("APP_NAME") or build_meta.get("name")
    if not app_name:
        app_name = os.path.basename(os.getcwd()) or "unknown"

    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "unknown"

    release = (
        os.getenv("APP_RELEASE")
        or build_meta.get("release")
        or _read_git_value(["git", "describe", "--tags", "--abbrev=0"])
        or "unknown"
    )

    commit = (
        os.getenv("APP_COMMIT")
        or build_meta.get("commit")
        or _read_git_value(["git", "rev-parse", "HEAD"])
        or "unknown"
    )

    return {
        "name": app_name,
        "hostname": hostname,
        "release": release,
        "commit": commit,
    }


APP_METADATA = _build_app_metadata()


# Custom Formatter untuk JSON
class CustomJSONFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        # Menambahkan fields default dan metadata aplikasi
        log_record["app"] = APP_METADATA
        log_record["level"] = record.levelname.lower()
        log_record["time"] = int(time.time())  # UNIX timestamp

        super().add_fields(log_record, record, message_dict)

        # Include custom structured fields passed via `extra={...}`.
        for key, value in record.__dict__.items():
            if key in _RESERVED_LOG_RECORD_KEYS or key.startswith("_"):
                continue
            if key not in log_record:
                log_record[key] = value

        # Menambahkan stack trace hanya jika level log adalah ERROR dan ada exception
        if record.levelname.lower() == "error" and record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            log_record["exception_type"] = getattr(exc_type, "__name__", str(exc_type))
            log_record["exception_message"] = str(exc_value)
            log_record["stack"] = self.format_stack_trace(record.exc_info)
            log_record["traceback"] = self.format_exception_lines(record.exc_info)

        # Menghilangkan exc_info jika tidak ada exception
        if "exc_info" in log_record:
            del log_record["exc_info"]

    def format_stack_trace(self, exc_info):
        # Extract the stack trace from the exception info
        stack = traceback.format_exception(*exc_info)
        formatted_stack = []

        for line in stack:
            # Format each line to extract file path, function name, and line number
            if line.strip():
                # Example: '  File "main.py", line 20, in <module>'
                parts = line.strip().split(", ")
                if len(parts) >= 3:
                    file_info = parts[0].replace("File", "").strip().strip('"')
                    formatted_stack.append(f'"{file_info}"')

        return formatted_stack

    def format_exception_lines(self, exc_info):
        return [line.rstrip("\n") for line in traceback.format_exception(*exc_info)]


# Fungsi untuk mengatur logging
def setup_logging():
    # Konfigurasi Logging Utama
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    has_structured_handler = any(
        getattr(handler, "_mobee_structured_logger", False)
        for handler in root_logger.handlers
    )

    if not has_structured_handler:
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)

        log_handler = logging.StreamHandler()
        formatter = CustomJSONFormatter("%(message)s")
        log_handler.setFormatter(formatter)
        log_handler.addFilter(RequestContextFilter())
        log_handler._mobee_structured_logger = True
        root_logger.addHandler(log_handler)

    # Pastikan logger uvicorn mengikuti handler root (JSON)
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers = []
        uvicorn_logger.propagate = True
        uvicorn_logger.setLevel(logging.INFO)
