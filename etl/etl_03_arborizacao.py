"""
ETL 03 - Avaliação da Arborização Urbana e Impacto Ambiental
Fonte: Portal de Dados Abertos do Recife - Áreas Verdes e Arborização
Aluno 2 - Transformação e análise dos dados ambientais e arborização
"""

import requests
import pandas as pd
import json
import os
import random
from datetime import datetime

BASE_URL = "http://dados.recife.pe.gov.br/api/3/action"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)



def extrair_dados_arborizacao():
    """Busca datasets de arborização via API CKAN."""
    print("[EXTRAÇÃO] Buscando datasets de arborização e meio ambiente...")
    url = f"{BASE_URL}/package_search"
    params = {"q": "arborizacao OR arvores OR areas verdes OR meio ambiente", "rows": 30}
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        dados = resp.json()
        print(f"  → {len(dados['result']['results'])} datasets encontrados.")
        return dados["result"]["results"]
    except Exception as e:
        print(f"  [AVISO] API indisponível ({e}). Usando dados simulados.")
        return []


def gerar_dados_simulados_arborizacao():
    """Dados sintéticos de inventário arbóreo urbano do Recife."""
    random.seed(21)

    bairros = [
        "Casa Forte", "Espinheiro", "Graças", "Apipucos", "Monteiro",
        "Boa Viagem", "Pina", "Imbiribeira", "Ibura", "Jordão",
        "Beberibe", "Dois Unidos", "Água Fria", "Bomba do Hemetério", "Arruda"
    ]
    especies = [
        "Ficus benjamina", "Oiti (Licania tomentosa)", "Mangueira (Mangifera indica)",
        "Sibipiruna", "Flamboyant", "Amendoeira (Terminalia catappa)",
        "Cajueiro", "Jaqueira", "Castanhola", "Pau-brasil"
    ]
    condicoes = ["Boa", "Regular", "Ruim", "Crítica"]
    tipo_area = ["Calçada", "Praça", "Parque", "Canteiro", "Área de lazer"]

    registros = []
    for i in range(800):
        dap = round(random.uniform(5, 150), 1)  
        altura = round(random.uniform(2, 20), 1)
        registros.append({
            "id": i + 1,
            "bairro": random.choice(bairros),
            "especie": random.choice(especies),
            "tipo_area": random.choice(tipo_area),
            "condicao": random.choices(condicoes, weights=[0.45, 0.30, 0.15, 0.10])[0],
            "altura_m": altura,
            "dap_cm": dap,
            "area_copa_m2": round(3.14159 * (dap / 100) ** 2 * 10, 2),
            "data_inventario": datetime(
                2022, random.randint(1, 12), random.randint(1, 28)
            ).strftime("%Y-%m-%d"),
            "necessita_poda": random.choices([True, False], weights=[0.35, 0.65])[0],
            "risco_queda": random.choices([True, False], weights=[0.15, 0.85])[0],
            "latitude": round(-8.05 + random.uniform(-0.12, 0.12), 6),
            "longitude": round(-34.9 + random.uniform(-0.12, 0.12), 6),
            "co2_absorvido_kg_ano": round(dap * altura * 0.5, 2),
        })
    return pd.DataFrame(registros)


def gerar_dados_areas_verdes():
    """Dados das áreas verdes e parques do Recife."""
    random.seed(33)
    areas = [
        {"nome": "Parque Estadual Dois Irmãos", "bairro": "Dois Irmãos", "area_ha": 384.0},
        {"nome": "Parque da Jaqueira", "bairro": "Jaqueira", "area_ha": 8.7},
        {"nome": "Parque 13 de Maio", "bairro": "Santo Amaro", "area_ha": 4.0},
        {"nome": "Parque Santana", "bairro": "Várzea", "area_ha": 2.5},
        {"nome": "Jardim Botânico", "bairro": "Madalena", "area_ha": 13.2},
        {"nome": "Bosque de Apipucos", "bairro": "Apipucos", "area_ha": 6.1},
        {"nome": "Parque Arraial Moita Bonita", "bairro": "Arraial", "area_ha": 1.8},
        {"nome": "Parque dos Manguezais", "bairro": "Pina", "area_ha": 40.0},
        {"nome": "Parque Amorim", "bairro": "Madalena", "area_ha": 3.3},
        {"nome": "Mangue do Capibaribe", "bairro": "Várzea", "area_ha": 25.0},
    ]
    for a in areas:
        a["arvores_estimadas"] = int(a["area_ha"] * random.uniform(80, 200))
        a["visitantes_mes"] = int(random.uniform(1000, 50000))
        a["infraestrutura"] = random.choices(["Boa", "Regular", "Ruim"], weights=[0.4, 0.4, 0.2])[0]
    return pd.DataFrame(areas)




def transformar(df_arv: pd.DataFrame, df_areas: pd.DataFrame) -> dict:
    print("[TRANSFORMAÇÃO] Processando dados de arborização urbana...")

    total_arvores = len(df_arv)
    pct_boa = round((df_arv["condicao"] == "Boa").mean() * 100, 2)
    pct_critica = round((df_arv["condicao"] == "Crítica").mean() * 100, 2)
    necessitam_poda = df_arv["necessita_poda"].sum()
    risco_queda = df_arv["risco_queda"].sum()
    co2_total = round(df_arv["co2_absorvido_kg_ano"].sum() / 1000, 2)
    area_copa_total = round(df_arv["area_copa_m2"].sum(), 2)

    print(f"  → Total de árvores inventariadas: {total_arvores}")
    print(f"  → Em boa condição: {pct_boa}% | Em estado crítico: {pct_critica}%")
    print(f"  → Necessitam poda: {necessitam_poda} | Risco de queda: {risco_queda}")
    print(f"  → CO₂ absorvido estimado: {co2_total} toneladas/ano")

    por_bairro = (
        df_arv.groupby("bairro")
        .agg(
            total_arvores=("id", "count"),
            co2_absorvido_ton=("co2_absorvido_kg_ano", lambda x: round(x.sum() / 1000, 3)),
            area_copa_m2=("area_copa_m2", "sum"),
            risco_queda=("risco_queda", "sum"),
            poda_necessaria=("necessita_poda", "sum"),
        )
        .reset_index()
        .sort_values("total_arvores", ascending=False)
    )

    por_especie = (
        df_arv.groupby("especie")
        .agg(quantidade=("id", "count"), altura_media=("altura_m", "mean"))
        .reset_index()
        .sort_values("quantidade", ascending=False)
    )

    por_condicao = df_arv["condicao"].value_counts().reset_index()
    por_condicao.columns = ["condicao", "quantidade"]

    return {
        "kpis": {
            "total_arvores": total_arvores,
            "pct_condicao_boa": pct_boa,
            "pct_condicao_critica": pct_critica,
            "necessitam_poda": int(necessitam_poda),
            "risco_queda": int(risco_queda),
            "co2_absorvido_toneladas_ano": co2_total,
            "area_copa_total_m2": area_copa_total,
            "total_areas_verdes": len(df_areas),
            "area_verde_total_ha": round(df_areas["area_ha"].sum(), 2),
        },
        "por_bairro": por_bairro,
        "por_especie": por_especie,
        "por_condicao": por_condicao,
        "areas_verdes": df_areas,
        "df_completo": df_arv,
    }




def carregar(resultado: dict):
    print("[CARGA] Salvando dados de arborização...")
    resultado["df_completo"].to_csv(f"{OUTPUT_DIR}/arborizacao_completo.csv", index=False)
    resultado["por_bairro"].to_csv(f"{OUTPUT_DIR}/arborizacao_por_bairro.csv", index=False)
    resultado["por_especie"].to_csv(f"{OUTPUT_DIR}/arborizacao_por_especie.csv", index=False)
    resultado["por_condicao"].to_csv(f"{OUTPUT_DIR}/arborizacao_por_condicao.csv", index=False)
    resultado["areas_verdes"].to_csv(f"{OUTPUT_DIR}/areas_verdes.csv", index=False)
    with open(f"{OUTPUT_DIR}/arborizacao_kpis.json", "w", encoding="utf-8") as f:
        json.dump(resultado["kpis"], f, ensure_ascii=False, indent=2)
    print(f"  → Arquivos salvos em: {OUTPUT_DIR}")




def run():
    print("=" * 60)
    print("ETL 03 — Arborização Urbana e Impacto Ambiental")
    print("=" * 60)
    extrair_dados_arborizacao()
    df_arv = gerar_dados_simulados_arborizacao()
    df_areas = gerar_dados_areas_verdes()
    print(f"  → {len(df_arv)} árvores | {len(df_areas)} áreas verdes carregadas.")
    resultado = transformar(df_arv, df_areas)
    carregar(resultado)
    print("\n[OK] ETL 03 concluído com sucesso!\n")
    return resultado


if __name__ == "__main__":
    run()
