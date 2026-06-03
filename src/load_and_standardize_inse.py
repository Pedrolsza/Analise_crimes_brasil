"""
load_and_standardize_inse.py
-----------------------------
Carrega o arquivo CSV exportado do BigQuery com dados do INEP INSE,
filtra para o agregado estadual e salva em data/processed/inep_inse.csv.

DESCOBERTAS SOBRE OS DADOS (resultado da inspecao -- nao remover este bloco):
  - Arquivo fonte: data/raw/inep_inse/bq-results*.csv (exportacao BigQuery)
  - Shape bruto: 3.402 linhas x 16 colunas
  - Granularidade bruta: (sigla_uf, ano, rede, area, tipo_localizacao)
    Cada combinacao gera multiplas linhas -- nao e 1 linha por UF/ano.
  - Anos disponiveis: 2019 e 2021 apenas (nao ha serie continua)
  - UFs: todas as 27 UFs presentes em ambos os anos
  - Filtro correto para agregado estadual (1 linha por UF/ano):
      rede            == "Total (Federal, Estadual, Municipal e Privada)"
      area            == "Total (Capital e Interior)"
      tipo_localizacao == "Total (Urbana e Rural)"
  - Apos filtro: 54 linhas, 0 duplicatas, 0 nulos nas colunas principais
  - Colunas percentual_nivel_* tem nulos no dataset bruto mas nao no agregado total
  - Coluna `sigla_uf_nome` contem o nome por extenso -- descartada (join feito por sigla_uf)
  - Colunas `rede`, `area`, `tipo_localizacao` descartadas apos filtro (constantes no output)

LIMITACAO IMPORTANTE PARA A ANALISE:
  - INSE so cobre 2019 e 2021.
  - O merge com sinesp_crimes.csv (2016-2026) produzira apenas 2 anos de dados pareados.
  - Nao interpolar nem extrapolar os valores de INSE para outros anos sem justificativa metodologica.
"""

import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

# ── Caminhos ────────────────────────────────────────────────────────────────────
ROOT          = Path(__file__).resolve().parent.parent
RAW_DIR       = ROOT / "data" / "raw" / "inep_inse"
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_FILE   = PROCESSED_DIR / "inep_inse.csv"

# ── Configuracao ────────────────────────────────────────────────────────────────

# Padrao de glob para localizar o CSV exportado do BigQuery sem depender do nome exato.
# O INEP nao garante nome fixo em re-exportacoes.
RAW_GLOB = "bq-results*.csv"

# Filtros que selecionam exatamente 1 linha por (sigla_uf, ano): o agregado estadual completo.
# Qualquer outra combinacao representa um subgrupo (por rede, area ou localizacao).
FILTER_REDE             = "Total (Federal, Estadual, Municipal e Privada)"
FILTER_AREA             = "Total (Capital e Interior)"
FILTER_TIPO_LOCALIZACAO = "Total (Urbana e Rural)"

# Colunas retidas no arquivo processado -- apenas o que e util para o merge e analise.
COLS_KEEP = [
    "ano",
    "sigla_uf",
    "inse",
    "quantidade_alunos_inse",
    "percentual_nivel_1",
    "percentual_nivel_2",
    "percentual_nivel_3",
    "percentual_nivel_4",
    "percentual_nivel_5",
    "percentual_nivel_6",
    "percentual_nivel_7",
    "percentual_nivel_8",
]

# Colunas que devem ser numericas no output.
COLS_NUMERIC = [c for c in COLS_KEEP if c not in ("ano", "sigla_uf")]


# ── Funcoes auxiliares ──────────────────────────────────────────────────────────

def find_raw_file() -> Path:
    """Localiza o arquivo CSV bruto usando glob. Falha se nenhum ou mais de um for encontrado."""
    files = sorted(RAW_DIR.glob(RAW_GLOB))
    if not files:
        raise FileNotFoundError(
            f"Nenhum arquivo encontrado com o padrao '{RAW_GLOB}' em {RAW_DIR}.\n"
            "Exporte o dataset INSE do BigQuery e coloque o CSV em data/raw/inep_inse/."
        )
    if len(files) > 1:
        raise FileNotFoundError(
            f"Mais de um arquivo encontrado com '{RAW_GLOB}' em {RAW_DIR}:\n"
            + "\n".join(f"  {f.name}" for f in files)
            + "\nMantenha apenas o arquivo mais recente em data/raw/inep_inse/."
        )
    return files[0]


def load_raw(path: Path) -> pd.DataFrame:
    """Carrega o CSV bruto e aplica o filtro de agregado estadual."""
    print(f"  Carregando {path.name} ...", flush=True)
    df = pd.read_csv(path)
    raw_rows = len(df)
    print(f"  Linhas brutas carregadas: {raw_rows:,}", flush=True)

    filtered = df[
        (df["rede"]             == FILTER_REDE) &
        (df["area"]             == FILTER_AREA) &
        (df["tipo_localizacao"] == FILTER_TIPO_LOCALIZACAO)
    ].copy()

    print(f"  Linhas apos filtro de agregado estadual: {len(filtered):,}", flush=True)
    return filtered, raw_rows


def select_and_coerce(df: pd.DataFrame) -> pd.DataFrame:
    """Seleciona as colunas uteis e converte tipos numericos de forma segura."""
    missing = [c for c in COLS_KEEP if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas esperadas ausentes no arquivo bruto: {missing}")

    df = df[COLS_KEEP].copy()
    df["ano"]      = pd.to_numeric(df["ano"],      errors="coerce").astype("Int64")
    df["sigla_uf"] = df["sigla_uf"].astype(str).str.strip().str.upper()

    for col in COLS_NUMERIC:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def validate_output(df: pd.DataFrame) -> None:
    """Verificacoes de sanidade no DataFrame final antes de salvar."""
    assert "ano"      in df.columns, "Coluna 'ano' ausente"
    assert "sigla_uf" in df.columns, "Coluna 'sigla_uf' ausente"

    dupl = df.duplicated(subset=["sigla_uf", "ano"]).sum()
    assert dupl == 0, f"{dupl} duplicatas encontradas em (sigla_uf, ano)"

    nulls_key = df[["ano", "sigla_uf", "inse", "quantidade_alunos_inse"]].isnull().sum()
    if nulls_key.any():
        print("\n  ATENCAO: nulos encontrados nas colunas principais:", flush=True)
        print(nulls_key[nulls_key > 0].to_string(), flush=True)

    print("\n  Validacao concluida:", flush=True)
    print(f"    Anos presentes : {sorted(df['ano'].dropna().unique().tolist())}", flush=True)
    print(f"    UFs presentes  : {df['sigla_uf'].nunique()} UFs", flush=True)
    print(f"    Dimensoes      : {df.shape}", flush=True)
    print(f"    Colunas        : {list(df.columns)}", flush=True)
    print(f"    Duplicatas     : {dupl}", flush=True)
    print(f"    Nulos (ano, sigla_uf, inse, qtd_alunos):", flush=True)
    print(f"      {nulls_key.to_dict()}", flush=True)


# ── Pipeline principal ──────────────────────────────────────────────────────────

def run() -> pd.DataFrame:
    print("=" * 60, flush=True)
    print("Pipeline INSE -- load_and_standardize_inse.py", flush=True)
    print("=" * 60, flush=True)

    path = find_raw_file()

    df_filtered, raw_rows = load_raw(path)
    df = select_and_coerce(df_filtered)
    df = df.sort_values(["sigla_uf", "ano"]).reset_index(drop=True)

    validate_output(df)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"\n  Salvo -> {OUTPUT_FILE}", flush=True)
    print(f"\n  Resumo final:", flush=True)
    print(f"    Linhas brutas carregadas : {raw_rows:,}", flush=True)
    print(f"    Linhas apos filtro       : {len(df):,}", flush=True)
    print(f"    Linhas salvas            : {len(df):,}", flush=True)

    print("\n" + "=" * 60, flush=True)
    print("OBSERVACAO IMPORTANTE PARA O MERGE:", flush=True)
    print("  INSE disponivel apenas para 2019 e 2021.", flush=True)
    print("  O merge com sinesp_crimes.csv produzira apenas esses 2 anos.", flush=True)
    print("  Chave de merge: sigla_uf + ano", flush=True)
    print("  (sinesp usa coluna 'uf'; renomear para 'sigla_uf' antes do merge", flush=True)
    print("   ou renomear 'sigla_uf' para 'uf' neste output -- decidir na etapa de merge)", flush=True)
    print("=" * 60, flush=True)

    return df


if __name__ == "__main__":
    run()
