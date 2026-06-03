"""
merge_sinesp_inse.py
---------------------
Une sinesp_crimes.csv com inep_inse.csv pelas chaves (uf, ano).

DECISAO DE DESIGN:
  - SINESP usa coluna 'uf'; INSE usa 'sigla_uf'. Ambas contem os mesmos
    codigos IBGE de 2 letras (SP, RJ...). 'sigla_uf' e renomeada para 'uf'
    antes do merge para manter consistencia com o schema do projeto.
  - Dois arquivos de saida sao gerados:
      left join  -> todos os anos do SINESP; colunas INSE ficam NaN fora de 2019/2021.
      inner join -> apenas os anos com dados INSE correspondentes (esperado: 2019 e 2021).
  - Os arquivos de entrada NAO sao modificados.

LIMITACAO CONHECIDA:
  - INSE cobre apenas 2019 e 2021. O inner join produz dados apenas para esses 2 anos.
  - Nao interpolar valores INSE para outros anos sem justificativa metodologica.
  - Para correlacao de Pearson, usar o inner join (dados completos em ambas as fontes).
"""

import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

# ── Caminhos ────────────────────────────────────────────────────────────────────
ROOT          = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"

SINESP_FILE   = PROCESSED_DIR / "sinesp_crimes.csv"
INSE_FILE     = PROCESSED_DIR / "inep_inse.csv"

OUTPUT_LEFT   = PROCESSED_DIR / "sinesp_inse_left_join.csv"
OUTPUT_INNER  = PROCESSED_DIR / "sinesp_inse_inner_join.csv"

# Colunas-chave de merge no schema unificado (apos renomear sigla_uf -> uf no INSE)
MERGE_KEYS = ["uf", "ano"]


# ── Funcoes auxiliares ──────────────────────────────────────────────────────────

def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carrega os dois arquivos processados e normaliza os tipos das chaves."""
    for path in (SINESP_FILE, INSE_FILE):
        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo nao encontrado: {path}\n"
                "Execute o pipeline correspondente antes do merge."
            )

    sinesp = pd.read_csv(SINESP_FILE)
    sinesp["uf"]  = sinesp["uf"].astype(str).str.strip().str.upper()
    sinesp["ano"] = pd.to_numeric(sinesp["ano"], errors="coerce").astype("Int64")

    inse = pd.read_csv(INSE_FILE)
    inse = inse.rename(columns={"sigla_uf": "uf"})
    inse["uf"]  = inse["uf"].astype(str).str.strip().str.upper()
    inse["ano"] = pd.to_numeric(inse["ano"], errors="coerce").astype("Int64")

    return sinesp, inse


def report_inputs(sinesp: pd.DataFrame, inse: pd.DataFrame) -> None:
    """Imprime o diagnostico de cobertura antes do merge."""
    sinesp_anos = sorted(sinesp["ano"].dropna().unique().tolist())
    inse_anos   = sorted(inse["ano"].dropna().unique().tolist())
    overlap     = sorted(set(sinesp_anos) & set(inse_anos))

    sinesp_ufs  = sorted(sinesp["uf"].unique().tolist())
    inse_ufs    = sorted(inse["uf"].unique().tolist())
    ufs_only_sinesp = sorted(set(sinesp_ufs) - set(inse_ufs))
    ufs_only_inse   = sorted(set(inse_ufs) - set(sinesp_ufs))

    print("\n  --- Diagnostico de cobertura ---", flush=True)
    print(f"  SINESP: {len(sinesp):,} linhas | anos: {sinesp_anos} | {len(sinesp_ufs)} UFs", flush=True)
    print(f"  INSE  : {len(inse):,} linhas   | anos: {inse_anos}   | {len(inse_ufs)} UFs", flush=True)
    print(f"  Anos em comum           : {overlap}", flush=True)
    print(f"  UFs so no SINESP        : {ufs_only_sinesp if ufs_only_sinesp else 'nenhuma'}", flush=True)
    print(f"  UFs so no INSE          : {ufs_only_inse   if ufs_only_inse   else 'nenhuma'}", flush=True)


def do_merge(
    sinesp: pd.DataFrame,
    inse: pd.DataFrame,
    how: str,
) -> pd.DataFrame:
    """Executa o merge e ordena o resultado."""
    merged = sinesp.merge(inse, on=MERGE_KEYS, how=how)
    return merged.sort_values(MERGE_KEYS).reset_index(drop=True)


def validate_merge(df: pd.DataFrame, label: str, inse_cols: list[str]) -> None:
    """Imprime sumario de validacao para um DataFrame merged."""
    dupl   = df.duplicated(subset=MERGE_KEYS).sum()
    anos   = sorted(df["ano"].dropna().unique().tolist())
    n_ufs  = df["uf"].nunique()
    nulls  = df[inse_cols].isnull().any(axis=1).sum()

    print(f"\n  [{label}]", flush=True)
    print(f"    Linhas             : {len(df):,}", flush=True)
    print(f"    Duplicatas (uf+ano): {dupl}", flush=True)
    print(f"    Anos presentes     : {anos}", flush=True)
    print(f"    UFs presentes      : {n_ufs}", flush=True)
    print(f"    Linhas sem INSE    : {nulls:,}", flush=True)


# ── Pipeline principal ──────────────────────────────────────────────────────────

def run() -> tuple[pd.DataFrame, pd.DataFrame]:
    print("=" * 60, flush=True)
    print("Pipeline MERGE -- merge_sinesp_inse.py", flush=True)
    print("=" * 60, flush=True)

    sinesp, inse = load_inputs()
    report_inputs(sinesp, inse)

    inse_cols = [c for c in inse.columns if c not in MERGE_KEYS]

    print("\n  Executando left join ...", flush=True)
    left = do_merge(sinesp, inse, how="left")

    print("  Executando inner join ...", flush=True)
    inner = do_merge(sinesp, inse, how="inner")

    print("\n  --- Validacao ---", flush=True)
    validate_merge(left,  "LEFT JOIN  (sinesp_inse_left_join)", inse_cols)
    validate_merge(inner, "INNER JOIN (sinesp_inse_inner_join)", inse_cols)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    left.to_csv(OUTPUT_LEFT,  index=False, encoding="utf-8")
    inner.to_csv(OUTPUT_INNER, index=False, encoding="utf-8")

    print(f"\n  Salvo -> {OUTPUT_LEFT}", flush=True)
    print(f"  Salvo -> {OUTPUT_INNER}", flush=True)

    print("\n" + "=" * 60, flush=True)
    print("RECOMENDACAO PARA A ANALISE:", flush=True)
    print("  Correlacao de Pearson -> usar sinesp_inse_inner_join.csv", flush=True)
    print("    (apenas linhas com INSE completo: 2019 e 2021)", flush=True)
    print("  Analise temporal completa -> usar sinesp_inse_left_join.csv", flush=True)
    print("    (todos os anos do SINESP; colunas INSE serao NaN fora de 2019/2021)", flush=True)
    print("  Lembrete: calcular taxa_por_100k requer populacao do IBGE (pendente)", flush=True)
    print("=" * 60, flush=True)

    return left, inner


if __name__ == "__main__":
    run()
