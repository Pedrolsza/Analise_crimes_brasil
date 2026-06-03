"""
build_powerbi_dataset.py
-------------------------
Monta o arquivo mestre data/processed/powerbi_dataset.csv a partir dos
arquivos intermediarios processados, tornando o pipeline completamente
reproduzivel.

ENTRADAS:
  data/processed/sinesp_inse_pop_left_join.csv  -- todos os anos SINESP + INSE (NaN fora de 2019/2021) + populacao
  data/processed/sinesp_inse_pop_clusters.csv   -- 54 linhas (2019/2021) com cluster_id e perfil
  data/processed/ibge_percapita.csv             -- renda per capita anual por UF (2016-2024, sem 2020)
  data/processed/ibge_desocupacao.csv           -- taxa de desemprego anual por UF (2018-2025)
  data/processed/ibge_gini.csv                  -- coeficiente de Gini anual por UF (2016-2025)
  data/processed/ibge_area.csv                  -- area territorial em km2 por UF (estatica, sem ano)

SAIDA:
  data/processed/powerbi_dataset.csv            -- 297 linhas (27 UFs x 11 anos)

COLUNAS ADICIONADAS:
  fonte_crime          : "SINESP" (constante)
  cobertura_inse       : "sim" se o ano/UF tem dados INSE, "nao" caso contrario
  renda_per_capita     : rendimento medio mensal real domiciliar per capita (R$)
  taxa_desemprego      : taxa de desocupacao media anual (%)
  gini                 : coeficiente de Gini
  area_km2             : area territorial do estado em km2 (replicada por todos os anos)
  densidade_demografica: populacao / area_km2 (derivada, hab/km2)

DECISAO DE DESIGN:
  - Left join: todos os 297 pares UF-ano sao preservados.
  - cluster_id e perfil ficam NaN para linhas sem INSE (2016-2018, 2020, 2022-2026).
  - O arquivo de entrada left_join ja carrega todas as colunas de crimes,
    populacao, taxas e INSE. Este script apenas adiciona metadados de cluster,
    flags de cobertura e variaveis socioeconomicas externas.
  - Nulos nas novas colunas sao mantidos explicitamente (nao ha imputacao).
"""

import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

ROOT         = Path(__file__).resolve().parent.parent
PROCESSED    = ROOT / "data" / "processed"

LEFT_JOIN_FILE   = PROCESSED / "sinesp_inse_pop_left_join.csv"
CLUSTERS_FILE    = PROCESSED / "sinesp_inse_pop_clusters.csv"
OUTPUT_FILE      = PROCESSED / "powerbi_dataset.csv"

# Novos arquivos socioeconomicos e geograficos (IBGE)
PERCAPITA_FILE   = PROCESSED / "ibge_percapita.csv"
DESOCUPACAO_FILE = PROCESSED / "ibge_desocupacao.csv"
GINI_FILE        = PROCESSED / "ibge_gini.csv"
AREA_FILE        = PROCESSED / "ibge_area.csv"

MERGE_KEYS = ["uf", "ano"]


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    for path in (LEFT_JOIN_FILE, CLUSTERS_FILE):
        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo nao encontrado: {path}\n"
                "Execute os pipelines anteriores (SINESP -> INSE -> IBGE -> clusters) antes."
            )

    left = pd.read_csv(LEFT_JOIN_FILE)
    left["uf"]  = left["uf"].astype(str).str.strip().str.upper()
    left["ano"] = pd.to_numeric(left["ano"], errors="coerce").astype(int)

    clusters = pd.read_csv(CLUSTERS_FILE)
    clusters["uf"]  = clusters["uf"].astype(str).str.strip().str.upper()
    clusters["ano"] = pd.to_numeric(clusters["ano"], errors="coerce").astype(int)

    print(f"  left_join carregado : {len(left):,} linhas | {len(left.columns)} colunas", flush=True)
    print(f"  clusters carregado  : {len(clusters):,} linhas", flush=True)
    return left, clusters


def load_socio_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Carrega os arquivos socioeconomicos e geograficos gerados pelos pipelines IBGE."""
    missing = [p for p in (PERCAPITA_FILE, DESOCUPACAO_FILE, GINI_FILE, AREA_FILE) if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Arquivos IBGE ausentes:\n" + "\n".join(f"  {p}" for p in missing) +
            "\nExecute os pipelines IBGE (percapita, desocupacao, gini, area) antes."
        )

    percapita   = pd.read_csv(PERCAPITA_FILE)
    desocupacao = pd.read_csv(DESOCUPACAO_FILE)
    gini        = pd.read_csv(GINI_FILE)
    area        = pd.read_csv(AREA_FILE)

    for df_s in (percapita, desocupacao, gini):
        df_s["uf"]  = df_s["uf"].astype(str).str.strip().str.upper()
        df_s["ano"] = pd.to_numeric(df_s["ano"], errors="coerce").astype(int)

    area["uf"] = area["uf"].astype(str).str.strip().str.upper()

    print(f"  percapita carregado  : {len(percapita):,} linhas", flush=True)
    print(f"  desocupacao carregado: {len(desocupacao):,} linhas", flush=True)
    print(f"  gini carregado       : {len(gini):,} linhas", flush=True)
    print(f"  area carregado       : {len(area):,} linhas", flush=True)
    return percapita, desocupacao, gini, area


def build_dataset(left: pd.DataFrame, clusters: pd.DataFrame) -> pd.DataFrame:
    # Keep only the cluster metadata columns — everything else comes from left_join
    cluster_cols = MERGE_KEYS + [c for c in ["cluster_id", "perfil"] if c in clusters.columns]
    cluster_meta = clusters[cluster_cols].drop_duplicates(subset=MERGE_KEYS)

    df = left.merge(cluster_meta, on=MERGE_KEYS, how="left")

    df["fonte_crime"]    = "SINESP"
    df["cobertura_inse"] = df["inse"].notna().map({True: "sim", False: "nao"})

    # Carregar e integrar variaveis socioeconomicas e geograficas (IBGE)
    percapita, desocupacao, gini, area = load_socio_inputs()

    # Left joins: preserva todos os 297 pares UF-ano; nulos onde dados ausentes
    df = df.merge(percapita[["uf", "ano", "renda_per_capita"]],  on=MERGE_KEYS, how="left")
    df = df.merge(desocupacao[["uf", "ano", "taxa_desemprego"]], on=MERGE_KEYS, how="left")
    df = df.merge(gini[["uf", "ano", "gini"]],                  on=MERGE_KEYS, how="left")
    # Area nao tem coluna ano: merge apenas por UF, replica o valor para todos os anos
    df = df.merge(area[["uf", "area_km2"]],                     on="uf",       how="left")

    # Derivar densidade demografica: populacao (IBGE) / area_km2
    # Ficara nulo onde populacao for nula (ano 2026) ou area for nula (nao esperado)
    df["densidade_demografica"] = df["populacao"] / df["area_km2"]

    df = df.sort_values(MERGE_KEYS).reset_index(drop=True)
    return df


def validate(df: pd.DataFrame) -> None:
    print("\n  --- Validacao ---", flush=True)
    dupl = df.duplicated(subset=MERGE_KEYS).sum()
    print(f"  Linhas             : {len(df):,}", flush=True)
    print(f"  Duplicatas (uf+ano): {dupl}", flush=True)
    print(f"  Anos presentes     : {sorted(df['ano'].unique().tolist())}", flush=True)
    print(f"  UFs presentes      : {df['uf'].nunique()}", flush=True)
    print(f"  Colunas            : {list(df.columns)}", flush=True)

    # Gender column check
    gender_cols = [c for c in df.columns if any(c.endswith(s) for s in ("_feminino", "_masculino", "_nao_informado"))]
    print(f"  Colunas de genero  : {gender_cols}", flush=True)

    # Integrity check: gender sums == total for each crime
    for crime in ["estupro", "estupro_vulneravel"]:
        fem  = f"{crime}_feminino"
        masc = f"{crime}_masculino"
        nao  = f"{crime}_nao_informado"
        if all(c in df.columns for c in [fem, masc, nao, crime]):
            total_gender = df[fem] + df[masc] + df[nao]
            mismatch = (total_gender != df[crime]).sum()
            print(f"  [{crime}] genero sum != total: {mismatch} linhas", flush=True)

    nulls_cluster = df["cluster_id"].isna().sum() if "cluster_id" in df.columns else "N/A"
    print(f"  Linhas sem cluster : {nulls_cluster} (esperado: 243 = 27 UFs x 9 anos sem INSE)", flush=True)

    # Nulos esperados nas novas colunas socioeconomicas e geograficas
    socio_cols = ["renda_per_capita", "taxa_desemprego", "gini", "area_km2", "densidade_demografica"]
    print(f"\n  --- Nulos colunas socioeconomicas ---", flush=True)
    for col in socio_cols:
        if col in df.columns:
            n = df[col].isna().sum()
            print(f"  {col}: {n} nulos", flush=True)

    if dupl > 0:
        raise AssertionError(f"Duplicatas encontradas: {dupl}. Verificar entradas.")


def run() -> pd.DataFrame:
    print("=" * 60, flush=True)
    print("Pipeline POWERBI DATASET -- build_powerbi_dataset.py", flush=True)
    print("=" * 60, flush=True)

    left, clusters = load_inputs()
    print("\nCarregando arquivos socioeconomicos IBGE ...", flush=True)
    df = build_dataset(left, clusters)
    validate(df)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"\n  Salvo -> {OUTPUT_FILE}", flush=True)
    print("=" * 60, flush=True)
    return df


if __name__ == "__main__":
    run()
