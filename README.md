# Pipeline ETL — Análise Integrada de Serviços Públicos e Infraestrutura Urbana no Recife

**SENAC Pernambuco · Disciplina: Data Science · Professor: Heuryk Wylk**

---

## 📋 Descrição do Projeto

Pipeline ETL completo que consome dados públicos do portal **Recife Dados**, envolvendo cinco secretarias e áreas distintas para análise integrada de serviços públicos e infraestrutura urbana, com geração de insights para melhoria da gestão municipal.

---

## 🏗️ Arquitetura do Pipeline

```
Portal Recife Dados (API CKAN)
  http://dados.recife.pe.gov.br/api/3/action/
├── EMLURB           → ETL 01 — Limpeza Urbana
├── SEINFRA          → ETL 02 — Obras Públicas
├── Meio Ambiente    → ETL 03 — Arborização
├── SINESP / GM      → ETL 04 — Segurança Pública
└── Saúde / Educação → ETL 05 — Saúde & Educação

         ↓ EXTRAÇÃO (requests + API CKAN)
         ↓ TRANSFORMAÇÃO (pandas)
         ↓ CARGA (CSV + JSON)
         ↓ VISUALIZAÇÃO (Dashboard HTML/Chart.js)
```

---

## 📁 Estrutura do Projeto

```
etl_recife/
├── main.py                          # Pipeline principal (executa todos os ETLs)
├── dashboard.html                   # Dashboard interativo completo
├── etl/
│   ├── __init__.py
│   ├── etl_01_limpeza_urbana.py     # ETL 01: Limpeza e coleta de resíduos
│   ├── etl_02_obras_publicas.py     # ETL 02: Obras e licenciamento urbanístico
│   ├── etl_03_arborizacao.py        # ETL 03: Arborização e meio ambiente
│   ├── etl_04_seguranca_publica.py  # ETL 04: Segurança pública por região
│   └── etl_05_educacao_saude.py     # ETL 05: Educação e saúde pública
└── data/                            # CSVs e JSONs gerados pelo pipeline
    ├── limpeza_ocorrencias_completo.csv
    ├── limpeza_por_bairro.csv
    ├── limpeza_kpis.json
    ├── obras_completo.csv
    ├── obras_por_tipo.csv
    ├── arborizacao_completo.csv
    ├── arborizacao_por_bairro.csv
    ├── seguranca_completo.csv
    ├── seguranca_por_bairro.csv
    ├── saude_ubs.csv
    ├── saude_samu.csv
    ├── educacao_escolas.csv
    └── kpis_consolidados.json       # KPIs unificados de todos os temas
```

---

## 🔗 Fontes de Dados e APIs

| Tema | Fonte | Endpoint / Link |
|------|-------|-----------------|
| Limpeza Urbana | EMLURB · Portal Recife Dados | `http://dados.recife.pe.gov.br/api/3/action/package_search?q=emlurb` |
| Obras Públicas | SEINFRA · API CKAN | `http://dados.recife.pe.gov.br/api/3/action/package_search?q=obras` |
| Arborização | Sec. Meio Ambiente · API CKAN | `http://dados.recife.pe.gov.br/api/3/action/package_search?q=arborizacao` |
| Segurança Pública | Guarda Municipal + SINESP | `http://ec2-54-174-4-15.compute1.amazonaws.com/api?uf=pe&municipio=recife` |
| Saúde | Sec. Saúde · API CKAN | `https://dados.recife.pe.gov.br/organization/secretaria-de-saude` |
| Educação | Sec. Educação · API CKAN | `http://dados.recife.pe.gov.br/api/3/action/package_search?q=educacao` |

---

## 👥 Divisão de Tarefas

| Aluno | Responsabilidade |
|-------|-----------------|
| **Aluno 1** | Extração dos dados das APIs — ETL 01 (Limpeza) e ETL 02 (Obras) |
| **Aluno 2** | Transformação e análise — ETL 03 (Arborização e Meio Ambiente) |
| **Aluno 3** | Transformação e análise — ETL 04 (Segurança) e ETL 05 (Saúde) |
| **Aluno 4** | Carga dos dados e desenvolvimento do dashboard interativo |

---

## ▶️ Como Executar

### Pré-requisitos
```bash
pip install pandas requests
```

### Executar pipeline completo
```bash
cd etl_recife
python main.py
```

### Executar ETL individual
```bash
python etl/etl_01_limpeza_urbana.py
python etl/etl_02_obras_publicas.py
python etl/etl_03_arborizacao.py
python etl/etl_04_seguranca_publica.py
python etl/etl_05_educacao_saude.py
```

### Visualizar dashboard
Abra `dashboard.html` diretamente no navegador.

---

## 📊 KPIs Gerados

### ETL 01 — Limpeza Urbana
- Total de ocorrências registradas: **500**
- Taxa de resolução: **77%**
- Tempo médio de atendimento: **37.4 horas**
- Total coletado: **509 toneladas**

### ETL 02 — Obras Públicas
- Total de obras/licenças: **300**
- Obras concluídas: **71** | Paralisadas: **91**
- Obras com atraso: **229 (76%)**
- Investimento total: **R$ 733 milhões**

### ETL 03 — Arborização
- Árvores inventariadas: **800**
- Em boa condição: **43.75%** | Estado crítico: **9.25%**
- CO₂ absorvido: **347 toneladas/ano**
- Áreas verdes: **488 hectares**

### ETL 04 — Segurança Pública
- Ocorrências: **1.000** | Vítimas: **955**
- Taxa de prisão: **30.5%**
- Crime mais frequente: **Furto (30%)**
- Turno mais perigoso: **Noite (18h–00h)**

### ETL 05 — Saúde & Educação
- UBS ativas: **14** (5 superlotadas)
- Tempo de espera médio UBS: **111.9 min**
- Tempo de resposta SAMU: **24.2 min**
- Escolas municipais: **120** · Matrículas: **55.513**
- IDEB médio: **5.26** · Aprovação: **75.6%**

---

## 💡 Principais Insights

1. **Limpeza**: Pontos viciados de descarte irregular são o maior problema; reforço de ecopontos é recomendado.
2. **Obras**: 76% das obras estão atrasadas — auditoria de contratos é urgente.
3. **Arborização**: 117 árvores representam risco de queda; intervenção imediata necessária.
4. **Segurança**: Bairros periféricos (Ibura, Jordão, Beberibe) concentram risco alto; policiamento noturno deve ser reforçado.
5. **Saúde/Educação**: UBS superlotadas e IDEB abaixo da meta exigem investimento estrutural prioritário.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Uso |
|-----------|-----|
| Python 3.x | Linguagem principal do pipeline |
| pandas | Transformação e análise dos dados |
| requests | Consumo das APIs REST |
| JSON/CSV | Formato de carga dos dados |
| HTML/CSS/JS | Dashboard de visualização |
| Chart.js | Gráficos interativos do dashboard |
| API CKAN | Interface dos portais de dados abertos |

---

## 📚 Referências

- Portal de Dados Abertos do Recife: http://dados.recife.pe.gov.br/
- Hub de Dados Abertos do Recife: https://hubdedados.recife.pe.gov.br/
- Documentação API CKAN: https://docs.ckan.org/en/2.9/api/
- API SINESP (Segurança Pública): https://github.com/api_seguranca_publica
- Plataforma Fogo Cruzado: https://fogocruzado.org.br/
- Secretaria de Saúde Recife: https://dados.recife.pe.gov.br/organization/secretaria-de-saude
