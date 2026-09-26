import requests
from django.conf import settings


class SourceError(Exception):
    """Erro genérico ao consumir uma fonte externa."""


class SourceTimeoutError(SourceError):
    """A fonte não respondeu dentro do tempo limite."""


class SourceUnavailableError(SourceError):
    """A fonte está fora do ar, recusou a conexão ou retornou erro HTTP."""


class SourceFormatError(SourceError):
    """A fonte respondeu, mas em um formato diferente do esperado."""


class BaseSourceClient:
    """Contrato comum para consumir e normalizar uma fonte externa.

    Cada subclasse define `source` (um valor de `integrations.models.Source`)
    e implementa `normalize()`. As falhas de rede/HTTP já são tratadas aqui e
    sempre viram uma das três exceções acima, para que o restante da
    aplicação nunca precise conhecer detalhes de `requests`.
    """

    source: str
    url: str

    def fetch_raw(self):
        timeout = getattr(settings, "EXTERNAL_SOURCE_TIMEOUT", (3, 8))
        try:
            response = requests.get(self.url, timeout=timeout)
        except requests.exceptions.Timeout as exc:
            raise SourceTimeoutError(
                f"{self.source}: tempo limite excedido ao consultar {self.url}"
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise SourceUnavailableError(
                f"{self.source}: falha de conexão com {self.url} ({exc})"
            ) from exc

        if response.status_code >= 400:
            raise SourceUnavailableError(
                f"{self.source}: resposta HTTP {response.status_code} de {self.url}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise SourceFormatError(
                f"{self.source}: resposta não é um JSON válido"
            ) from exc

    def normalize(self, raw_data):
        """Deve devolver uma lista de dicts prontos para virar `Item`."""
        raise NotImplementedError

    def run(self):
        """Busca e normaliza os dados, traduzindo qualquer falha inesperada
        de parsing em `SourceFormatError` (schema com chave faltando, tipo
        errado etc.)."""
        raw_data = self.fetch_raw()
        try:
            return self.normalize(raw_data)
        except SourceError:
            raise
        except (KeyError, TypeError, ValueError) as exc:
            raise SourceFormatError(
                f"{self.source}: estrutura de dados inesperada ({exc})"
            ) from exc
