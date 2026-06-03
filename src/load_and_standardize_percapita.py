"""
load_and_standardize_percapita.py
-----------------------------------
Padroniza a tabela SIDRA 7395 (rendimento medio mensal real domiciliar per capita)
para o formato do projeto: (uf, ano, renda_per_capita).

FONTE:
  data/raw/ibge/bq-percapita_result.csv
  IBGE/SIDRA Tabela 7395 - formato wide, separador ponto-e-virgula, codificacao UTF-8 BOM.

QUIRKS DO ARQUIVO FONTE:
  - Linha 0: titulo da tabela (ignorar)
  - Linha 1: nome da variavel (ignorar)
  - Linha 2: cabecalho de texto "Nivel;Cod.;Brasil, ..." (ignorar)
  - Linha 3: cabecalho com anos: "Nivel";"Cod.";"...";"2016";;"2017";;...
    Cada ano ocupa 2 colunas: valor + "Reais" (coluna de unidade a descartar).
  - Linhas de dados: campo[0] indica nivel ("BR", "GR", "UF").
    Apenas linhas "UF" sao processadas.
  - Campo[1] = codigo IBGE numerico (ex: "11" -> RO).
  - Valores sao inteiros sem decimal. "..." indica dado suprimido -> None.
  - ANO 2020 ESTA AUSENTE nesta serie (PNAD Continua suspensa em 2020).

SAIDA:
  data/processed/ibge_percapita.csv
  Colunas: uf (str), ano (int), renda_per_capita (float, nullable)

JOIN:
  Merge com outras tabelas por (uf, ano). Nota: 2020 tera null para todos os UFs.
"""

from pathlib import Path

import pandas as pd

ROOT      = Path(__file__).resolve().parent.parent
RAW_FILE  = ROOT / "data" / "raw" / "ibge" / "bq-percapita_result.csv"
OUT_FILE  = ROOT / "data" / "processed" / "ibge_percapita.csv"

# IBGE codigo numerico -> sigla UF (27 estados)
IBGE_TO_UF = {
    '11': 'RO', '12': 'AC', '13': 'AM', '14': 'RR', '15': 'PA',
    '16': 'AP', '17': 'TO', '21': 'MA', '22': 'PI', '23': 'CE',
    '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL', '28': 'SE',
    '29': 'BA', '31': 'MG', '32': 'ES', '33': 'RJ', '35': 'SP',
    '41': 'PR', '42': 'SC', '43': 'RS', '50': 'MS', '51': 'MT',
    '52': 'GO', '53': 'DF',
}


def parse_percapita() -> pd.DataFrame:
    # Ler como texto puro para controlar o parsing linha a linha (SIDRA nao e CSV convencional)
    raw = RAW_FILE.read_text(encoding="utf-8-sig")
    lines = [ln.rstrip("\r") for ln in raw.split("\n")]

    # Linha 3 (0-indexed) contem os cabecalhos com os anos
    header_line = lines[3]
    header_fields = [f.strip('"') for f in header_line.split(";")]
    # Campos: ["Nivel","Cod.","Brasil, ...","2016","","2017","","2018",...]
    # Extrair anos: campos nas posicoes 3, 5, 7, ... (pares: valor + "Reais")
    years = []
    for i in range(3, len(header_fields), 2):
        token = header_fields[i].strip()
        if token.isdigit():
            years.append(int(token))

    records = []
    # Dados comecam na linha 4 (linha 5 no editor = index 4)
    for line in lines[4:]:
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

        # Valores comecam no indice 3, alternando: valor (i), unidade (i+1)
        for j, year in enumerate(years):
            val_idx = 3 + j * 2
            if val_idx >= len(fields):
                records.append({"uf": uf, "ano": year, "renda_per_capita": None})
                continue
            raw_val = fields[val_idx].strip()
            if raw_val == "..." or raw_val == "":
                val = None
            else:
                # Valores inteiros nesta serie; substituir virgula por ponto por precaucao
                val = float(raw_val.replace(",", "."))
            records.append({"uf": uf, "ano": year, "renda_per_capita": val})

    df = pd.DataFrame(records)
    df["ano"] = df["ano"].astype(int)
    df = df.sort_values(["uf", "ano"]).reset_index(drop=True)
    return df


def run() -> None:
    print("=" * 60, flush=True)
    print("Pipeline PERCAPITA -- load_and_standardize_percapita.py", flush=True)
    print("=" * 60, flush=True)

    df = parse_percapita()

    # Validacao
    print(f"\n  Shape           : {df.shape}", flush=True)
    print(f"  Anos presentes  : {sorted(df['ano'].unique().tolist())}", flush=True)
    print(f"  UFs presentes   : {df['uf'].nunique()}", flush=True)
    print(f"  Nulos           : {df['renda_per_capita'].isna().sum()} (esperado: 27 para 2020 ausente)", flush=True)
    print(f"\n  Amostra:\n{df.head(10).to_string(index=False)}", flush=True)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False, encoding="utf-8")
    print(f"\n  Salvo -> {OUT_FILE}", flush=True)
    print("=" * 60, flush=True)


if __name__ == "__main__":
    run()
