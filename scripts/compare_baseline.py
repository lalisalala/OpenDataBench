import os
import json
import numpy as np
import unicodedata
import re

# --- Config: change this to "GOV" or "LDS" ---
DATASET = "GOV"

# --- Paths ---
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "../data")
RESULTS_DIR = os.path.join(BASE_DIR, f"../results/{DATASET}")

# Pick the right evaluation dataset file
EVAL_PATH = os.path.join(DATA_DIR, f"evaluation_dataset_{DATASET}.json")

# Auto-discover all result files for the chosen dataset
BASELINE_FILES = {}
for family in ["LLMs", "portals"]:
    family_dir = os.path.join(RESULTS_DIR, family)
    if not os.path.exists(family_dir):
        continue
    for fname in os.listdir(family_dir):
        if fname.endswith("_results.json"):
            system_name = fname.replace("_results.json", "")
            label = f"{family}_{system_name}"
            BASELINE_FILES[label] = os.path.join(family_dir, fname)

OUTPUT_DIR = os.path.join(BASE_DIR, f"../baselines/{DATASET}")

# ✅ Only count these eval types for baseline-level hallucination metrics
EVAL_TYPES_FOR_FREQ = {"described dataset", "dataset request", "implied dataset"}

# --- Load ground truth ---
with open(EVAL_PATH, "r", encoding="utf-8") as f:
    ground_truth_data = {c["conversation_id"]: c for c in json.load(f)}

# --- Normalization ---
def normalize_title(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFC", s)
    s = s.lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*([,.:;()\-–])\s*", r"\1", s)
    return s.strip()

# --- Utility functions ---
def relevance_score(title, truth):
    norm_title = normalize_title(title)
    for item in truth:
        if norm_title == normalize_title(item["dataset_title"]):
            return item["relevance"]
    return 0

def ndcg_score(relevance_scores, k=5):
    dcg = sum((2**rel - 1) / np.log2(i+2) for i, rel in enumerate(relevance_scores[:k]))
    ideal = sorted(relevance_scores, reverse=True)
    idcg = sum((2**rel - 1) / np.log2(i+2) for i, rel in enumerate(ideal[:k]))
    return round(dcg / idcg, 3) if idcg > 0 else 0.0

def evaluate_turn(predictions, ground_truth, hallucinations=None):
    """Evaluate one query (per-turn metrics)."""
    if not ground_truth:
        return "skipped (no ground truth)"

    pred_set = {normalize_title(t) for t in predictions}
    gold_titles = {normalize_title(item["dataset_title"]) for item in ground_truth}

    true_positives = pred_set & gold_titles
    precision = len(true_positives) / len(pred_set) if pred_set else 0
    recall = len(true_positives) / len(gold_titles) if gold_titles else 0
    f1 = (2 * precision * recall) / (precision + recall) if precision + recall > 0 else 0

    avg_relevance = (
        sum(relevance_score(t, ground_truth) for t in true_positives) / len(true_positives)
        if true_positives else 0
    )

    rel_scores = [relevance_score(t, ground_truth) for t in predictions]
    ndcg = ndcg_score(rel_scores, k=5)

    halluc_count = len(hallucinations) if hallucinations else 0
    halluc_rate = halluc_count / len(pred_set) if pred_set else 0

    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "avg_relevance": round(avg_relevance, 2),
        "ndcg": ndcg,
        "hallucination_rate": round(halluc_rate, 3),
    }

# --- Evaluate all discovered systems ---
os.makedirs(OUTPUT_DIR, exist_ok=True)

for label, path in BASELINE_FILES.items():
    with open(path, "r", encoding="utf-8") as f:
        baseline_data = {c["conversation_id"]: c for c in json.load(f)}

    baseline_eval_results = []

    total_queries = 0
    total_predictions = 0
    queries_with_halluc = 0
    total_hallucinations = 0

    for convo_id, baseline in baseline_data.items():
        eval_convo = ground_truth_data.get(convo_id)
        if not eval_convo:
            continue

        convo_output = {"conversation_id": convo_id, "turns": []}

        for i, turn in enumerate(baseline["turns"]):
            eval_type = (turn.get("eval_type") or "").strip().lower()
            user_query = turn.get("user")
            top_results = turn.get("top_results", []) or []
            hallucinations = turn.get("hallucination", []) or []
            gt_turn = eval_convo["turns"][i]
            ground_truth = gt_turn.get("eval", {}).get("ground_truth_ld", [])

            if eval_type in EVAL_TYPES_FOR_FREQ:
                total_queries += 1
                total_predictions += len(top_results)
                if hallucinations:
                    queries_with_halluc += 1
                    total_hallucinations += len(hallucinations)

            if not ground_truth:
                result = "skipped (no ground truth)"
            elif eval_type in EVAL_TYPES_FOR_FREQ:
                result = evaluate_turn(top_results, ground_truth, hallucinations)
            else:
                result = "skipped"

            convo_output["turns"].append({
                "user": user_query,
                "eval_type": turn.get("eval_type"),
                "top_results": top_results,
                "hallucination": hallucinations,
                "result": result
            })

        baseline_eval_results.append(convo_output)

    halluc_freq = (queries_with_halluc / total_queries) if total_queries > 0 else 0
    halluc_rate = (total_hallucinations / total_predictions) if total_predictions > 0 else 0

    baseline_eval_results.append({
        "baseline_summary": {
            "hallucination_rate": round(halluc_rate, 3),
            "hallucination_frequency": round(halluc_freq, 3),
        }
    })

    # Save to baselines/{DATASET}/LLMs|portals/
    family = "LLMs" if "LLMs" in path else "portals"
    system_name = os.path.basename(path).replace("_results.json", "")
    output_path = os.path.join(OUTPUT_DIR, family, f"{system_name}_baseline.json")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(baseline_eval_results, f, indent=2, ensure_ascii=False)

    print(f"✅ Evaluated {label} → saved: {output_path}")
