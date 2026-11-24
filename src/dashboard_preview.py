"""Render a static PNG preview of the Power BI dashboard from the exported CSVs."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import PercentFormatter

from src.config import FIGURES_DIR, POWERBI_DIR

T, C, Y, N, BG = "#2a9d8f", "#e76f51", "#e9c46a", "#264653", "#F6F8FA"


def _style(ax, title):
    ax.set_title(title, loc="left", fontsize=12, color=N, weight="bold")
    ax.set_facecolor("white")
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)


def render() -> None:
    d = pd.read_csv(POWERBI_DIR / "applications_scored.csv", dtype={"PriorDefaultFlag": str})
    fi = pd.read_csv(POWERBI_DIR / "feature_importance.csv")
    tm = pd.read_csv(POWERBI_DIR / "test_metrics.csv").set_index("Metric")["Value"]

    fig = plt.figure(figsize=(16, 9), facecolor=BG)
    gs = fig.add_gridspec(3, 4, height_ratios=[0.5, 1, 1], hspace=0.5, wspace=0.45,
                          left=0.1, right=0.95, top=0.9, bottom=0.07)
    fig.suptitle("Credit Card Approvals: Dashboard Preview", x=0.1, ha="left",
                 fontsize=18, color=N, weight="bold")

    kpis = [("Total Applications", f"{len(d):,}"), ("Approval Rate", f"{d.Approved.mean():.1%}"),
            ("Model ROC AUC (test)", f"{tm['ROC AUC']:.3f}"), ("Accuracy (test)", f"{tm['Accuracy']:.1%}")]
    for i, (k, v) in enumerate(kpis):
        ax = fig.add_subplot(gs[0, i]); ax.set_facecolor("white"); ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color("#E9ECEF")
        ax.text(0.05, 0.6, v, fontsize=24, weight="bold", color=N, transform=ax.transAxes)
        ax.text(0.05, 0.18, k, fontsize=11, color="#6c757d", transform=ax.transAxes)

    ax = fig.add_subplot(gs[1, 0]); v = d.ActualStatus.value_counts().reindex(["Approved", "Rejected"])
    ax.pie(v, labels=v.index, colors=[T, C], wedgeprops=dict(width=0.4), autopct="%1.0f%%", startangle=90)
    ax.set_title("Outcomes", loc="left", fontsize=12, color=N, weight="bold")

    ax = fig.add_subplot(gs[1, 1]); r = d.groupby("PriorDefaultFlag").Approved.mean().reindex(["False", "True"])
    ax.barh(r.index, r.values, color=[C, T]); _style(ax, "Approval rate by A9 flag")
    ax.xaxis.set_major_formatter(PercentFormatter(1))

    ax = fig.add_subplot(gs[1, 2]); o = ["0", "1-500", "501-2k", "2k-10k", "10k+"]
    r = d.groupby("IncomeBand").Approved.mean().reindex(o)
    ax.bar(o, r.values, color=T); _style(ax, "Approval rate by income band"); ax.tick_params(axis="x", labelsize=8)
    ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax = fig.add_subplot(gs[1, 3]); o = ["<25", "25-34", "35-44", "45-54", "55+"]
    ax.bar(o, d.AgeBand.value_counts().reindex(o).values, color="#cfe8e5")
    ax2 = ax.twinx(); ax2.plot(o, d.groupby("AgeBand").Approved.mean().reindex(o).values, color=N, marker="o")
    ax2.yaxis.set_major_formatter(PercentFormatter(1, decimals=0)); ax2.spines["top"].set_visible(False)
    _style(ax, "Volume & approval rate by age")

    ax = fig.add_subplot(gs[2, 0:2]); f = fi.head(8)[::-1]
    ax.barh(f.Feature, f.Importance, color=T); _style(ax, "Feature importance (final model)")
    ax.xaxis.set_major_formatter(PercentFormatter(1))

    ax = fig.add_subplot(gs[2, 2]); t = d[d.Dataset == "Test"]
    cm = pd.crosstab(t.ActualStatus, t.PredictedStatus)
    ax.imshow(cm.values, cmap="Greens", vmin=0, vmax=cm.values.max() * 1.6)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm.values[i, j], ha="center", va="center", fontsize=16, color=N, weight="bold")
    ax.set_xticks([0, 1], cm.columns); ax.set_yticks([0, 1], cm.index)
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual"); ax.grid(False)
    ax.set_title("Confusion matrix (test)", loc="left", fontsize=12, color=N, weight="bold")

    ax = fig.add_subplot(gs[2, 3]); o = ["High Risk", "Review", "Low Risk"]
    ax.bar(o, d.RiskSegment.value_counts().reindex(o).values, color=[C, Y, T]); _style(ax, "Risk segments")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / "powerbi_dashboard_preview.png", dpi=110, facecolor=BG)
    plt.close(fig)


if __name__ == "__main__":
    render()
