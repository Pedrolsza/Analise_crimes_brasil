"""
load_and_standardize_sinesp.py
--------------------------------
Carrega todos os arquivos Excel BancoVDE do SINESP (2016-2026), padroniza o schema
e gera uma agregacao anual por UF salva em data/processed/sinesp_crimes.csv.

DESCOBERTAS SOBRE OS DADOS (resultado da inspecao -- nao remover este bloco):
  - Arquivos fonte: data/raw/Sinesp/BancoVDE YYYY.xlsx (uma aba por arquivo, nomeada com o ano)
  - Schema: identico em todos os 11 anos -- 14 colunas, sem alteracoes detectadas
  - Granularidade: uma linha por (UF, municipio, evento, mes)
  - Coluna `uf` ja contem codigos IBGE de UF (ex: 'SP', 'RJ') -- sem normalizacao necessaria
  - `total_vitima` e a coluna correta de contagem de vitimas (int)
  - `total` e `total_peso` sao sempre nulos nas linhas de crimes -- nao utilizados
  - `feminino`, `masculino`, `nao_informado` sao armazenados como strings -- nao usados diretamente
  - `abrangencia` tem 3 valores: 'Estadual', 'Policia Federal', 'Policia Rodoviaria Federal'
    Apenas 'Estadual' e mantido (orgaos federais usam agregacao geografica diferente)

DISPONIBILIDADE DOS CRIMES:
  - 'Estupro de vulneravel'  -> DISPONIVEL em todos os anos 2016-2026 -> mapeado para estupro_vulneravel
  - 'Estupro'                -> DISPONIVEL em todos os anos 2016-2026 -> mapeado para estupro (contexto)
  - 'Sequestro'              -> NAO DISPONIVEL no SINESP -- nao consta neste dataset
  - 'Exploracao infantil'    -> NAO DISPONIVEL no SINESP -- nao consta neste dataset

  O README lista sequestro e exploracao_infantil como variaveis-alvo. Esses dados precisam ser
  obtidos de outra fonte (ex: Anuario Brasileiro de Seguranca Publica, SSPs estaduais).
  Este script produz apenas o que o SINESP efetivamente contem.
"""

import re
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

# ── Caminhos ───────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw" / "Sinesp"
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_FILE = PROCESSED_DIR / "sinesp_crimes.csv"

# ── Configuracao ───────────────────────────────────────────────────────────────

# Apenas registros de abrangencia estadual. Orgaos federais (PRF, PF) agregam de forma diferente.
ABRANGENCIA_KEEP = "Estadual"

# Colunas necessarias da fonte -- carregar apenas estas evita ler 9 colunas desnecessarias
USECOLS = ["uf", "evento", "data_referencia", "total_vitima", "abrangencia"]

# Mapeia o nome normalizado (minusculo, sem acentos) do evento para o nome canonico da coluna.
# A ordem importa: padroes mais especificos devem vir antes dos mais abrangentes.
# 'estupro de vulneravel' deve ser verificado antes de 'estupro' para evitar classificacao errada.
CRIME_MAP = {
    "estupro de vulneravel": "estupro_vulneravel",   # Art. 217-A CP -- estupro de pessoa vulneravel
    "estupro": "estupro",                             # Art. 213 CP -- categoria mais ampla (apenas contexto)
}


# ── Funcoes auxiliares ─────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Converte para minusculo, remove espacos e acentos para comparacao normalizada."""
    import unicodedata
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.lower().strip()


def extract_year_from_filename(path: Path) -> int:
    """Extrai o ano de 4 digitos do nome de arquivo no formato 'BancoVDE 2022.xlsx'."""
    match = re.search(r"(\d{4})", path.stem)
    if not match:
        raise ValueError(f"Nao foi possivel extrair o ano do arquivo: {path.name}")
    return int(match.group(1))


def load_single_file(path: Path) -> pd.DataFrame:
    """
    Carrega um arquivo Excel do SINESP e retorna um DataFrame filtrado e tipado.
    Aplica o filtro de abrangencia e a coercao de tipos no momento do carregamento para economizar memoria.
    """
    year = extract_year_from_filename(path)
    print(f"  Carregando {path.name} ...", end=" ", flush=True)

    df = pd.read_excel(
        path,
        sheet_name=str(year),   # a aba sempre tem o nome do ano
        usecols=USECOLS,
        engine="openpyxl",
    )

    original_rows = len(df)

    # Manter apenas registros estaduais (excluir linhas da Policia Federal e PRF)
    df = df[df["abrangencia"] == ABRANGENCIA_KEEP].copy()

    # Extrair o ano da coluna de data (data_referencia e mensal, ex: 2022-03-01)
    df["ano"] = pd.to_datetime(df["data_referencia"]).dt.year

    # total_vitima chega como int do openpyxl; coercao defensiva para garantir tipo correto
    df["total_vitima"] = pd.to_numeric(df["total_vitima"], errors="coerce").fillna(0).astype(int)

    kept_rows = len(df)
    print(f"{original_rows:,} linhas -> {kept_rows:,} apos filtro de abrangencia", flush=True)

    return df[["uf", "ano", "evento", "total_vitima"]]


def classify_crimes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mapeia os valores brutos de evento para nomes canonicos de colunas usando comparacao normalizada.
    Retorna apenas as linhas que correspondem aos crimes-alvo definidos.
    Padroes mais especificos sao verificados primeiro para evitar correspondencias parciais incorretas.
    """
    df = df.copy()
    evento_normalized = df["evento"].astype(str).apply(_normalize)

    df["crime"] = None
    for raw_pattern, label in CRIME_MAP.items():
        mask = (evento_normalized == raw_pattern) & df["crime"].isna()
        df.loc[mask, "crime"] = label

    unmatched = df["crime"].isna().sum()
    df = df.dropna(subset=["crime"])
    print(
        f"  Classificacao: {len(df):,} linhas correspondidas | {unmatched:,} eventos nao-alvo removidos",
        flush=True,
    )
    return df


def aggregate_annual(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega contagens mensais por municipio em totais anuais por UF.
    Pivota o resultado para que cada tipo de crime seja uma coluna separada.
    """
    annual = (
        df.groupby(["uf", "ano", "crime"])["total_vitima"]
        .sum()
        .reset_index()
    )

    pivoted = annual.pivot_table(
        index=["uf", "ano"],
        columns="crime",
        values="total_vitima",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    pivoted.columns.name = None  # remove o nome do MultiIndex gerado pelo pivot
    return pivoted


def validate_output(df: pd.DataFrame) -> None:
    """Verificacoes basicas de sanidade no DataFrame final antes de salvar."""
    assert "uf" in df.columns, "Coluna 'uf' ausente"
    assert "ano" in df.columns, "Coluna 'ano' ausente"
    assert df["uf"].nunique() <= 27, f"Numero inesperado de UFs: {df['uf'].nunique()}"
    assert df["ano"].between(2016, 2026).all(), "Valores de ano fora do intervalo esperado 2016-2026"
    assert (df.select_dtypes(include="number") >= 0).all().all(), "Valores negativos encontrados nas contagens"

    print("\n  Validacao concluida:", flush=True)
    print(f"    UFs presentes  : {sorted(df['uf'].unique())}", flush=True)
    print(f"    Anos presentes : {sorted(df['ano'].unique())}", flush=True)
    print(f"    Dimensoes      : {df.shape}", flush=True)
    print(f"    Colunas        : {list(df.columns)}", flush=True)

    # Alertar se alguma combinacao UF-ano parecer ausente
    expected = 27 * df["ano"].nunique()
    if len(df) < expected:
        missing = expected - len(df)
        print(
            f"\n  ATENCAO: {missing} combinacoes UF-ano ausentes nos dados.",
            flush=True,
        )
        print(
            "  Pode indicar estados com zero ocorrencias registradas OU estados que nao",
            flush=True,
        )
        print(
            "  reportaram ao SINESP naquele ano. Nao trate zeros como ausencia confirmada.",
            flush=True,
        )


# ── Pipeline principal ─────────────────────────────────────────────────────────

def run() -> pd.DataFrame:
    print("=" * 60, flush=True)
    print("Pipeline SINESP -- load_and_standardize_sinesp.py", flush=True)
    print("=" * 60, flush=True)

    # Descobrir arquivos disponiveis
    files = sorted(RAW_DIR.glob("BancoVDE *.xlsx"))
    if not files:
        raise FileNotFoundError(
            f"Nenhum arquivo SINESP encontrado em {RAW_DIR}.\n"
            "Faca o download em dados.gov.br e coloque os arquivos em data/raw/Sinesp/"
        )
    print(f"\nEncontrado(s) {len(files)} arquivo(s):", flush=True)
    for f in files:
        print(f"  {f.name}", flush=True)
    print(flush=True)

    # Carregar, classificar e coletar cada ano
    all_frames = []
    for path in files:
        raw = load_single_file(path)
        classified = classify_crimes(raw)
        all_frames.append(classified)

    # Concatenar todos os anos
    print("\nConcatenando todos os anos ...", flush=True)
    combined = pd.concat(all_frames, ignore_index=True)

    # Agregar para nivel anual por UF e pivotar
    print("Agregando totais anuais por UF ...", flush=True)
    result = aggregate_annual(combined)

    # Ordenar para facilitar leitura
    result = result.sort_values(["uf", "ano"]).reset_index(drop=True)

    # Validar antes de salvar
    validate_output(result)

    # Salvar resultado
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"\nSalvo -> {OUTPUT_FILE}", flush=True)

    print("\n" + "=" * 60, flush=True)
    print("OBSERVACOES IMPORTANTES PARA A ANALISE:", flush=True)
    print("  1. 'sequestro' NAO consta no SINESP. Obter do", flush=True)
    print("     Anuario Brasileiro de Seguranca Publica ou SSPs estaduais.", flush=True)
    print("  2. 'exploracao_infantil' NAO consta no SINESP. Idem.", flush=True)
    print("  3. 'estupro_vulneravel' = Art. 217-A CP apenas.", flush=True)
    print("     Nao confundir com 'estupro' (Art. 213 CP).", flush=True)
    print("  4. Zero = zero registrado OU ausencia de reporte --", flush=True)
    print("     nao confirma ausencia real. Validar por UF/ano antes da analise.", flush=True)
    print("=" * 60, flush=True)

    return result


if __name__ == "__main__":
    run()
