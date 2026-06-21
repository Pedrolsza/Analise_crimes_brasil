# Análise de Crimes Contra Vulneráveis no Brasil

## Equipe
- Sanderson Machado
- Pedro Abreu
- Arthur Cavalcante

---

## Problema

O Brasil registra crescimento contínuo de crimes sexuais contra vulneráveis desde 2018. As taxas variam amplamente entre estados, e a relação entre fatores socioeconômicos e a incidência registrada desses crimes não é plenamente compreendida.

**Pergunta central:** Existe correlação entre indicadores socioeconômicos estaduais (renda, desigualdade, desemprego, densidade demográfica) e as taxas registradas de estupro e estupro de vulnerável por 100.000 habitantes?

---

## Objetivo Geral

Analisar a distribuição geográfica e temporal dos crimes de estupro e estupro de vulnerável no Brasil (período principal: 2018–2025), correlacionar com indicadores socioeconômicos e agrupar os estados em perfis de risco observado por meio de clusterização K-Means.

---

## Objetivos Específicos

- Identificar padrões temporais dos crimes registrados
- Avaliar a distribuição geográfica por estado e macrorregião
- Analisar correlações entre indicadores socioeconômicos e taxas de crime por 100k habitantes
- Identificar estados com maior crescimento acumulado de crimes
- Analisar a distribuição de vítimas por gênero
- Agrupar estados em perfis de risco observado por K-Means

---

## Hipótese

Estados com maior desigualdade (Gini), maior desemprego e menor renda per capita apresentam maior incidência registrada de crimes contra vulneráveis, controlando pelo efeito de subnotificação estrutural.

> **Nota:** Os dados do SINESP refletem crimes *registrados*, não crimes *ocorridos*. Parte da variação entre estados pode ser explicada pela capacidade institucional de registro, não pela incidência real.

---

## Escopo do Estudo

| Dimensão       | Detalhes                                          |
|----------------|---------------------------------------------------|
| Geográfico     | Todos os 27 estados + DF                          |
| Temporal       | **2018–2025** (análise principal)                 |
| Granularidade  | Anual por estado (UF)                             |
| Crimes         | Estupro (Art. 213 CP) e Estupro de Vulnerável (Art. 217-A CP) |

> 2016 e 2017 estão disponíveis no SINESP mas apresentam subnotificação sistêmica em vários estados e são excluídos da análise principal. 2026 está disponível parcialmente (jan–mar) e não é usado como ano de análise.

---

## Variáveis de Interesse

### Crimes analisados (SINESP)
| Variável | Disponibilidade |
|----------|----------------|
| `estupro` | 2016–2026, todos os estados |
| `estupro_vulneravel` | 2016–2026, todos os estados |
| `estupro_feminino` / `estupro_masculino` / `estupro_nao_informado` | 2016–2026, cobertura 82–96% |
| `estupro_vulneravel_feminino` / `_masculino` / `_nao_informado` | 2016–2026, cobertura 82–96% |

> **Crimes não disponíveis no SINESP:** sequestro e exploração infantil não constam nesta base de dados. Não foram incluídos neste projeto.

### Variáveis socioeconômicas integradas
| Variável | Fonte | Anos disponíveis |
|----------|-------|-----------------|
| `renda_per_capita` | IBGE SIDRA Tabela 7395 | 2016–2019, 2021–2024 *(2020 ausente — PNAD suspensa)* |
| `taxa_desemprego` | IBGE SIDRA Tabela 4093 | 2018–2020, 2022–2025 *(2021 suprimido no SIDRA a nível UF)* |
| `gini` | IBGE PNAD Contínua | 2016–2025 |
| `area_km2` | IBGE — Área territorial 2025 | Estático, replicado a todos os anos |
| `densidade_demografica` | Derivada: `populacao / area_km2` | 2016–2025 |

### Variável educacional
| Variável | Fonte | Anos disponíveis |
|----------|-------|-----------------|
| `inse` (Indicador de Nível Socioeconômico Educacional) | INEP | **2019 e 2021 apenas** |
| Distribuição por nível INSE (1–8) | INEP | **2019 e 2021 apenas** |

> **Importante:** O INSE não é uma série anual contínua. Está disponível apenas para os anos em que o INEP divulgou os resultados oficiais (2019 e 2021). Não foram criados valores para outros anos. Tratar como dado de contexto complementar, não como série temporal.

---

## Fontes de Dados

| Fonte | Dataset | Granularidade | Período |
|-------|---------|--------------|---------|
| SINESP / dados.gov.br | Ocorrências criminais por UF | UF × mês → agregado por ano | 2016–2026 |
| IBGE SIDRA — Tabela 7395 | Rendimento médio mensal domiciliar per capita | UF × ano | 2016–2024 (exc. 2020) |
| IBGE SIDRA — Tabela 4093 | Taxa de desocupação | UF × trimestre → média anual | 2018–2025 (exc. 2021 UF) |
| IBGE PNAD Contínua | Índice de Gini por UF | UF × ano | 2016–2025 |
| IBGE — Área territorial | Área km² por UF | UF (estático) | 2025 |
| IBGE — Estimativas populacionais | População estadual | UF × ano | 2016–2025 |
| INEP | INSE — Indicador de Nível Socioeconômico Educacional | UF × ano | 2019 e 2021 |

---

## Pipeline de Dados

### Execução (ordem obrigatória)

```bash
# 1. Padronização de fontes individuais
python src/load_and_standardize_sinesp.py
python src/load_and_standardize_inse.py
python src/load_and_standardize_ibge_population.py
python src/load_and_standardize_percapita.py
python src/load_and_standardize_desocupacao.py
python src/load_and_standardize_gini.py
python src/load_and_standardize_area.py

# 2. Merges SINESP + INSE
python src/merge_sinesp_inse.py
python src/merge_sinesp_inse_populacao.py

# 3. Clusterização K-Means
# Executar o notebook: notebooks/01_eda_crimes_vulneraveis.ipynb
# Seção 10b — gera data/processed/sinesp_inse_pop_clusters.csv

# 4. Dataset mestre e modelo Power BI
python src/build_powerbi_dataset.py
python src/generate_powerbi_model.py
```

### Arquivos gerados (dados processados)

| Arquivo | Descrição | Linhas |
|---------|-----------|--------|
| `data/processed/sinesp_crimes.csv` | SINESP padronizado com colunas de gênero | 297 |
| `data/processed/inep_inse.csv` | INSE agregado estadual (2019 e 2021) | 54 |
| `data/processed/ibge_populacao.csv` | População estadual IBGE (2016–2025) | 270 |
| `data/processed/ibge_percapita.csv` | Renda per capita por UF/ano | 216 |
| `data/processed/ibge_desocupacao.csv` | Taxa de desemprego por UF/ano | 189 |
| `data/processed/ibge_gini.csv` | Índice de Gini por UF/ano | 270 |
| `data/processed/ibge_area.csv` | Área territorial km² por UF (estático) | 27 |
| `data/processed/powerbi_dataset.csv` | Dataset mestre consolidado | 297 |
| `data/processed/sinesp_inse_inner_join.csv` | SINESP × INSE (inner join) | 54 |
| `data/processed/sinesp_inse_left_join.csv` | SINESP × INSE (left join) | 297 |
| `data/processed/sinesp_inse_pop_inner_join.csv` | SINESP × INSE × Pop (inner join) | 54 |
| `data/processed/sinesp_inse_pop_left_join.csv` | SINESP × INSE × Pop (left join) | 297 |
| `data/processed/sinesp_inse_pop_clusters.csv` | Dataset com K-Means (2019 e 2021) | 54 |

---

## Arquivos Power BI

Todos os arquivos abaixo estão em `data/powerbi/`.  
Formato: **UTF-8 com BOM**, separador **ponto e vírgula (;)**, decimal **vírgula (,)**.

| Arquivo | Descrição | Linhas | Colunas |
|---------|-----------|--------|---------|
| `fact_crimes.csv` | Tabela fato principal | 297 | 20 |
| `fact_inse.csv` | Tabela fato INSE (2019 e 2021) | 54 | 13 |
| `dim_uf.csv` | Dimensão estado | 27 | 3 |
| `dim_ano.csv` | Dimensão ano | 11 | 4 |
| `dim_cluster.csv` | Dimensão cluster K-Means | 3 | 3 |

### Como importar no Power BI Desktop

1. **Página Inicial → Obter Dados → Texto/CSV**
2. Para cada arquivo em `data/powerbi/`:
   - Origem do arquivo: `65001: Unicode (UTF-8)`
   - Delimitador: `Ponto e vírgula`
   - Locale: `Português (Brasil)` *(garante que vírgula seja o separador decimal)*
3. Após carregar, criar os relacionamentos no modelo:
   - `fact_crimes[uf]` → `dim_uf[uf]` (N:1)
   - `fact_crimes[ano]` → `dim_ano[ano]` (N:1)
   - `fact_inse[uf]` → `dim_uf[uf]` (N:1)
   - `fact_inse[ano]` → `dim_ano[ano]` (N:1)
   - `fact_inse[cluster_id]` → `dim_cluster[cluster_id]` (N:1)
4. Direção do filtro: filtro simples (dimensão → fato) em todos os relacionamentos.

---

## KPIs Suportados (20)

### Indicadores de Crime
| # | KPI | Colunas utilizadas |
|---|-----|--------------------|
| 1 | Total de estupro de vulnerável por ano | `estupro_vulneravel`, `ano` |
| 2 | Total de estupro (adulto) por ano | `estupro`, `ano` |
| 3 | Total de crimes sexuais combinados | `estupro` + `estupro_vulneravel` |
| 4 | Taxa de estupro de vulnerável por 100k hab | `taxa_estupro_vulneravel_por_100k` |
| 5 | Taxa de estupro adulto por 100k hab | `taxa_estupro_por_100k` |
| 6 | Ranking de UF por taxa de crime | `taxa_*`, `uf` |
| 7 | Distribuição por macrorregião | `regiao` (dim_uf), `estupro_vulneravel` |
| 8 | Série histórica nacional (2018–2025) | `ano`, `estupro_vulneravel` |
| 9 | Variação % anual de estupro de vulnerável | `estupro_vulneravel`, `ano` |
| 10 | Proporção estupro vulnerável / total crimes sexuais | `estupro`, `estupro_vulneravel` |
| 11 | UFs com maior crescimento acumulado de crimes | `taxa_*`, `uf`, `ano` |

### Indicadores de Gênero das Vítimas
| # | KPI | Colunas utilizadas |
|---|-----|--------------------|
| 12 | % vítimas femininas — estupro de vulnerável | `estupro_vulneravel_feminino`, `estupro_vulneravel` |
| 13 | % vítimas masculinas — estupro de vulnerável | `estupro_vulneravel_masculino`, `estupro_vulneravel` |

### Indicadores Socioeconômicos
| # | KPI | Colunas utilizadas | Cobertura |
|---|-----|--------------------|-----------|
| 14 | Correlação Gini vs taxa de crime | `gini`, `taxa_*` | 2016–2025 (n=270) |
| 15 | Correlação desemprego vs taxa de crime | `taxa_desemprego`, `taxa_*` | 2018–2025 (n=189) |
| 16 | Correlação renda per capita vs taxa de crime | `renda_per_capita`, `taxa_*` | 2016–2024 exc. 2020 (n=216) |
| 17 | Densidade demográfica por UF | `densidade_demografica` | 2016–2025 |

### Indicadores Educacionais e de Cluster
| # | KPI | Colunas utilizadas | Cobertura |
|---|-----|--------------------|-----------|
| 18 | Distribuição de alunos por nível INSE (1–8) | `percentual_nivel_1…8` | 2019 e 2021 |
| 19 | Cluster de risco observado por UF (K-Means) | `cluster_id`, `perfil` | 2019 e 2021 |
| 20 | INSE médio por UF | `inse` | 2019 e 2021 |

---

## Metodologia

### Análise Exploratória (EDA)
- Distribuição de crimes por UF e ano
- Identificação de outliers e subnotificação (ex.: RJ com zero registros de estupro_vulneravel)
- Análise de cobertura de gênero por ano

### Correlação de Pearson
- Variável dependente: `taxa_estupro_vulneravel_por_100k` e `taxa_estupro_por_100k`
- Variáveis independentes: `gini`, `taxa_desemprego`, `renda_per_capita`, `inse`
- Resultados são exploratórios e descritivos; não estabelecem causalidade

### Clusterização K-Means
- Algoritmo: K-Means (k=3, random_state=42, n\_init=20), StandardScaler aplicado
- Features: taxas de crime por 100k + indicadores INSE
- Executado sobre o inner join SINESP × INSE (n=54: 27 UFs × 2 anos)
- Silhouette score: 0,491 para k=3

---

## Tecnologias

| Componente | Tecnologia |
|-----------|-----------|
| Linguagem | Python 3 |
| Dados | pandas, numpy |
| Estatística e ML | scipy, scikit-learn |
| Visualização | matplotlib, seaborn |
| Dashboard | Power BI Desktop |

---

## Estrutura do Projeto

```
Dados_Crimes/
├── data/
│   ├── raw/
│   │   ├── sinesp/          # Excels SINESP (não versionados — baixar separadamente)
│   │   ├── ibge/            # CSVs IBGE SIDRA (versionados)
│   │   └── inep_inse/       # CSV INSE raw (versionado)
│   ├── processed/           # CSVs padronizados e mergeados
│   └── powerbi/             # CSVs prontos para importação no Power BI
├── notebooks/
│   └── 01_eda_crimes_vulneraveis.ipynb
├── reports/
│   └── relatorio_final.md
├── src/
│   ├── load_and_standardize_sinesp.py
│   ├── load_and_standardize_inse.py
│   ├── load_and_standardize_ibge_population.py
│   ├── load_and_standardize_percapita.py
│   ├── load_and_standardize_desocupacao.py
│   ├── load_and_standardize_gini.py
│   ├── load_and_standardize_area.py
│   ├── merge_sinesp_inse.py
│   ├── merge_sinesp_inse_populacao.py
│   ├── build_powerbi_dataset.py
│   └── generate_powerbi_model.py
├── .gitignore
└── README.MD
```

---

## Entregáveis

- Dataset tratado e consolidado (`data/processed/powerbi_dataset.csv`)
- Modelo de dados Power BI (`data/powerbi/`)
- Notebook analítico (`notebooks/01_eda_crimes_vulneraveis.ipynb`)
- Relatório final (`reports/relatorio_final.md`)
- Dashboard interativo no Power BI

---

## Limitações

### Dados de Crime (SINESP)
- O SINESP reflete crimes **registrados**, não crimes ocorridos. Subnotificação é sistêmica e varia por UF, crime e período.
- **Rio de Janeiro** apresenta zero registros de `estupro_vulneravel` em todos os anos do SINESP. Tratado como falha de notificação, não ausência real.
- 2016 e 2017 excluídos da análise principal: subnotificação sistêmica em múltiplos estados.
- 2026 excluído: dados parciais (jan–mar apenas).

### Variáveis Socioeconômicas
- **`renda_per_capita`:** ausente em 2020 (PNAD suspensa naquele ano), 2025 e 2026. Não interpolado.
- **`taxa_desemprego`:** valores suprimidos ("...") pelo IBGE a nível estadual em 2021 no SIDRA. Resultado: 2021 permanece nulo. Não interpolado.
- **`gini`:** ausente apenas para 2026 (ainda não publicado). Não interpolado.

### INSE (Nível Socioeconômico Educacional)
- **O INSE está disponível apenas para 2019 e 2021.** Não é uma série anual contínua.
- Não foram criados valores INSE para outros anos (não duplicar, não interpolar).
- Usar como dado de contexto complementar, não como variável principal de correlação.
- A correlação INSE × crime é limitada a n=54 observações (2 pontos temporais). Resultados são frágeis e exploratórios.

### Metodológicas
- Correlação não implica causalidade. Todos os resultados são descritivos e correlacionais.
- O K-Means foi executado com n=54. Os clusters refletem padrões de notificação, não necessariamente risco real.
- Área territorial de 2025 foi replicada para todos os anos. Alterações de limites estaduais não foram tratadas.
- Crimes de sequestro e exploração infantil não estão disponíveis no SINESP e não foram analisados neste projeto.

---

## Conclusão

Este projeto integra dados de segurança pública (SINESP), indicadores educacionais (INSE/INEP) e socioeconômicos (IBGE) para analisar a relação entre fatores estruturais e a incidência registrada de crimes contra vulneráveis no Brasil entre 2018 e 2025.

O Gini (2016–2025, n=270) é a variável com maior cobertura temporal para análise de correlação com taxas de crime. A análise confirmou crescimento de **+45,3%** nos registros de estupro de vulnerável entre 2018 e 2025, com concentração nos estados do Norte e Centro-Oeste quando normalizado por 100k habitantes.

Todos os resultados são descritivos e correlacionais. **Correlação não implica causalidade.**
