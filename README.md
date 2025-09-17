# OpenDataBench

**OpenDataBench** is an open-source benchmark for evaluating **natural language dataset discovery** across open data portals and large language models (LLMs).  
It provides curated evaluation datasets, baseline results, evaluation scripts, and visualization tools to assess retrieval performance in multilingual, real-world settings.

---

## ✨ Key Features

- **Multilingual benchmark datasets**  
  - **London Datastore (LDS)** — English, municipal-scale.  
  - **GovData.de** — German, national-scale.  

## Baselines

The benchmark currently includes the following **baselines** for comparison:

- **Native portal search** — keyword-based search using the portals’ own CKAN interfaces:  
  - [London Datastore](https://data.london.gov.uk/) (English, municipal-scale)  
  - [GovData.de](https://www.govdata.de/) (German, national-scale)  

- **[data.europa.eu](https://data.europa.eu/)** — an aggregator portal that federates datasets from national and municipal portals, including LDS and GovData.  

- **ChatGPT-5.0** — instructed to return datasets specifically from the target portal.  

- **Gemini 2.5 Flash** — same setup as ChatGPT.  

- **DeepSeek 3.1** — search-enabled, restricted to the target portal by prompting.  

- **Ground truth annotations**  
  - 118 natural language queries.  
  - Fine-grained relevance scores (0–4).  

- **Evaluation metrics**  
  - Precision, Recall, F1.  
  - Average Relevance.  
  - nDCG@5.  
  - Hallucination Frequency & Rate (LLMs only).  

- **Reproducible evaluation pipeline**  
  - Scripts to compute baselines and generate plots.  
  - Outputs figures in `docs/figures/`.  

---

## 📂 Repository Structure
```
OpenDataBench/
│
├── data/ # Evaluation datasets (GovData, LDS)
│ ├── evaluation_dataset_GOV.json
│ ├── evaluation_dataset_LDS.json
│ └── README.md
│
├── results/ # Raw system outputs (LLMs and portals)
│ ├── GOV/
│ └── LDS/
│
├── baselines/ # Evaluated baseline JSONs
│ ├── GOV/
│ └── LDS/
│
├── scripts/ # Evaluation and visualization scripts
│ ├── compare_baseline.py
│ ├── metrics_dashboard.py
│ └── README.md
│
├── docs/ # Documentation and figures
│ ├── methodology.md
│ └── figures/
│ ├── GOV/
│ └── LDS/
│
├── requirements.txt # Python dependencies
└── README.md # Main repository overview
```

---

## 🚀 Quickstart

Clone the repo and install dependencies:

```bash
git clone https://github.com/your-username/OpenDataBench.git
cd OpenDataBench
pip install -r requirements.txt
```
Run evaluation for GovData.de:
```bash
cd scripts
python compare_baseline.py
python metrics_dashboard.py
```

Switch to London Datastore (LDS) by editing the DATASET variable in the scripts:
```bash
DATASET = "LDS"
```

Outputs:
```bash
Baseline JSONs → baselines/{DATASET}/

Figures → docs/figures/{DATASET}/
```
📖 Documentation

Methodology
 — detailed description of benchmark design, baselines, and metrics.

Scripts Guide
 — how to run evaluation and visualization scripts.

📊 Example Figures

Evaluation metrics and hallucination comparisons are automatically generated in docs/figures/{DATASET}/.

📜 License

This project is released under the MIT License.


## 🔮 Limitations & Future Work

- **Single-turn focus**:  
  The current benchmark only evaluates **first-turn queries** (single queries).  
  This allows us to standardize evaluation and ground truth, but it does not yet capture multi-turn interactions.  

- **Planned extensions**:  
  1. **Larger query set** — expanding the number and diversity of queries across domains.  
  2. **Multi-turn conversations** — extending the benchmark to support follow-up queries and conversational dataset discovery.  
