"""Aplicativo Flask para organizar estudos teológicos.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from flask import Flask, redirect, render_template_string, request, url_for
from jinja2 import DictLoader

APP_TITLE = "Biblioteca de Estudos Teológicos"
DATA_FILE = Path("dados_teologia.json")
DEFAULT_TOPICS = [
    "Teologia Sistemática",
    "Estudos Bíblicos",
    "Línguas Originais (Grego)",
    "Línguas Originais (Hebraico)",
    "Assuntos Polêmicos",
    "Curiosidades",
    "Apologética",
    "História da Igreja",
    "Outros",
]

app = Flask(__name__)


def load_data() -> Dict[str, List[dict]]:
    if not DATA_FILE.exists():
        return {"temas": DEFAULT_TOPICS, "estudos": []}

    try:
        with DATA_FILE.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
    except json.JSONDecodeError:
        data = {"temas": DEFAULT_TOPICS, "estudos": []}

    temas = data.get("temas", DEFAULT_TOPICS)
    estudos = data.get("estudos", [])

    for estudo in estudos:
        estudo.setdefault("criado_em_iso", estudo.get("criado_em", ""))
        estudo.setdefault("criado_em", estudo.get("criado_em_iso", ""))

    # Garantir que todos os temas padrão existam
    for tema in DEFAULT_TOPICS:
        if tema not in temas:
            temas.append(tema)

    return {"temas": temas, "estudos": estudos}


def save_data(data: Dict[str, List[dict]]) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)


HTML_BASE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ titulo }}</title>
    <style>
        :root {
            color-scheme: light dark;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: #f7f9fc;
            color: #1f2937;
        }
        header {
            background: linear-gradient(135deg, #1d4ed8, #312e81);
            color: white;
            padding: 2rem 1rem;
            text-align: center;
        }
        header h1 {
            margin: 0 0 0.5rem 0;
            font-size: 2rem;
        }
        header p {
            margin: 0;
            opacity: 0.85;
        }
        main {
            max-width: 1100px;
            margin: -2rem auto 0;
            padding: 0 1rem 3rem;
        }
        .card {
            background: white;
            border-radius: 18px;
            box-shadow: 0 10px 40px rgba(15, 23, 42, 0.15);
            padding: 2rem;
            margin-bottom: 2rem;
        }
        .grid {
            display: grid;
            gap: 1.5rem;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        }
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(37, 99, 235, 0.1);
            color: #1d4ed8;
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .entry {
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 16px;
            padding: 1.5rem;
            background: linear-gradient(180deg, rgba(255, 255, 255, 0.85), rgba(248, 250, 252, 0.85));
        }
        .entry h3 {
            margin: 0 0 0.75rem 0;
            font-size: 1.25rem;
        }
        .entry p {
            margin: 0.5rem 0;
            line-height: 1.6;
        }
        .entry-footer {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
            font-size: 0.875rem;
            color: #475569;
        }
        .entry-footer a {
            color: #1d4ed8;
            text-decoration: none;
        }
        .entry-footer a:hover {
            text-decoration: underline;
        }
        form {
            display: grid;
            gap: 1rem;
        }
        label {
            font-weight: 600;
            color: #1f2937;
        }
        input[type="text"], textarea, select {
            padding: 0.75rem 1rem;
            border-radius: 12px;
            border: 1px solid rgba(15, 23, 42, 0.2);
            font-size: 1rem;
            width: 100%;
            box-sizing: border-box;
        }
        textarea {
            min-height: 140px;
            resize: vertical;
        }
        button {
            padding: 0.85rem 1.5rem;
            border-radius: 12px;
            border: none;
            background: linear-gradient(135deg, #2563eb, #1e40af);
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.1s ease, box-shadow 0.1s ease;
        }
        button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.35);
        }
        nav {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-bottom: 1.5rem;
        }
        nav a {
            text-decoration: none;
            background: rgba(79, 70, 229, 0.08);
            color: #312e81;
            padding: 0.65rem 1.2rem;
            border-radius: 12px;
            font-weight: 600;
            transition: background 0.2s ease;
        }
        nav a:hover {
            background: rgba(79, 70, 229, 0.15);
        }
        .muted {
            color: #6b7280;
            font-size: 0.95rem;
        }
        .search-bar {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            margin-bottom: 1.5rem;
        }
        .search-bar input[type="search"] {
            flex: 1 1 280px;
        }
        @media (max-width: 600px) {
            header h1 { font-size: 1.6rem; }
            .card { padding: 1.5rem; }
        }
    </style>
</head>
<body>
    <header>
        <h1>{{ titulo }}</h1>
        <p>Centralize seus estudos, referências, links e notas de temas teológicos, línguas bíblicas e assuntos polêmicos.</p>
    </header>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
"""


@app.route("/")
def index():
    data = load_data()
    query = request.args.get("q", "").strip().lower()

    estudos = data["estudos"]
    if query:
        estudos = [
            estudo
            for estudo in estudos
            if query in estudo["titulo"].lower()
            or query in estudo.get("resumo", "").lower()
            or any(query in nota.lower() for nota in estudo.get("anotacoes", "").splitlines())
            or any(query in tag.lower() for tag in estudo.get("tags", []))
        ]

    temas_com_contagem = {
        tema: sum(1 for estudo in estudos if estudo["tema"] == tema)
        for tema in data["temas"]
    }
    estudos_ordenados = sorted(
        estudos,
        key=lambda item: item.get("criado_em_iso", ""),
        reverse=True,
    )

    return render_template_string(
        """
        {% extends "base.html" %}
        {% block content %}
        <div class="card">
            <div class="search-bar">
                <form method="get" style="flex:1;display:flex;gap:.75rem;flex-wrap:wrap;">
                    <input type="search" name="q" placeholder="Buscar por tema, título, tag ou palavra-chave" value="{{ request.args.get('q', '') }}">
                    <button type="submit">Pesquisar</button>
                </form>
                <a href="{{ url_for('novo_estudo') }}" style="align-self:center;text-decoration:none;">
                    <button type="button">Adicionar Estudo</button>
                </a>
            </div>
            <p class="muted">Dica: use tags para separar estudos por autores, livros bíblicos, disciplinas acadêmicas ou palavras-chave específicas.</p>
        </div>
        <div class="card">
            <h2>Temas principais</h2>
            <div class="grid">
                {% for tema, quantidade in temas.items() %}
                <a href="{{ url_for('ver_tema', tema_slug=tema) }}" style="text-decoration:none;color:inherit;">
                    <div class="entry">
                        <div class="badge">{{ quantidade }} estudos</div>
                        <h3>{{ tema }}</h3>
                        <p class="muted">Clique para ver todos os materiais relacionados a este tema.</p>
                    </div>
                </a>
                {% endfor %}
            </div>
        </div>
        {% if estudos_ordenados %}
        <div class="card">
            <h2>{% if busca %}Resultados da pesquisa{% else %}Últimos estudos registrados{% endif %}</h2>
            {% if busca %}
            <p class="muted">Encontramos {{ estudos_ordenados|length }} resultado(s) para "{{ busca }}".</p>
            {% endif %}
            {% set lista = estudos_ordenados[:6] if not busca else estudos_ordenados %}
            <div class="grid">
                {% for estudo in lista %}
                <div class="entry">
                    <div class="badge">{{ estudo.tema }}</div>
                    <h3>{{ estudo.titulo }}</h3>
                    <p>{{ estudo.resumo or 'Sem resumo adicionado ainda.' }}</p>
                    {% if estudo.tags %}
                    <p class="muted">Tags: {{ estudo.tags | join(', ') }}</p>
                    {% endif %}
                    <div class="entry-footer">
                        {% if estudo.criado_em %}
                        <span>Atualizado em {{ estudo.criado_em }}</span>
                        {% endif %}
                        {% if estudo.link %}
                        <a href="{{ estudo.link }}" target="_blank" rel="noopener">Abrir referência externa</a>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% else %}
        <div class="card">
            {% if busca %}
            <p class="muted">Não encontramos resultados para "{{ busca }}". Tente ajustar os termos da pesquisa.</p>
            {% else %}
            <p class="muted">Nenhum estudo cadastrado ainda. Comece adicionando seus materiais.</p>
            {% endif %}
        </div>
        {% endif %}
        {% endblock %}
        """,
        titulo=APP_TITLE,
        temas=temas_com_contagem,
        estudos_ordenados=estudos_ordenados,
        busca=query,
    )


@app.route("/tema/<path:tema_slug>")
def ver_tema(tema_slug: str):
    data = load_data()
    estudos = [estudo for estudo in data["estudos"] if estudo["tema"] == tema_slug]
    estudos = sorted(estudos, key=lambda item: item.get("criado_em_iso", ""), reverse=True)

    return render_template_string(
        """
        {% extends "base.html" %}
        {% block content %}
        <nav>
            <a href="{{ url_for('index') }}">← Voltar</a>
            <a href="{{ url_for('novo_estudo', tema=tema_slug) }}">Adicionar estudo para este tema</a>
        </nav>
        <div class="card">
            <h2>{{ tema }}</h2>
            <p class="muted">Total de estudos: {{ estudos|length }}</p>
        </div>
        <div class="grid">
            {% for estudo in estudos %}
            <div class="entry">
                <div class="badge">{{ estudo.tema }}</div>
                <h3>{{ estudo.titulo }}</h3>
                <p>{{ estudo.resumo or 'Sem resumo adicionado ainda.' }}</p>
                {% if estudo.anotacoes %}
                <p class="muted">Anotações:</p>
                <p>{{ estudo.anotacoes.replace('\n', '<br>') | safe }}</p>
                {% endif %}
                <div class="entry-footer">
                    {% if estudo.criado_em %}
                    <span>Registrado em {{ estudo.criado_em }}</span>
                    {% endif %}
                    {% if estudo.tags %}
                    <span>Tags: {{ estudo.tags | join(', ') }}</span>
                    {% endif %}
                    {% if estudo.link %}
                    <a href="{{ estudo.link }}" target="_blank" rel="noopener">Abrir referência externa</a>
                    {% endif %}
                </div>
            </div>
            {% else %}
            <div class="card">
                <p class="muted">Ainda não há estudos cadastrados neste tema. Clique em "Adicionar estudo" para começar.</p>
            </div>
            {% endfor %}
        </div>
        {% endblock %}
        """,
        titulo=f"{APP_TITLE} · {tema_slug}",
        tema=tema_slug,
        estudos=estudos,
    )


@app.route("/novo", methods=["GET", "POST"])
def novo_estudo():
    data = load_data()
    temas = data["temas"]
    tema_sugerido = request.args.get("tema")

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        tema_escolhido = request.form.get("tema_existente", "Outros").strip()
        tema_novo = request.form.get("tema_novo", "").strip()
        tema = tema_novo or tema_escolhido or "Outros"
        resumo = request.form.get("resumo", "").strip()
        anotacoes = request.form.get("anotacoes", "").strip()
        link = request.form.get("link", "").strip()
        tags = [tag.strip() for tag in request.form.get("tags", "").split(",") if tag.strip()]

        if tema and tema not in temas:
            temas.append(tema)

        if titulo:
            agora = datetime.now()
            novo_registro = {
                "id": str(uuid.uuid4()),
                "titulo": titulo,
                "tema": tema or "Outros",
                "resumo": resumo,
                "anotacoes": anotacoes,
                "link": link,
                "tags": tags,
                "criado_em_iso": agora.isoformat(),
                "criado_em": agora.strftime("%d/%m/%Y %H:%M"),
            }
            data["temas"] = temas
            data["estudos"].append(novo_registro)
            save_data(data)
            return redirect(url_for("ver_tema", tema_slug=novo_registro["tema"]))

    return render_template_string(
        """
        {% extends "base.html" %}
        {% block content %}
        <nav>
            <a href="{{ url_for('index') }}">← Voltar ao painel</a>
        </nav>
        <div class="card">
            <h2>Registrar novo estudo</h2>
            <form method="post">
                <div>
                    <label for="titulo">Título do estudo</label>
                    <input type="text" id="titulo" name="titulo" placeholder="Ex.: Justificação pela fé em Romanos" required>
                </div>
                <div>
                    <label for="tema">Tema</label>
                    <select id="tema" name="tema_existente">
                        {% for tema in temas %}
                        <option value="{{ tema }}" {% if tema == tema_sugerido %}selected{% endif %}>{{ tema }}</option>
                        {% endfor %}
                    </select>
                    <p class="muted">Não encontrou um tema? Informe abaixo para criar um novo.</p>
                </div>
                <div>
                    <label for="novo_tema">Adicionar novo tema (opcional)</label>
                    <input type="text" id="novo_tema" name="tema_novo" placeholder="Digite um novo tema para categorizar este estudo">
                </div>
                <div>
                    <label for="resumo">Resumo</label>
                    <textarea id="resumo" name="resumo" placeholder="Sinopse do estudo, insights principais, contexto histórico, etc."></textarea>
                </div>
                <div>
                    <label for="anotacoes">Anotações detalhadas</label>
                    <textarea id="anotacoes" name="anotacoes" placeholder="Use este espaço para colocar notas em grego/hebraico, intertextualidades, polêmicas, perguntas para debate..."></textarea>
                </div>
                <div>
                    <label for="tags">Tags (separe por vírgulas)</label>
                    <input type="text" id="tags" name="tags" placeholder="Ex.: soteriologia, calvinismo, graça comum">
                </div>
                <div>
                    <label for="link">Link de referência externa</label>
                    <input type="text" id="link" name="link" placeholder="Cole aqui o link de artigos, vídeos, PDFs, etc.">
                </div>
                <button type="submit">Salvar estudo</button>
            </form>
        </div>
        {% endblock %}
        """,
        titulo=f"{APP_TITLE} · Novo estudo",
        temas=temas,
        tema_sugerido=tema_sugerido,
    )


# Registrar o template base no ambiente Jinja
app.jinja_loader = DictLoader({"base.html": HTML_BASE})


if __name__ == "__main__":
    print("=" * 60)
    print(APP_TITLE)
    print("Acesse: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
