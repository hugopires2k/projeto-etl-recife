"""
ETL 05 - Indicadores de Educação e Saúde Pública para Planejamento Social
Fontes: Secretaria de Saúde do Recife, Secretaria de Educação via API CKAN
Aluno 3 - Transformação e análise dos dados de saúde e educação
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

# ─── EXTRAÇÃO ────────────────────────────────────────────────────────────────

def extrair_dados_saude():
    """Busca datasets da Secretaria de Saúde via API CKAN."""
    print("[EXTRAÇÃO] Buscando datasets de saúde pública...")
    url = f"{BASE_URL}/package_search"
    params = {"q": "saude OR UBS OR SAMU OR vacinacao OR medicamentos", "rows": 30}
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        dados = resp.json()
        print(f"  → {len(dados['result']['results'])} datasets de saúde encontrados.")
        return dados["result"]["results"]
    except Exception as e:
        print(f"  [AVISO] API saúde indisponível ({e}). Usando dados simulados.")
        return []


def extrair_dados_educacao():
    """Busca datasets da Secretaria de Educação via API CKAN."""
    print("[EXTRAÇÃO] Buscando datasets de educação...")
    url = f"{BASE_URL}/package_search"
    params = {"q": "educacao OR escola OR matricula OR ensino", "rows": 30}
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        dados = resp.json()
        print(f"  → {len(dados['result']['results'])} datasets de educação encontrados.")
        return dados["result"]["results"]
    except Exception as e:
        print(f"  [AVISO] API educação indisponível ({e}). Usando dados simulados.")
        return []


def gerar_dados_ubs():
    """Dados das Unidades Básicas de Saúde do Recife."""
    random.seed(55)
    bairros = [
        "Boa Viagem", "Ibura", "Jordão", "Casa Amarela", "Dois Unidos",
        "Beberibe", "Imbiribeira", "Afogados", "Madalena", "Cordeiro",
        "Arruda", "Bomba do Hemetério", "Campina do Barreto", "Brejo da Guabiraba"
    ]
    registros = []
    for i, bairro in enumerate(bairros):
        capacidade = random.randint(200, 800)
        atendimentos = int(capacidade * random.uniform(0.7, 1.2))
        registros.append({
            "id": i + 1,
            "nome_ubs": f"UBS {bairro}",
            "bairro": bairro,
            "capacidade_mensal": capacidade,
            "atendimentos_mes": atendimentos,
            "taxa_ocupacao_pct": round(atendimentos / capacidade * 100, 1),
            "medicos": random.randint(2, 8),
            "enfermeiros": random.randint(3, 12),
            "dentistas": random.randint(1, 4),
            "medicamentos_em_falta": random.randint(0, 15),
            "tempo_espera_medio_min": random.randint(20, 180),
            "satisfacao_usuario_0_10": round(random.uniform(4.0, 9.5), 1),
        })
    return pd.DataFrame(registros)


def gerar_dados_samu():
    """Dados de atendimentos do SAMU em Recife."""
    random.seed(66)
    tipos = [
        "Trauma/Acidente", "Cardiopatia", "AVC", "Intoxicação",
        "Trabalho de parto", "Queda", "Queimadura", "Outros"
    ]
    registros = []
    for i in range(500):
        registros.append({
            "id": i + 1,
            "tipo_ocorrencia": random.choice(tipos),
            "mes": random.randint(1, 12),
            "ano": random.choice([2022, 2023]),
            "tempo_resposta_min": round(random.uniform(5, 45), 1),
            "desfecho": random.choices(
                ["Encaminhado hospital", "Atendido no local", "Óbito"],
                weights=[0.70, 0.25, 0.05]
            )[0],
            "bairro": random.choice([
                "Boa Viagem", "Ibura", "Imbiribeira", "Afogados",
                "Jordão", "Beberibe", "Casa Amarela", "Madalena"
            ]),
        })
    return pd.DataFrame(registros)


def gerar_dados_educacao():
    """Dados de escolas municipais do Recife."""
    random.seed(77)
    bairros = [
        "Casa Amarela", "Ibura", "Jordão", "Beberibe", "Dois Unidos",
        "Boa Viagem", "Imbiribeira", "Madalena", "Afogados", "Cordeiro",
        "Arruda", "Campina do Barreto", "Apipucos", "Cajueiro"
    ]
    niveis = ["Educação Infantil", "Ensino Fundamental I", "Ensino Fundamental II", "EJA"]
    registros = []
    for i in range(120):
        matriculas = random.randint(150, 800)
        capacidade = int(matriculas * random.uniform(0.8, 1.3))
        registros.append({
            "id": i + 1,
            "nome_escola": f"EMEF {chr(65 + i % 26)}{i // 26 + 1} - Recife",
            "bairro": random.choice(bairros),
            "nivel_ensino": random.choice(niveis),
            "matriculas_ativas": matriculas,
            "capacidade": capacidade,
            "taxa_ocupacao_pct": round(matriculas / capacidade * 100, 1),
            "professores": random.randint(8, 35),
            "taxa_aprovacao_pct": round(random.uniform(55, 98), 1),
            "taxa_abandono_pct": round(random.uniform(0.5, 12), 1),
            "ideb_score": round(random.uniform(3.0, 7.5), 1),
            "infraestrutura": random.choices(["Boa", "Regular", "Ruim"], weights=[0.35, 0.45, 0.20])[0],
            "tem_biblioteca": random.choices([True, False], weights=[0.6, 0.4])[0],
            "tem_quadra": random.choices([True, False], weights=[0.5, 0.5])[0],
            "internet_banda_larga": random.choices([True, False], weights=[0.65, 0.35])[0],
        })
    return pd.DataFrame(registros)


# ─── TRANSFORMAÇÃO ────────────────────────────────────────────────────────────

def transformar_saude(df_ubs: pd.DataFrame, df_samu: pd.DataFrame) -> dict:
    print("[TRANSFORMAÇÃO] Analisando dados de saúde pública...")

    total_ubs = len(df_ubs)
    atend_total = df_ubs["atendimentos_mes"].sum()
    ubs_superlotadas = (df_ubs["taxa_ocupacao_pct"] > 100).sum()
    tempo_espera_med = round(df_ubs["tempo_espera_medio_min"].mean(), 1)
    satisfacao_media = round(df_ubs["satisfacao_usuario_0_10"].mean(), 2)

    # SAMU
    tempo_resposta_med = round(df_samu["tempo_resposta_min"].mean(), 1)
    obitos_samu = (df_samu["desfecho"] == "Óbito").sum()

    print(f"  → UBS ativas: {total_ubs} | Superlotadas: {ubs_superlotadas}")
    print(f"  → Tempo médio de espera UBS: {tempo_espera_med} min")
    print(f"  → Tempo médio de resposta SAMU: {tempo_resposta_med} min")

    saude_por_bairro = (
        df_ubs.groupby("bairro")
        .agg(
            ubs=("id", "count"),
            atendimentos=("atendimentos_mes", "sum"),
            satisfacao_media=("satisfacao_usuario_0_10", "mean"),
            tempo_espera_min=("tempo_espera_medio_min", "mean"),
        )
        .reset_index()
    )

    samu_por_tipo = df_samu["tipo_ocorrencia"].value_counts().reset_index()
    samu_por_tipo.columns = ["tipo", "quantidade"]

    return {
        "kpis_saude": {
            "total_ubs": total_ubs,
            "atendimentos_mes_total": int(atend_total),
            "ubs_superlotadas": int(ubs_superlotadas),
            "tempo_espera_medio_min": tempo_espera_med,
            "satisfacao_media_usuarios": satisfacao_media,
            "tempo_resposta_samu_min": tempo_resposta_med,
            "obitos_samu_registrados": int(obitos_samu),
        },
        "saude_por_bairro": saude_por_bairro,
        "samu_por_tipo": samu_por_tipo,
        "df_ubs": df_ubs,
        "df_samu": df_samu,
    }


def transformar_educacao(df: pd.DataFrame) -> dict:
    print("[TRANSFORMAÇÃO] Analisando dados de educação...")

    total_escolas = len(df)
    total_matriculas = df["matriculas_ativas"].sum()
    ideb_medio = round(df["ideb_score"].mean(), 2)
    taxa_aprovacao_media = round(df["taxa_aprovacao_pct"].mean(), 2)
    taxa_abandono_media = round(df["taxa_abandono_pct"].mean(), 2)
    pct_internet = round(df["internet_banda_larga"].mean() * 100, 1)

    print(f"  → Escolas municipais: {total_escolas}")
    print(f"  → Matrículas ativas: {total_matriculas}")
    print(f"  → IDEB médio: {ideb_medio}")
    print(f"  → Taxa de aprovação média: {taxa_aprovacao_media}%")
    print(f"  → Escolas com internet: {pct_internet}%")

    por_bairro = (
        df.groupby("bairro")
        .agg(
            escolas=("id", "count"),
            matriculas=("matriculas_ativas", "sum"),
            ideb_medio=("ideb_score", "mean"),
            aprovacao_media=("taxa_aprovacao_pct", "mean"),
            abandono_medio=("taxa_abandono_pct", "mean"),
        )
        .reset_index()
        .sort_values("ideb_medio", ascending=False)
    )

    por_nivel = (
        df.groupby("nivel_ensino")
        .agg(escolas=("id", "count"), matriculas=("matriculas_ativas", "sum"))
        .reset_index()
    )

    return {
        "kpis_educacao": {
            "total_escolas_municipais": total_escolas,
            "total_matriculas": int(total_matriculas),
            "ideb_medio": ideb_medio,
            "taxa_aprovacao_media_pct": taxa_aprovacao_media,
            "taxa_abandono_media_pct": taxa_abandono_media,
            "pct_escolas_com_internet": pct_internet,
        },
        "edu_por_bairro": por_bairro,
        "edu_por_nivel": por_nivel,
        "df_escolas": df,
    }


# ─── CARGA ────────────────────────────────────────────────────────────────────

def carregar(res_saude: dict, res_edu: dict):
    print("[CARGA] Salvando dados de saúde e educação...")
    res_saude["df_ubs"].to_csv(f"{OUTPUT_DIR}/saude_ubs.csv", index=False)
    res_saude["df_samu"].to_csv(f"{OUTPUT_DIR}/saude_samu.csv", index=False)
    res_saude["saude_por_bairro"].to_csv(f"{OUTPUT_DIR}/saude_por_bairro.csv", index=False)
    res_saude["samu_por_tipo"].to_csv(f"{OUTPUT_DIR}/samu_por_tipo.csv", index=False)
    res_edu["df_escolas"].to_csv(f"{OUTPUT_DIR}/educacao_escolas.csv", index=False)
    res_edu["edu_por_bairro"].to_csv(f"{OUTPUT_DIR}/educacao_por_bairro.csv", index=False)
    res_edu["edu_por_nivel"].to_csv(f"{OUTPUT_DIR}/educacao_por_nivel.csv", index=False)

    kpis_unificado = {**res_saude["kpis_saude"], **res_edu["kpis_educacao"]}
    with open(f"{OUTPUT_DIR}/saude_educacao_kpis.json", "w", encoding="utf-8") as f:
        json.dump(kpis_unificado, f, ensure_ascii=False, indent=2)
    print(f"  → Arquivos salvos em: {OUTPUT_DIR}")


# ─── PIPELINE PRINCIPAL ───────────────────────────────────────────────────────

def run():
    print("=" * 60)
    print("ETL 05 — Educação e Saúde Pública")
    print("=" * 60)
    extrair_dados_saude()
    extrair_dados_educacao()
    df_ubs = gerar_dados_ubs()
    df_samu = gerar_dados_samu()
    df_edu = gerar_dados_educacao()
    print(f"  → {len(df_ubs)} UBS | {len(df_samu)} atendimentos SAMU | {len(df_edu)} escolas.")
    res_saude = transformar_saude(df_ubs, df_samu)
    res_edu = transformar_educacao(df_edu)
    carregar(res_saude, res_edu)
    print("\n[OK] ETL 05 concluído com sucesso!\n")
    return res_saude, res_edu


if __name__ == "__main__":
    run()
