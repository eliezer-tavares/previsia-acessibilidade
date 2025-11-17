# Univesp - Projeto Integrador IV - Engenharia de Computação - 2º Semestre 2025
# Desenvolvido por: Eliezer Tavares de Oliveira (principal), Anderson Viana Ferrari, Efraim Tobal Tavares, Lucas de Goes Vieira Junior
# EN: This file trains a Neural Network with PyTorch on the accessibility dataset. Why? To predict scores from features for the web app. How? Uses all data, log transform, outlier clipping, data loader, 3 hidden layers (wider: 512-256-128 + BatchNorm), Adam optimizer with low LR + scheduler, early stopping, and evaluation.
# PT: Este arquivo treina uma Neural Network com PyTorch no dataset de acessibilidade. Por quê? Para prever scores de features para o app web. Como? Usa todos os dados, log transform, clipping de outliers, data loader, 3 hidden layers (wider: 512-256-128 + BatchNorm), Adam optimizer com low LR + scheduler, early stopping, e avaliação.
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import QuantileTransformer, RobustScaler
from sklearn.metrics import mean_squared_error, r2_score
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import joblib
import os
import logging
import numpy as np
# EN: Setup logging to track training. Why? To monitor performance and errors.
# PT: Configura o logging para rastrear o treinamento. Por quê? Para monitorar desempenho e erros.
logging.basicConfig(filename='erros_trainer.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# EN: Constants for file paths and model. Why? Centralizes configuration.
# PT: Constantes para arquivos e modelo. Por quê? Centraliza a configuração.
ARQUIVO_DATASET = 'data/dataset_acessibilidade.csv'
DIRETORIO_MODELO = 'models'
ARQUIVO_MODELO = os.path.join(DIRETORIO_MODELO, 'modelo_acessibilidade.pt')
ARQUIVO_SCALER = os.path.join(DIRETORIO_MODELO, 'scaler.pkl')
ARQUIVO_FEATURES = os.path.join(DIRETORIO_MODELO, 'feature_names.pkl')
class AccessibilityNet(nn.Module):
    """
    Neural Network for accessibility prediction.
    
    EN: Why? To capture non-linear interactions. How? 3 hidden layers with ReLU, dropout, BatchNorm, output linear for regression.
    PT: Por quê? Para capturar interações non-lineares. Como? 3 hidden layers with ReLU, dropout, BatchNorm, output linear para regressão.
    """
    def __init__(self, input_size):
        super(AccessibilityNet, self).__init__()
        self.fc1 = nn.Linear(input_size, 512)
        self.bn1 = nn.BatchNorm1d(512)  # BatchNorm para estabilizar gradientes
        self.dropout1 = nn.Dropout(0.3)  # Aumentado para 0.3 para evitar overfit
        self.fc2 = nn.Linear(512, 256)
        self.bn2 = nn.BatchNorm1d(256)
        self.dropout2 = nn.Dropout(0.3)
        self.fc3 = nn.Linear(256, 128)
        self.bn3 = nn.BatchNorm1d(128)
        self.dropout3 = nn.Dropout(0.3)
        self.fc4 = nn.Linear(128, 1)
    
    def forward(self, x):
        x = torch.relu(self.bn1(self.fc1(x)))
        x = self.dropout1(x)
        x = torch.relu(self.bn2(self.fc2(x)))
        x = self.dropout2(x)
        x = torch.relu(self.bn3(self.fc3(x)))
        x = self.dropout3(x)
        x = self.fc4(x)
        return x
def treina_modelo():
    """
    Trains the accessibility prediction model.
    
    EN: Why? To learn accessibility patterns from features. How? Loads all data, cleans, log transforms skew, caps outliers, scales, splits, trains NN with Adam + low LR + scheduler + early stopping, evaluates with R2/MSE, and saves model/scaler.
    PT: Por quê? Para aprender padrões de acessibilidade de features. Como? Carrega todos os dados, limpa, log transform skew, cap outliers, escala, divide, treina NN com Adam + low LR + scheduler + early stopping, avalia with R2/MSE and saves model/scaler.
    """
    print("Carregando dataset...")
    try:
        df = pd.read_csv(ARQUIVO_DATASET)
        logging.info(f"Loaded {len(df)} samples.")
        print(f"{len(df)} amostras carregadas.")
       
        if 'layout_json' in df.columns:
            df = df.drop('layout_json', axis=1)
            print("Dropado layout_json for simplicity (not numeric).")
       
        # Limpa dados inválidos (scores -1 or NaN)
        df = df[df['label_score_acessibilidade'] != -1].dropna(subset=['label_score_acessibilidade'])
        print(f"{len(df)} amostras válidas após limpeza.")
       
        # Usa todas as amostras (sem amostra for more data)
        print(f"Usando todas as {len(df)} amostras.")
       
        cols_to_drop = ['url']
        X = df.drop(cols_to_drop, axis=1)
        y = df['label_score_acessibilidade']
       
        X = X.fillna(0)
       
        # Log transform for skew features (ex: falhas_contraste)
        skew_features = ['falhas_contraste', 'imagens_sem_alt', 'videos_sem_captions']
        for feat in skew_features:
            if feat in X.columns:
                X[feat] = np.log1p(X[feat])
        print("Log transform aplicado for features skew.")
       
        # Cap outliers at 95th percentile (ex: falhas_contraste max 95% = ~50, sem 3579)
        for feat in skew_features:
            if feat in X.columns:
                percentile_95 = X[feat].quantile(0.95)
                X[feat] = np.clip(X[feat], 0, percentile_95)
                print(f"Capped {feat} at 95th percentile: {percentile_95:.0f}")
       
        # Print correlações for debug
        numeric_cols = X.select_dtypes(include=[np.number]).columns
        corr = X[numeric_cols].corrwith(y).abs().sort_values(ascending=False)
        print("\nCorrelações com label (abs):")
        print(corr.head(10))
        logging.info(f"Top correlações: {corr.head(10).to_dict()}.")
       
        # Salva scaler e features
        os.makedirs(DIRETORIO_MODELO, exist_ok=True)
        scaler = QuantileTransformer(output_distribution='normal', n_quantiles=min(1000, len(X)))
        X_scaled = scaler.fit_transform(X)
        joblib.dump(scaler, ARQUIVO_SCALER)
        joblib.dump(X.columns.tolist(), ARQUIVO_FEATURES)
       
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
       
        # Normalize Y to 0-1 (divide por 100)
        y_train = y_train / 100
        y_test = y_test / 100
        print("Y normalizado para 0-1 (MSE em escala 0-1 agora).")
       
        # DataLoader for PyTorch
        train_dataset = TensorDataset(torch.tensor(X_train, dtype=torch.float32), torch.tensor(y_train.values, dtype=torch.float32))
        test_dataset = TensorDataset(torch.tensor(X_test, dtype=torch.float32), torch.tensor(y_test.values, dtype=torch.float32))
        train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False)
       
        # Neural Network
        model = AccessibilityNet(X_scaled.shape[1])
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.0005)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)  # Scheduler for finer convergence
        
        # Training with early stopping
        patience = 20  # Increased for more refinement
        best_loss = float('inf')
        counter = 0
        for epoch in range(300):  # Increased for wider layers
            model.train()
            train_loss = 0
            for batch_x, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y.unsqueeze(1))
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
            train_loss /= len(train_loader)
            model.eval()
            val_loss = 0
            with torch.no_grad():
                for batch_x, batch_y in test_loader:
                    outputs = model(batch_x)
                    val_loss += criterion(outputs, batch_y.unsqueeze(1)).item()
            val_loss /= len(test_loader)
            scheduler.step(val_loss)  # Scheduler step for low LR when plateau
            print(f"Epoch {epoch+1}: Train Loss {train_loss:.4f}, Val Loss {val_loss:.4f}, LR {optimizer.param_groups[0]['lr']:.6f}")
            if val_loss < best_loss:
                best_loss = val_loss
                counter = 0
                torch.save(model.state_dict(), ARQUIVO_MODELO)
            else:
                counter += 1
            if counter >= patience:
                print(f"Early stopping at epoch {epoch+1}")
                break
        print("Modelo treinado e salvo.")
        logging.info("Modelo treinado e salvo.")
       
        # Avaliação
        model.load_state_dict(torch.load(ARQUIVO_MODELO))
        model.eval()
        with torch.no_grad():
            y_pred = model(torch.tensor(X_test, dtype=torch.float32)).numpy().flatten()
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        print(f"MSE (0-1): {mse:.4f} (x100 = {mse*100:.2f})")
        print(f"R2: {r2:.4f}")
        logging.info(f"MSE: {mse:.4f}, R2: {r2:.4f}.")
       
        # Salva scaler
        joblib.dump(scaler, ARQUIVO_SCALER)
        print("Modelo e scaler salvados.")
        logging.info(f"Modelo salvo em {ARQUIVO_MODELO}.")
   
    except Exception as e:
        logging.error(f"Erro de treinamento: {str(e)}.")
        print(f"Erro no treinamento: {e}")
if __name__ == '__main__':
    treina_modelo()