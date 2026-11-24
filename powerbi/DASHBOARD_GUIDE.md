# Building the Power BI report

The data comes from `python main.py`, which writes four CSVs into `powerbi/data/`. Building the report in Power BI Desktop takes about 30 to 45 minutes. When you're done, save it here as `CreditApproval.pbix`.

## Load the data

Use Get data > Text/CSV and load:
- `applications_scored.csv`
- `model_comparison.csv`
- `feature_importance.csv`
- `test_metrics.csv`

Rename the tables to `Applications`, `ModelComparison`, `FeatureImportance` and `TestMetrics`.

If you want refresh to keep working after the folder moves, create a text parameter called `DataFolder` and use the queries in `PowerQuery.m` instead. The `ModelComparison` query in that file also unpivots the metrics into long format, which makes the comparison chart easier.

## Model setup

- The tables don't need relationships. Everything filters off `Applications`.
- Use "Sort by column" so the bands appear in the right order, then hide the `*Order` columns:
  - AgeBand → AgeBandOrder
  - IncomeBand → IncomeBandOrder
  - CreditScoreBand → CreditScoreBandOrder
  - DebtBand → DebtBandOrder
  - RiskSegment → RiskSegmentOrder
- Format `ApprovalProbability` as a percentage.
- Add a numeric range parameter named `Threshold`: 0.05 to 0.95, step 0.05, default 0.45 (the threshold the model uses).
- Make an empty `_Measures` table and paste in the measures from `DAX_measures.dax`.
- Import `theme.json` under View > Themes > Browse for themes.

## Page 1: Overview

- **Cards:**
  - Total Applications
  - Approved Applications
  - Approval Rate
  - Avg Approval Probability
- **Donut:** ActualStatus by Total Applications.
- **Bar charts of Approval Rate:**
  - by PriorDefaultFlag
  - by EmployedLabel
  - by IncomeBand
- **Combo chart:** AgeBand on the axis, Total Applications as columns, Approval Rate as the line.
- **Slicers:**
  - CitizenLabel
  - EmployedLabel
  - PriorDefaultFlag
  - AgeBand

## Page 2: Drivers

- **Matrix:** CreditScoreBand rows × DebtBand columns, showing Approval Rate. Turn on background colour formatting from coral (low) to teal (high).
- **Scatter:** Income (log axis) against YearsEmployed, coloured by ActualStatus.
- **Bar:** FeatureImportance, sorted descending.
- **Key Influencers:** analyse ActualStatus = Approved, explained by these fields:
  - the numeric fields
  - PriorDefaultFlag
  - EmployedLabel
  - CitizenLabel
  - DriversLicenseLabel

## Page 3: Model

- **Cards:**
  - Model Accuracy
  - Model Precision
  - Model Recall
  - Model F1
  - ROC AUC
- **Confusion matrix:** a matrix with ActualStatus rows × PredictedStatus columns, counting applications. Filter it to Dataset = Test.
- **Model comparison:** clustered bar of ModelComparison, Score by Model, with Metric as the legend.
- **Risk segments:** donut of RiskSegment.
- **Probability histogram:** group ApprovalProbability into 0.1 bins, coloured by ActualStatus.
- **Threshold simulator:** the Threshold slicer plus these four cards:
  - Approval Rate at Threshold
  - Accuracy at Threshold
  - Missed Good Applicants at Threshold
  - Risky Approvals at Threshold
- **Review queue:** a table of applicants in the Review segment, sorted by probability.

## Finishing

- Add a page navigator.
- Sync the slicers across pages.
- Publish to the Power BI service if you want to share the report. To get scheduled refresh, point `DataFolder` at OneDrive or SharePoint.
