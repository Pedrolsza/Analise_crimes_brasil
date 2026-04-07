# 📊 Análise de Crimes Contra Vulneráveis no Brasil

## 👥 Equipe
- Sanderson Machado  
- Pedro Abreu  
- Arthur Cavalcante  

---

## 🎯 Problema

Observa-se um possível aumento nos relatos de crimes contra vulneráveis no Brasil, como sequestro e abuso infantil, ao longo dos anos.

Levanta-se a hipótese de que esse aumento esteja relacionado a fatores socioeconômicos, especialmente:

- Renda per capita  
- Desigualdade social  

---

## 🎯 Objetivo Geral

Analisar a relação entre fatores socioeconômicos e a incidência de crimes contra vulneráveis no Brasil, com foco na correlação entre renda per capita e a ocorrência desses crimes.

---

## 🎯 Objetivos Específicos

- 📈 Identificar padrões temporais dos crimes  
- 🌎 Avaliar a distribuição geográfica  
- 🔗 Analisar a correlação entre renda e incidência de crimes  
- ⚠️ Identificar regiões de maior risco  
- 🛡️ Propor medidas de mitigação baseadas em dados  

---

## 🧠 Hipótese

Regiões com menor renda per capita apresentam maior incidência de crimes contra vulneráveis devido à:

- Maior vulnerabilidade social  
- Desigualdade econômica  
- Menor acesso a políticas públicas de proteção  

---

## 🌎 Escopo do Estudo

| Dimensão       | Detalhes                    |
|----------------|----------------------------|
| Geográfico     | Todos os estados do Brasil |
| Temporal       | 2016 – 2026                |
| Granularidade  | Análise anual por estado   |

---

## 🗂️ Variáveis de Interesse

### 🔴 Crimes Analisados
- Sequestro  
- Estupro de vulnerável  
- Exploração infantil  

> Conforme classificação das bases oficiais de segurança pública

---

### 🟢 Variáveis Socioeconômicas
- Renda per capita  
- Índice de Gini (desigualdade)  
- Taxa de desemprego  
- Percentual da população abaixo da linha da pobreza  
- Densidade demográfica  

---

### 🔵 Variáveis Educacionais
- Indicador de nível socioeconômico (INSE)  
- Dados educacionais do INEP  

---

## 🗃️ Fontes de Dados

### 📍 Segurança Pública
- dados.gov.br  
- SINESP  
- Anuário Brasileiro de Segurança Pública  

**Dados:**
- Ocorrências criminais por estado  
- Relatórios de segurança  

---

### 📍 Socioeconômico
- IBGE  
- Síntese de Indicadores Sociais  
- Atlas de Vulnerabilidade Social  

---

### 📍 Educacional
- INEP (Indicador INSE)  

---

### 📍 Complementares
- Base dos Dados  
- Our World in Data *(uso condicionado à compatibilidade)*  

---

## 🔗 Integração dos Dados

- Chaves principais:
  - **Estado**
  - **Ano**

- Ajustes realizados:
  - Padronização de nomes de estados  
  - Uso de códigos oficiais (IBGE)  

---

## 🔧 Tratamento dos Dados

- Remoção de valores nulos ou inconsistentes  
- Padronização de variáveis categóricas  
- Conversão de datas  
- Filtragem dos crimes relevantes  
- Criação de métricas derivadas:
  - Taxa por 100 mil habitantes  
- Normalização para análise comparativa  

---

## 📊 KPIs

### 📌 Indicadores Principais
- Total de sequestros no período  
- Total de crimes envolvendo menores  
- Variação percentual anual  
- Média anual de ocorrências  
- Estados com maior incidência  
- Taxa por 100 mil habitantes  

### 📌 Indicadores Socioeconômicos
- Renda média das regiões  
- Taxa de desemprego  
- Índice de Gini  
- Percentual de população em pobreza  
- Densidade demográfica  

### 📌 Indicadores Avançados
- Proporção de crimes em áreas de alta vs baixa renda  
- Sazonalidade anual  
- Faixa etária das vítimas *(se disponível)*  
- Gênero das vítimas *(se disponível)*  
- Correlação (Pearson) entre renda e crimes  
- Cluster de risco (alto, médio, baixo)  

---

## 📈 Metodologia

### 🔍 Análise Exploratória (EDA)
- Distribuição dos dados  
- Identificação de outliers  
- Análise temporal  

---

### 📊 Correlação Estatística
- Correlação de **Pearson** entre:
  - Renda per capita  
  - Índice de crimes  

---

### 🤖 Clusterização
- Algoritmo: **K-Means**  
- Objetivo: identificar grupos de risco entre estados  

---

### 📅 Análise Temporal
- Evolução dos crimes ao longo dos anos  
- Identificação de tendências  

---

## 🛠️ Tecnologias Utilizadas

### 💻 Análise de Dados
- Python (Google Colab)  
- Pandas  
- NumPy  
- Matplotlib / Seaborn  
- Scikit-learn  

### 📊 Visualização
- Power BI  

---

## 📤 Entregáveis

- 📁 Dataset tratado e consolidado  
- 📓 Notebook analítico em Python  
- 📊 Dashboard interativo no Power BI  
- 📄 Relatório final com insights  

---

## 📁 Estrutura do Projeto

```
dados-de-crimes/
├── data/
│   ├── raw/           # Dados brutos coletados das fontes
│   └── processed/     # Dados tratados e prontos para análise
│
├── notebooks/
│   └── analise_inicial.ipynb   # Análise exploratória inicial (EDA)
│
├── src/               # Scripts auxiliares e funções do projeto
│
├── .gitignore         # Arquivos ignorados pelo Git
├── README.md          # Documentação do projeto
```


## ⚠️ Limitações

- Subnotificação de crimes  
- Diferença na qualidade dos dados entre estados  
- Falta de granularidade em algumas bases  
- Dados indisponíveis em alguns anos  
- Diferença de classificação entre fontes  
- ⚠️ Correlação não implica causalidade  

---

## 🧩 Próximos Passos

- Definir bases finais  
- Validar compatibilidade dos datasets  
- Realizar coleta e limpeza dos dados  
- Iniciar análise exploratória  

---

## 🎯 Conclusão

Este projeto aplica técnicas de **Ciência de Dados** para analisar a relação entre fatores socioeconômicos e crimes contra vulneráveis no Brasil.

Através de análise estatística, exploração de dados e técnicas de clusterização, busca-se gerar **insights acionáveis** que possam contribuir para:

- Formulação de políticas públicas  
- Identificação de padrões de risco  
- Apoio à tomada de decisão baseada em dados  

---
