"""
load_and_standardize_ibge_population.py
-----------------------------------------
Carrega o CSV municipal do IBGE (BigQuery), agrega para nivel estadual
(sigla_uf + ano) e salva em data/processed/ibge_populacao.csv.

DESCOBERTAS SOBRE OS DADOS (resultado da inspecao -- nao remover este bloco):
  - Arquivo fonte: data/raw/ibge_populacao/bq-results-pop.csv
  - Shape bruto: 55.701 linhas x 6 colunas
  - Colunas brutas: ano, sigla_uf, sigla_uf_nome, id_municipio, id_municipio_nome, populacao
  - Granularidade bruta: municipal (uma linha por municipio por ano)
  - Anos disponiveis: 2016 a 2025 (10 anos; sobreposicao total com o SINESP)
  - UFs: 27 validas + 1 linha com sigla_uf vazia (ano=2025, pop=5877) -> descartada
  - Duplicatas (uf+ano+municipio): 0
  - Nulos em populacao: 0
  - Agregacao: GROUP BY (sigla_uf, ano), SUM(populacao) -> 270 linhas esperadas

LIMITACAO CONHECIDA:
  - Dados municipais do IBGE podem ser estimativas intercensitarias para anos nao-censo.
  - Nao interpolar nem extrapolar populacao para anos fora do arquivo sem justificativa.
"""

import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

# ── Caminhos ────────────────────────────────────────────────────────────────────
ROOT          = Path(__file__).resolve().parent.parent
RAW_DIR       = ROOT / "data" / "raw" / "ibge_populacao"
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_FILE   = PROCESSED_DIR / "ibge_populacao.csv"

RAW_GLOB = "bq-results*.csv"


# ── Funcoes auxiliares ──────────────────────────────────────────────────────────

def find_raw_file() -> Path:
    """Localiza o CSV bruto usando glob. Falha se nenhum ou mais de um for encontrado."""
    files = sorted(RAW_DIR.glob(RAW_GLOB))
    if not files:
        raise FileNotFoundError(
            f"Nenhum arquivo encontrado com o padrao '{RAW_GLOB}' em {RAW_DIR}.\n"
            "Exporte o dataset de populacao do BigQuery e coloque o CSV em data/raw/ibge_populacao/."
        )
    if len(files) > 1:
        raise FileNotFoundError(
            f"Mais de um arquivo encontrado com '{RAW_GLOB}' em {RAW_DIR}:\n"
            + "\n".join(f"  {f.name}" for f in files)
            + "\nMantenha apenas o arquivo mais recente em data/raw/ibge_populacao/."
        )
    return files[0]


def load_and_aggregate(path: Path) -> tuple[pd.DataFrame, int]:
    """Carrega o CSV municipal, descarta linha sem UF e agrega para nivel estadual."""
    print(f"  Carregando {path.name} ...", flush=True)
    df = pd.read_csv(path, dtype={"id_municipio": str})
    raw_rows = len(df)
    print(f"  Linhas brutas carregadas: {raw_rows:,}", flush=True)

    # Descarta linha com sigla_uf vazia (artefato identificado na inspecao)
    antes = len(df)
    df = df[df["sigla_uf"].astype(str).str.strip() != ""].copy()
    descartadas = antes - len(df)
    if descartadas:
        print(f"  Linhas descartadas (sigla_uf vazia): {descartadas}", flush=True)

    df["sigla_uf"] = df["sigla_uf"].astype(str).str.strip().str.upper()
    df["ano"]      = pd.to_numeric(df["ano"],      errors="coerce").astype("Int64")
    df["populacao"] = pd.to_numeric(df["populacao"], errors="coerce")

    agregado = (
        df.groupby(["sigla_uf", "ano"], as_index=False)["populacao"]
        .sum()
        .rename(columns={"sigla_uf": "uf"})
    )

    print(f"  Linhas apos agregacao estadual: {len(agregado):,}", flush=True)
    return agregado, raw_rows


def validate_output(df: pd.DataFrame) -> None:
    """Verificacoes de sanidade no DataFrame final antes de salvar."""
    assert "uf"        in df.columns, "Coluna 'uf' ausente"
    assert "ano"       in df.columns, "Coluna 'ano' ausente"
    assert "populacao" in df.columns, "Coluna 'populacao' ausente"

    dupl = df.duplicated(subset=["uf", "ano"]).sum()
    assert dupl == 0, f"{dupl} duplicatas encontradas em (uf, ano)"

    nulls = df[["uf", "ano", "populacao"]].isnull().sum()
    if nulls.any():
        print("\n  ATENCAO: nulos encontrados nas colunas principais:", flush=True)
        print(nulls[nulls > 0].to_string(), flush=True)

    anos = sorted(df["ano"].dropna().unique().tolist())
    n_ufs = df["uf"].nunique()

    print("\n  Validacao concluida:", flush=True)
    print(f"    Anos presentes : {anos}", flush=True)
    print(f"    UFs presentes  : {n_ufs} UFs", flush=True)
    print(f"    Dimensoes      : {df.shape}", flush=True)
    print(f"    Colunas        : {list(df.columns)}", flush=True)
    print(f"    Duplicatas     : {dupl}", flush=True)
    print(f"    Nulos (uf, ano, populacao): {nulls.to_dict()}", flush=True)


# ── Pipeline principal ──────────────────────────────────────────────────────────

def run() -> pd.DataFrame:
    print("=" * 60, flush=True)
    print("Pipeline IBGE Populacao -- load_and_standardize_ibge_population.py", flush=True)
    print("=" * 60, flush=True)

    path = find_raw_file()
    df, raw_rows = load_and_aggregate(path)
    df = df.sort_values(["uf", "ano"]).reset_index(drop=True)

    validate_output(df)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"\n  Salvo -> {OUTPUT_FILE}", flush=True)
    print(f"\n  Resumo final:", flush=True)
    print(f"    Linhas brutas carregadas : {raw_rows:,}", flush=True)
    print(f"    Linhas apos agregacao    : {len(df):,}", flush=True)
    print(f"    Linhas salvas            : {len(df):,}", flush=True)

    print("\n" + "=" * 60, flush=True)
    print("PROXIMO PASSO (Bloco 5b):", flush=True)
    print("  Merge com sinesp_inse_inner_join.csv por (uf + ano)", flush=True)
    print("  Calcular: taxa_por_100k = crime / populacao * 100000", flush=True)
    print("=" * 60, flush=True)

    return df


if __name__ == "__main__":
    run()
