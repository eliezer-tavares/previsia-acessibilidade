# trainer.py
# -*- coding: utf-8 -*-
"""
Treina modelo de ML.
Por quê? Aprende de dataset para prever scores sem reanalisar sites. Isso é o "cérebro" da previsão.
Como? Carrega CSV, divide dados com train_test_split, fit() treina, predict avalia MSE, salva com joblib. Desserializa layout_json se presente para consistência.
Conceitos básicos: ML usa X (features) para prever y (label); overfitting é memorizar treino sem generalizar, evitado com split.
"""

# Importações.
import pandas as pd  # Para ler CSV.
from sklearn.model_selection import train_test_split  # Divide dados (sklearn: biblioteca ML). Por quê? Validação.
from sklearn.ensemble import RandomForestRegressor  # Modelo: Floresta de árvores para regressão (robusto a outliers).
from sklearn.metrics import mean_squared_error  # Calcula erro (métrica de precisão: média de quadrados de diferenças).
import joblib  # Para dump (salvar objeto Python como arquivo). Por quê? Reuse sem re-treino.
import os  # Para makedirs.
import json  # Para loads (desserializar JSON para dict).

# Configurações.
ARQUIVO_DATASET = 'data/dataset_acessibilidade.csv'
DIRETORIO_MODELO = 'models'
ARQUIVO_MODELO = os.path.join(DIRETORIO_MODELO, 'modelo_acessibilidade.pkl')  # Join: combina caminhos cross-plataforma.
ARQUIVO_FEATURES = os.path.join(DIRETORIO_MODELO, 'feature_names.pkl')

def treina_modelo():
    """
    Função principal de treinamento.
    Por quê? Separa treino/teste para validar (evita overfitting: modelo memoriza em vez de aprender).
    Como? Drop remove colunas não numéricas, fillna limpa NaNs, fit treina, predict testa. Ignora layout para ML (usado em guia).
    """
    print("Carregando dataset...")
    df = pd.read_csv(ARQUIVO_DATASET)  # Lê CSV para DataFrame.
    print(f"{len(df)} amostras carregadas.")  # Len: número de linhas.

    # Desserializa layout_json se existe (para consistência, mas não usado no ML).
    # Por quê? Layout é para guia; json.loads converte string para dict.
    if 'layout_json' in df.columns:
        df['layout'] = df['layout_json'].apply(lambda x: json.loads(x) if pd.notna(x) else {})  # Apply: aplica a cada célula; pd.notna verifica não nulo.
        df = df.drop('layout_json', axis=1)  # Remove coluna JSON após conversão.

    # Separa X (features) e y (label).
    # Por quê? ML precisa de inputs (X) e outputs (y) para aprender.
    # Como? Drop: remove colunas (axis=1: colunas). Exclui 'layout' se presente (não numérico para modelo).
    cols_to_drop = ['url', 'label_score_acessibilidade']
    if 'layout' in df.columns:
        cols_to_drop.append('layout')
    X = df.drop(cols_to_drop, axis=1)
    y = df['label_score_acessibilidade']

    # Limpa dados faltantes (fillna: preenche com 0).
    # Por quê? ML não lida com NaN (not a number); 0 é neutro para contagens.
    X = X.fillna(0)

    # Salva nomes das features (para previsão usar mesma ordem).
    # Por quê? Predição precisa de colunas idênticas.
    os.makedirs(DIRETORIO_MODELO, exist_ok=True)
    joblib.dump(X.columns.tolist(), ARQUIVO_FEATURES)  # Columns.tolist: lista de nomes.

    # Divide: test_size=0.2 (20% teste), random_state=42 (reprodutível, mesma divisão sempre).
    # Por quê? Teste verifica se modelo generaliza (não só memoriza treino).
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Instancia e treina modelo.
    # Por quê? RandomForest: robusto, média de múltiplas árvores reduz erros; n_estimators=100 balança precisão/tempo.
    # Como? n_jobs=-1: usa todos CPUs para paralelismo.
    modelo = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    modelo.fit(X_train, y_train)  # Fit: ajusta parâmetros com dados de treino.

    # Avalia: predict faz previsões no teste, MSE calcula diferença quadrática média.
    # Por quê? MSE baixo indica boas previsões; .2f formata para 2 decimais.
    previsoes = modelo.predict(X_test)
    mse = mean_squared_error(y_test, previsoes)
    print(f"MSE: {mse:.2f}")

    # Salva modelo.
    joblib.dump(modelo, ARQUIVO_MODELO)
    print("Modelo salvo.")

if __name__ == '__main__':
    treina_modelo()
