# Relatorio Final — Analise de Crimes Contra Vulneraveis no Brasil

**Disciplina:** Analise de Dados  
**Equipe:** Sanderson Machado, Pedro Abreu, Arthur Cavalcante  
**Data:** Maio de 2026

---

## 1. Problema de Pesquisa

O Brasil registra um crescimento continuo de crimes sexuais contra vulneraveis desde 2018. No entanto, as taxas de notificacao variam amplamente entre estados, e a relacao entre o nivel socioeconomico educacional e a incidencia registrada desses crimes nao e bem compreendida.

**Pergunta central:** Existe correlacao entre o nivel socioeconomico educacional dos estados (medido pelo INSE/INEP) e as taxas registradas de estupro e estupro de vulneravel por 100.000 habitantes?

---

## 2. Objetivo

Analisar a distribuicao geografica e temporal dos crimes de estupro e estupro de vulneravel no Brasil (2016–2025), correlacionar com o Indicador de Nivel Socioeconomico Educacional (INSE/INEP) e agrupar os estados em perfis de risco observado por meio de clusterizacao K-Means.

Os resultados sao descritivos e correlacionais. Nao sao estabelecidas relacoes de causalidade.

---

## 3. Fontes de Dados

| Fonte | Descricao | Granularidade | Periodo |
|---|---|---|---|
| SINESP | Ocorrencias de estupro e estupro de vulneravel | UF + ano | 2016–2026 |
| INEP — INSE | Indicador de Nivel Socioeconomico Educacional | UF + ano | 2019 e 2021 |
| IBGE — Estimativas Populacionais | Populacao municipal agregada por UF | UF + ano | 2016–2025 |

**Fontes ausentes desta versao (pendentes):**
- IBGE PNAD Continua: renda per capita, taxa de desemprego, indice Gini, % pobreza
- Anuario Brasileiro de Seguranca Publica: dados de sequestro e exploracao infantil
- Dados de densidade demografica por UF

---

## 4. Metodologia

1. **Carregamento e padronizacao** de cada fonte em scripts Python independentes (`src/`).
2. **Merge em camadas:**
   - SINESP + INSE (left join e inner join) por `(uf, ano)`
   - Adicao de populacao IBGE; calculo de `taxa_por_100k`
3. **Analise exploratoria (EDA):** distribuicoes, tendencias temporais, cobertura por UF.
4. **Correlacao de Pearson** entre variaveis INSE e taxas de crime por 100k.
5. **Clusterizacao K-Means** com features baseadas em taxas e indicadores INSE; StandardScaler aplicado antes do clustering.

---

## 5. Etapas de Tratamento dos Dados

| Etapa | Script | Output |
|---|---|---|
| Padronizacao SINESP | `src/load_and_standardize_sinesp.py` | `data/processed/sinesp_crimes.csv` |
| Padronizacao INSE | `src/load_and_standardize_inse.py` | `data/processed/inep_inse.csv` |
| Padronizacao IBGE Populacao | `src/load_and_standardize_ibge_population.py` | `data/processed/ibge_populacao.csv` |
| Merge SINESP + INSE | `src/merge_sinesp_inse.py` | `sinesp_inse_left_join.csv` / `sinesp_inse_inner_join.csv` |
| Merge + taxas por 100k | `src/merge_sinesp_inse_populacao.py` | `sinesp_inse_pop_left_join.csv` / `sinesp_inse_pop_inner_join.csv` |
| Clusterizacao K-Means | Notebook (Secao 10b) | `sinesp_inse_pop_clusters.csv` |

**Decisoes de tratamento relevantes:**
- Anos 2016–2017 excluidos das analises de tendencia: 10 UFs com zeros sistematicos (subnotificacao).
- 2026 excluido de comparacoes anuais: ano parcial (Jan–Mar apenas).
- RJ marcado como NaN para `estupro_vulneravel` em todos os anos (zero sistematico — falha de notificacao confirmada).
- INSE filtrado para o agregado estadual total (`rede=Total`, `area=Total`, `tipo_localizacao=Total`).
- Populacao IBGE: linha com `sigla_uf` vazia (artefato) descartada antes da agregacao municipal→estadual.

---

## 6. KPIs Principais

| Indicador | Valor |
|---|---|
| Total de registros de estupro de vulneravel (2018–2025) | ~404.500 ocorrencias |
| Crescimento de estupro de vulneravel (2018→2025) | +45,3% |
| Proporcao media de estupro de vulneravel sobre total (2018–2025) | 63,7% |
| UFs com zero sistematico em estupro_vulneravel | RJ (todos os anos), RO e ES (varios anos) |
| Taxa media nacional estupro de vulneravel (2019+2021, por 100k) | 23,3 por 100.000 hab. |
| Estados com maior taxa observada de estupro de vulneravel | TO (72,5), RR, AP, GO (acima de 35/100k) |

---

## 7. Resumo da EDA

- **Tendencia nacional:** crescimento continuo de `estupro_vulneravel` de 2018 a 2023, com leve estabilizacao em 2024–2025. `estupro` (Art. 213) mostra leve queda no mesmo periodo.
- **Sazonalidade:** dados anuais; nao e possivel analisar sazonalidade mensal nesta versao.
- **Cobertura:** 27 UFs x 11 anos no SINESP (2016–2026). A partir de 2018 a cobertura e consistente com excecao de RJ.
- **Distribuicao:** forte assimetria positiva nos contadores absolutos — estados grandes (SP, MG, BA) dominam em volume absoluto. Taxas por 100k apresentam distribuicao mais equilibrada.
- **Destaque:** SP lidera em volume absoluto (88.186 registros 2018–2025), mas estados do Norte apresentam taxas por 100k mais altas quando normalizadas pela populacao.

---

## 8. Resultados da Correlacao de Pearson

**Dataset utilizado:** `sinesp_inse_pop_inner_join.csv` (n=54: 27 UFs x 2 anos, 2019 e 2021).

| Variavel INSE | r vs estupro/100k | Sig | r vs estupro_vuln/100k | Sig |
|---|---|---|---|---|
| inse (score agregado) | +0,259 | n.s. (p=0,059) | +0,116 | n.s. |
| percentual_nivel_1 | **−0,391** | ** (p=0,003) | −0,057 | n.s. |
| percentual_nivel_2 | **−0,308** | * (p=0,023) | −0,085 | n.s. |
| percentual_nivel_5 | **+0,342** | * (p=0,011) | +0,066 | n.s. |
| demais niveis (3,4,6,7,8) | |n.s. | | n.s. |

Sig: `**` p<0,01 · `*` p<0,05 · `n.s.` nao significativo

**Interpretacao:**

- `taxa_estupro_vulneravel_por_100k` **nao apresentou correlacao significativa com nenhuma variavel INSE.** Consistente com subnotificacao estrutural e generalizada desta categoria criminal.
- `taxa_estupro_por_100k` apresentou correlacao negativa com os niveis socieconomicos mais baixos do INSE (nivel_1 e nivel_2) e positiva com nivel_5. O padrao sugere um **efeito de infraestrutura de notificacao:** estados com maior desenvolvimento institucional registram mais crimes, nao necessariamente porque tem mais crimes.
- O resultado e o inverso da hipotese ingênua "mais pobreza → mais crime registrado", o que e coerente com o problema estrutural de subnotificacao do SINESP em regioes menos desenvolvidas.

> **Limitacao critica:** n=54, apenas 2 pontos temporais, sem controles para fatores confundidores. Os resultados sao frageis e exploratórios.

---

## 9. Resultados da Clusterizacao K-Means

**Configuracao:** K-Means (k=3, random_state=42, n_init=20), StandardScaler aplicado.  
**Features:** `taxa_estupro_por_100k`, `taxa_estupro_vulneravel_por_100k`, `inse`, `percentual_nivel_1`, `percentual_nivel_2`, `percentual_nivel_5`.  
**Silhouette scores:** k=2: 0,481 | k=3: 0,491 (selecionado) | k=4: 0,450.

| Perfil | n obs | n UFs | taxa_estupro_vuln/100k | taxa_estupro/100k | INSE |
|---|---|---|---|---|---|
| Risco observado mais alto | 17 | 9 | 33,4 | 14,7 | 5,34 |
| Risco observado mais baixo | 28 | 14 | 24,5 | 10,9 | 4,56 |
| Padrao atipico | 9 | 5 | 0,6 | 55,8 | 5,05 |

**UFs por perfil:**
- **Risco observado mais alto:** DF, GO, MG, MT, PR, RS, SC, SP, TO (*)
- **Risco observado mais baixo:** AC, AL, AM, AP, BA, CE, MA, PA, PB, PE, PI, RN, RR, SE
- **Padrao atipico:** ES, MS, RJ, RO, TO (*)

(*) TO aparece em perfis diferentes entre 2019 e 2021.

**Interpretacao dos clusters:**
- O cluster "mais alto" concentra estados do Sul, Sudeste e Centro-Oeste, com maior INSE e maiores taxas registradas. Isso provavelmente reflete melhor infraestrutura de notificacao, nao necessariamente maior incidencia real.
- O cluster "mais baixo" concentra estados do Norte e Nordeste, com menor INSE e menores taxas registradas. Pode refletir subnotificacao estrutural.
- O cluster "atipico" isolou estados com alta taxa de estupro mas taxa de estupro de vulneravel proxima de zero — sinal de falha grave de notificacao dessa categoria especifica (especialmente RJ, com zero registros de estupro_vulneravel em todo o periodo SINESP).

> Os clusters sao exploratórios e **nao devem ser interpretados como grupos de risco real** sem controlar por capacidade de notificacao e outros fatores socioeconomicos nao observados.

---

## 10. Limitacoes

1. **Subnotificacao:** O SINESP reflete crimes notificados, nao crimes ocorridos. A subnotificacao e sistematica e varia por UF, tipo de crime e periodo.
2. **Cobertura do INSE:** Disponivel apenas para 2019 e 2021. A correlacao com crimes se baseia em n=54 observacoes e apenas 2 pontos temporais.
3. **Ausencia de variaveis socioeconomicas:** Renda per capita, indice Gini, taxa de desemprego, percentual de pobreza e densidade demografica nao foram incorporados por limitacao de tempo. Sao variaveis confundidoras importantes.
4. **RJ:** Rio de Janeiro registra zero ocorrencias de estupro de vulneravel em todos os anos do SINESP. Tratado como NaN, mas a causa raiz (falha sistemica de notificacao) nao foi investigada.
5. **2026 parcial:** Dados de 2026 cobrem apenas jan–mar. Excluidos de todas as analises de tendencia.
6. **Correlacao nao implica causalidade:** Todos os resultados sao correlacionais. Nenhuma relacao de causa e efeito e estabelecida.
7. **K-Means e sensivel a outliers e a escala:** O cluster "atipico" e fortemente influenciado pelos estados com taxa de estupro_vulneravel proxima de zero, o que pode distorcer os demais clusters.

---

## 11. Conclusao

O conjunto de dados do SINESP revela um crescimento de **45,3% no registro de estupro de vulneravel entre 2018 e 2025**, com aceleracao a partir de 2022. A proporcao desse crime sobre o total de crimes sexuais aumentou de 56,1% para 71,1% no mesmo periodo.

A correlacao com o INSE e **fraca e ambigua.** Os unicas correlacoes significativas encontradas (com `taxa_estupro_por_100k`) apontam na direcao oposta da hipotese intuitiva: estados com maior proporcao de alunos nos niveis socioeconomicos mais baixos registram *menos* crimes por habitante — o que e consistente com um efeito de subnotificacao estrutural, nao com ausencia real de crimes.

A clusterizacao K-Means produziu tres perfis exploratórios que refletem mais a **capacidade de notificacao dos estados** do que niveis reais de criminalidade. Sem variaveis socioeconomicas adicionais (renda, Gini, desemprego), e impossivel separar o efeito da pobreza do efeito da subnotificacao.

**Conclusao metodologica:** Os dados do SINESP sao necessarios mas insuficientes para estabelecer correlacoes robustas entre nivel socioeconomico e crimes contra vulneraveis. A analise confirma a hipotese de pesquisa de que ha variacao geografica expressiva nas taxas observadas, mas nao consegue atribuir essa variacao a fatores causais especificos.

---

## 12. Recomendacoes para Trabalho Futuro

### Dados prioritarios

| Variavel | Fonte sugerida | Impacto esperado |
|---|---|---|
| Renda per capita estadual | IBGE PNAD Continua | Alta — principal confundidor nao controlado |
| Indice Gini por UF | IBGE Atlas de Vulnerabilidade Social | Alta — mede desigualdade, nao apenas pobreza media |
| Taxa de desemprego | IBGE PNAD Continua | Media |
| % populacao abaixo da linha de pobreza | IBGE Sintese de Indicadores Sociais | Alta |
| Densidade demografica | IBGE | Media |
| Sequestro e exploracao infantil | Anuario Brasileiro de Seguranca Publica | Alta — ampliar escopo de crimes contra vulneraveis |

### Melhorias metodologicas

1. **Adicionar variaveis de infraestrutura de notificacao** (delegacias por 100k, investimento em seguranca publica) para separar o efeito de subnotificacao do efeito real.
2. **Regressao multipla ou modelos de painel** (fixed effects por UF) para controlar heterogeneidade nao observada entre estados.
3. **Serie temporal mais longa com INSE:** aguardar o proximo Censo Escolar (previsto 2023 ou posterior) para ampliar a base de correlacao.
4. **Analise de cluster com features socioeconomicas completas** — refazer K-Means incluindo renda, Gini e desemprego.
5. **Investigar RJ:** buscar fontes alternativas (SSP-RJ, Anuario) para validar se o zero sistematico e falha de notificacao ou problema de integracao com o SINESP.
6. **Mapas coropleticos** por UF para visualizacao geografica no Power BI.

---

*Este relatorio foi gerado com base nos dados disponiveis em maio de 2026.*  
*Correlacao nao implica causalidade. Os resultados sao exploratórios e descritivos.*
