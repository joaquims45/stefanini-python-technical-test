import json
import logging

# Campos padrão de um LogRecord — usados para separar os campos "extra"
# (os que a aplicação passou explicitamente) do resto do record.
_STANDARD_LOG_RECORD_FIELDS = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__)


class JsonFormatter(logging.Formatter):
    """Formatter mínimo que serializa cada log como uma linha JSON.

    Sem dependência nova: só usa `json` da stdlib. Os campos passados via
    `extra={...}` no `logger.info(...)` viram chaves de primeiro nível no
    JSON de saída.
    """

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra = {
            key: value
            for key, value in record.__dict__.items()
            if key not in _STANDARD_LOG_RECORD_FIELDS
        }
        payload.update(extra)
        return json.dumps(payload, default=str, ensure_ascii=False)
