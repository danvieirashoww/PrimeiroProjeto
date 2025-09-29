# Buscador de Cupons - Sistema Web com Flask
# Criado para buscar cupons de desconto em sites populares brasileiros

# Importando as bibliotecas necessárias
from flask import Flask, render_template_string, request
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Criando a aplicação Flask
app = Flask(__name__)

# Template HTML para a interface web
# Usando render_template_string para simplificar (sem arquivos separados)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Buscador de Cupons</title>
    <style>
        /* Estilos CSS para deixar a interface bonita */
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .search-box {
            margin: 20px 0;
        }
        input[type="text"] {
            width: 70%;
            padding: 10px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 5px;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .results {
            margin-top: 30px;
        }
        .cupom-item {
            background-color: #f9f9f9;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #4CAF50;
            border-radius: 5px;
        }
        .cupom-site {
            font-weight: bold;
            color: #4CAF50;
        }
        .cupom-link {
            color: #0066cc;
            text-decoration: none;
        }
        .cupom-link:hover {
            text-decoration: underline;
        }
        .no-results {
            color: #666;
            text-align: center;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎫 Buscador de Cupons de Desconto</h1>
        <p style="text-align: center; color: #666;">Digite o nome do produto para encontrar cupons disponíveis</p>
        
        <!-- Formulário de busca -->
        <form method="POST" class="search-box">
            <input type="text" name="produto" placeholder="Ex: notebook, smartphone, fone de ouvido..." required>
            <button type="submit">Buscar Cupons</button>
        </form>
        
        <!-- Resultados da busca -->
        {% if cupons %}
            <div class="results">
                <h2>Cupons Encontrados:</h2>
                {% for cupom in cupons %}
                    <div class="cupom-item">
                        <div class="cupom-site">{{ cupom.site }}</div>
                        <div>{{ cupom.titulo }}</div>
                        <a href="{{ cupom.link }}" target="_blank" class="cupom-link">Ver cupom →</a>
                    </div>
                {% endfor %}
            </div>
        {% elif busca_realizada %}
            <div class="no-results">
                <p>Nenhum cupom encontrado para "{{ produto_buscado }}". Tente outro produto!</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

def buscar_cupons_pelando(produto):
    """
    Função para buscar cupons no site Pelando
    
    Args:
        produto (str): Nome do produto a ser buscado
    
    Returns:
        list: Lista de dicionários com cupons encontrados
    """
    cupons = []
    try:
        # Preparando a URL de busca no Pelando
        url = f"https://www.pelando.com.br/search?q={urllib.parse.quote(produto)}"
        
        # Fazendo a requisição HTTP
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        # Se a requisição foi bem-sucedida
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscando ofertas na página (ajuste os seletores conforme necessário)
            # Nota: Os seletores podem mudar, esta é uma implementação exemplo
            ofertas = soup.find_all('article', limit=5)  # Pegando as primeiras 5 ofertas
            
            for oferta in ofertas:
                titulo_elem = oferta.find(['h2', 'h3', 'a'])
                if titulo_elem:
                    titulo = titulo_elem.get_text(strip=True)
                    link_elem = oferta.find('a', href=True)
                    link = link_elem['href'] if link_elem else '#'
                    
                    # Garantindo que o link seja completo
                    if link.startswith('/'):
                        link = f"https://www.pelando.com.br{link}"
                    
                    cupons.append({
                        'site': 'Pelando',
                        'titulo': titulo,
                        'link': link
                    })
    except Exception as e:
        # Em caso de erro, apenas registra (não quebra a aplicação)
        print(f"Erro ao buscar no Pelando: {e}")
    
    return cupons

def buscar_cupons_cuponomia(produto):
    """
    Função para buscar cupons no site Cuponomia
    
    Args:
        produto (str): Nome do produto a ser buscado
    
    Returns:
        list: Lista de dicionários com cupons encontrados
    """
    cupons = []
    try:
        # Preparando a URL de busca no Cuponomia
        url = f"https://www.cuponomia.com.br/busca?q={urllib.parse.quote(produto)}"
        
        # Fazendo a requisição HTTP
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        # Se a requisição foi bem-sucedida
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscando cupons na página (ajuste os seletores conforme necessário)
            cupons_elem = soup.find_all(['div', 'article'], class_=lambda x: x and 'cupom' in x.lower(), limit=5)
            
            for cupom_elem in cupons_elem:
                titulo_elem = cupom_elem.find(['h2', 'h3', 'h4', 'a'])
                if titulo_elem:
                    titulo = titulo_elem.get_text(strip=True)
                    link_elem = cupom_elem.find('a', href=True)
                    link = link_elem['href'] if link_elem else '#'
                    
                    # Garantindo que o link seja completo
                    if link.startswith('/'):
                        link = f"https://www.cuponomia.com.br{link}"
                    
                    cupons.append({
                        'site': 'Cuponomia',
                        'titulo': titulo,
                        'link': link
                    })
    except Exception as e:
        # Em caso de erro, apenas registra (não quebra a aplicação)
        print(f"Erro ao buscar no Cuponomia: {e}")
    
    return cupons

def buscar_google_cupons(produto):
    """
    Função para buscar cupons via Google (busca genérica)
    Retorna links de busca do Google para sites de cupons
    
    Args:
        produto (str): Nome do produto a ser buscado
    
    Returns:
        list: Lista de dicionários com links de busca
    """
    cupons = []
    
    # Sites populares de cupons no Brasil
    sites_cupons = [
        'pelando.com.br',
        'cuponomia.com.br',
        'promobit.com.br',
        'promocode.com.br'
    ]
    
    # Criando links de busca do Google para cada site
    for site in sites_cupons:
        query = f"{produto} cupom desconto site:{site}"
        google_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        
        cupons.append({
            'site': f'Google - {site}',
            'titulo': f'Buscar cupons de "{produto}" em {site}',
            'link': google_url
        })
    
    return cupons

# Rota principal da aplicação
@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Rota principal que exibe o formulário e processa a busca
    
    Returns:
        str: HTML renderizado com os resultados
    """
    cupons = []
    busca_realizada = False
    produto_buscado = ''
    
    # Se o formulário foi submetido (método POST)
    if request.method == 'POST':
        produto = request.form.get('produto', '')
        produto_buscado = produto
        busca_realizada = True
        
        if produto:
            # Buscando cupons em diferentes sites
            print(f"Buscando cupons para: {produto}")
            
            # Busca no Pelando
            cupons_pelando = buscar_cupons_pelando(produto)
            cupons.extend(cupons_pelando)
            
            # Busca no Cuponomia
            cupons_cuponomia = buscar_cupons_cuponomia(produto)
            cupons.extend(cupons_cuponomia)
            
            # Se não encontrou cupons diretos, adiciona links de busca do Google
            if len(cupons) == 0:
                cupons_google = buscar_google_cupons(produto)
                cupons.extend(cupons_google)
            
            print(f"Total de cupons encontrados: {len(cupons)}")
    
    # Renderizando o template com os resultados
    return render_template_string(
        HTML_TEMPLATE,
        cupons=cupons,
        busca_realizada=busca_realizada,
        produto_buscado=produto_buscado
    )

# Ponto de entrada da aplicação
if __name__ == '__main__':
    """
    Inicia o servidor Flask
    
    Para executar:
    1. Instale as dependências: pip install flask requests beautifulsoup4
    2. Execute: python buscador_cupom.py
    3. Acesse: http://localhost:5000
    """
    print("="*50)
    print("Buscador de Cupons - Iniciando...")
    print("Acesse: http://localhost:5000")
    print("="*50)
    
    # Iniciando o servidor Flask
    # debug=True permite ver erros e recarrega automaticamente ao modificar o código
    app.run(debug=True, host='0.0.0.0', port=5000)
