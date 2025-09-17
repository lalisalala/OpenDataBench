# Data

This folder contains the ground truth benchmark datasets used in **OpenDataBench**.

## Files

- **evaluation_dataset_GOV.json**  
  Queries and gold labels derived from the **German National Open Data Portal** ([GovData.de](https://www.govdata.de/)).  

- **evaluation_dataset_LDS.json**  
  Queries and gold labels derived from the **London Datastore (LDS)**, the Greater London Authority’s open data portal ([data.london.gov.uk](https://data.london.gov.uk/)).  

## Format

Each file is a JSON list of conversations.  
A conversation contains:
```json
{
  "conversation_id": "Property Prices #1",
  "turns": [
    {
      "user": "Can you find me a dataset with the average property prices in London?",
      "eval_type": "described dataset",
      "ground_truth": [
        "Average House Prices by Borough, Ward, MSOA & LSOA"
      ]
    }
  ]
}
