# Scripts

This folder contains the evaluation and visualization scripts for **OpenDataBench**.

## Scripts

- **compare_baseline.py**  
  Computes evaluation metrics for all systems under `results/{DATASET}/`.  
  Saves per-turn metrics and baseline summaries into `baselines/{DATASET}/`.

- **metrics_dashboard.py**  
  Aggregates baseline JSONs and generates comparative plots.  
  Saves figures into `docs/figures/{DATASET}/`.

## Usage

Select the dataset to evaluate by setting the `DATASET` variable at the top of each script:
```python
DATASET = "GOV"   # or "LDS"
Then run:
# Evaluate systems for GovData
python compare_baseline.py

# Generate plots for GovData
python metrics_dashboard.py

Switch DATASET = "LDS" to evaluate the London Datastore.