Methodology
Evaluation Setup

To assess the retrieval quality of OpenDORA and comparable systems, we designed a benchmark tailored to natural language dataset discovery. Our evaluation focuses on single-turn queries and measures a system’s ability to retrieve relevant datasets using both binary and graded metrics.

The multilingual benchmark is constructed from two contrasting open data portals introduced in the retrieval pipeline:

London Datastore (data.london.gov.uk
) — municipal-scale, English.

GovData.de (govdata.de
) — national-scale, German.

To highlight differences across infrastructures, we also include data.europa.eu (data.europa.eu
), a European aggregator that federates datasets from both portals.

This setup highlights retrieval challenges across different scales of open data infrastructure. In addition to the native portal searches, we also include state-of-the-art LLMs as baselines.

User Queries

Following prior dataset search research, we adopt three query types observed in user studies:

Described dataset — the user specifies dataset features in detail without naming it directly.

Dataset request — the user explicitly names a dataset.

Implied dataset — the user expresses an information need indirectly without explicitly referring to data.

With these categories in mind, we curated 118 queries in total:

68 for the London Datastore (English).

50 for GovData.de (German).

The queries were drawn from three sources:

Existing dataset search user studies.

ChatGPT-generated variants on relevant topics (e.g., housing, environment).

Manually crafted queries inspired by observed portal search patterns.

Ground Truth

Each query was manually annotated with a set of relevant datasets and assigned graded relevance scores on a 0–4 scale:

4 – Highly relevant: directly satisfies the query.

3 – Relevant: useful but less specific.

2 – Partially relevant: contains some relevant information but requires filtering or interpretation.

1 – Marginally relevant: only tangentially related.

0 – Not relevant: no meaningful alignment with the query.

Ground truth construction was iterative:

We first reviewed datasets retrieved through keyword search on the portals.

To avoid bias toward keyword-only retrieval, we then examined outputs from OpenDORA and the LLM baselines (ChatGPT, Gemini, DeepSeek). Additional relevant datasets from these systems were incorporated into the ground truth.

Baselines

We compare six baselines alongside OpenDORA:

OpenDORA — our proposed RAG-based system combining dense retrieval (BAAI/bge-m3), reranking, and local LLaMA3:8B generation.

Native portal search — keyword-based search on GovData.de and LDS, returning the top-5 results.

data.europa.eu — aggregator portal baseline (CKAN-based).

ChatGPT-5.0 — instructed to return datasets specifically from the target portal.

Gemini 2.5 Flash — same setup as ChatGPT.

DeepSeek 3.1 — search-enabled, restricted to the target portal by prompting.

This setup ensures a fair comparison between:

Portal-native keyword search.

Aggregated catalogue search.

Prompted LLM baselines.

Metrics

We evaluate retrieval quality using both binary and graded metrics over the top-5 retrieved results:

Precision

Recall

F1-score

Average relevance (0–4 scale)

nDCG@5

For the LLM baselines, we additionally assess hallucination, defined as a dataset prediction (title, link) that does not appear in the ground truth set of the target portal.

Two complementary measures are reported:

Hallucination frequency — fraction of queries that produced at least one hallucination.

Hallucination rate — fraction of all returned predictions across queries that were hallucinated.

Together, these provide a reliability perspective:

Frequency shows how widespread hallucination is.

Rate shows how contaminated predictions are overall.

Evaluation Pipeline

Collect system outputs (LLMs and portals) in results/{DATASET}/.

Run compare_baseline.py to compute evaluation baselines in baselines/{DATASET}/.

Run metrics_dashboard.py to generate figures in docs/figures/{DATASET}/.

Limitations

Manual annotation bias — ground truth reflects annotator judgment.

Incomplete ground truth — not all relevant datasets may have been found.

Language coverage — more queries in English (LDS) than in German (GovData.de).

System diversity — currently limited to three LLMs and selected portals.