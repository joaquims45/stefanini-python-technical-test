"""Config raiz do pytest.

Os testes marcados `external_api` pegam as APIs públicas reais (não mocks) —
servem para detectar se uma delas mudou de formato. Ficam de fora do `pytest`
padrão (que precisa rodar sem internet) e só executam com `--run-external`.
"""
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-external",
        action="store_true",
        default=False,
        help="Roda também os testes marcados 'external_api' (requer internet).",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-external"):
        return

    skip_external = pytest.mark.skip(
        reason="marcado 'external_api' — rode com --run-external para incluir"
    )
    for item in items:
        if "external_api" in item.keywords:
            item.add_marker(skip_external)
