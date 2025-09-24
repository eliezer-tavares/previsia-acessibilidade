# Univesp - Projeto Integrador IV - Engenharia de Computação - 2º Semestre 2025
# Desenvolvido por: Eliezer Tavares de Oliveira (principal), Anderson Vianna Ferrari, Efrain Tobal Tavares, Lucas de Goes Vieira Junior
# EN: This file orchestrates parallel URL analysis to generate the dataset. Why? To automate large-scale data collection efficiently. How? Uses threads and saves results to CSV.
# PT: Este arquivo orquestra a análise paralela de URLs para gerar o dataset. Por quê? Para automatizar a coleta de dados em larga escala eficientemente. Como? Usa threads e salva resultados em CSV.

import pandas as pd
from collector import analisar_url_completa
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
import json
import logging

# EN: Setup logging to track orchestration errors. Why? Facilitates debugging with NVDA, saving errors to file.
# PT: Configura o logging para rastrear erros de orquestração. Por quê? Facilita depuração com NVDA, salvando erros em arquivo.
logging.basicConfig(filename='erros_orquestrador.log', level=logging.ERROR, format='%(asctime)s - %(message)s')

# EN: Constants for file paths and workers. Why? Centralizes configuration for easy maintenance.
# PT: Constantes para caminhos de arquivos e workers. Por quê? Centraliza a configuração para fácil manutenção.
ARQUIVO_URLS = 'data/tranco_top_1000.csv'
ARQUIVO_DATASET = 'data/dataset_acessibilidade.csv'
MAX_WORKERS = 3

def gera_dataset(batch_size=200):
    """
    Generates accessibility dataset.
    
    :param batch_size: Number of URLs to process (default: 200).
    
    EN: Why? To process URLs in parallel and save features for ML. How? Reads URLs, schedules threads, and serializes layout as JSON.
    PT: Por quê? Para processar URLs em paralelo e salvar features para ML. Como? Lê URLs, agenda threads e serializa layout como JSON.
    """
    print("Iniciando coleta paralela...")
    try:
        urls = pd.read_csv(ARQUIVO_URLS, header=None)[0].tolist()
    except FileNotFoundError as e:
        logging.error(f"EN: File not found: {str(e)}. PT: Arquivo não encontrado: {str(e)}.")
        print(f"Erro: {e}. Rode prepare_urls.py.")
        return
    
    dados = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(analisar_url_completa, url): url for url in urls[:batch_size]}
        for i, future in enumerate(as_completed(futures)):
            url = futures[future]
            print(f"Processando {i+1}/{batch_size}: {url}")
            try:
                resultado = future.result()
                if resultado:
                    if 'layout' in resultado:
                        resultado['layout_json'] = json.dumps(resultado['layout'])
                        del resultado['layout']
                    resultado['url'] = url
                    dados.append(resultado)
            except Exception as e:
                logging.error(f"EN: Error in thread for {url}: {str(e)}. PT: Erro em thread para {url}: {str(e)}.")
                print(f"Erro em thread para {url}: {e}")
            time.sleep(1)
    
    if dados:
        os.makedirs('data', exist_ok=True)
        df = pd.DataFrame(dados)
        cols = ['url', 'label_score_acessibilidade'] + [c for c in df.columns if c not in ['url', 'label_score_acessibilidade']]
        df = df[cols]
        df.to_csv(ARQUIVO_DATASET, index=False)
        print(f"Dataset salvo: {len(df)} linhas.")
    else:
        print("Nenhum dado coletado.")

if __name__ == '__main__':
    gera_dataset()