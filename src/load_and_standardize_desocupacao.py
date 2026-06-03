"""
load_and_standardize_desocupacao.py
--------------------------------------
Padroniza a tabela SIDRA 4093 (taxa de desocupacao trimestral) para o formato
do projeto: (uf, ano, taxa_desemprego), com media anual das 4 semanas de cada ano.

FONTE:
  data/raw/ibge/bq-desocupacao_result.csv
  IBGE/SIDRA Tabela 4093 - formato wide trimestral, separador ponto-e-virgula, UTF-8 BOM.

QUIRKS DO ARQUIVO FONTE:
  - Linha 0: titulo (ignorar)
  - Linha 1: nome da variavel (ignorar)
  - Linha 2: cabecalho de texto (ignorar)
  - Linha 3: cabecalho com trimestres: "Nivel";"Cod.";"...";"1o trimestre 2018";;...
    Cada trimestre ocupa 2 colunas: valor + "%" (coluna de unidade a descartar).
  - Linha 4: sub-cabecalho "Total" (ignorar)
  - Linhas de dados: campo[0] indica nivel. Apenas "UF" e processado.
  - Valores usam virgula como decimal: "13,2" -> 13.2. "..." -> None.
  - 2026 SO TEM Q1 (ano parcial): excluido do output por instrucao explicita.
  - Para anos com dados de GR (Grande Regiao) suprimidos (GR tem "..." em 2020/2021),
    os dados de UF individuais ainda podem estar presentes (verificar por UF).

LOGICA DE MEDIA ANUAL:
  - Agrupamento por (uf, ano): media de todos os trimestres nao-nulos do ano.
  - Se nenhum trimestre do ano tiver dado, o ano nao aparece no output.
  - Anos com ao menos 1 trimestre valido sao incluidos.

SAIDA:
  data/processed/ibge_desocupacao.csv
  Colunas: uf (str), ano (int), taxa_desemprego (float, 2 casas decimais, nullable)

JOIN:
  Merge com outras tabelas por (uf, ano).
  Cobertura: 2018-2025 (PNAD Continua comecou em 2012, SIDRA disponibiliza a partir de 2018).
"""

import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT      = Path(__file__).resolve().parent.parent
RAW_FILE  = ROOT / "data" / "raw" / "ibge" / "bq-desocupacao_result.csv"
OUT_FILE  = ROOT / "data" / "processed" / "ibge_desocupacao.csv"

IBGE_TO_UF = {
    '11': 'RO', '12': 'AC', '13': 'AM', '14': 'RR', '15': 'PA',
    '16': 'AP', '17': 'TO', '21': 'MA', '22': 'PI', '23': 'CE',
    '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL', '28': 'SE',
    '29': 'BA', '31': 'MG', '32': 'ES', '33': 'RJ', '35': 'SP',
    '41': 'PR', '42': 'SC', '43': 'RS', '50': 'MS', '51': 'MT',
    '52': 'GO', '53': 'DF',
}

# Anos parciais a excluir do output (2026: apenas Q1 disponivel)
EXCLUDE_YEARS = {2026}


def parse_quarter_header(token: str):
    """Extrai o ano de um nome de trimestre como '1o trimestre 2018'. Retorna int ou None."""
    m = re.search(r"\b(\d{4})\b", token)
    return int(m.group(1)) if m else None


def parse_desocupacao() -> pd.DataFrame:
    # Ler como texto puro -- SIDRA nao e CSV convencional
    raw = RAW_FILE.read_text(encoding="utf-8-sig")
    lines = [ln.rstrip("\r") for ln in raw.split("\n")]

    # Linha 3 (0-indexed): cabecalho com nomes dos trimestres
    header_line = lines[3]
    header_fields = [f.strip('"') for f in header_line.split(";")]
    # Posicoes 3, 5, 7, ... = nomes dos trimestres; posicoes 4, 6, 8, ... = "%" (descartar)
    quarter_years = []  # lista de anos, um por coluna de valor
    for i in range(3, len(header_fields), 2):
        token = header_fields[i].strip()
        year = parse_quarter_header(token)
        quarter_years.append(year)  # None se nao identificado

    records = []
    # Linhas de dados comecam na linha 5 (indice 5), linha 4 e sub-cabecalho "Total"
    for line in lines[5:]:
        if not line.strip():
            continue
        fields = [f.strip('"') for f in line.split(";")]
        if not fields or fields[0] != "UF":
            continue

        ibge_code = fields[1].strip()
        uf = IBGE_TO_UF.get(ibge_code)
        if uf is None:
            print(f"  [AVISO] Codigo IBGE desconhecido: {ibge_code} -- linha ignorada", flush=True)
            continue

        # Agrupar valores trimestrais por ano
        year_values: dict[int, list] = defaultdict(list)
        for j, year in enumerate(quarter_years):
            if year is None:
                continue
            val_idx = 3 + j * 2
            if val_idx >= len(fields):
                continue
            raw_val = fields[val_idx].strip()
            if raw_val == "..." or raw_val == "":
                # Dado suprimido: nao inclui na media (skipna=True equivalente)
                continue
            try:
                val = float(raw_val.replace(",", "."))
                year_values[year].append(val)
            except ValueError:
                pass

        # Gerar media anual para cada ano com ao menos 1 valor valido
        for year, vals in year_values.items():
            if year in EXCLUDE_YEARS:
                continue
            mean_val = round(sum(vals) / len(vals), 2) if vals else None
            records.append({"uf": uf, "ano": year, "taxa_desemprego": mean_val})

    df = pd.DataFrame(records)
    df["ano"] = df["ano"].astype(int)
    df = df.sort_values(["uf", "ano"]).reset_index(drop=True)
    return df


def run() -> None:
    print("=" * 60, flush=True)
    print("Pipeline DESOCUPACAO -- load_and_standardize_desocupacao.py", flush=True)
    print("=" * 60, flush=True)

    df = parse_desocupacao()

    # Validacao
    print(f"\n  Shape           : {df.shape}", flush=True)
    print(f"  Anos presentes  : {sorted(df['ano'].unique().tolist())}", flush=True)
    print(f"  UFs presentes   : {df['uf'].nunique()}", flush=True)
    print(f"  Nulos           : {df['taxa_desemprego'].isna().sum()}", flush=True)
    print(f"\n  Amostra:\n{df.head(10).to_string(index=False)}", flush=True)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False, encoding="utf-8")
    print(f"\n  Salvo -> {OUT_FILE}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    run()
