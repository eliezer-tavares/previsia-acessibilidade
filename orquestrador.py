# Univesp - Projeto Integrador IV - Engenharia de Computação - 2º Semestre 2025
# Desenvolvido por: Eliezer Tavares de Oliveira (principal), Anderson Vianna Ferrari, Efrain Tobal Tavares, Lucas de Goes Vieira Junior
# EN: This file orchestrates parallel URL analysis to generate the dataset. Why? To automate large-scale data collection efficiently. How? Uses threads and saves results to CSV.
# PT: Este arquivo orquestra a análise paralela de URLs para gerar o dataset. Por quê? Para automatizar a coleta de dados em larga escala eficientemente. Como? Usa threads e salva resultados em CSV.
import pandas as pd
import glob
from collector import analisar_url_completa
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
import json
import logging

# EN: Setup logging to track orchestration errors. Why? Facilitates debugging with NVDA, saving errors to file.
# PT: Configura o logging para rastrear erros de orquestração. Por quê? Facilita depuração com NVDA, salvando erros em arquivo.
logging.basicConfig(
    filename="erros_orquestrador.log",
    level=logging.ERROR,
    format="%(asctime)s - %(message)s",
)
# EN: Constants for file paths and workers. Why? Centralizes configuration for easy maintenance.
# PT: Constantes para caminhos de arquivos e workers. Por quê? Centraliza a configuração para fácil manutenção.
ARQUIVO_URLS = "data/tranco_top_10000.csv"  # CSV full com 5874 URLs
ARQUIVO_DATASET = "data/dataset_acessibilidade.csv"
MAX_WORKERS = 3  # Mantido em 3


def gera_dataset(batch_size=5874):  # Processa todas, mas filtra processadas
    """
    Generates accessibility dataset, resuming from last partial if exists.

    :param batch_size: Number of URLs to process (default: 5874).

    EN: Why? To process URLs in parallel and save features for ML. How? Reads URLs, schedules threads, and serializes layout as JSON.
    PT: Por quê? Para processar URLs em paralelo e salvar features para ML. Como? Lê URLs, agenda threads e serializa layout as JSON.
    """
    print("Iniciando coleta paralela (com resumo de partial se existir)...")
    try:
        all_urls = pd.read_csv(ARQUIVO_URLS, header=None)[0].tolist()
        all_urls = [url.strip() for url in all_urls]  # Limpeza
        print(f"Carregadas {len(all_urls)} URLs do CSV full para processamento.")
    except FileNotFoundError as e:
        logging.error(
            f"EN: File not found: {str(e)}. PT: Arquivo não encontrado: {str(e)}."
        )
        print(f"Erro: {e}. Rode prepare_urls.py.")
        return

    # Carrega o último partial (maior número)
    partial_files = glob.glob("data/dataset_acessibilidade_partial_*.csv")
    if partial_files:
        partial_files.sort(key=lambda x: int(x.split("_")[-1].split(".")[0]))
        last_partial = partial_files[-1]
        dados_existentes = pd.read_csv(last_partial)
        processed_urls = set(dados_existentes["url"].tolist())
        urls_to_process = [url for url in all_urls if url not in processed_urls][
            :batch_size
        ]
        print(
            f"Resumindo de {last_partial}: {len(dados_existentes)} já processadas. Faltam {len(urls_to_process)} novas."
        )
        dados = dados_existentes.to_dict("records")  # Carrega existentes como base
        processed_count = len(dados)
    else:
        urls_to_process = all_urls[:batch_size]
        dados = []
        processed_count = 0
        print("Sem partials encontrados - iniciando do zero.")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(analisar_url_completa, url): url for url in urls_to_process
        }
        for i, future in enumerate(as_completed(futures)):
            url = futures[future]
            print(
                f"Processando {processed_count + i + 1}/{len(all_urls)} (nova: {i+1}/{len(urls_to_process)}): {url}"
            )
            try:
                resultado = future.result()
                if resultado:
                    if "layout" in resultado:
                        resultado["layout_json"] = json.dumps(resultado["layout"])
                        del resultado["layout"]
                    resultado["url"] = url
                    dados.append(resultado)
                    processed_count += 1
                    print(
                        f"Sucesso! Total sucessos: {processed_count}"
                    )  # <-- Adicionado para monitorar sucessos
                    # Save parcial a cada 100 novas processadas com sucesso
                    if processed_count % 100 == 0:
                        partial_df = pd.DataFrame(dados)
                        cols = ["url", "label_score_acessibilidade"] + [
                            c
                            for c in partial_df.columns
                            if c not in ["url", "label_score_acessibilidade"]
                        ]
                        partial_df = partial_df[cols]
                        partial_filename = (
                            f"data/dataset_acessibilidade_partial_{processed_count}.csv"
                        )
                        partial_df.to_csv(partial_filename, index=False)
                        print(
                            f"Checkpoint salvo: {processed_count} processadas no total em {partial_filename}"
                        )
                else:
                    print(f"Falha na análise para {url} - pulando.")
            except Exception as e:
                logging.error(
                    f"EN: Error in thread for {url}: {str(e)}. PT: Erro em thread para {url}: {str(e)}."
                )
                print(f"Erro em thread para {url}: {e}")
            time.sleep(4)  # Mantido em 4s

    if dados:
        os.makedirs("data", exist_ok=True)
        df = pd.DataFrame(dados)
        cols = ["url", "label_score_acessibilidade"] + [
            c for c in df.columns if c not in ["url", "label_score_acessibilidade"]
        ]
        df = df[cols]
        df.to_csv(ARQUIVO_DATASET, index=False)
        print(f"Dataset final salvo: {len(df)} linhas em {ARQUIVO_DATASET}.")
    else:
        print("Nenhum dado coletado.")


if __name__ == "__main__":
    gera_dataset()
