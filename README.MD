📊 Análise de Crimes Contra Vulneráveis no Brasil






👥 Membros do Grupo
Sanderson Machado, Pedro Abreu e Arthur Cavalcante

🎯 Problema Identificado

Observa-se um possível aumento nos relatos de crimes contra vulneráveis (sequestro, abuso infantil) no Brasil.
Hipótese: esse aumento pode estar relacionado a fatores socioeconômicos, especialmente renda per capita e desigualdade social.

🎯 Objetivo Geral

Analisar a relação entre fatores socioeconômicos e crimes contra vulneráveis, com foco na correlação entre renda per capita e ocorrência de crimes.

🎯 Objetivos Específicos
Identificar padrões temporais na ocorrência de crimes
Avaliar a distribuição geográfica
Analisar correlação renda x crimes
Identificar regiões de maior risco
Propor medidas de mitigação
🧠 Hipótese Inicial

Regiões com menor renda per capita apresentam maior incidência de crimes contra vulneráveis devido à vulnerabilidade social e desigualdade econômica.

🌎 Recorte do Estudo
Dimensão	Detalhes
Geográfico	Todos os estados do Brasil
Temporal	2016 – 2026
Granularidade	Análise anual por estado
🗂️ Variáveis de Interesse
🔴 Crimes analisados
Sequestro
Estupro de vulnerável
Exploração infantil
🟢 Variáveis Socioeconômicas
Renda per capita
Índice de Gini (desigualdade)
Taxa de desemprego
Percentual da população abaixo da linha da pobreza
Densidade demográfica
🔵 Variáveis Educacionais
Indicador INSE (Nível socioeconômico)
Dados educacionais do INEP
🗃️ Fontes de Dados
Tipo	Fonte	Datasets
Segurança Pública	dados.gov.br
, SINESP, Anuário Brasileiro de Segurança Pública	Ocorrências criminais por estado, Relatórios
Socioeconômico	IBGE
, Atlas de Vulnerabilidade Social	Indicadores sociais por estado
Educacional	INEP
	Indicador INSE
Complementares	Base dos Dados, Our World in Data	Diversos
🔗 Integração dos Dados
Chaves de integração: Estado e Ano
Padronização de nomes de estados ou uso de códigos oficiais (IBGE)
🔧 Tratamento dos Dados
Remoção de valores nulos ou inconsistentes
Padronização de variáveis categóricas
Conversão de datas
Filtragem de crimes relevantes
Criação de métricas derivadas (taxa por 100 mil habitantes)
Normalização para análise comparativa
📊 KPIs Principais
Total de sequestros
Total de crimes envolvendo menores
Variação percentual ano a ano
Média anual de ocorrências
Estados com maior incidência
Taxa de crimes por 100 mil habitantes
Indicadores socioeconômicos correlacionados (renda, Gini, pobreza, desemprego)
📈 Metodologia Analítica
<details> <summary>🔍 Análise Exploratória (EDA)</summary> - Distribuição dos dados - Identificação de outliers - Análise temporal </details> <details> <summary>📊 Correlação Estatística</summary> - Correlação de **Pearson** entre renda per capita e crimes </details> <details> <summary>🤖 Clusterização</summary> - Algoritmo: **K-Means** - Objetivo: identificar grupos de risco entre estados </details> <details> <summary>📅 Análise Temporal</summary> - Evolução dos crimes ao longo dos anos - Identificação de tendências </details>
🛠️ Ferramentas Utilizadas
Python (Google Colab): Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn
Power BI: dashboards interativos
📤 Saída do Projeto
Dataset tratado e consolidado
Notebook analítico em Python
Dashboard Power BI
Relatório final com insights e conclusões
⚠️ Limitações do Estudo
Possível subnotificação de crimes
Diferença na qualidade dos dados entre estados
Falta de granularidade em algumas bases
Dados indisponíveis para certos anos
Diferença de classificação entre fontes
Correlação não implica causalidade
🧩 Próximos Passos
Definir bases finais
Validar compatibilidade entre datasets
Coletar e limpar dados
Iniciar análise exploratória
🎯 Conclusão

Este projeto utiliza técnicas de ciência de dados para analisar crimes contra crianças no Brasil, buscando gerar insights úteis para políticas públicas e mitigação de riscos.
