# prepare_urls.py
# -*- coding: utf-8 -*-
"""
Prepara lista de URLs da Tranco List.
Por quê? Transforma domínios em URLs completas para análise, limitando a 1000 para escala inicial. Isso garante dados reais para treinamento.
Como? Lê CSV com pandas (biblioteca para dados tabulares como Excel), adiciona 'https://' usando apply (aplica função a cada linha), salva novo arquivo sem índice extra.
Conceitos básicos: CSV é um arquivo de texto com valores separados por vírgulas; pandas lê isso como DataFrame (tabela em memória).
"""

# Importações: pd é apelido para pandas (biblioteca para dados tabulares).
import pandas as pd
import os  # Para criar pastas (os: operating system, interage com arquivos/sistema).

# Cria pasta 'data' se não existir (exist_ok=True evita erro se já existir). Por quê? Organiza arquivos; evita erros de pasta inexistente.
os.makedirs('data', exist_ok=True)

# Lê o arquivo CSV completo (header=None: sem cabeçalho, names define colunas manualmente).
# Por quê? Tranco List tem colunas rank e domain sem cabeçalho; definimos nomes para clareza.
# Como? pd.read_csv carrega o arquivo em df (DataFrame: estrutura como tabela).
df = pd.read_csv('data/tranco_full.csv', header=None, names=['rank', 'domain'])

# Seleciona top 1000 domínios e adiciona 'https://' (apply: aplica função a cada linha da série 'domain').
# Por quê? URLs precisam de protocolo (https://) para requests.get funcionar; head(1000) limita para top sites.
# Lambda: função curta anônima (x é cada domain); f-string formata string com variáveis.
urls = df['domain'].head(1000).apply(lambda x: f'https://{x}')

# Salva em novo CSV (index=False: sem coluna de números extras, header=False: sem cabeçalho).
# Por quê? Cria arquivo limpo só com URLs, uma por linha.
urls.to_csv('data/tranco_top_1000.csv', index=False, header=False)

# Imprime resultado (print: exibe no terminal, acessível via NVDA). Por quê? Confirmação imediata de sucesso.
print(f"Gerado tranco_top_1000.csv com {len(urls)} URLs.")
