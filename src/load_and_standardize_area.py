"""
load_and_standardize_area.py
------------------------------
Padroniza o arquivo de area territorial por UF para o formato do projeto.

FONTE:
  data/raw/ibge/bq-area_result.csv
  Colunas originais: ano, sigla_uf, sigla_uf_nome, area_km2
  Unico ano disponivel: 2025 (area territorial e considerada estatica para fins do projeto).

TRANSFORMACOES:
  - Area territorial e estavel ao longo do tempo (limites estaduais nao mudam de ano para ano).
    Por isso, replicamos o unico valor disponivel (2025) para todos os anos do projeto,
    omitindo a coluna ano no output -- o merge com a tabela principal deve ser feito apenas por uf.
  - Renomeia sigla_uf -> uf.
  - Descarta sigla_uf_nome e ano.

SAIDA:
  data/processed/ibge_area.csv
  Colunas: uf (str), area_km2 (float) -- 27 linhas, SEM coluna ano.

JOIN:
  Merge com outras tabelas por uf APENAS (sem ano), replicando a area para todos os anos.
"""

from pathlib import Path

import pandas as pd

ROOT     = Path(__file__).resolve().parent.parent
RAW_FILE = ROOT / "data" / "raw" / "ibge" / "bq-area_result.csv"
OUT_FILE = ROOT / "data" / "processed" / "ibge_area.csv"


def run() -> None:
    print("=" * 60, flush=True)
    print("Pipeline AREA -- load_and_standardize_area.py", flush=True)
    print("=" * 60, flush=True)

    df = pd.read_csv(RAW_FILE)
    print(f"  Raw shape: {df.shape} | colunas: {list(df.columns)}", flush=True)
    print(f"  Anos no raw: {sorted(df['ano'].unique().tolist())} (esperado: [2025])", flush=True)

    # Renomear para padrao do projeto
    df = df.rename(columns={"sigla_uf": "uf"})

    # Apenas as colunas necessarias -- sem ano, pois area e estatica
    df = df[["uf", "area_km2"]].copy()
    df["uf"] = df["uf"].astype(str).str.strip().str.upper()
    df = df.sort_values("uf").reset_index(drop=True)

    # Validacao
    print(f"\n  Shape           : {df.shape} (esperado: (27, 2))", flush=True)
    print(f"  UFs presentes   : {df['uf'].nunique()}", flush=True)
    print(f"  Nulos em area   : {df['area_km2'].isna().sum()}", flush=True)
    print(f"  Min area_km2    : {df['area_km2'].min():,.3f}", flush=True)
    print(f"  Max area_km2    : {df['area_km2'].max():,.3f}", flush=True)
    print(f"\n  Amostra:\n{df.head(10).to_string(index=False)}", flush=True)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False, encoding="utf-8")
    print(f"\n  Salvo -> {OUT_FILE}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    run()
