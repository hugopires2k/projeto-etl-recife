"""
PIPELINE PRINCIPAL - ETL Integrado
Análise Integrada de Serviços Públicos e Infraestrutura Urbana no Recife
SENAC Pernambuco | Disciplina: Data Science | Professor: Heuryk Wylk
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from etl import (
    etl_01_limpeza_urbana,
    etl_02_obras_publicas,
    etl_03_arborizacao,
    etl_04_seguranca_publica,
    etl_05_educacao_saude,
)
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def main():
    print("\n" + "═" * 60)
    print("  PIPELINE ETL — RECIFE DADOS")
    print("  Análise Integrada de Serviços Públicos e Infraestrutura")
    print("═" * 60 + "\n")

    resultados = {}

    
    r1 = etl_01_limpeza_urbana.run()
    resultados["limpeza"] = r1["kpis"]

    
    r2 = etl_02_obras_publicas.run()
    resultados["obras"] = r2["kpis"]

    
    r3 = etl_03_arborizacao.run()
    resultados["arborizacao"] = r3["kpis"]

    
    r4 = etl_04_seguranca_publica.run()
    resultados["seguranca"] = r4["kpis"]

    
    r5_saude, r5_edu = etl_05_educacao_saude.run()
    resultados["saude"] = r5_saude["kpis_saude"]
    resultados["educacao"] = r5_edu["kpis_educacao"]

    
    print("═" * 60)
    print("  RESUMO GERAL DOS KPIs")
    print("═" * 60)
    for tema, kpis in resultados.items():
        print(f"\n  [{tema.upper()}]")
        for k, v in kpis.items():
            print(f"    {k}: {v}")

    
    with open(f"{DATA_DIR}/kpis_consolidados.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    print("\n" + "═" * 60)
    print("  [PIPELINE CONCLUÍDO] Todos os ETLs executados com sucesso!")
    print(f"  Dados salvos em: {DATA_DIR}/")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
