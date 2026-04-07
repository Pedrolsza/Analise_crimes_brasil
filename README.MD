📊 Projeto Prático de Ciência de Dados 

👥 Membros do Grupo 

Sanderson Machado  

Pedro Abreu  

Arthur Cavalcante  

 

🎯 Problema Identificado 

Observa-se um possível aumento nos relatos de crimes contra vulneráveis (como sequestro e abuso infantil) ao longo dos anos no Brasil. Levanta-se a hipótese de que esse aumento possa estar relacionado a fatores socioeconômicos, especialmente à renda per capita e à desigualdade social. 

 

🎯 Objetivo Geral 

Analisar a relação entre fatores socioeconômicos e a incidência de crimes contra vulneráveis no Brasil, com foco na correlação entre renda per capita e ocorrência de crimes como sequestro e abuso infantil. 

 

🎯 Objetivos Específicos 

Identificar padrões temporais na ocorrência de crimes contra vulneráveis 

Avaliar a distribuição geográfica dos crimes  

Analisar a correlação entre renda per capita e incidência de crimes  

Identificar regiões de maior risco  

Propor possíveis medidas de mitigação com base nos dados  

 

🧠 Hipótese Inicial 

Regiões com menor renda per capita apresentam maior incidência de crimes contra vulnerável devido à maior vulnerabilidade social, desigualdade econômica e menor acesso a políticas públicas de proteção. 

 

🌎 Recorte do Estudo 

Geográfico: Todos os estados do Brasil  

Temporal: 2016 – 2026 

Granularidade: Análise anual por estado  

 

🗂️ Definição das Variáveis de Interesse 

🔴 Crimes analisados 

Serão considerados crimes classificados como: 

Sequestro  

Estupro de vulnerável  

Exploração infantil  

Conforme classificação das bases oficiais de segurança pública. 

 

🟢 Variáveis Socioeconômicas 

Renda per capita  

Índice de Gini (desigualdade)  

Taxa de desemprego  

Percentual da população abaixo da linha da pobreza  

Densidade demográfica  

 

🔵 Variáveis Educacionais 

Indicador de nível socioeconômico (INSE)  

Dados educacionais relevantes do INEP  

 

🗃️ Fontes de Dados 

📍 Fonte A – Segurança Pública 

dados.gov.br  

SINESP  

Anuário Brasileiro de Segurança Pública  

Datasets: 

Ocorrências criminais por estado  

Relatórios de segurança pública  

 

📍 Fonte B – Socioeconômico 

IBGE  

Síntese de Indicadores Sociais  

Atlas de Vulnerabilidade Social  

 

📍 Fonte C – Educacional 

INEP (Indicador INSE)  

 

📍 Fonte D – Complementares 

Base dos Dados  

Our World in Data (uso condicionado à compatibilidade com recorte geográfico)  

 

🔗 Integração dos Dados 

Os datasets serão integrados com base nas seguintes chaves: 

Estado  

Ano  

Caso necessário: 

Padronização de nomes de estados  

Uso de códigos oficiais (IBGE)  

 

🔧 Tratamento dos Dados 

As etapas de tratamento incluirão: 

Remoção de valores nulos ou inconsistentes  

Padronização de variáveis categóricas (ex: nomes de estados)  

Conversão de datas para formato adequado  

Filtragem dos crimes relevantes  

Criação de métricas derivadas (ex: taxa por 100 mil habitantes)  

Normalização de variáveis para análise comparativa  

 

📊 KPIs (Indicadores de Desempenho) 

Total de relatos de sequestro no período  

Total de relatos envolvendo menores de idade  

Variação percentual de casos (ano a ano)  

Média anual de ocorrências  

Estados com maior incidência  

Taxa de crimes por 100 mil habitantes  

Renda média das regiões afetadas  

Taxa de desemprego por estado  

Índice de Gini por estado  

Percentual de população em pobreza  

Densidade demográfica  

Proporção de crimes em áreas de alta vs baixa renda  

Sazonalidade anual  

Faixa etária média das vítimas (se disponível)  

Gênero predominante das vítimas (se disponível)  

Correlação (Pearson) entre renda e número de crimes  

Cluster de risco (alto, médio, baixo)  

 

📈 Metodologia Analítica 

🔍 Análise Exploratória (EDA) 

Distribuição dos dados  

Identificação de outliers  

Análise temporal  

 

📊 Correlação Estatística 

Correlação de Pearson entre:  

Renda per capita  

Índice de crimes  

 

🤖 Clusterização 

Algoritmo: K-Means  

Objetivo: Identificar grupos de risco entre estados  

 

📅 Análise Temporal 

Evolução dos crimes ao longo dos anos  

Identificação de tendências  

 

📊 Ferramentas Utilizadas 

Python (Google Colab)  

Pandas  

NumPy  

Matplotlib / Seaborn  

Scikit-learn  

Power BI (para visualização e dashboard)  

 

📤 Saída do Projeto 

Dataset tratado e consolidado  

Notebook analítico em Python  

Dashboard interativo no Power BI  

Relatório final com insights e conclusões  

 

⚠️ Limitações do Estudo 

Possível subnotificação de crimes  

Diferença na qualidade dos dados entre estados  

Falta de granularidade em algumas bases  

Dados indisponíveis para certos anos (solucionar em breve)  

Diferença de classificação de crimes entre fontes (solucionar em breve)  

Correlação não implica causalidade  

 

🧩 Próximos Passos 

Definir bases finais a serem utilizadas (solucionar em breve)  

Validar compatibilidade entre datasets (solucionar em breve)  

Realizar coleta e limpeza dos dados  

Iniciar análise exploratória  

 

🎯 Conclusão do Documento 

Este projeto busca aplicar técnicas de ciência de dados para compreender a relação entre fatores socioeconômicos e crimes contra crianças no Brasil, utilizando dados reais e métodos estatísticos para gerar insights relevantes e apoiar possíveis estratégias de mitigação. 

     
