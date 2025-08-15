# PrevisIA: Previsor e Guia de Acessibilidade Web 👁️‍🗨️🤖

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Feito com ❤️](https://img.shields.io/badge/Feito%20com-%E2%9D%A4%EF%B8%8F-red.svg)](https://github.com/eliezer-tavares/previsia-acessibilidade)

## Sobre o Projeto

PrevisIA é uma ferramenta inovadora desenvolvida para a disciplina Projeto Integrador IV da graduação em Engenharia de Computação da Universidade Virtual do Estado de São Paulo (Univesp). Nosso objetivo é democratizar a avaliação de acessibilidade web, fornecendo uma solução que não apenas prevê um *score* de acessibilidade, mas também oferece um Guia de Navegação Preditivo em linguagem natural, otimizado para usuários com deficiência visual.

Este projeto funciona como um motor inteligente que, por meio de técnicas de *Machine Learning*, identifica padrões de acessibilidade em *websites*. A interface web amigável permite que qualquer pessoa insira uma URL e receba *insights* valiosos sobre a experiência de navegação por voz em uma página, ajudando a mitigar frustrações antes da visita.

## Funcionalidades Principais

- **Previsão de Acessibilidade**: Gera um *score* de 0 a 100 que indica o quão acessível uma página web é, baseado em um modelo de *Machine Learning* treinado com dados reais.
- **Guia de Navegação Preditivo**: Compila uma narrativa detalhada em linguagem natural, simulando um "guia de viagem" para usuários de leitores de tela. Descreve a estrutura da página (cabeçalho, navegação, conteúdo, formulários) e aponta potenciais pontos de atrito (links genéricos, imagens sem descrição, erros de hierarquia).
- **Análise Dupla**:
  - **Rápida**: Estimativa instantânea baseada em HTML estático.
  - **Completa**: Mais precisa e detalhada, utilizando Selenium para renderizar JavaScript e Axe-core para auditoria de acessibilidade, ideal para treinamento do modelo e análises aprofundadas.
- **Feedback por Áudio**: Integra a API `SpeechSynthesis` do navegador, permitindo que o usuário ouça o Guia de Navegação Preditivo.
- **Coleta de Dados em Escala**: Um módulo orquestrador permite a coleta paralela de *features* de milhares de URLs da Tranco List, otimizando o tempo de geração do *dataset*.
- **Engenharia de Features**: Extração robusta de características relevantes do HTML e do comportamento dinâmico da página, com foco nas "dores" de acessibilidade de usuários cegos.
- **Modelo de Machine Learning**: Treinamento de um `RandomForestRegressor` para aprender a correlação entre *features* extraídas e o *score* de acessibilidade, servindo como o "cérebro" da previsão.
- **Interface Web (Flask)**: Uma aplicação web leve e acessível para interação intuitiva com a ferramenta.
- **Testes Automatizados**: Cobertura abrangente de testes unitários, de integração e de acessibilidade (com Axe-core) para garantir a qualidade e robustez do código.

## Como Funciona (Arquitetura)

O projeto PrevisIA é estruturado em fases interdependentes, garantindo a automação e a qualidade da previsão de acessibilidade:

1. **Fase 1: Preparação de Dados** (`prepare_urls.py`)
   - Baixa a Tranco List (top 1M *sites*).
   - Filtra e formata as 1000 primeiras URLs para uso no projeto.
2. **Fase 2: Coleta de Dados e Engenharia de Features** (`collector.py`)
   - Extrai *features* estáticas (HTML) e dinâmicas (via Selenium/Axe-core) de uma URL.
   - Gera um *label* (pontuação de acessibilidade) baseado nas violações do Axe-core.
   - Extrai *features* de layout semântico para o Guia Preditivo.
3. **Fase 3: Orquestração e Geração do Dataset** (`orquestrador.py`)
   - Lê a lista de URLs preparadas.
   - Chama o `collector` em paralelo para analisar múltiplas URLs simultaneamente, construindo o *dataset* de treinamento (`dataset_acessibilidade.csv`).
   - Serializa dados de layout aninhados para JSON para compatibilidade com CSV.
4. **Fase 4: Treinamento do Modelo** (`trainer.py`)
   - Carrega o `dataset_acessibilidade.csv`.
   - Pré-processa os dados (tratamento de valores faltantes).
   - Divide o *dataset* em conjuntos de treino e teste.
   - Treina um modelo `RandomForestRegressor`.
   - Avalia o desempenho do modelo (MSE).
   - Salva o modelo treinado (`modelo_acessibilidade.pkl`) e os nomes das *features* (`feature_names.pkl`).
5. **Fase 5: Interface Web e *Deploy*** (`app.py`, `templates/`)
   - Cria uma aplicação web usando Flask.
   - Carrega o modelo treinado para previsões em tempo real.
   - Oferece opções de "Análise Rápida" (estática) ou "Análise Completa" (dinâmica em *background*).
   - Implementa a lógica para gerar o Guia de Navegação Preditivo com base nas *features*.
   - Integra `SpeechSynthesis` para *feedback* de áudio.
   - Renderiza *templates* HTML para a interface do usuário.
6. **Fase 6: Testes e Validação** (`tests/`)
   - Implementa testes unitários, de integração e de acessibilidade (com `pytest` e `axe-selenium-python`) para garantir a qualidade e a cobertura do código.

## Primeiros Passos

Siga estas instruções para configurar e executar o projeto localmente:

### Pré-requisitos

- Python 3.8 ou superior
- `pip` (gerenciador de pacotes do Python)
- Google Chrome ou Chromium instalado (necessário para o Selenium e `webdriver-manager`)

### Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/eliezer-tavares/previsia-acessibilidade.git
   cd previsia-acessibilidade
   ```

2. Crie e ative um ambiente virtual (recomendado):

   ```bash
   python -m venv venv
   # No Windows:
   .\venv\Scripts\activate
   # No macOS/Linux:
   source venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

### Configuração e Geração de Artefatos

Siga os passos na ordem para preparar os dados e treinar o modelo:

1. **Baixe e prepare a Tranco List**:
   - Crie a pasta `data/` na raiz do projeto, se não existir.
   - Baixe o arquivo `top-1m.csv.zip` da [Tranco List](https://tranco-list.eu/).
   - Descompacte o `top-1m.csv` para `data/tranco_full.csv`.
   - Execute o script para gerar a lista de 1000 URLs:

     ```bash
     python prepare_urls.py
     ```

     Isso criará `data/tranco_top_1000.csv`.

2. **Gere o Dataset de Acessibilidade**:
   - Este passo pode levar um tempo considerável (dependendo do `MAX_WORKERS` e da conectividade).
   - Execute o orquestrador (ajuste `batch_size` em `orquestrador.py` se quiser testar com menos URLs, por exemplo, `gera_dataset(batch_size=20)`):

     ```bash
     python orquestrador.py
     ```

     Isso criará `data/dataset_acessibilidade.csv`.

3. **Treine o Modelo de Machine Learning**:
   - Execute o script de treinamento:

     ```bash
     python trainer.py
     ```

     Isso criará a pasta `models/` (se não existir) e salvará `models/modelo_acessibilidade.pkl` e `models/feature_names.pkl`.

### Executando a Aplicação Web

Após completar os passos de configuração e geração de artefatos, inicie a aplicação Flask:

```bash
python app.py
```

Acesse a aplicação no navegador: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Estrutura do Projeto

```
.
├── app.py                      # Aplicação web Flask e lógica do Guia Preditivo
├── collector.py                # Funções para extração de features e geração de label com Axe-core
├── orquestrador.py             # Orquestra a coleta paralela de dados para o dataset
├── prepare_urls.py             # Prepara a lista de URLs da Tranco List
├── trainer.py                  # Treina e salva o modelo de Machine Learning
├── requirements.txt            # Lista de dependências do projeto
├── README.md                   # Este arquivo
├── data/
│   ├── tranco_full.csv         # (Baixado) Lista completa da Tranco List
│   ├── tranco_top_1000.csv     # (Gerado) Top 1000 URLs formatadas
│   └── dataset_acessibilidade.csv # (Gerado) Dataset final para treinamento do ML
├── models/
│   ├── modelo_acessibilidade.pkl # (Gerado) Modelo de ML treinado
│   └── feature_names.pkl        # (Gerado) Nomes das features usadas pelo modelo
├── templates/
│   ├── index.html              # Página inicial da web app (formulário de URL)
│   └── resultado.html          # Página de resultados da web app (score, guia, áudio)
└── tests/
    ├── test_collector.py       # Testes unitários para collector.py
    ├── test_orquestrador.py    # Testes de integração para orquestrador.py
    ├── test_trainer.py         # Testes unitários para trainer.py
    ├── test_app.py             # Testes de integração para app.py
    └── test_acessibilidade.py  # Testes de acessibilidade automatizados com Axe-core
```

## Testes Automatizados

O projeto possui uma suíte de testes automatizados abrangente para garantir a qualidade do código e a robustez das funcionalidades.

Para executar todos os testes e gerar um relatório de cobertura de código em HTML:

```bash
pytest --cov --cov-report=html
```

O relatório de cobertura HTML estará disponível em `htmlcov/index.html`.

## Contribuição

Contribuições são bem-vindas! Se você tiver sugestões, melhorias ou encontrar *bugs*, sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*.

## Licença

Este projeto está licenciado sob a [Licença MIT](https://opensource.org/licenses/MIT).

## Desenvolvido por

Este projeto foi desenvolvido para a disciplina Projeto Integrador IV da graduação em Engenharia de Computação da Univesp (Universidade Virtual do Estado de São Paulo) pelos alunos:

- Eliezer Tavares de Oliveira
- Anderson Vianna Ferrari
- Efrain Tobal Tavares
- Lucas de Goes Vieira Junior