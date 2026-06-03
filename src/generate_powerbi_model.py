"""
generate_powerbi_model.py
--------------------------
Gera os arquivos CSV do modelo de dados Power BI em esquema estrela (galaxy schema)
a partir do arquivo mestre data/processed/powerbi_dataset.csv.

ARQUIVOS GERADOS em data/powerbi/:
  dim_uf.csv          -- 27 linhas  | UF, nome completo, regiao
  dim_ano.csv         -- 11 linhas  | ano, flags de cobertura, agrupamento de periodo
  dim_cluster.csv     --  3 linhas  | cluster_id, perfil, ordem de risco
  fact_crimes.csv     -- 297 linhas | crimes + populacao + taxas + socioeconomico por UF/ano
  fact_inse.csv       --  54 linhas | INSE + niveis + cluster (apenas 2019 e 2021)

COLUNAS SOCIOECONOMICAS em fact_crimes (podem ter nulos onde dados ausentes):
  renda_per_capita     -- rendimento medio mensal real (R$), SIDRA 7395 (sem 2020, sem 2025/2026)
  taxa_desemprego      -- taxa de desocupacao media anual (%), SIDRA 4093 (2018-2025)
  gini                 -- coeficiente de Gini, IBGE (2016-2025, sem 2026)
  area_km2             -- area territorial km2 (estatica, 2025 replicada)
  densidade_demografica-- populacao / area_km2 (derivada; nula em 2026)

DECISOES DE DESIGN:
  - O arquivo data/processed/powerbi_dataset.csv NAO e modificado.
  - Todos os arquivos de saida sao codificados como UTF-8 com BOM (utf-8-sig)
    para garantir deteccao correta de encoding no Power BI Desktop no Windows.
  - Separador de campo : ponto-e-virgula (;) -- locale brasileiro
  - Separador decimal  : virgula (,)         -- locale brasileiro
  - fact_inse.csv contem APENAS linhas onde INSE existe (zero nulos nas colunas INSE).
  - fact_crimes.csv contem TODAS as 297 combinacoes UF-ano (2016-2026).
  - dim_uf.csv e enriquecida com nome completo e regiao a partir de dicionario interno
    (nao requer arquivo externo).
  - cluster_id -1 NAO e inserido como linha em dim_cluster; o Power BI trata a FK nula
    em fact_inse como ausencia de cluster (linhas sem INSE nao aparecem em fact_inse).

RELACIONAMENTOS ESPERADOS NO POWER BI:
  fact_crimes[uf]          -> dim_uf[uf]          (N:1, filtro simples)
  fact_crimes[ano]         -> dim_ano[ano]         (N:1, filtro simples)
  fact_inse[uf]            -> dim_uf[uf]           (N:1, filtro simples)
  fact_inse[ano]           -> dim_ano[ano]         (N:1, filtro simples)
  fact_inse[cluster_id]    -> dim_cluster[cluster_id] (N:1, filtro simples)
"""

import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

# ── Caminhos ─────────────────────────────────────────────────────────────────────
ROOT         = Path(__file__).resolve().parent.parent
PROCESSED    = ROOT / "data" / "processed"
POWERBI_DIR  = ROOT / "data" / "powerbi"
SOURCE_FILE  = PROCESSED / "powerbi_dataset.csv"

ENCODING  = "utf-8-sig"  # UTF-8 com BOM -- detectado automaticamente pelo Power BI no Windows
SEP       = ";"          # ponto-e-virgula: padrao CSV brasileiro
DECIMAL   = ","          # virgula como separador decimal: locale pt-BR

# ── Dicionario de enriquecimento de UF ───────────────────────────────────────────
UF_META: dict[str, dict] = {
    "AC": {"nome_uf": "Acre",                  "regiao": "Norte"},
    "AL": {"nome_uf": "Alagoas",               "regiao": "Nordeste"},
    "AM": {"nome_uf": "Amazonas",              "regiao": "Norte"},
    "AP": {"nome_uf": "Amapa",                 "regiao": "Norte"},
    "BA": {"nome_uf": "Bahia",                 "regiao": "Nordeste"},
    "CE": {"nome_uf": "Ceara",                 "regiao": "Nordeste"},
    "DF": {"nome_uf": "Distrito Federal",      "regiao": "Centro-Oeste"},
    "ES": {"nome_uf": "Espirito Santo",        "regiao": "Sudeste"},
    "GO": {"nome_uf": "Goias",                 "regiao": "Centro-Oeste"},
    "MA": {"nome_uf": "Maranhao",              "regiao": "Nordeste"},
    "MG": {"nome_uf": "Minas Gerais",          "regiao": "Sudeste"},
    "MS": {"nome_uf": "Mato Grosso do Sul",    "regiao": "Centro-Oeste"},
    "MT": {"nome_uf": "Mato Grosso",           "regiao": "Centro-Oeste"},
    "PA": {"nome_uf": "Para",                  "regiao": "Norte"},
    "PB": {"nome_uf": "Paraiba",               "regiao": "Nordeste"},
    "PE": {"nome_uf": "Pernambuco",            "regiao": "Nordeste"},
    "PI": {"nome_uf": "Piaui",                 "regiao": "Nordeste"},
    "PR": {"nome_uf": "Parana",                "regiao": "Sul"},
    "RJ": {"nome_uf": "Rio de Janeiro",        "regiao": "Sudeste"},
    "RN": {"nome_uf": "Rio Grande do Norte",   "regiao": "Nordeste"},
    "RO": {"nome_uf": "Rondonia",              "regiao": "Norte"},
    "RR": {"nome_uf": "Roraima",               "regiao": "Norte"},
    "RS": {"nome_uf": "Rio Grande do Sul",     "regiao": "Sul"},
    "SC": {"nome_uf": "Santa Catarina",        "regiao": "Sul"},
    "SE": {"nome_uf": "Sergipe",               "regiao": "Nordeste"},
    "SP": {"nome_uf": "Sao Paulo",             "regiao": "Sudeste"},
    "TO": {"nome_uf": "Tocantins",             "regiao": "Norte"},
}

# Ordem de exibicao das regioes nos visuais do Power BI (usada em dim_ano.periodo)
PERIODO_MAP: dict[int, str] = {
    2016: "2016-2018",
    2017: "2016-2018",
    2018: "2016-2018",
    2019: "2019-2021",
    2020: "2019-2021",
    2021: "2019-2021",
    2022: "2022-2026",
    2023: "2022-2026",
    2024: "2022-2026",
    2025: "2022-2026",
    2026: "2022-2026",
}

# Anos com dados INSE (ajustar se novos anos forem adicionados ao dataset INEP)
ANOS_COM_INSE = {2019, 2021}

# Anos com dados de populacao IBGE (2026 ainda sem estimativa)
ANOS_SEM_POPULACAO = {2026}

NIVEL_COLS = [f"percentual_nivel_{i}" for i in range(1, 9)]

GENDER_COLS = [
    "estupro_feminino",            "estupro_masculino",            "estupro_nao_informado",
    "estupro_vulneravel_feminino", "estupro_vulneravel_masculino", "estupro_vulneravel_nao_informado",
]

SOCIO_COLS = [
    "renda_per_capita", "taxa_desemprego", "gini", "area_km2", "densidade_demografica",
]


# ── Funcoes auxiliares ────────────────────────────────────────────────────────────

def load_source() -> pd.DataFrame:
    """Carrega e faz coercao de tipos no arquivo mestre."""
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Arquivo mestre nao encontrado: {SOURCE_FILE}\n"
            "Execute o pipeline completo (SINESP -> INSE -> IBGE -> clusters) antes."
        )

    df = pd.read_csv(SOURCE_FILE)
    df["uf"]  = df["uf"].astype(str).str.strip().str.upper()
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype(int)

    for col in ["estupro", "estupro_vulneravel"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    for col in ["populacao", "taxa_estupro_por_100k", "taxa_estupro_vulneravel_por_100k",
                "inse", "quantidade_alunos_inse"] + NIVEL_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "cluster_id" in df.columns:
        df["cluster_id"] = pd.to_numeric(df["cluster_id"], errors="coerce")

    for col in SOCIO_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    print(f"  Fonte carregada: {len(df):,} linhas | {len(df.columns)} colunas", flush=True)
    return df


def build_dim_uf(df: pd.DataFrame) -> pd.DataFrame:
    """Dimensao UF: 27 estados com nome completo e regiao."""
    ufs = sorted(df["uf"].unique())
    missing = [u for u in ufs if u not in UF_META]
    if missing:
        raise ValueError(f"UFs sem metadados no dicionario UF_META: {missing}")

    rows = [{"uf": u, **UF_META[u]} for u in ufs]
    dim = pd.DataFrame(rows)[["uf", "nome_uf", "regiao"]]
    return dim


def build_dim_ano(df: pd.DataFrame) -> pd.DataFrame:
    """Dimensao ano: flags de cobertura e agrupamento de periodo."""
    anos = sorted(df["ano"].unique())
    rows = []
    for ano in anos:
        rows.append({
            "ano":             ano,
            "tem_populacao":   ano not in ANOS_SEM_POPULACAO,
            "tem_inse":        ano in ANOS_COM_INSE,
            "periodo":         PERIODO_MAP.get(ano, str(ano)),
        })
    dim = pd.DataFrame(rows)
    # Converter booleanos para inteiro (0/1) -- mais simples no Power BI como campo de filtro
    dim["tem_populacao"] = dim["tem_populacao"].astype(int)
    dim["tem_inse"]      = dim["tem_inse"].astype(int)
    return dim


def build_dim_cluster(df: pd.DataFrame) -> pd.DataFrame:
    """Dimensao cluster: mapeamento de ID para perfil e ordenacao de risco."""
    mask = df["cluster_id"].notna()
    pairs = (
        df[mask][["cluster_id", "perfil"]]
        .drop_duplicates()
        .copy()
    )
    pairs["cluster_id"] = pairs["cluster_id"].astype(int)
    pairs = pairs.sort_values("cluster_id").reset_index(drop=True)

    # ordem_risco: permite ordenar corretamente em visuais do Power BI
    # 0=Alto -> 1 (mais grave), 1=Baixo -> 2, 2=Atipico -> 3
    ORDEM = {0: 1, 1: 2, 2: 3}
    pairs["ordem_risco"] = pairs["cluster_id"].map(ORDEM)

    return pairs[["cluster_id", "perfil", "ordem_risco"]]


def build_fact_crimes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tabela fato de crimes: uma linha por UF-ano (297 linhas).
    Contem contagens, populacao e taxas. Campo cobertura_inse indica
    se o ano/UF possui dados INSE correspondentes em fact_inse.
    """
    cols = [
        "uf",
        "ano",
        "estupro",
        "estupro_vulneravel",
        "populacao",
        "taxa_estupro_por_100k",
        "taxa_estupro_vulneravel_por_100k",
        "cobertura_inse",
        "fonte_crime",
    ] + [c for c in GENDER_COLS if c in df.columns] + [c for c in SOCIO_COLS if c in df.columns]
    fact = df[cols].copy()

    # Normalizar cobertura_inse para inteiro (0/1)
    fact["cobertura_inse"] = (
        fact["cobertura_inse"]
        .astype(str)
        .str.lower()
        .str.strip()
        .map({"sim": 1, "nao": 0, "1": 1, "0": 0, "true": 1, "false": 0})
        .fillna(0)
        .astype(int)
    )

    fact = fact.sort_values(["uf", "ano"]).reset_index(drop=True)
    return fact


def build_fact_inse(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tabela fato INSE: apenas linhas com dados INSE completos (54 linhas).
    Contem INSE, distribuicao de niveis e cluster. Zero nulos nas colunas INSE.
    """
    inse_mask = df["inse"].notna()
    sub = df[inse_mask].copy()

    cols = (
        ["uf", "ano", "cluster_id", "inse", "quantidade_alunos_inse"]
        + NIVEL_COLS
    )
    fact = sub[cols].copy()
    fact["cluster_id"]          = fact["cluster_id"].astype(int)
    fact["quantidade_alunos_inse"] = fact["quantidade_alunos_inse"].astype(int)
    fact = fact.sort_values(["uf", "ano"]).reset_index(drop=True)
    return fact


def save(df: pd.DataFrame, path: Path, label: str) -> None:
    """Salva um DataFrame como CSV UTF-8-BOM com separador ; e decimal ,  (locale pt-BR)."""
    df.to_csv(path, index=False, encoding=ENCODING, sep=SEP, decimal=DECIMAL)
    print(f"  Salvo -> {path.relative_to(ROOT)} ({len(df):,} linhas)", flush=True)


# ── Validacao ─────────────────────────────────────────────────────────────────────

def validate_all(
    dim_uf:      pd.DataFrame,
    dim_ano:     pd.DataFrame,
    dim_cluster: pd.DataFrame,
    fact_crimes: pd.DataFrame,
    fact_inse:   pd.DataFrame,
    source:      pd.DataFrame,
) -> None:
    print("\n" + "-" * 60, flush=True)
    print("VALIDACAO", flush=True)
    print("-" * 60, flush=True)

    errors: list[str] = []

    # ── Contagens esperadas ──────────────────────────────────────────────────────
    def check(label, actual, expected):
        status = "OK" if actual == expected else "FALHA"
        print(f"  [{status}] {label}: {actual} (esperado: {expected})", flush=True)
        if status == "FALHA":
            errors.append(f"{label}: {actual} != {expected}")

    check("dim_uf linhas",      len(dim_uf),      27)
    check("dim_ano linhas",     len(dim_ano),      11)
    check("dim_cluster linhas", len(dim_cluster),   3)
    check("fact_crimes linhas", len(fact_crimes), 297)
    check("fact_inse linhas",   len(fact_inse),    54)

    # ── Chaves primarias unicas ──────────────────────────────────────────────────
    def check_pk(label, df, cols):
        dupl = df.duplicated(subset=cols).sum()
        status = "OK" if dupl == 0 else "FALHA"
        print(f"  [{status}] {label} duplicatas: {dupl}", flush=True)
        if dupl:
            errors.append(f"{label}: {dupl} duplicatas em {cols}")

    check_pk("dim_uf PK",       dim_uf,      ["uf"])
    check_pk("dim_ano PK",      dim_ano,     ["ano"])
    check_pk("dim_cluster PK",  dim_cluster, ["cluster_id"])
    check_pk("fact_crimes PK",  fact_crimes, ["uf", "ano"])
    check_pk("fact_inse PK",    fact_inse,   ["uf", "ano"])

    # ── Integridade referencial ──────────────────────────────────────────────────
    def check_fk(label, fk_vals, pk_vals):
        orphans = set(fk_vals) - set(pk_vals)
        status = "OK" if not orphans else "FALHA"
        print(f"  [{status}] {label} orfaos: {len(orphans)}", flush=True)
        if orphans:
            errors.append(f"{label}: {len(orphans)} FKs sem correspondencia -> {orphans}")

    check_fk("fact_crimes[uf] -> dim_uf",          fact_crimes["uf"],         dim_uf["uf"])
    check_fk("fact_crimes[ano] -> dim_ano",         fact_crimes["ano"],        dim_ano["ano"])
    check_fk("fact_inse[uf] -> dim_uf",             fact_inse["uf"],           dim_uf["uf"])
    check_fk("fact_inse[ano] -> dim_ano",           fact_inse["ano"],          dim_ano["ano"])
    check_fk("fact_inse[cluster_id] -> dim_cluster", fact_inse["cluster_id"], dim_cluster["cluster_id"])

    # ── Nulos em fact_inse (deve ser zero em colunas INSE) ───────────────────────
    inse_check_cols = ["inse", "quantidade_alunos_inse", "cluster_id"] + NIVEL_COLS
    nulls_inse = fact_inse[inse_check_cols].isnull().sum()
    total_nulls = nulls_inse.sum()
    status = "OK" if total_nulls == 0 else "FALHA"
    print(f"  [{status}] fact_inse nulos em colunas INSE: {total_nulls}", flush=True)
    if total_nulls:
        errors.append(f"fact_inse: {total_nulls} nulos em colunas INSE")

    # ── Nulos aceitaveis em fact_crimes (apenas 2026 sem populacao) ──────────────
    nulls_pop = fact_crimes["populacao"].isnull().sum()
    print(f"  [INFO] fact_crimes nulos em populacao: {nulls_pop} (esperado: 27 -- ano 2026)", flush=True)

    # ── Soma de crimes deve coincidir com a fonte ────────────────────────────────
    for col in ["estupro", "estupro_vulneravel"]:
        soma_fact   = int(fact_crimes[col].sum())
        soma_source = int(source[col].sum())
        status = "OK" if soma_fact == soma_source else "FALHA"
        print(f"  [{status}] soma {col}: fact={soma_fact:,} | source={soma_source:,}", flush=True)
        if soma_fact != soma_source:
            errors.append(f"soma {col} diverge: {soma_fact} != {soma_source}")

    # ── Soma dos generos deve igualar total de crimes ─────────────────────────────
    for crime in ["estupro", "estupro_vulneravel"]:
        fem  = f"{crime}_feminino"
        masc = f"{crime}_masculino"
        nao  = f"{crime}_nao_informado"
        if all(c in fact_crimes.columns for c in [fem, masc, nao]):
            total_gender = fact_crimes[fem] + fact_crimes[masc] + fact_crimes[nao]
            mismatch = int((total_gender != fact_crimes[crime]).sum())
            status = "OK" if mismatch == 0 else "FALHA"
            print(f"  [{status}] {crime}: genero sum == total ({mismatch} discrepancias)", flush=True)
            if mismatch:
                errors.append(f"{crime}: {mismatch} linhas com soma de generos != total")

    # ── Nulos esperados em colunas socioeconomicas ─────────────────────────────
    for col in SOCIO_COLS:
        if col in fact_crimes.columns:
            n = fact_crimes[col].isnull().sum()
            print(f"  [INFO] {col} nulos: {n}", flush=True)

    # ── Resultado final ──────────────────────────────────────────────────────────
    print("-" * 60, flush=True)
    if errors:
        print(f"VALIDACAO FALHOU ({len(errors)} erro(s)):", flush=True)
        for e in errors:
            print(f"  ! {e}", flush=True)
        raise AssertionError("Validacao do modelo Power BI falhou. Ver erros acima.")
    else:
        print("VALIDACAO APROVADA -- todos os checks passaram.", flush=True)
    print("-" * 60, flush=True)


# ── Relatorio final ───────────────────────────────────────────────────────────────

def print_report(tables: dict[str, pd.DataFrame]) -> None:
    print("\n" + "=" * 60, flush=True)
    print("RELATORIO DO MODELO POWER BI", flush=True)
    print("=" * 60, flush=True)

    for name, df in tables.items():
        print(f"\n  {name}", flush=True)
        print(f"    Linhas  : {len(df):,}", flush=True)
        print(f"    Colunas : {list(df.columns)}", flush=True)
        nulls = df.isnull().sum()
        nulls = nulls[nulls > 0]
        if not nulls.empty:
            print(f"    Nulos   : {nulls.to_dict()}", flush=True)
        else:
            print(f"    Nulos   : nenhum", flush=True)

    print("\n" + "-" * 60, flush=True)
    print("COMO IMPORTAR NO POWER BI DESKTOP:", flush=True)
    print("-" * 60, flush=True)
    print("  1. Pagina inicial -> Obter dados -> Texto/CSV", flush=True)
    print("     Para cada arquivo em data/powerbi/:", flush=True)
    print("     - Origem do arquivo : 65001: Unicode (UTF-8)", flush=True)
    print("     - Delimitador       : Ponto e virgula", flush=True)
    print("     - Locale            : Portugues (Brasil)", flush=True)
    print("       [garante que ',' seja o separador decimal]", flush=True)
    print(flush=True)
    print("  2. Apos carregar, va em Exibicao de Modelo e crie os relacionamentos:", flush=True)
    print("     fact_crimes[uf]          -> dim_uf[uf]              (N:1)", flush=True)
    print("     fact_crimes[ano]         -> dim_ano[ano]            (N:1)", flush=True)
    print("     fact_inse[uf]            -> dim_uf[uf]              (N:1)", flush=True)
    print("     fact_inse[ano]           -> dim_ano[ano]            (N:1)", flush=True)
    print("     fact_inse[cluster_id]    -> dim_cluster[cluster_id] (N:1)", flush=True)
    print(flush=True)
    print("  3. Direcao do filtro: todos os relacionamentos usam filtro simples", flush=True)
    print("     (da dimensao para a fato). Nao ativar filtro bidirecional.", flush=True)
    print(flush=True)
    print("  4. Medidas DAX sugeridas (criar em fact_crimes ou em tabela separada):", flush=True)
    print("     Total Estupros              = SUM(fact_crimes[estupro])", flush=True)
    print("     Total Estupros Vulneravel   = SUM(fact_crimes[estupro_vulneravel])", flush=True)
    print("     Total Crimes Sexuais        = [Total Estupros] + [Total Estupros Vulneravel]", flush=True)
    print("     Populacao Total             = SUM(fact_crimes[populacao])", flush=True)
    print("     Taxa Estupro por 100k       =", flush=True)
    print("       DIVIDE(SUM(fact_crimes[estupro]),", flush=True)
    print("              SUM(fact_crimes[populacao])) * 100000", flush=True)
    print("     INSE Medio                  = AVERAGE(fact_inse[inse])", flush=True)
    print("     % Vitimas Femininas (vuln)  =", flush=True)
    print("       DIVIDE(SUM(fact_crimes[estupro_vulneravel_feminino]),", flush=True)
    print("              SUM(fact_crimes[estupro_vulneravel]))", flush=True)
    print("     % Vitimas Masculinas (vuln) =", flush=True)
    print("       DIVIDE(SUM(fact_crimes[estupro_vulneravel_masculino]),", flush=True)
    print("              SUM(fact_crimes[estupro_vulneravel]))", flush=True)
    print("     Rank UF por Taxa            =", flush=True)
    print("       RANKX(ALL(dim_uf), [Taxa Estupro por 100k],,DESC,DENSE)", flush=True)
    print("     Gini medio por UF        = AVERAGE(fact_crimes[gini])", flush=True)
    print("     Renda per capita media   = AVERAGE(fact_crimes[renda_per_capita])", flush=True)
    print("     Taxa desemprego media    = AVERAGE(fact_crimes[taxa_desemprego])", flush=True)
    print("     Densidade demografica    = AVERAGE(fact_crimes[densidade_demografica])", flush=True)
    print("=" * 60, flush=True)


# ── Pipeline principal ────────────────────────────────────────────────────────────

def run() -> None:
    print("=" * 60, flush=True)
    print("Pipeline POWER BI -- generate_powerbi_model.py", flush=True)
    print("=" * 60, flush=True)

    POWERBI_DIR.mkdir(parents=True, exist_ok=True)

    print("\nCarregando fonte ...", flush=True)
    source = load_source()

    print("\nConstruindo dimensoes ...", flush=True)
    dim_uf      = build_dim_uf(source)
    dim_ano     = build_dim_ano(source)
    dim_cluster = build_dim_cluster(source)

    print("Construindo fatos ...", flush=True)
    fact_crimes = build_fact_crimes(source)
    fact_inse   = build_fact_inse(source)

    validate_all(dim_uf, dim_ano, dim_cluster, fact_crimes, fact_inse, source)

    print("\nSalvando arquivos ...", flush=True)
    save(dim_uf,      POWERBI_DIR / "dim_uf.csv",      "dim_uf")
    save(dim_ano,     POWERBI_DIR / "dim_ano.csv",      "dim_ano")
    save(dim_cluster, POWERBI_DIR / "dim_cluster.csv",  "dim_cluster")
    save(fact_crimes, POWERBI_DIR / "fact_crimes.csv",  "fact_crimes")
    save(fact_inse,   POWERBI_DIR / "fact_inse.csv",    "fact_inse")

    tables = {
        "dim_uf.csv":      dim_uf,
        "dim_ano.csv":     dim_ano,
        "dim_cluster.csv": dim_cluster,
        "fact_crimes.csv": fact_crimes,
        "fact_inse.csv":   fact_inse,
    }
    print_report(tables)


if __name__ == "__main__":
    run()
