import json
import os
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from matplotlib.cm import get_cmap

# --- Global Style Settings ---
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10
})
colors = get_cmap("Set2").colors  # soft, colorblind-friendly

# --- Config: change to "GOV" or "LDS" ---
DATASET = "GOV"   # or "LDS"

# --- Paths ---
BASE_DIR = os.path.dirname(__file__)
BASELINE_DIR = os.path.join(BASE_DIR, f"../baselines/{DATASET}")
DOCS_FIG_DIR = os.path.join(BASE_DIR, f"../docs/figures/{DATASET}")
os.makedirs(DOCS_FIG_DIR, exist_ok=True)

# --- Load & Aggregate ---
def load_results(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    metrics_by_type = defaultdict(list)
    baseline_summary = {}

    for convo in data:
        if "baseline_summary" in convo:
            baseline_summary = convo["baseline_summary"]
            continue
        for turn in convo["turns"]:
            eval_type = turn.get("eval_type", turn.get("type", "")).strip().lower()
            result = turn.get("result", {})
            if isinstance(result, dict):
                metrics_by_type[eval_type].append(result)

    summary = {}
    for eval_type, results in metrics_by_type.items():
        agg = defaultdict(list)
        for r in results:
            for k, v in r.items():
                if isinstance(v, (int, float)):
                    if k == "hallucination_rate":
                        v = min(max(v, 0), 1)
                    agg[k].append(v)
        summary[eval_type] = {k: round(np.mean(v), 3) for k, v in agg.items()}

    return summary, baseline_summary

# --- Auto-discover all systems for this dataset ---
systems = {}
summaries = {}
baseline_summaries = {}

for family in ["LLMs", "portals"]:
    family_dir = os.path.join(BASELINE_DIR, family)
    if not os.path.exists(family_dir):
        continue
    for fname in os.listdir(family_dir):
        if fname.endswith("_baseline.json"):
            system_name = fname.replace("_baseline.json", "")
            label = f"{system_name} ({family})"
            path = os.path.join(family_dir, fname)
            summary, bsum = load_results(path)
            systems[label] = system_name
            summaries[label] = summary
            baseline_summaries[label] = bsum

# --- Main metrics plot ---
eval_types = sorted({et for s in summaries.values() for et in s})
metrics = ["precision", "recall", "f1", "avg_relevance", "ndcg"]

models = list(summaries.keys())
bar_width = 0.8 / len(models)
x = np.arange(len(eval_types))

fig, axs = plt.subplots(len(metrics), 1, figsize=(15, 12), sharex=True)

for i, metric in enumerate(metrics):
    ax = axs[i]
    ax.set_title(f"{metric.capitalize()} by System ({DATASET})", fontsize=14, fontweight="bold")

    for j, model in enumerate(models):
        vals = [summaries[model].get(et, {}).get(metric, 0) for et in eval_types]
        bars = ax.bar(
            x + j*bar_width,
            vals,
            width=bar_width,
            label=model,
            color=colors[j % len(colors)],
            edgecolor="black",
            linewidth=0.5,
            alpha=0.9
        )
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, height + 0.02,
                        f"{height:.2f}", ha="center", va="bottom", fontsize=9)

    ax.set_ylabel(metric.capitalize(), fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    if metric == "avg_relevance":
        ax.set_ylim(0, 4.2)
    elif metric == "ndcg":
        ax.set_ylim(0, 1.1)
    else:
        ax.set_ylim(0, 1.05)

axs[-1].set_xticks(x + (len(models)-1)*bar_width/2)
axs[-1].set_xticklabels(eval_types, rotation=30, ha="right")
axs[-1].set_xlabel("Evaluation Type", fontsize=13)
axs[0].legend(loc="upper left", bbox_to_anchor=(1.01, 1.0))

plt.suptitle(f"Evaluation Comparison Across Systems ({DATASET})", fontsize=16, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.96])

# Save both PNG and SVG
plot_path = os.path.join(DOCS_FIG_DIR, f"evaluation_metrics_{DATASET}.png")
plt.savefig(plot_path, dpi=300, bbox_inches="tight")
plt.savefig(plot_path.replace(".png", ".svg"), format="svg", bbox_inches="tight")
plt.close()
print(f"✅ Saved metric comparison plot to {plot_path} (+ SVG)")

# --- Hallucination Metrics Plot (LLMs only) ---
llm_labels = [m for m in models if "(LLMs)" in m]
halluc_metrics = ["hallucination_rate", "hallucination_frequency"]

fig, axs = plt.subplots(1, len(halluc_metrics), figsize=(5 * len(halluc_metrics), 5))
if len(halluc_metrics) == 1:
    axs = [axs]

x = np.arange(len(llm_labels))
bar_width = 0.5

for i, hm in enumerate(halluc_metrics):
    ax = axs[i]
    values = [baseline_summaries[m].get(hm, 0) for m in llm_labels]
    bars = ax.bar(
        x,
        values,
        width=bar_width,
        color=colors[:len(llm_labels)],
        edgecolor="black",
        linewidth=0.5,
        alpha=0.9
    )
    ax.set_title(hm.replace("_", " ").capitalize(), fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(llm_labels, rotation=20)

    if hm == "hallucination_rate":
        ax.set_ylabel("Hallucination Rate (can exceed 1)")
        max_val = max(values) if values else 1
        if max_val <= 1:
            ax.set_ylim(0, 1.05)
        else:
            ax.set_ylim(0, max_val * 1.15)
        ax.axhline(1.0, linestyle="--", linewidth=1, alpha=0.5)
    else:
        ax.set_ylabel("Fraction of Queries with ≥1 Hallucination")
        ax.set_ylim(0, 1.05)

    ax.grid(axis="y", linestyle="--", alpha=0.6)

    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width()/2, h + (0.02 if h <= 1 else 0.04),
                    f"{h:.2f}", ha="center", va="bottom", fontsize=9)

plt.suptitle(f"LLM Hallucination Metrics ({DATASET})", fontsize=16, fontweight="bold")
plt.tight_layout(rect=[0, 0, 1, 0.95])

halluc_plot_path = os.path.join(DOCS_FIG_DIR, f"hallucination_metrics_{DATASET}.png")
plt.savefig(halluc_plot_path, dpi=300, bbox_inches="tight")
plt.savefig(halluc_plot_path.replace(".png", ".svg"), format="svg", bbox_inches="tight")
plt.close()
print(f"✅ Saved hallucination metrics plot to {halluc_plot_path} (+ SVG)")

# --- Print out all results per baseline ---
def print_summary(label, summary, baseline_summary=None):
    print(f"\n📊 {label} Evaluation Summary:")
    for eval_type, metrics in summary.items():
        print(f"  🔹 {eval_type.title()}:")
        for metric_name, value in metrics.items():
            print(f"     {metric_name}: {value:.3f}")
    if baseline_summary:
        print("  --- Baseline-level Hallucination Metrics ---")
        for metric_name, value in baseline_summary.items():
            print(f"     {metric_name}: {value:.3f}")

for model in models:
    print_summary(model, summaries[model], baseline_summaries[model])
