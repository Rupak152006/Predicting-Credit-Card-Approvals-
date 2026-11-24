// Builds docs/Credit_Card_Approval_Project_Report.docx
// node docs/build_report.js   (run from the project root, after python main.py)
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, ImageRun, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType, LevelFormat, BorderStyle, Footer, PageNumber,
  PageBreak,
} = require("docx");

const root = path.resolve(__dirname, "..");
const fig = (f) => path.join(root, "reports", "figures", f);
const metrics = JSON.parse(fs.readFileSync(path.join(root, "reports", "metrics.json")));
const tm = metrics.test_metrics;
const pct = (v) => (v * 100).toFixed(1) + "%";

const FONT = "Calibri";
const TEXT_W = 9026; // A4 width minus 1" margins, in DXA
const TEAL = "2A9D8F";

const p = (text, opts = {}) => new Paragraph({
  spacing: { after: 120, line: 276 }, ...opts,
  children: Array.isArray(text) ? text : [new TextRun(text)],
});
const b = (t) => new TextRun({ text: t, bold: true });
const t = (s) => new TextRun(s);
const h1 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(s)] });
const h2 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(s)] });
const bullet = (children) => new Paragraph({
  numbering: { reference: "bullets", level: 0 }, spacing: { after: 60 },
  children: typeof children === "string" ? [new TextRun(children)] : children,
});
const step = (children) => new Paragraph({
  numbering: { reference: "steps", level: 0 }, spacing: { after: 60 },
  children: typeof children === "string" ? [new TextRun(children)] : children,
});

function image(file, srcW, srcH, widthPx, caption) {
  const out = [new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 }, keepNext: true,
    children: [new ImageRun({
      type: "png", data: fs.readFileSync(fig(file)),
      transformation: { width: widthPx, height: Math.round(widthPx * srcH / srcW) },
      altText: { title: caption, description: caption, name: file },
    })],
  })];
  out.push(new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { after: 200 },
    children: [new TextRun({ text: caption, italics: true, size: 18, color: "555555" })],
  }));
  return out;
}

const border = { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" };
const borders = { top: border, bottom: border, left: border, right: border };
function table(headers, rows, widths) {
  const total = widths.reduce((a, c) => a + c, 0);
  const cell = (text, w, head, bold) => new TableCell({
    borders, width: { size: w, type: WidthType.DXA },
    shading: head ? { fill: "E8F4F2", type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ children: [new TextRun({ text: String(text), bold: head || bold, size: 20 })] })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, widths[i], true)) }),
      ...rows.map((r) => new TableRow({ children: r.map((c, i) => cell(c, widths[i], false, r.bold && i === 0)) })),
    ],
  });
}
const gap = () => new Paragraph({ spacing: { after: 120 }, children: [] });

// model comparison from CSV
const cmpLines = fs.readFileSync(path.join(root, "reports", "model_comparison.csv"), "utf8").trim().split("\n").slice(1);
const nice = { GradientBoosting: "Gradient boosting", SVM: "SVM", LogisticRegression: "Logistic regression",
  RandomForest: "Random forest", XGBoost: "XGBoost" };
const cmpRows = cmpLines.map((l) => {
  const [m, ...v] = l.split(",");
  return [nice[m] || m, ...v.slice(0, 5).map((x) => Number(x).toFixed(3))];
});

const fiLines = fs.readFileSync(path.join(root, "powerbi", "data", "feature_importance.csv"), "utf8").trim().split("\n").slice(1, 7);
const fiRows = fiLines.map((l) => { const [f, v] = l.split(","); return [f, pct(Number(v))]; });

const bp = metrics.best_params;

const children = [
  // Title page
  new Paragraph({ spacing: { before: 2400, after: 200 }, children: [new TextRun({ text: "Credit Card Approval Prediction", bold: true, size: 52, font: FONT, color: "264653" })] }),
  new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: "Project report: machine learning model and Power BI dashboard", size: 28, color: "555555" })] }),
  new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: TEAL, space: 1 } }, children: [] }),
  p([b("Dataset: "), t("UCI Credit Approval (690 applications)")], { spacing: { before: 300, after: 80 } }),
  p([b("Final model: "), t("Gradient boosting with a tuned decision threshold")], { spacing: { after: 80 } }),
  p([b("Test results: "), t(`${pct(tm.accuracy)} accuracy, ROC AUC ${tm.roc_auc.toFixed(3)}`)], { spacing: { after: 80 } }),
  p([b("Tools: "), t("Python (pandas, scikit-learn, XGBoost), Streamlit, Power BI")]),
  new Paragraph({ children: [new PageBreak()] }),

  new Paragraph({ children: [new TextRun({ text: "Contents", bold: true, size: 32, color: "264653" })], spacing: { after: 200 } }),
  ...["1. Introduction", "2. Dataset", "3. Exploratory Data Analysis", "4. Methodology", "5. Results",
      "6. Power BI Dashboard", "7. Using the Model", "8. Limitations", "9. Future Work", "10. Conclusion"]
    .map((s) => new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: s, size: 24 })] })),
  new Paragraph({ children: [new PageBreak()] }),

  // 1
  h1("1. Introduction"),
  p("Banks receive a large number of credit card applications, and checking each one by hand is slow and not always consistent. Most of the information needed for a decision (income, debt, employment, credit history) is already in the application form, so a model can learn from past decisions and score new applications."),
  p("The goal of this project is to predict whether an application will be approved, explain which factors matter most, and present the results in a Power BI dashboard that a credit team could actually use. The model is not meant to replace a credit officer. A realistic use is to approve or reject the clear cases automatically and send the uncertain ones for manual review."),
  p("The project covers the full workflow:"),
  bullet("loading and cleaning the data"),
  bullet("exploratory analysis"),
  bullet("feature preprocessing"),
  bullet("comparing several models"),
  bullet("tuning the best ones"),
  bullet("choosing a decision threshold"),
  bullet("evaluating on unseen data"),
  bullet("exporting the scored data to Power BI"),

  // 2
  h1("2. Dataset"),
  p("The data is the Credit Approval dataset from the UCI Machine Learning Repository (file crx.data). It contains 690 real credit card applications with 15 input attributes and one target column. To protect the applicants, all attribute names and values were replaced with meaningless symbols (A1 to A16)."),
  p("I used the column names that are commonly given to this dataset. They are reasonable guesses based on the value ranges, not official definitions."),
  table(["Column", "Type", "Notes"], [
    ["Age, Debt, YearsEmployed", "Numeric", "Continuous values"],
    ["CreditScore, Income", "Numeric", "Integers, strongly right-skewed"],
    ["PriorDefault (A9), Employed (A10)", "Binary (t/f)", "Strongest predictors"],
    ["Gender, Married, BankCustomer", "Categorical", "2 to 3 levels each"],
    ["EducationLevel, Ethnicity", "Categorical", "9 to 14 levels"],
    ["DriversLicense, Citizen", "Categorical", "Weak signal"],
    ["ZipCode", "Categorical", "Dropped, behaves like an ID"],
    ["Approved", "Target", "+ approved (307), - rejected (383)"],
  ], [3300, 1900, 3826]),
  gap(),
  p([b("Missing values. "), t("37 rows (5.4%) have at least one missing value, shown as \"?\" in the raw file. They are spread across Age, Gender, Married, BankCustomer, EducationLevel, Ethnicity and ZipCode. Dropping these rows would lose data from an already small dataset, so they are imputed inside the model pipeline instead.")]),
  p([b("Class balance. "), t("44.5% of applications are approved and 55.5% rejected. That is close enough to balanced that no resampling was needed.")]),

  // 3
  h1("3. Exploratory Data Analysis"),
  p("Before modelling I looked at how each attribute relates to the outcome. These are the main findings."),
  ...image("03_approval_by_category.png", 1800, 480, 600, "Figure 1. Approval rate by A9 flag, employment and citizenship"),
  bullet([b("A9 flag (PriorDefault). "), t("This is the biggest factor by far. Applicants with A9 = t were approved 78.7% of the time, compared with only 7.0% for A9 = f. Because \"t\" goes with approval, the column most likely means \"no prior default\" rather than \"has defaulted\". In the dashboard it is labelled neutrally as the A9 flag.")]),
  bullet([b("Employment. "), t("70.8% of employed applicants were approved, against 24.8% of the rest.")]),
  bullet([b("Income, years employed and credit score. "), t("All three are clearly higher for approved applicants. Every applicant with income above 10,000 was approved.")]),
  bullet([b("Age. "), t("Approval rises steadily with age, from about 38% for under-25s to about 68% for over-55s.")]),
  ...image("02_numeric_by_outcome.png", 2160, 480, 600, "Figure 2. Numeric features by outcome (outliers hidden)"),
  p("The numeric features are heavily skewed. Most applicants have small values, and a few have very large ones (Income has a skewness of about 13). This matters for linear models and SVMs, so these columns were log-transformed (see section 4)."),

  // 4
  h1("4. Methodology"),
  h2("4.1 Train/test split"),
  p("I set aside 20% of the data (138 applications) as a test set, using a stratified split so that both sets keep the same approval rate. The test set was used only once, at the very end. All model selection, tuning and threshold choice was done on the remaining 552 training rows."),
  h2("4.2 Preprocessing"),
  p("All preprocessing steps live inside a single scikit-learn Pipeline together with the model. This has two benefits. First, nothing is learned from the validation folds during cross-validation, which prevents data leakage. Second, the saved model can take raw application data directly, with no separate cleaning step."),
  table(["Feature group", "Steps"], [
    ["Debt, YearsEmployed, CreditScore, Income", "Median imputation, then log(1 + x), then standard scaling"],
    ["Age", "Median imputation, then standard scaling"],
    ["Categorical features", "Most-frequent imputation, then one-hot encoding (levels with fewer than 10 rows grouped together, unknown levels ignored)"],
    ["ZipCode", "Dropped"],
  ], [3600, 5426]),
  gap(),
  h2("4.3 Model comparison"),
  p("I compared five common classifiers using their default settings: logistic regression, SVM, random forest, gradient boosting and XGBoost. With only 552 training rows, a single 5-fold cross-validation gives noisy results. So I used 5-fold CV repeated 3 times (15 fits per model) and ranked the models by ROC AUC, which measures ranking quality independently of any threshold."),
  table(["Model", "Accuracy", "Precision", "Recall", "F1", "ROC AUC"], cmpRows, [2426, 1320, 1320, 1320, 1320, 1320]),
  gap(),
  p("The models are close. The top four are within 0.006 AUC of each other, which is smaller than the standard deviation across folds (about 0.02). XGBoost was slightly behind. Rather than picking a winner from this table alone, I tuned the top three."),
  h2("4.4 Hyperparameter tuning"),
  p("Each of the top three models was tuned with RandomizedSearchCV: 40 random parameter combinations, 5-fold CV, optimising ROC AUC. Randomised search covers a wider range than a small grid at the same cost. The tuned CV scores were:"),
  bullet("Gradient boosting: AUC 0.939"),
  bullet("SVM: AUC 0.924"),
  bullet("Logistic regression: AUC 0.917"),
  p([t("Gradient boosting was selected. The best settings were "), b(`${bp.n_estimators} trees, max depth ${bp.max_depth}, learning rate ${bp.learning_rate}, subsample ${bp.subsample}`), t(". Shallow trees and row subsampling are both forms of regularisation, which makes sense for a dataset this small.")]),
  h2("4.5 Decision threshold"),
  p(`A classifier outputs a probability, and by default anything above 0.5 counts as approved. That default is arbitrary. I generated out-of-fold predictions on the training set and chose the threshold between 0.30 and 0.70 that gave the highest F1 score. The result was ${metrics.threshold}. The threshold is saved together with the model, so the prediction script and the web app both use it automatically.`),
  p("In a real bank the threshold would be set from business costs, for example the cost of a bad approval compared with the lost revenue from rejecting a good customer. The Power BI report includes a threshold slider so these trade-offs can be explored."),

  // 5
  h1("5. Results"),
  p("The tuned model was retrained on all 552 training rows and evaluated once on the 138 test applications."),
  table(["Accuracy", "Precision", "Recall", "F1 score", "ROC AUC"],
    [[pct(tm.accuracy), pct(tm.precision), pct(tm.recall), pct(tm.f1), tm.roc_auc.toFixed(3)]],
    [1805, 1805, 1805, 1805, 1806]),
  gap(),
  p("The test AUC (0.962) is in line with the cross-validated AUC (0.939). Some difference is expected with a test set this small, and a gap this size gives no sign of overfitting. Out of 138 test applications, 122 were classified correctly: 53 approvals and 69 rejections. There were 8 false approvals and 8 missed approvals."),
  ...image("05_confusion_matrix.png", 600, 480, 300, "Figure 3. Confusion matrix on the test set"),
  ...image("06_roc_curve.png", 600, 480, 300, "Figure 4. ROC curve on the test set"),
  h2("5.1 What drives the predictions"),
  p("Feature importance was measured with permutation importance: shuffle one column at a time and see how much the AUC drops. Unlike the built-in tree importance, this works on the original columns rather than the one-hot encoded ones, and it is not biased towards high-cardinality features."),
  table(["Feature", "Share of importance"], fiRows, [4513, 4513]),
  gap(),
  p("The A9 flag dominates, which matches the EDA. Income, debt, years employed and employment status add useful information on top of it. Gender, ethnicity and driver's licence contribute almost nothing. That is good from a fairness point of view, but it should still be checked formally before any real use (see section 8)."),

  // 6
  h1("6. Power BI Dashboard"),
  p("The Python pipeline exports four tables that Power BI reads directly. The main table, applications_scored.csv, has one row per application. Alongside the original fields it adds:"),
  bullet("readable labels for coded fields"),
  bullet("age, income, debt and credit score bands, with sort-order columns"),
  bullet("the model's approval probability and its decision at the chosen threshold"),
  bullet("whether each prediction was right (true/false positive, true/false negative)"),
  bullet("a risk segment"),
  bullet("a flag saying whether the row was in the training or test set"),
  p("The other three tables hold the model comparison, the feature importances and the test metrics."),
  ...image("powerbi/1_overview.png", 1920, 1080, 600, "Figure 5. Report page 1: Overview (mock-up drawn from the exported data)"),
  ...image("powerbi/2_drivers.png", 1920, 1080, 600, "Figure 6. Report page 2: Drivers"),
  ...image("powerbi/3_model_and_risk.png", 1920, 1080, 600, "Figure 7. Report page 3: Model & Risk"),
  p("The report has three pages:"),
  bullet([b("Overview. "), t("Total applications, approved count, approval rate and average predicted probability. Approval rate broken down by A9 flag, employment, income band and age band. Slicers for citizenship, employment and age.")]),
  bullet([b("Drivers. "), t("A heat map of approval rate by credit score band and debt band, an income vs. years employed scatter plot, the feature importance chart, and Power BI's Key Influencers visual.")]),
  bullet([b("Model and risk. "), t("Accuracy, precision, recall, F1 and AUC cards, the confusion matrix, the model comparison chart, the risk segment split and a probability histogram. There is also a threshold simulator: moving a slider recalculates the approval rate, accuracy, missed good applicants and risky approvals at that threshold. Finally, a review queue lists applicants in the uncertain middle band.")]),
  p("Applications are split into three risk segments by predicted probability:"),
  bullet("High Risk: below 0.3 (305 applications)"),
  bullet("Review: 0.3 to 0.7 (166 applications)"),
  bullet("Low Risk: above 0.7 (219 applications)"),
  p("In practice, the two outer groups could be handled automatically, and only the Review group would need a person to look at it."),
  p("Measures are written in DAX (powerbi/DAX_measures.dax). The data loads through Power Query with a folder parameter, so the report refreshes after the Python pipeline runs again. A few examples of the measures:"),
  table(["Measure", "DAX"], [
    ["Approval Rate", "DIVIDE([Approved Applications], [Total Applications])"],
    ["Model Recall", "DIVIDE([TP], [TP] + [FN])"],
    ["Approvals at Threshold", "CALCULATE([Total Applications], FILTER(Applications, Applications[ApprovalProbability] >= [Selected Threshold]))"],
  ], [2600, 6426]),
  gap(),

  // 7
  h1("7. Using the Model"),
  p("There are two ways to get predictions for new applicants:"),
  bullet([b("Batch scoring: "), t("python -m src.predict --input new.csv --output scored.csv adds a probability and an Approve/Reject decision to every row of a CSV file.")]),
  bullet([b("Web app: "), t("streamlit run app/streamlit_app.py opens a form where you enter one applicant's details and get the decision and probability back.")]),
  ...image("08_streamlit_app.png", 900, 1000, 330, "Figure 8. Streamlit app"),
  p("To rebuild everything from scratch, follow these steps:"),
  step("Install the packages: pip install -r requirements.txt"),
  step("Run the pipeline: python main.py (about 25 seconds). This writes the charts, the model, the metrics and the Power BI tables."),
  step("Run the tests: pytest -q"),
  step("In Power BI Desktop, click Refresh."),

  // 8
  h1("8. Limitations"),
  bullet([b("Small dataset. "), t("690 rows is not much. One or two test applications moving either way changes test accuracy by about 1.5 points, so the cross-validated scores are the more reliable estimate.")]),
  bullet([b("Anonymised features. "), t("The meaning of each column is inferred, not documented, so business interpretations should be treated with care.")]),
  bullet([b("Fairness. "), t("The data includes gender, ethnicity and age, which are protected attributes under lending laws such as the US Equal Credit Opportunity Act. They have very little influence on this model, but a production system would need a proper fairness audit and would probably exclude them.")]),
  bullet([b("Old data. "), t("The dataset is decades old and from a single source. A model trained on it would not transfer directly to today's applicants.")]),

  // 9
  h1("9. Future Work"),
  bullet("Per-applicant explanations with SHAP values, so a rejected applicant can be told the main reasons."),
  bullet("Choosing the threshold from real business costs instead of F1."),
  bullet("Probability calibration, so a score of 0.8 really means an 80% chance of approval."),
  bullet("Serving the model through an API (FastAPI) in a Docker container, with automated tests in CI."),
  bullet("Monitoring for data drift once the model is in use."),

  // 10
  h1("10. Conclusion"),
  p(`This project produced a credit card approval model that reaches ${pct(tm.accuracy)} accuracy and an AUC of ${tm.roc_auc.toFixed(3)} on unseen data. It was chosen through repeated cross-validation, randomised tuning and a data-driven threshold, with the test set kept apart until the end. The analysis shows that the A9 flag (most likely a clean credit history) is the main driver, followed by income, debt and employment. The Power BI report turns the model output into something a credit team can use: an overview of approvals, the factors behind them, how well the model performs, and a slider to see what happens when the approval threshold changes.`),
];

const doc = new Document({
  creator: "Credit Card Approval Project",
  title: "Credit Card Approval Prediction: Project Report",
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 32, bold: true, color: "264653" },
        paragraph: { spacing: { before: 360, after: 160 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: 26, bold: true, color: TEAL },
        paragraph: { spacing: { before: 240, after: 100 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: "steps", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "888888" })] })] }) },
    children,
  }],
});

const out = path.join(root, "docs", "Credit_Card_Approval_Project_Report.docx");
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(out, buf); console.log("wrote", out); });
