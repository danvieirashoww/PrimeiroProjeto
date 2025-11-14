# PrimeiroProjeto

Meu primeiro repositório de testes com Python.

## Aplicativos disponíveis

- `buscador_cupom.py`: buscador web de cupons de desconto.
- `teologia_app.py`: painel web para organizar estudos teológicos, notas em grego/hebraico, links externos e temas polêmicos.

## Como usar o aplicativo de estudos teológicos

1. Instale as dependências necessárias:

   ```bash
   pip install flask jinja2 pytest
   ```

2. Execute o servidor local:

   ```bash
   python teologia_app.py
   ```

3. Acesse `http://localhost:5000` no navegador para:
   - Cadastrar novos estudos com título, resumo, anotações, tags e links.
   - Organizar materiais por temas como Teologia Sistemática, Línguas Originais (Grego/Hebraico), assuntos polêmicos e curiosidades.
   - Pesquisar rapidamente por palavras-chave, tags ou títulos.

Os dados ficam salvos no arquivo `dados_teologia.json`, criado automaticamente no primeiro uso.

## Como testar o projeto

Para validar que o fluxo básico de cadastro está funcionando, execute os testes automatizados com o `pytest`:

```bash
pytest
```

> Observação: os testes são ignorados automaticamente caso o Flask não esteja instalado. Certifique-se de instalar as dependências antes de rodar os testes para receber os resultados completos.
