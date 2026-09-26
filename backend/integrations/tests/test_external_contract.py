"""Testes de contrato contra as APIs públicas reais (opt-in).

Diferente de test_clients.py (que mocka as respostas para os cenários
obrigatórios de falha), estes testes fazem a chamada HTTP de verdade. Servem
para detectar quando a fonte externa muda de formato de um jeito que o
parsing atual não capturaria como erro — por isso ficam fora do `pytest`
padrão (marcados `external_api`, ver conftest.py) e rodam sob demanda com:

    pytest -m external_api --run-external
"""
from datetime import date

import pytest

from integrations.clients.brasilapi_feriados import BrasilApiFeriadosClient
from integrations.clients.open_brewery_db import OpenBreweryDbClient
from integrations.models import Source


@pytest.mark.external_api
def test_contrato_real_da_brasilapi_feriados():
    items = BrasilApiFeriadosClient().run()

    assert len(items) > 0
    for item in items:
        assert item["source"] == Source.BRASILAPI_FERIADOS
        assert isinstance(item["external_id"], str) and item["external_id"]
        assert isinstance(item["title"], str) and item["title"]
        assert isinstance(item["event_date"], date)
        assert isinstance(item["payload"], dict)


@pytest.mark.external_api
def test_contrato_real_do_open_brewery_db():
    items = OpenBreweryDbClient().run()

    assert len(items) > 0
    for item in items:
        assert item["source"] == Source.OPEN_BREWERY_DB
        assert isinstance(item["external_id"], str) and item["external_id"]
        assert isinstance(item["title"], str) and item["title"]
        assert isinstance(item["payload"], dict)
