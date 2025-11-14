"""Testes automatizados para o aplicativo teológico."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import unquote

import pytest

pytest.importorskip("flask")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import teologia_app


@pytest.fixture(autouse=True)
def usar_arquivo_de_teste(tmp_path, monkeypatch):
    """Garante que cada teste use um arquivo de dados isolado."""
    data_file = tmp_path / "dados_testes.json"
    monkeypatch.setattr(teologia_app, "DATA_FILE", data_file)
    yield data_file


def test_load_data_retorna_valores_padrao():
    dados = teologia_app.load_data()

    assert dados["estudos"] == []
    assert set(teologia_app.DEFAULT_TOPICS).issubset(set(dados["temas"]))


def test_criacao_de_novo_estudo_salva_no_arquivo(usar_arquivo_de_teste):
    app = teologia_app.app
    app.config.update(TESTING=True)

    with app.test_client() as client:
        resposta = client.post(
            "/novo",
            data={
                "titulo": "A prova da fé",
                "tema_existente": teologia_app.DEFAULT_TOPICS[0],
                "tema_novo": "",
                "resumo": "Um estudo sobre Tiago 1.",
                "anotacoes": "Texto base: Tg 1.2-4",
                "tags": "fé, provações",
                "link": "https://example.com/estudo",
            },
            follow_redirects=False,
        )

    assert resposta.status_code == 302
    assert "/tema/" in resposta.headers["Location"]
    assert teologia_app.DEFAULT_TOPICS[0] in unquote(resposta.headers["Location"])

    dados_salvos = json.loads(usar_arquivo_de_teste.read_text(encoding="utf-8"))
    assert len(dados_salvos["estudos"]) == 1

    estudo = dados_salvos["estudos"][0]
    assert estudo["titulo"] == "A prova da fé"
    assert estudo["tema"] == teologia_app.DEFAULT_TOPICS[0]
    assert estudo["resumo"] == "Um estudo sobre Tiago 1."
    assert "criado_em" in estudo and estudo["criado_em"]
    assert "criado_em_iso" in estudo and estudo["criado_em_iso"]
    assert estudo["tags"] == ["fé", "provações"]
    assert estudo["link"] == "https://example.com/estudo"
