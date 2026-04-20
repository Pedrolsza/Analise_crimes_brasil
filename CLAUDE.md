# CLAUDE.md — Análise de Crimes Contra Vulneráveis no Brasil

## Project Purpose

Data science research project correlating socioeconomic factors with crimes against vulnerable people (kidnapping, child sexual abuse, child exploitation) across all Brazilian states from 2016 onward. The goal is to generate actionable insights for public policy, not to build a production system.

**Team:** Sanderson Machado, Pedro Abreu, Arthur Cavalcante

---

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.x |
| Data manipulation | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Machine learning | Scikit-learn (K-Means clustering, Pearson correlation) |
| BI Dashboard | Power BI (.pbix) |
| Notebook format | Jupyter (.ipynb) |

No web framework, no database, no API — this is a pure data/analytics project.

---

## Folder Structure

```
dados-crimes/
├── data/
│   ├── raw/          # Original files downloaded from sources — never modify these
│   └── processed/    # Cleaned, merged datasets ready for analysis
├── notebooks/
│   └── analise_inicial.ipynb   # Main EDA notebook
├── src/              # Reusable Python helper functions/scripts
├── .gitignore
├── CLAUDE.md
└── README.MD
```

`data/raw/` is gitignored — raw data files must never be committed. `data/processed/` files may be committed if small enough (< 50 MB) and non-sensitive.

---

## Data Sources

| Category | Source |
|---|---|
| Crime data | SINESP, Anuário Brasileiro de Segurança Pública, dados.gov.br |
| Socioeconomic | IBGE (Síntese de Indicadores Sociais, Atlas de Vulnerabilidade Social) |
| Educational | INEP (Indicador INSE) |
| Supplementary | Base dos Dados, Our World in Data |

**Join keys:** `estado` (state name or IBGE code) + `ano` (year as integer, e.g. 2019).

Always use official IBGE state codes when merging datasets to avoid name inconsistencies.

---

## Variables of Interest

**Crime variables (target):**
- `estupro_vulneravel` — rape of a vulnerable person (Art. 217-A CP) — **available in SINESP**
- `estupro` — broader rape category (Art. 213 CP) — **available in SINESP**, kept for context
- `sequestro` — kidnapping — **NOT in SINESP**, must be sourced from Anuario Brasileiro de Seguranca Publica or state SSPs
- `exploracao_infantil` — child exploitation — **NOT in SINESP**, same alternative sources
- Derived: `taxa_por_100k` — rate per 100,000 inhabitants (requires IBGE population data)

**Socioeconomic variables (features):**
- `renda_per_capita`
- `indice_gini`
- `taxa_desemprego`
- `pct_pobreza` — % of population below poverty line
- `densidade_demografica`

**Educational variables:**
- `inse` — Indicador de Nível Socioeconômico (INEP)

---

## Coding Conventions

- All variable and column names in **snake_case Portuguese** (e.g. `taxa_por_100k`, `renda_per_capita`).
- State names follow IBGE official notation; use UF codes (e.g. `SP`, `RJ`) for brevity in columns.
- Notebook cells should be short and focused — one logical step per cell.
- Helper functions that are reused across notebooks go in `src/`.
- Comment data transformations with the source and rationale, not just what the code does.

---

## Analysis Methodology

1. **EDA** — distributions, missing values, outliers per variable and state
2. **Temporal analysis** — year-over-year trends per state and nationally
3. **Correlation** — Pearson correlation between `renda_per_capita` and each crime rate
4. **Clustering** — K-Means on states using socioeconomic + crime variables to define risk groups (high/medium/low)
5. **Geographic visualization** — choropleth maps by state

---

## Commands

```bash
# Install dependencies (once a requirements.txt exists)
pip install -r requirements.txt

# Launch Jupyter
jupyter notebook

# Run a specific script in src/
python src/<script>.py
```

There is no build system, test suite, or linting configuration yet. If you add one, record it here.

---

## What to Avoid

- **Never modify files in `data/raw/`** — treat them as read-only source of truth.
- Do not commit large binary files (CSV > 50 MB, .pbix, .xlsx with raw data).
- Do not invent data or fill missing values with arbitrary numbers — document and handle gaps explicitly.
- Do not draw causal conclusions from correlations — the project hypothesis is correlational.
- Do not add machine learning models beyond K-Means without team alignment; the scope is EDA + correlation + clustering.
- Do not rename existing columns without updating all notebooks and scripts that reference them.

---

## Known Limitations

- Crime underreporting varies significantly between states.
- Data quality and availability differ across states and years.
- Some years/states may be missing from certain sources.
- Classification of crimes differs between sources — always document which source and classification was used.
- Correlation ≠ causation.

---

## Safe Change Checklist

Before committing any change:
- [ ] Raw data files are still in `data/raw/` and not modified.
- [ ] No credentials, API keys, or PII are included.
- [ ] Column names and join keys (`estado`, `ano`) are consistent across files.
- [ ] Notebook outputs are cleared before committing (avoid large embedded outputs).
- [ ] New helper functions are in `src/`, not copy-pasted across notebooks.
