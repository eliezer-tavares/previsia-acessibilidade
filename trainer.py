# Univesp - Projeto Integrador IV - Engenharia de Computação - 2º Semestre 2025
# Desenvolvido por: Eliezer Tavares de Oliveira (principal), Anderson Vianna Ferrari, Efrain Tobal Tavares, Lucas de Goes Vieira Junior
# EN: This file trains a RandomForest model to predict accessibility scores. Why? To learn from dataset for real-time predictions. How? Loads CSV, splits data, trains, and saves model.
# PT: Este arquivo treina um modelo RandomForest para prever escores de acessibilidade. Por quê? Para aprender com o dataset para previsões em tempo real. Como? Carrega CSV, divide dados, treina e salva o modelo.

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib
import os
import json
import logging

# EN: Setup logging to track training. Why? To monitor performance and errors.
# PT: Configura o logging para rastrear o treinamento. Por quê? Para monitorar desempenho e erros.
logging.basicConfig(filename='erros_trainer.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# EN: Constants for file paths. Why? Centralizes configuration.
# PT: Constantes para caminhos de arquivos. Por quê? Centraliza a configuração.
ARQUIVO_DATASET = 'data/dataset_acessibilidade.csv'
DIRETORIO_MODELO = 'models'
ARQUIVO_MODELO = os.path.join(DIRETORIO_MODELO, 'modelo_acessibilidade.pkl')
ARQUIVO_FEATURES = os.path.join(DIRETORIO_MODELO, 'feature_names.pkl')

def treina_modelo():
    """
    Trains the accessibility prediction model.
    
    EN: Why? To avoid overfitting and ensure generalization. How? Drops non-numeric columns, fills NaNs, trains RandomForest, and evaluates MSE.
    PT: Por quê? Para evitar overfitting e garantir generalização. Como? Remove colunas não numéricas, preenche NaNs, treina RandomForest e avalia MSE.
    """
    print("Carregando dataset...")
    try:
        df = pd.read_csv(ARQUIVO_DATASET)
        logging.info(f"EN: Loaded {len(df)} samples. PT: Carregadas {len(df)} amostras.")
        print(f"{len(df)} amostras carregadas.")
        
        if 'layout_json' in df.columns:
            df['layout'] = df['layout_json'].apply(lambda x: json.loads(x) if pd.notna(x) else {})
            df = df.drop('layout_json', axis=1)
        
        cols_to_drop = ['url', 'label_score_acessibilidade']
        if 'layout' in df.columns:
            cols_to_drop.append('layout')
        X = df.drop(cols_to_drop, axis=1)
        y = df['label_score_acessibilidade']
        
        X = X.fillna(0)
        
        os.makedirs(DIRETORIO_MODELO, exist_ok=True)
        joblib.dump(X.columns.tolist(), ARQUIVO_FEATURES)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        modelo = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        modelo.fit(X_train, y_train)
        
        previsoes = modelo.predict(X_test)
        mse = mean_squared_error(y_test, previsoes)
        logging.info(f"EN: MSE: {mse:.2f}. PT: MSE: {mse:.2f}.")
        print(f"MSE: {mse:.2f}")
        
        joblib.dump(modelo, ARQUIVO_MODELO)
        logging.info(f"EN: Model saved to {ARQUIVO_MODELO}. PT: Modelo salvo em {ARQUIVO_MODELO}.")
        print("Modelo salvo.")
    
    except Exception as e:
        logging.error(f"EN: Training error: {str(e)}. PT: Erro de treinamento: {str(e)}.")
        print(f"Erro no treinamento: {e}")

if __name__ == '__main__':
    treina_modelo()