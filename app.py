# Univesp - Projeto Integrador IV - Engenharia de Computação - 2º Semestre 2025
# Desenvolvido por: Eliezer Tavares de Oliveira (principal), Anderson Viana Ferrari, Efrain Tobal Tavares, Lucas de Goes Vieira Junior
# EN: This file runs the Flask web app for accessibility analysis. Why? To provide an accessible interface for URL analysis and predictive guides. How? Uses Flask routes and SpeechSynthesis.
# PT: Este arquivo executa a aplicação web Flask para análise de acessibilidade. Por quê? Para fornecer uma interface acessível para análise de URLs e guias preditivos. Como? Usa rotas Flask e SpeechSynthesis.
from flask import Flask, render_template, request, session, g, redirect, url_for
from flask_babel import Babel, gettext, ngettext, _, lazy_gettext
from datetime import timedelta  # FIX: Import pra permanent session
import joblib
import pandas as pd
from collector import analisar_url_rapida, analisar_url_completa
import logging
from tenacity import RetryError
import torch
import torch.nn as nn
import numpy as np
import os

# EN: Setup logging for web app. Why? To track requests and errors for debugging.
# PT: Configura o logging para a aplicação web. Por quê? Para rastrear requisições e erros para depuração.
logging.basicConfig(
    filename="erros_app.log", level=logging.ERROR, format="%(asctime)s - %(message)s"
)
app = Flask(__name__)
app.config["SECRET_KEY"] = (
    "dev"  # TODO: Em produção, use um valor secreto gerado por os.urandom(24)
)
app.config["BABEL_DEFAULT_LOCALE"] = "pt_BR"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"
app.permanent_session_lifetime = timedelta(
    days=31
)  # FIX: Sessions permanentes pra idioma persistir (31 dias)


# Defina a função get_locale ANTES
def get_locale():
    if "language" in session:
        return session["language"]
    return request.accept_languages.best_match(["pt_BR", "en_US"]) or "pt_BR"


# Inicialize o Babel passando a app e o locale_selector diretamente (sem decorador!)
babel = Babel(app, locale_selector=get_locale)


# FIX: Context processor pra injetar locale nos templates (obrigatório no Babel 4.0)
@app.context_processor
def inject_locale():
    return dict(locale=get_locale())


# ALTERAÇÃO: Definir a classe AccessibilityNet ANTES do try, para evitar "name not defined", e com BatchNorm para matching the trainer.
class AccessibilityNet(nn.Module):
    def __init__(self, input_size):
        super(AccessibilityNet, self).__init__()
        self.fc1 = nn.Linear(input_size, 512)  # Wider layers from option 5
        self.bn1 = nn.BatchNorm1d(512)  # BatchNorm for stable gradients
        self.dropout1 = nn.Dropout(0.3)  # Increased to 0.3 for less overfit
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


# ALTERAÇÃO: Lógica de carregamento do modelo e dos artefatos
DIRETORIO_MODELO = "models"
modelo = None
scaler = None
feature_names = None
try:
    # Carrega os nomes das features e o scaler, que foram salvos com joblib
    path_features = os.path.join(DIRETORIO_MODELO, "feature_names.pkl")
    path_scaler = os.path.join(DIRETORIO_MODELO, "scaler.pkl")
    path_modelo = os.path.join(
        DIRETORIO_MODELO, "modelo_acessibilidade.pt"
    )  # Usar o arquivo .pt
    feature_names = joblib.load(path_features)
    scaler = joblib.load(path_scaler)

    # Instancia o modelo com o número correto de features de entrada
    input_size = len(feature_names)
    modelo = AccessibilityNet(input_size)

    # Carrega os pesos (o estado) do modelo treinado
    modelo.load_state_dict(torch.load(path_modelo))

    # Coloca o modelo em modo de avaliação (importante para camadas como Dropout)
    modelo.eval()

    print("Modelo PyTorch, scaler e features carregados com sucesso.")
except FileNotFoundError as e:
    logging.error(
        f"EN: Model artifact not found: {e}. PT: Artefato do modelo não encontrado: {e}."
    )
    print(f"Erro: Arquivo do modelo não encontrado. Verifique o caminho: {e}")
except Exception as e:
    logging.error(f"EN: Error loading model: {e}. PT: Erro ao carregar o modelo: {e}.")
    print(f"Erro ao carregar o modelo: {e}")


def gerar_guia_preditivo(features, score, url):
    """
    Generates predictive navigation guide in natural language.
    """
    guia = _(
        "Análise da página {0} de {1}. Pontuação prevista: {2}. Guia rápido e alertas: "
    ).format(url.split("//")[-1].split("/")[0], url, score)
    layout = features.get("layout", {})

    if layout.get("header_presente"):
        guia += _("A página começa com um cabeçalho, ")
    if layout.get("nav_itens", 0) > 0:
        guia += ngettext(
            "seguido por um menu de navegação com {0} item.",
            "seguido por um menu de navegação com {0} itens.",
            layout["nav_itens"],
        ).format(layout["nav_itens"])
        if features.get("pct_links_genericos", 0) > 20:
            guia += _(
                "Cuidado: muitos links genéricos no menu podem confundir a navegação. "
            )
    if layout.get("carousel_imagens", 0) > 0:
        guia += ngettext(
            "Em seguida, há uma galeria ou carrossel com {0} imagem.",
            "Em seguida, há uma galeria ou carrossel com {0} imagens.",
            layout["carousel_imagens"],
        ).format(layout["carousel_imagens"])
        if layout.get("carousel_sem_alt", 0) > 0:
            guia += ngettext(
                "Alerta: {0} imagem sem descrição; seu leitor de tela pode ignorá-la.",
                "Alerta: {0} imagens sem descrição; seu leitor de tela pode ignorá-las.",
                layout["carousel_sem_alt"],
            ).format(layout["carousel_sem_alt"])
    if layout.get("main_presente"):
        guia += _("A área de conteúdo principal segue, ")
        if features.get("erros_hierarquia", 0) > 0:
            guia += ngettext(
                "mas com {0} erro de hierarquia em títulos, o que pode bagunçar a navegação por seções.",
                "mas com {0} erros de hierarquia em títulos, o que pode bagunçar a navegação por seções.",
                features["erros_hierarquia"],
            ).format(features["erros_hierarquia"])
    if layout.get("form_campos", 0) > 0:
        guia += ngettext(
            "há um formulário com {0} campo no meio ou final da página.",
            "há um formulário com {0} campos no meio ou final da página.",
            layout["form_campos"],
        ).format(layout["form_campos"])
        if features.get("inputs_sem_label", 0) > 0:
            guia += ngettext(
                "Alerta: {0} campo sem rótulo adequado; formulários podem ser difíceis.",
                "Alerta: {0} campos sem rótulos adequados; formulários podem ser difíceis.",
                features["inputs_sem_label"],
            ).format(features["inputs_sem_label"])
        else:
            guia += _("Todos os campos parecem rotulados corretamente. ")
    if layout.get("footer_presente"):
        guia += _("A página termina com um rodapé. ")

    if features.get("imagens_sem_alt", 0) > 0:
        guia += ngettext(
            "Alerta: {0} imagem sem texto alternativo pode dificultar a navegação para leitores de tela.",
            "Alerta: {0} imagens sem texto alternativo podem dificultar a navegação para leitores de tela.",
            features["imagens_sem_alt"],
        ).format(features["imagens_sem_alt"])
    if features.get("videos_sem_captions", 0) > 0:
        guia += ngettext(
            "Alerta: {0} vídeo sem legenda; áudio pode ser inacessível.",
            "Alerta: {0} vídeos sem legendas; áudio pode ser inacessível.",
            features["videos_sem_captions"],
        ).format(features["videos_sem_captions"])
    if features.get("falhas_contraste", 0) > 0:
        guia += ngettext(
            "Alerta: {0} problema de contraste detectado, afetando legibilidade para baixa visão.",
            "Alerta: {0} problemas de contraste detectados, afetando legibilidade para baixa visão.",
            features["falhas_contraste"],
        ).format(features["falhas_contraste"])
    if features.get("aria_presente", 0) == 0:
        guia += _(
            "Alerta: Falta de ARIA em elementos dinâmicos; interações podem não ser anunciadas. "
        )

    if score > 80:
        guia += _("A navegação deve ser direta e acessível.")
    elif score > 50:
        guia += _("A navegação é razoável, mas evite seções problemáticas.")
    else:
        guia += _(
            "Sugiro usar ferramentas alternativas como busca do site para evitar frustrações."
        )

    return guia


# Rota home
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# Rota para alternar idioma
@app.route("/set_language", methods=["POST"])
def set_language():
    lang = request.form.get("language", request.args.get("lang", "pt_BR"))
    if lang in ["pt_BR", "en_US"]:
        session["language"] = lang
    return redirect(url_for("home"))


@app.route("/predict", methods=["POST"])
def predict():
    if not all([modelo, scaler, feature_names]):
        logging.error(
            "EN: Model or artifacts not available. PT: Modelo ou artefatos não disponíveis."
        )
        return render_template(
            "resultado.html",
            error=_(
                "Modelo ou seus componentes não estão disponíveis. Verifique a configuração do servidor."
            ),
            url="",
            features={},
        )

    url = request.form["url"]
    if not url.startswith("http"):
        url = f"https://{url}"
    tipo_analise = request.form.get("tipo_analise", "rapida")

    # DEBUG: Print locale durante previsão
    print(f"Locale durante previsão: {get_locale()}")

    aviso = None
    try:
        if tipo_analise == "completa":
            features = analisar_url_completa(url)
            if features is None:
                print(f"Fallback para análise rápida para {url}")
                features = analisar_url_rapida(url)
                aviso = _(
                    "A análise completa falhou; usamos a análise rápida como fallback para {0}."
                ).format(url)
        else:
            features = analisar_url_rapida(url)
        if not features:
            logging.error(
                f"EN: Failed to analyze URL {url}. PT: Falha ao analisar URL {url}."
            )
            return render_template(
                "resultado.html",
                error=_("Falha ao extrair características da URL: {0}").format(url),
                url=url,
                features={},
            )

        # Lógica de Previsão with PyTorch
        # 1. Garantir que todas as features esperadas pelo modelo estejam presentes.
        features_df = pd.DataFrame([features])
        features_df = features_df.reindex(columns=feature_names, fill_value=0)
        # 2. Aplicar as mesmas transformações do treinamento (log e clipping)
        skew_features = ["falhas_contraste", "imagens_sem_alt", "videos_sem_captions"]
        for feat in skew_features:
            if feat in features_df.columns:
                features_df[feat] = np.log1p(features_df[feat])
                # In trainer, we clipped. Ideally, save the clip values.
                # For simplicity, assume input values won't be extreme outliers.

        # 3. Escalonar os dados with o scaler carregado
        X_scaled = scaler.transform(features_df)

        # 4. Converter para um Tensor PyTorch
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32)

        # 5. Fazer a previsão (dentro de um bloco 'no_grad' for efficiency)
        with torch.no_grad():
            prediction_normalized = modelo(X_tensor)

        # 6. Processar o resultado
        # The trainer normalized 'y' to 0-1 (dividing by 100). Need to reverse.
        score_pred = prediction_normalized.numpy().flatten()[0] * 100
        score = round(max(0, min(100, score_pred)))  # Ensure score between 0 and 100

        print(f"Score: {score}, Features: {features}, URL: {url}")

        guia = gerar_guia_preditivo(features, score, url)
        print(f"Guia: {guia}")

        logging.info(f"Analysis completed for {url}: {score}.")
        return render_template(
            "resultado.html",
            url=url,
            score=score,
            guia=guia,
            features=features,
            aviso=aviso,
        )

    except Exception as e:
        logging.error(f"Error in prediction for {url}: {str(e)}.")
        print(f"Erro na previsão: {str(e)}")
        import traceback

        logging.error(traceback.format_exc())
        return render_template(
            "resultado.html",
            error=_("Ocorreu um erro inesperado during the analysis: {0}").format(e),
            url=url,
            features={},
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)  # debug=False pra prod
