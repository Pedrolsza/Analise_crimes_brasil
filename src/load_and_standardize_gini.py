"""
load_and_standardize_gini.py
------------------------------
Padroniza o arquivo de coeficiente de Gini por UF/ano para o formato do projeto.

FONTE:
  data/raw/ibge/bq-gini_result.csv
  Colunas originais: ano, sigla_uf, sigla_uf_nome, gini
  Anos disponíveis: 2012-2025 (todos os 27 UFs, sem nulos).

TRANSFORMACOES:
  - Renomeia sigla_uf -> uf para compatibilidade com as chaves de join do projeto.
  - Filtra para os anos do projeto (2016-2026). 2026 nao tem dado disponivel -> ausente.
  - Descarta sigla_uf_nome (informacao redundante com dim_uf).
  - Ordena por (uf, ano).

SAIDA:
  data/processed/ibge_gini.csv
  Colunas: uf (str), ano (int), gini (float)

JOIN:
  Merge com outras tabelas por (uf, ano).
"""

from pathlib import Path

import pandas as pd

ROOT     = Path(__file__).resolve().parent.parent
RAW_FILE = ROOT / "data" / "raw" / "ibge" / "bq-gini_result.csv"
OUT_FILE = ROOT / "data" / "processed" / "ibge_gini.csv"

# Anos do projeto (filtro de relevancia)
ANOS_PROJETO = set(range(2016, 2027))


def run() -> None:
    print("=" * 60, flush=True)
    print("Pipeline GINI -- load_and_standardize_gini.py", flush=True)
    print("=" * 60, flush=True)

    df = pd.read_csv(RAW_FILE)
    print(f"  Raw shape: {df.shape} | colunas: {list(df.columns)}", flush=True)

    # Renomear para padrao do projeto
    df = df.rename(columns={"sigla_uf": "uf"})

    # Filtrar anos relevantes ao projeto
    df = df[df["ano"].isin(ANOS_PROJETO)].copy()

    # Manter apenas colunas necessarias
    df = df[["uf", "ano", "gini"]].copy()

    df["uf"]  = df["uf"].astype(str).str.strip().str.upper()
    df["ano"] = df["ano"].astype(int)
    df = df.sort_values(["uf", "ano"]).reset_index(drop=True)

    # Validacao
    print(f"\n  Shape           : {df.shape}", flush=True)
    print(f"  Anos presentes  : {sorted(df['ano'].unique().tolist())}", flush=True)
    print(f"  UFs presentes   : {df['uf'].nunique()}", flush=True)
    print(f"  Nulos em gini   : {df['gini'].isna().sum()}", flush=True)
    print(f"\n  Amostra:\n{df.head(10).to_string(index=False)}", flush=True)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False, encoding="utf-8")
    print(f"\n  Salvo -> {OUT_FILE}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    run()
