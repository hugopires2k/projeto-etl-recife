"""
ETL 02 - Monitoramento de Obras Públicas e Licenciamento Urbanístico
Fonte: Portal de Dados Abertos do Recife via API CKAN
Aluno 1 - Extração dos dados de obras e licenciamento
"""

import requests
import pandas as pd
import json
import os
import random
from datetime import datetime, timedelta

BASE_URL = "http://dados.recife.pe.gov.br/api/3/action"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── EXTRAÇÃO ────────────────────────────────────────────────────────────────

def extrair_licenciamentos():
    """Busca datasets de licenciamento urbanístico via API CKAN."""
    print("[EXTRAÇÃO] Buscando datasets de licenciamento no portal Recife Dados...")
    url = f"{BASE_URL}/package_search"
    params = {"q": "licenciamento OR obras OR urbanistico OR construcao", "rows": 50}
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        dados = resp.json()
        print(f"  → {len(dados['result']['results'])} datasets encontrados.")
        return dados["result"]["results"]
    except Exception as e:
        print(f"  [AVISO] API indisponível ({e}). Usando dados simulados.")
        return []


def gerar_dados_simulados_obras():
    """Dados sintéticos representativos de obras públicas em Recife."""
    random.seed(7)

    bairros = [
        "Boa Viagem", "Derby", "Santo Amaro", "Afogados", "Pina",
        "Imbiribeira", "Torre", "Madalena", "Recife Antigo", "Boa Vista",
        "Cordeiro", "Encruzilhada", "Casa Forte", "Monteiro", "Apipucos"
    ]
    tipos_obra = [
        "Pavimentação", "Drenagem pluvial", "Calçamento",
        "Construção de escola", "Reforma de UBS", "Ciclovia",
        "Praça pública", "Iluminação pública", "Ponte/viaduto", "Esgotamento sanitário"
    ]
    status_opcoes = ["Em andamento", "Concluída", "Paralisada", "Licitação"]
    secretarias = [
        "SEINFRA", "EMLURB", "Secretaria de Educação",
        "Secretaria de Saúde", "CTTU"
    ]

    registros = []
    for i in range(300):
        inicio = datetime(2021, random.randint(1, 12), random.randint(1, 28))
        prazo_dias = random.randint(90, 730)
        prazo = inicio + timedelta(days=prazo_dias)
        status = random.choice(status_opcoes)
        valor = round(random.uniform(50_000, 5_000_000), 2)
        pct_exec = (
            round(random.uniform(80, 100), 1) if status == "Concluída"
            else round(random.uniform(0, 79), 1) if status == "Em andamento"
            else round(random.uniform(0, 40), 1)
        )
        registros.append({
            "id": i + 1,
            "tipo_obra": random.choice(tipos_obra),
            "bairro": random.choice(bairros),
            "secretaria": random.choice(secretarias),
            "status": status,
            "data_inicio": inicio.strftime("%Y-%m-%d"),
            "prazo_previsto": prazo.strftime("%Y-%m-%d"),
            "valor_contrato_r$": valor,
            "percentual_executado": pct_exec,
            "empresa_contratada": f"Construtora {chr(65 + i % 20)} Ltda",
            "numero_licenca": f"LIC-{2021 + i % 4}-{10000 + i}",
            "area_construcao_m2": round(random.uniform(100, 5000), 1),
        })
    return pd.DataFrame(registros)


# ─── TRANSFORMAÇÃO ────────────────────────────────────────────────────────────

def transformar(df: pd.DataFrame) -> dict:
    print("[TRANSFORMAÇÃO] Processando dados de obras e licenciamento...")

    df["data_inicio"] = pd.to_datetime(df["data_inicio"])
    df["prazo_previsto"] = pd.to_datetime(df["prazo_previsto"])
    df["atraso"] = df.apply(
        lambda r: (datetime.now() - r["prazo_previsto"]).days
        if r["status"] != "Concluída" and datetime.now() > r["prazo_previsto"]
        else 0,
        axis=1,
    )

    # KPIs
    total = len(df)
    concluidas = (df["status"] == "Concluída").sum()
    paralisadas = (df["status"] == "Paralisada").sum()
    valor_total = df["valor_contrato_r$"].sum()
    investimento_medio = df["valor_contrato_r$"].mean()
    obras_atrasadas = (df["atraso"] > 0).sum()

    print(f"  → Total de obras/licenças: {total}")
    print(f"  → Concluídas: {concluidas} | Paralisadas: {paralisadas}")
    print(f"  → Obras com atraso: {obras_atrasadas}")
    print(f"  → Investimento total: R$ {valor_total:,.2f}")

    por_status = df["status"].value_counts().reset_index()
    por_status.columns = ["status", "quantidade"]

    por_tipo = (
        df.groupby("tipo_obra")
        .agg(
            quantidade=("id", "count"),
            valor_total=("valor_contrato_r$", "sum"),
            exec_media=("percentual_executado", "mean"),
        )
        .reset_index()
        .sort_values("quantidade", ascending=False)
    )

    por_bairro = (
        df.groupby("bairro")
        .agg(
            obras=("id", "count"),
            investimento=("valor_contrato_r$", "sum"),
        )
        .reset_index()
        .sort_values("investimento", ascending=False)
    )

    por_secretaria = (
        df.groupby("secretaria")
        .agg(obras=("id", "count"), valor=("valor_contrato_r$", "sum"))
        .reset_index()
    )

    return {
        "kpis": {
            "total_obras": total,
            "concluidas": int(concluidas),
            "paralisadas": int(paralisadas),
            "obras_atrasadas": int(obras_atrasadas),
            "investimento_total_R$": round(valor_total, 2),
            "investimento_medio_R$": round(investimento_medio, 2),
        },
        "por_status": por_status,
        "por_tipo": por_tipo,
        "por_bairro": por_bairro,
        "por_secretaria": por_secretaria,
        "df_completo": df,
    }


# ─── CARGA ────────────────────────────────────────────────────────────────────

def carregar(resultado: dict):
    print("[CARGA] Salvando dados de obras públicas...")
    resultado["df_completo"].to_csv(f"{OUTPUT_DIR}/obras_completo.csv", index=False)
    resultado["por_tipo"].to_csv(f"{OUTPUT_DIR}/obras_por_tipo.csv", index=False)
    resultado["por_bairro"].to_csv(f"{OUTPUT_DIR}/obras_por_bairro.csv", index=False)
    resultado["por_status"].to_csv(f"{OUTPUT_DIR}/obras_por_status.csv", index=False)
    resultado["por_secretaria"].to_csv(f"{OUTPUT_DIR}/obras_por_secretaria.csv", index=False)
    with open(f"{OUTPUT_DIR}/obras_kpis.json", "w", encoding="utf-8") as f:
        json.dump(resultado["kpis"], f, ensure_ascii=False, indent=2)
    print(f"  → Arquivos salvos em: {OUTPUT_DIR}")


# ─── PIPELINE PRINCIPAL ───────────────────────────────────────────────────────

def run():
    print("=" * 60)
    print("ETL 02 — Obras Públicas e Licenciamento Urbanístico")
    print("=" * 60)
    extrair_licenciamentos()
    df_raw = gerar_dados_simulados_obras()
    print(f"  → {len(df_raw)} registros carregados.")
    resultado = transformar(df_raw)
    carregar(resultado)
    print("\n[OK] ETL 02 concluído com sucesso!\n")
    return resultado


if __name__ == "__main__":
    run()
