// One query per block (Blank Query > Advanced Editor). Needs a text parameter
// DataFolder pointing at ...\credit-card-approval\powerbi\data\

// Applications
let
    Source   = Csv.Document(File.Contents(DataFolder & "applications_scored.csv"),
                            [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Headers  = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed    = Table.TransformColumnTypes(Headers, {
        {"ApplicantID", Int64.Type}, {"Age", type number}, {"Debt", type number},
        {"YearsEmployed", type number}, {"CreditScore", Int64.Type}, {"Income", Int64.Type},
        {"Approved", Int64.Type}, {"ApprovalProbability", type number},
        {"PredictedApproved", Int64.Type},
        {"AgeBandOrder", Int64.Type}, {"IncomeBandOrder", Int64.Type},
        {"CreditScoreBandOrder", Int64.Type}, {"DebtBandOrder", Int64.Type},
        {"RiskSegmentOrder", Int64.Type}
    }, "en-US")
in
    Typed

// ModelComparison
let
    Source  = Csv.Document(File.Contents(DataFolder & "model_comparison.csv"), [Delimiter = ",", Encoding = 65001]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed   = Table.TransformColumnTypes(Headers, {
        {"accuracy", type number}, {"precision", type number}, {"recall", type number},
        {"f1", type number}, {"roc_auc", type number}}, "en-US"),
    Long    = Table.UnpivotOtherColumns(Typed, {"Model"}, "Metric", "Score")
in
    Long

// FeatureImportance
let
    Source  = Csv.Document(File.Contents(DataFolder & "feature_importance.csv"), [Delimiter = ",", Encoding = 65001]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed   = Table.TransformColumnTypes(Headers, {{"Importance", type number}}, "en-US")
in
    Typed

// TestMetrics
let
    Source  = Csv.Document(File.Contents(DataFolder & "test_metrics.csv"), [Delimiter = ",", Encoding = 65001]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed   = Table.TransformColumnTypes(Headers, {{"Value", type number}}, "en-US")
in
    Typed
