"""
ETL 04 - Análise de Ocorrências de Segurança Pública por Região
Fontes: Guarda Municipal do Recife, SINESP, Fogo Cruzado
Aluno 3 - Transformação e análise dos dados de segurança pública
"""

import requests
import pandas as pd
import json
import os
import random
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)



def extrair_sinesp():
    """
    Consulta a API SINESP para dados criminais de Recife/PE.
    Endpoint: http://ec2-54-174-4-15.compute1.amazonaws.com/api?uf=pe&municipio=recife
    """
    print("[EXTRAÇÃO] Consultando API SINESP (Segurança Pública)...")
    url = "http://ec2-54-174-4-15.compute1.amazonaws.com/api"
    params = {"uf": "pe", "municipio": "recife"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        print("  → Dados SINESP obtidos com sucesso.")
        return resp.json()
    except Exception as e:
        print(f"  [AVISO] SINESP indisponível ({e}). Usando dados simulados.")
        return None


def extrair_guarda_municipal():
    """Busca dataset de ocorrências da Guarda Municipal no portal Recife Dados."""
    print("[EXTRAÇÃO] Buscando ocorrências da Guarda Municipal...")
    url = "http://dados.recife.pe.gov.br/api/3/action/package_search"
    params = {"q": "guarda municipal OR ocorrencias OR seguranca", "rows": 20}
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        dados = resp.json()
        print(f"  → {len(dados['result']['results'])} datasets encontrados.")
        return dados["result"]["results"]
    except Exception as e:
        print(f"  [AVISO] Portal indisponível ({e}).")
        return []


def gerar_dados_simulados_seguranca():
    """Dados sintéticos de ocorrências de segurança pública em Recife."""
    random.seed(99)

    bairros_risco = {
        "Ibura": "alto",
        "Jordão": "alto",
        "Beberibe": "alto",
        "Dois Unidos": "alto",
        "Água Fria": "alto",
        "Boa Viagem": "médio",
        "Imbiribeira": "médio",
        "Torre": "médio",
        "Casa Amarela": "médio",
        "Madalena": "baixo",
        "Casa Forte": "baixo",
        "Graças": "baixo",
        "Espinheiro": "baixo",
        "Aflitos": "baixo",
        "Recife Antigo": "médio",
    }

    tipos_crime = {
        "Furto": 0.30,
        "Roubo a pedestre": 0.20,
        "Roubo a veículo": 0.15,
        "Tráfico de drogas": 0.12,
        "Lesão corporal": 0.10,
        "Homicídio": 0.03,
        "Arrombamento": 0.05,
        "Perturbação da ordem": 0.05,
    }

    turnos = {"Manhã (6h-12h)": 0.20, "Tarde (12h-18h)": 0.25, "Noite (18h-00h)": 0.35, "Madrugada (00h-6h)": 0.20}

    registros = []
    for i in range(1000):
        bairro = random.choice(list(bairros_risco.keys()))
        nivel = bairros_risco[bairro]
       
        if nivel == "alto":
            pesos = [0.25, 0.22, 0.18, 0.15, 0.10, 0.05, 0.03, 0.02]
        elif nivel == "médio":
            pesos = [0.32, 0.18, 0.15, 0.10, 0.12, 0.02, 0.06, 0.05]
        else:
            pesos = [0.40, 0.15, 0.12, 0.05, 0.10, 0.01, 0.08, 0.09]

        tipo = random.choices(list(tipos_crime.keys()), weights=pesos)[0]
        mes = random.randint(1, 12)
        registros.append({
            "id": i + 1,
            "tipo_ocorrencia": tipo,
            "bairro": bairro,
            "nivel_risco_bairro": nivel,
            "mes": mes,
            "ano": random.choice([2022, 2023]),
            "turno": random.choices(list(turnos.keys()), weights=list(turnos.values()))[0],
            "vitimas": random.choices([0, 1, 2, 3], weights=[0.3, 0.5, 0.15, 0.05])[0],
            "prisoes_efetuadas": random.choices([0, 1], weights=[0.7, 0.3])[0],
            "latitude": round(-8.05 + random.uniform(-0.12, 0.12), 6),
            "longitude": round(-34.9 + random.uniform(-0.12, 0.12), 6),
        })
    return pd.DataFrame(registros)




def transformar(df: pd.DataFrame) -> dict:
    print("[TRANSFORMAÇÃO] Analisando dados de segurança pública...")

    total = len(df)
    total_vitimas = df["vitimas"].sum()
    total_prisoes = df["prisoes_efetuadas"].sum()
    taxa_prisao = round(total_prisoes / total * 100, 2)
    crime_mais_freq = df["tipo_ocorrencia"].value_counts().idxmax()
    turno_perigoso = df["turno"].value_counts().idxmax()

    print(f"  → Total de ocorrências: {total}")
    print(f"  → Vítimas registradas: {total_vitimas}")
    print(f"  → Taxa de prisões: {taxa_prisao}%")
    print(f"  → Crime mais frequente: {crime_mais_freq}")
    print(f"  → Turno mais perigoso: {turno_perigoso}")

    por_bairro = (
        df.groupby(["bairro", "nivel_risco_bairro"])
        .agg(
            ocorrencias=("id", "count"),
            vitimas=("vitimas", "sum"),
            prisoes=("prisoes_efetuadas", "sum"),
        )
        .reset_index()
        .sort_values("ocorrencias", ascending=False)
    )

    por_tipo = df["tipo_ocorrencia"].value_counts().reset_index()
    por_tipo.columns = ["tipo", "quantidade"]

    por_turno = df["turno"].value_counts().reset_index()
    por_turno.columns = ["turno", "ocorrencias"]

    por_mes = (
        df.groupby(["ano", "mes"])
        .agg(ocorrencias=("id", "count"))
        .reset_index()
        .sort_values(["ano", "mes"])
    )

    por_nivel_risco = df["nivel_risco_bairro"].value_counts().reset_index()
    por_nivel_risco.columns = ["nivel_risco", "ocorrencias"]

    return {
        "kpis": {
            "total_ocorrencias": total,
            "total_vitimas": int(total_vitimas),
            "total_prisoes": int(total_prisoes),
            "taxa_prisao_pct": taxa_prisao,
            "crime_mais_frequente": crime_mais_freq,
            "turno_mais_perigoso": turno_perigoso,
        },
        "por_bairro": por_bairro,
        "por_tipo": por_tipo,
        "por_turno": por_turno,
        "por_mes": por_mes,
        "por_nivel_risco": por_nivel_risco,
        "df_completo": df,
    }




def carregar(resultado: dict):
    print("[CARGA] Salvando dados de segurança pública...")
    resultado["df_completo"].to_csv(f"{OUTPUT_DIR}/seguranca_completo.csv", index=False)
    resultado["por_bairro"].to_csv(f"{OUTPUT_DIR}/seguranca_por_bairro.csv", index=False)
    resultado["por_tipo"].to_csv(f"{OUTPUT_DIR}/seguranca_por_tipo.csv", index=False)
    resultado["por_turno"].to_csv(f"{OUTPUT_DIR}/seguranca_por_turno.csv", index=False)
    resultado["por_mes"].to_csv(f"{OUTPUT_DIR}/seguranca_por_mes.csv", index=False)
    with open(f"{OUTPUT_DIR}/seguranca_kpis.json", "w", encoding="utf-8") as f:
        json.dump(resultado["kpis"], f, ensure_ascii=False, indent=2)
    print(f"  → Arquivos salvos em: {OUTPUT_DIR}")




def run():
    print("=" * 60)
    print("ETL 04 — Segurança Pública por Região")
    print("=" * 60)
    extrair_sinesp()
    extrair_guarda_municipal()
    df_raw = gerar_dados_simulados_seguranca()
    print(f"  → {len(df_raw)} ocorrências carregadas.")
    resultado = transformar(df_raw)
    carregar(resultado)
    print("\n[OK] ETL 04 concluído com sucesso!\n")
    return resultado


if __name__ == "__main__":
    run()
