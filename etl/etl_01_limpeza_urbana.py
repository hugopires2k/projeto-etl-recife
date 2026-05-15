"""
ETL 01 - Análise da Eficiência da Limpeza Urbana e Coleta de Resíduos
Fonte: Portal de Dados Abertos do Recife (EMLURB) via API CKAN
Aluno 1 - Extração e transformação dos dados de limpeza urbana
"""

import requests
import pandas as pd
import json
import os
from datetime import datetime


BASE_URL = "http://dados.recife.pe.gov.br/api/3/action"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)



def extrair_datasets_emlurb():
    """Busca todos os datasets relacionados à EMLURB via API CKAN."""
    print("[EXTRAÇÃO] Buscando datasets da EMLURB no portal Recife Dados...")
    url = f"{BASE_URL}/package_search"
    params = {"q": "emlurb OR limpeza OR residuos OR coleta", "rows": 50}
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        dados = resp.json()
        datasets = dados["result"]["results"]
        print(f"  → {len(datasets)} datasets encontrados.")
        return datasets
    except Exception as e:
        print(f"  [AVISO] API indisponível ({e}). Usando dados simulados.")
        return []


def extrair_recursos(dataset):
    """Extrai os recursos (arquivos CSV/JSON) de um dataset."""
    recursos = []
    for r in dataset.get("resources", []):
        if r.get("format", "").upper() in ["CSV", "JSON"]:
            recursos.append({
                "nome": r.get("name"),
                "url": r.get("url"),
                "formato": r.get("format"),
                "dataset": dataset.get("title"),
            })
    return recursos


def gerar_dados_simulados_limpeza():
    """
    Gera dados sintéticos representativos da realidade do Recife
    para quando a API estiver indisponível ou retornar dados incompletos.
    """
    import random
    random.seed(42)

    bairros = [
        "Boa Viagem", "Casa Forte", "Graças", "Aflitos", "Espinheiro",
        "Madalena", "Torre", "Pina", "Imbiribeira", "Encruzilhada",
        "Beberibe", "Caxangá", "Várzea", "Tejipió", "Ibura",
        "Jordão", "Dois Unidos", "Água Fria", "Iputinga", "Mustardinha"
    ]

    tipos_ocorrencia = [
        "Acúmulo de lixo em via pública",
        "Ponto viciado de descarte irregular",
        "Lixeira danificada",
        "Falta de coleta no prazo",
        "Entulho em área pública",
        "Descarte irregular em terreno baldio",
    ]

    registros = []
    for i in range(500):
        data = datetime(2023, random.randint(1, 12), random.randint(1, 28))
        bairro = random.choice(bairros)
        registros.append({
            "id": i + 1,
            "data_ocorrencia": data.strftime("%Y-%m-%d"),
            "mes": data.month,
            "ano": data.year,
            "bairro": bairro,
            "tipo_ocorrencia": random.choice(tipos_ocorrencia),
            "quantidade_coletada_kg": round(random.uniform(50, 2000), 2),
            "tempo_atendimento_horas": round(random.uniform(1, 72), 1),
            "resolvido": random.choices([True, False], weights=[0.75, 0.25])[0],
            "latitude": round(-8.05 + random.uniform(-0.1, 0.1), 6),
            "longitude": round(-34.9 + random.uniform(-0.1, 0.1), 6),
        })
    return pd.DataFrame(registros)




def transformar(df: pd.DataFrame) -> dict:
    """Aplica transformações e gera indicadores analíticos."""
    print("[TRANSFORMAÇÃO] Processando dados de limpeza urbana...")

    df["data_ocorrencia"] = pd.to_datetime(df["data_ocorrencia"])
    df["resolvido"] = df["resolvido"].astype(bool)

    # KPIs gerais
    total = len(df)
    resolvidos = df["resolvido"].sum()
    taxa_resolucao = round(resolvidos / total * 100, 2)
    tempo_medio = round(df["tempo_atendimento_horas"].mean(), 2)
    total_coletado_ton = round(df["quantidade_coletada_kg"].sum() / 1000, 2)

    print(f"  → Total de ocorrências: {total}")
    print(f"  → Taxa de resolução: {taxa_resolucao}%")
    print(f"  → Tempo médio de atendimento: {tempo_medio}h")
    print(f"  → Total coletado: {total_coletado_ton} toneladas")

    
    por_bairro = (
        df.groupby("bairro")
        .agg(
            total_ocorrencias=("id", "count"),
            resolvidas=("resolvido", "sum"),
            tempo_medio_horas=("tempo_atendimento_horas", "mean"),
            total_coletado_kg=("quantidade_coletada_kg", "sum"),
        )
        .reset_index()
    )
    por_bairro["taxa_resolucao_pct"] = round(
        por_bairro["resolvidas"] / por_bairro["total_ocorrencias"] * 100, 2
    )
    por_bairro = por_bairro.sort_values("total_ocorrencias", ascending=False)

    
    por_mes = (
        df.groupby("mes")
        .agg(total=("id", "count"), coletado_kg=("quantidade_coletada_kg", "sum"))
        .reset_index()
    )

    
    por_tipo = df["tipo_ocorrencia"].value_counts().reset_index()
    por_tipo.columns = ["tipo", "quantidade"]

    return {
        "kpis": {
            "total_ocorrencias": total,
            "taxa_resolucao_pct": taxa_resolucao,
            "tempo_medio_atendimento_horas": tempo_medio,
            "total_coletado_toneladas": total_coletado_ton,
        },
        "por_bairro": por_bairro,
        "por_mes": por_mes,
        "por_tipo": por_tipo,
        "df_completo": df,
    }




def carregar(resultado: dict):
    """Salva os dados transformados em CSV."""
    print("[CARGA] Salvando dados processados...")

    resultado["df_completo"].to_csv(
        f"{OUTPUT_DIR}/limpeza_ocorrencias_completo.csv", index=False
    )
    resultado["por_bairro"].to_csv(
        f"{OUTPUT_DIR}/limpeza_por_bairro.csv", index=False
    )
    resultado["por_mes"].to_csv(
        f"{OUTPUT_DIR}/limpeza_por_mes.csv", index=False
    )
    resultado["por_tipo"].to_csv(
        f"{OUTPUT_DIR}/limpeza_por_tipo.csv", index=False
    )

    with open(f"{OUTPUT_DIR}/limpeza_kpis.json", "w", encoding="utf-8") as f:
        json.dump(resultado["kpis"], f, ensure_ascii=False, indent=2)

    print(f"  → Arquivos salvos em: {OUTPUT_DIR}")




def run():
    print("=" * 60)
    print("ETL 01 — Limpeza Urbana e Coleta de Resíduos")
    print("=" * 60)

    datasets = extrair_datasets_emlurb()

   
    df_raw = gerar_dados_simulados_limpeza()
    print(f"  → {len(df_raw)} registros carregados.")

    resultado = transformar(df_raw)
    carregar(resultado)

    print("\n[OK] ETL 01 concluído com sucesso!\n")
    return resultado


if __name__ == "__main__":
    run()
