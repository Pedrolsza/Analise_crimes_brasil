# 📊 Análise de Crimes Contra Vulneráveis no Brasil

## 👥 Equipe
- Sanderson Machado  
- Pedro Abreu  
- Arthur Cavalcante  

---

## 🎯 Problema

Observa-se um possível aumento nos relatos de crimes contra vulneráveis no Brasil, como:

- Sequestro  
- Abuso infantil  
- Exploração infantil  

**Hipótese:** esse aumento pode estar relacionado a fatores socioeconômicos, especialmente renda per capita e desigualdade social.

---

## 🎯 Objetivo Geral

Analisar a relação entre fatores socioeconômicos e a ocorrência de crimes contra vulneráveis no Brasil.

---

## 🎯 Objetivos Específicos

- 📈 Identificar padrões temporais dos crimes  
- 🌎 Avaliar a distribuição geográfica  
- 🔗 Analisar correlação entre renda e criminalidade  
- ⚠️ Identificar regiões de maior risco  
- 🛡️ Propor medidas de mitigação  

---

## 🧠 Hipótese

Regiões com menor renda per capita apresentam maior incidência de crimes contra vulneráveis devido à vulnerabilidade social e desigualdade econômica.

---

## 🌎 Escopo do Estudo

| Dimensão      | Detalhes                     |
|--------------|-----------------------------|
| Geográfico   | Todos os estados do Brasil  |
| Temporal     | 2016 – 2026                 |
| Granularidade| Análise anual por estado    |

---

## 🗂️ Variáveis de Interesse

### 🔴 Crimes
- Sequestro  
- Estupro de vulnerável  
- Exploração infantil  

### 🟢 Socioeconômicas
- Renda per capita  
- Índice de Gini  
- Taxa de desemprego  
- População abaixo da linha da pobreza  
- Densidade demográfica  

### 🔵 Educacionais
- Indicador INSE  
- Dados do INEP  

---

## 🗃️ Fontes de Dados

| Tipo              | Fonte                              | Dados |
|------------------|-----------------------------------|------|
| Segurança Pública| dados.gov.br, SINESP, Anuário     | Ocorrências por estado |
| Socioeconômico   | IBGE, Atlas da Vulnerabilidade    | Indicadores sociais |
| Educacional      | INEP                              | INSE |
| Complementar     | Base dos Dados, Our World in Data | Diversos |

---

## 🔗 Integração dos Dados

- Chaves: **Estado + Ano**  
- Padronização por códigos do IBGE  
- Normalização de nomes de estados  

---

## 🔧 Tratamento dos Dados

- Remoção de valores nulos/inconsistentes  
- Padronização de categorias  
- Conversão de datas  
- Filtragem dos crimes relevantes  
- Criação de métricas (ex: taxa por 100 mil habitantes)  
- Normalização dos dados  

---

## 📊 KPIs

- Total de sequestros  
- Total de crimes contra menores  
- Variação percentual anual  
- Média anual de ocorrências  
- Estados com maior incidência  
- Taxa por 100 mil habitantes  
- Correlação com indicadores socioeconômicos  

---

## 📈 Metodologia

### 🔍 Análise Exploratória (EDA)
- Distribuição dos dados  
- Identificação de outliers  
- Análise temporal  

### 📊 Correlação Estatística
- Correlação de **Pearson**  

### 🤖 Clusterização
- Algoritmo: **K-Means**  
- Objetivo: identificar grupos de risco  

### 📅 Análise Temporal
- Evolução ao longo dos anos  
- Identificação de tendências  

---

## 🛠️ Ferramentas

- **Python (Google Colab)**
  - Pandas  
  - NumPy  
  - Matplotlib  
  - Seaborn  
  - Scikit-learn  

- **Power BI**
  - Dashboards interativos  

---

## 📤 Entregáveis

- 📁 Dataset tratado e consolidado  
- 📓 Notebook analítico  
- 📊 Dashboard no Power BI  
- 📄 Relatório final com insights  

---

## ⚠️ Limitações

- Subnotificação de crimes  
- Diferença na qualidade dos dados  
- Falta de granularidade  
- Dados indisponíveis em alguns anos  
- Diferença de classificação entre fontes  
- ⚠️ Correlação ≠ causalidade  

---

## 🧩 Próximos Passos

- Definir bases finais  
- Validar compatibilidade dos dados  
- Coletar e tratar dados  
- Iniciar análise exploratória  

---

## 🎯 Conclusão

Este projeto aplica técnicas de **Ciência de Dados** para analisar crimes contra vulneráveis no Brasil, com o objetivo de gerar **insights relevantes para políticas públicas** e redução de riscos sociais.

---
