"""
merge_sinesp_inse_populacao.py
-------------------------------
Une os datasets SINESP+INSE (left e inner join) com a populacao estadual do IBGE
e calcula as taxas de crime por 100.000 habitantes.

DECISAO DE DESIGN:
  - Populacao e adicionada via left join em (uf, ano) nos dois datasets existentes:
      sinesp_inse_left_join.csv  -> todos os anos SINESP (2016-2025)
      sinesp_inse_inner_join.csv -> apenas 2019 e 2021 (anos com INSE)
  - IBGE cobre 2016-2025; populacao estara disponivel para todos os anos dos dois arquivos.
  - Colunas de taxa calculadas:
      taxa_estupro_por_100k          = estupro          / populacao * 100_000
      taxa_estupro_vulneravel_por_100k = estupro_vulneravel / populacao * 100_000
  - Os arquivos SINESP+INSE originais NAO sao modificados.

LIMITACAO CONHECIDA:
  - Populacao IBGE para anos pos-Censo usa estimativas intercensitarias; nao e contagem exata.
  - Para correlacao de Pearson com INSE, usar sinesp_inse_pop_inner_join.csv (2019 e 2021).
"""

import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

# ── Caminhos ────────────────────────────────────────────────────────────────────
ROOT          = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"

LEFT_FILE   = PROCESSED_DIR / "sinesp_inse_left_join.csv"
INNER_FILE  = PROCESSED_DIR / "sinesp_inse_inner_join.csv"
POP_FILE    = PROCESSED_DIR / "ibge_populacao.csv"

OUTPUT_LEFT  = PROCESSED_DIR / "sinesp_inse_pop_left_join.csv"
OUTPUT_INNER = PROCESSED_DIR / "sinesp_inse_pop_inner_join.csv"

MERGE_KEYS   = ["uf", "ano"]
CRIME_COLS   = ["estupro", "estupro_vulneravel"]


# ── Funcoes auxiliares ──────────────────────────────────────────────────────────

def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Carrega e normaliza os tres arquivos de entrada."""
    for path in (LEFT_FILE, INNER_FILE, POP_FILE):
        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo nao encontrado: {path}\n"
                "Execute os pipelines anteriores antes deste merge."
            )

    def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
        df["uf"]  = df["uf"].astype(str).str.strip().str.upper()
        df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
        return df

    left  = normalize_keys(pd.read_csv(LEFT_FILE))
    inner = normalize_keys(pd.read_csv(INNER_FILE))
    pop   = normalize_keys(pd.read_csv(POP_FILE))

    print(f"  LEFT JOIN carregado  : {len(left):,} linhas", flush=True)
    print(f"  INNER JOIN carregado : {len(inner):,} linhas", flush=True)
    print(f"  Populacao carregada  : {len(pop):,} linhas "
          f"| anos: {sorted(pop['ano'].dropna().unique().tolist())}", flush=True)

    return left, inner, pop


def add_population(df: pd.DataFrame, pop: pd.DataFrame, label: str) -> pd.DataFrame:
    """Merge com populacao e calcula taxas por 100k."""
    merged = df.merge(pop[MERGE_KEYS + ["populacao"]], on=MERGE_KEYS, how="left")

    sem_pop = merged["populacao"].isnull().sum()
    if sem_pop:
        anos_sem = sorted(
            merged.loc[merged["populacao"].isnull(), "ano"].dropna().unique().tolist()
        )
        print(f"  [{label}] ATENCAO: {sem_pop} linhas sem populacao | anos: {anos_sem}", flush=True)
    else:
        print(f"  [{label}] Populacao disponivel para todas as {len(merged):,} linhas.", flush=True)

    for crime in CRIME_COLS:
        if crime in merged.columns:
            merged[crime] = pd.to_numeric(merged[crime], errors="coerce")
            taxa_col = f"taxa_{crime}_por_100k"
            merged[taxa_col] = merged[crime] / merged["populacao"] * 100_000

    return merged.sort_values(MERGE_KEYS).reset_index(drop=True)


def validate_output(df: pd.DataFrame, label: str) -> None:
    """Imprime sumario de validacao para um DataFrame final."""
    anos  = sorted(df["ano"].dropna().unique().tolist())
    n_ufs = df["uf"].nunique()
    dupl  = df.duplicated(subset=MERGE_KEYS).sum()

    taxa_cols = [c for c in df.columns if c.startswith("taxa_")]
    nulls_taxa = df[taxa_cols].isnull().sum().to_dict() if taxa_cols else {}

    print(f"\n  [{label}]", flush=True)
    print(f"    Linhas             : {len(df):,}", flush=True)
    print(f"    Duplicatas (uf+ano): {dupl}", flush=True)
    print(f"    Anos presentes     : {anos}", flush=True)
    print(f"    UFs presentes      : {n_ufs}", flush=True)
    print(f"    Colunas de taxa    : {taxa_cols}", flush=True)
    print(f"    Nulos nas taxas    : {nulls_taxa}", flush=True)


# ── Pipeline principal ──────────────────────────────────────────────────────────

def run() -> tuple[pd.DataFrame, pd.DataFrame]:
    print("=" * 60, flush=True)
    print("Pipeline POPULACAO -- merge_sinesp_inse_populacao.py", flush=True)
    print("=" * 60, flush=True)

    left, inner, pop = load_inputs()

    print("\n  Adicionando populacao ao left join ...", flush=True)
    left_pop = add_population(left, pop, "LEFT")

    print("  Adicionando populacao ao inner join ...", flush=True)
    inner_pop = add_population(inner, pop, "INNER")

    print("\n  --- Validacao ---", flush=True)
    validate_output(left_pop,  "sinesp_inse_pop_left_join")
    validate_output(inner_pop, "sinesp_inse_pop_inner_join")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    left_pop.to_csv(OUTPUT_LEFT,  index=False, encoding="utf-8")
    inner_pop.to_csv(OUTPUT_INNER, index=False, encoding="utf-8")

    print(f"\n  Salvo -> {OUTPUT_LEFT}", flush=True)
    print(f"  Salvo -> {OUTPUT_INNER}", flush=True)

    print("\n" + "=" * 60, flush=True)
    print("RECOMENDACAO PARA A ANALISE:", flush=True)
    print("  Correlacao de Pearson -> usar sinesp_inse_pop_inner_join.csv", flush=True)
    print("    (2019 e 2021; INSE + populacao completos)", flush=True)
    print("  Analise temporal -> usar sinesp_inse_pop_left_join.csv", flush=True)
    print("    (todos os anos; colunas INSE NaN fora de 2019/2021)", flush=True)
    print("=" * 60, flush=True)

    return left_pop, inner_pop


if __name__ == "__main__":
    run()
