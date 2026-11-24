"""Mock-ups of the three Power BI report pages, drawn from the exported CSVs.

These are not Power BI screenshots. They follow the layout in powerbi/DASHBOARD_GUIDE.md
so the README and report have something to show before the .pbix is built.

    python -m src.dashboard_preview
"""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.ticker import PercentFormatter

from src.config import FIGURES_DIR, POWERBI_DIR, REPORTS_DIR

TEAL, CORAL, GOLD, NAVY = "#2a9d8f", "#e76f51", "#e9c46a", "#264653"
GREY, CANVAS, LINE = "#605e5c", "#eaeaea", "#e1dfdd"
PAGES = ["Overview", "Drivers", "Model & Risk"]
OUT_DIR = FIGURES_DIR / "powerbi"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": LINE,
                     "axes.labelcolor": GREY, "xtick.color": GREY, "ytick.color": GREY,
                     "axes.spines.top": False, "axes.spines.right": False})

# canvas coordinates: figure fraction, report area starts right of the filter pane
X0, X1, Y0, Y1 = 0.175, 0.99, 0.065, 0.895


def frame(page_idx, slicers):
    fig = plt.figure(figsize=(16, 9), facecolor=CANVAS)
    # header bar
    fig.patches.append(Rectangle((0, 0.94), 1, 0.06, transform=fig.transFigure, color="#252423"))
    fig.text(0.012, 0.968, "Credit Card Approvals", color="white", fontsize=13, weight="bold", va="center")
    fig.text(0.99, 0.968, "Data refreshed from main.py  |  690 applications", color="#c8c6c4",
             fontsize=9, ha="right", va="center")
    # page title
    fig.text(X0, 0.915, PAGES[page_idx], fontsize=16, weight="bold", color=NAVY, va="center")
    # filter pane
    fig.patches.append(Rectangle((0, 0.045), 0.16, 0.895, transform=fig.transFigure, color="white"))
    fig.text(0.012, 0.91, "Filters", fontsize=12, weight="bold", color=NAVY)
    y = 0.865
    for title, items in slicers:
        fig.text(0.012, y, title, fontsize=9, weight="bold", color=GREY)
        y -= 0.03
        for item in items:
            fig.patches.append(Rectangle((0.014, y - 0.006), 0.009, 0.016, transform=fig.transFigure,
                                         fill=False, edgecolor=GREY, lw=0.8))
            fig.text(0.03, y + 0.002, item, fontsize=9, color="#323130", va="center")
            y -= 0.028
        y -= 0.02
    # page tabs
    fig.patches.append(Rectangle((0, 0), 1, 0.045, transform=fig.transFigure, color="#f3f2f1"))
    x = 0.175
    for i, name in enumerate(PAGES):
        w = 0.012 + 0.0075 * len(name)
        active = i == page_idx
        fig.patches.append(Rectangle((x, 0.006), w, 0.033, transform=fig.transFigure,
                                     color="white" if active else "#f3f2f1"))
        if active:
            fig.patches.append(Rectangle((x, 0.006), w, 0.004, transform=fig.transFigure, color=TEAL))
        fig.text(x + w / 2, 0.0225, name, ha="center", va="center", fontsize=9,
                 color="#323130" if active else GREY, weight="bold" if active else "normal")
        x += w + 0.004
    return fig


def visual(fig, rect, title=None, pad=(0.05, 0.045, 0.012, 0.05)):
    """White card at rect=(x, y, w, h) in canvas fraction; returns the axes inside it.

    pad = (left, bottom, right, top) in figure fraction, room for tick labels and the title.
    """
    x, y, w, h = rect
    fx, fy = X0 + x * (X1 - X0), Y0 + y * (Y1 - Y0)
    fw, fh = w * (X1 - X0), h * (Y1 - Y0)
    fig.patches.append(FancyBboxPatch((fx, fy), fw, fh, boxstyle="round,pad=0,rounding_size=0.004",
                                      transform=fig.transFigure, facecolor="white", edgecolor=LINE, lw=0.8,
                                      zorder=0.5))
    if title:
        fig.text(fx + 0.008, fy + fh - 0.024, title, fontsize=10, weight="bold", color="#252423")
    else:
        pad = (0.008, 0.008, 0.008, 0.008)
    left, bottom, right, top = pad
    ax = fig.add_axes([fx + left, fy + bottom, fw - left - right, fh - bottom - top])
    ax.set_facecolor("white")
    ax.set_zorder(2)
    return ax


def kpi(fig, rect, value, label, color=NAVY):
    ax = visual(fig, rect)
    ax.axis("off")
    ax.text(0.04, 0.62, value, fontsize=24, weight="bold", color=color, transform=ax.transAxes, va="center")
    ax.text(0.04, 0.16, label, fontsize=10, color=GREY, transform=ax.transAxes)


def bar_labels(ax, bars, fmt="{:.0%}", horizontal=False):
    for b in bars:
        v = b.get_width() if horizontal else b.get_height()
        if horizontal:
            ax.text(v, b.get_y() + b.get_height() / 2, " " + fmt.format(v), va="center", fontsize=8, color=GREY)
        else:
            ax.text(b.get_x() + b.get_width() / 2, v, fmt.format(v), ha="center", va="bottom", fontsize=8, color=GREY)


def load():
    d = pd.read_csv(POWERBI_DIR / "applications_scored.csv", dtype={"PriorDefaultFlag": str})
    fi = pd.read_csv(POWERBI_DIR / "feature_importance.csv")
    mc = pd.read_csv(POWERBI_DIR / "model_comparison.csv")
    tm = pd.read_csv(POWERBI_DIR / "test_metrics.csv").set_index("Metric")["Value"]
    meta = json.loads((REPORTS_DIR / "metrics.json").read_text())
    return d, fi, mc, tm, meta


SLICERS = [("Citizen", ["By birth", "By naturalisation", "Other"]),
           ("Employed", ["Yes", "No"]),
           ("A9 flag", ["True", "False"]),
           ("Age band", ["<25", "25-34", "35-44", "45-54", "55+"])]


def page_overview(d):
    fig = frame(0, SLICERS)
    n, appr = len(d), d.Approved.sum()
    for i, (v, lab) in enumerate([(f"{n:,}", "Total Applications"), (f"{appr:,}", "Approved Applications"),
                                  (f"{appr / n:.1%}", "Approval Rate"),
                                  (f"{d.ApprovalProbability.mean():.1%}", "Avg Approval Probability")]):
        kpi(fig, (i * 0.25 + 0.002, 0.82, 0.24, 0.17), v, lab)

    ax = visual(fig, (0.002, 0.42, 0.24, 0.38), "Applications by outcome")
    v = d.ActualStatus.value_counts().reindex(["Approved", "Rejected"])
    ax.pie(v, colors=[TEAL, CORAL], startangle=90, counterclock=False, wedgeprops=dict(width=0.38),
           autopct=lambda p: f"{p:.0f}%", pctdistance=0.8, textprops=dict(color="white", fontsize=9, weight="bold"))
    ax.text(0, 0, f"{n}", ha="center", va="center", fontsize=16, weight="bold", color=NAVY)
    ax.legend(v.index, loc="lower center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False, fontsize=8)

    ax = visual(fig, (0.252, 0.42, 0.24, 0.38), "Approval rate by A9 flag")
    r = d.groupby("PriorDefaultFlag").Approved.mean().reindex(["False", "True"])
    bars = ax.barh(r.index, r.values, color=[CORAL, TEAL], height=0.55)
    bar_labels(ax, bars, horizontal=True); ax.set_xlim(0, 1.1); ax.xaxis.set_major_formatter(PercentFormatter(1))

    ax = visual(fig, (0.502, 0.42, 0.24, 0.38), "Approval rate by employment")
    r = d.groupby("EmployedLabel").Approved.mean().reindex(["No", "Yes"])
    bars = ax.barh(r.index, r.values, color=[CORAL, TEAL], height=0.55)
    bar_labels(ax, bars, horizontal=True); ax.set_xlim(0, 1.1); ax.xaxis.set_major_formatter(PercentFormatter(1))

    ax = visual(fig, (0.752, 0.42, 0.24, 0.38), "Approval rate by citizenship",
                pad=(0.075, 0.045, 0.02, 0.05))
    r = d.groupby("CitizenLabel").Approved.mean().sort_values()
    bars = ax.barh(r.index, r.values, color=TEAL, height=0.55)
    bar_labels(ax, bars, horizontal=True); ax.set_xlim(0, 1.1); ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.tick_params(axis="y", labelsize=8)

    ax = visual(fig, (0.002, 0.0, 0.49, 0.4), "Approval rate by income band")
    o = ["0", "1-500", "501-2k", "2k-10k", "10k+"]
    r = d.groupby("IncomeBand").Approved.mean().reindex(o)
    bars = ax.bar(o, r.values, color=TEAL, width=0.6); bar_labels(ax, bars)
    ax.set_ylim(0, 1.12); ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax = visual(fig, (0.502, 0.0, 0.49, 0.4), "Applications and approval rate by age band",
                pad=(0.04, 0.045, 0.04, 0.05))
    o = ["<25", "25-34", "35-44", "45-54", "55+"]
    ax.bar(o, d.AgeBand.value_counts().reindex(o).values, color="#b7dcd7", width=0.6, label="Applications")
    ax2 = ax.twinx()
    ax2.set_zorder(3)
    ax2.plot(o, d.groupby("AgeBand").Approved.mean().reindex(o).values, color=NAVY, marker="o", lw=2,
             label="Approval rate")
    ax2.set_ylim(0, 0.8); ax2.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax2.spines["right"].set_visible(True)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", bbox_to_anchor=(0.5, 1.0), frameon=False, fontsize=8)
    return fig


def page_drivers(d, fi):
    fig = frame(1, SLICERS)

    ax = visual(fig, (0.002, 0.5, 0.36, 0.5), "Approval rate: credit score band x debt band")
    rows, cols = ["0", "1-2", "3-5", "6-10", "11+"], ["<1", "1-3", "3-7", "7+"]
    m = d.pivot_table(index="CreditScoreBand", columns="DebtBand", values="Approved", aggfunc="mean")
    m = m.reindex(index=rows, columns=cols)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("pbi", [CORAL, GOLD, TEAL])
    ax.imshow(m.values, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    for i in range(len(rows)):
        for j in range(len(cols)):
            if not np.isnan(m.values[i, j]):
                ax.text(j, i, f"{m.values[i, j]:.0%}", ha="center", va="center", fontsize=9, color="#1b1b1b")
    ax.set_xticks(range(len(cols)), cols); ax.set_yticks(range(len(rows)), rows)
    ax.set_xlabel("Debt band"); ax.set_ylabel("Credit score band")

    ax = visual(fig, (0.372, 0.5, 0.36, 0.5), "Income vs years employed")
    for status, c in [("Rejected", CORAL), ("Approved", TEAL)]:
        s = d[d.ActualStatus == status]
        ax.scatter(s.Income + 1, s.YearsEmployed, s=14, alpha=0.6, color=c, label=status, edgecolors="none")
    ax.set_xscale("log"); ax.set_xlabel("Income + 1 (log scale)"); ax.set_ylabel("Years employed")
    ax.legend(frameon=False, fontsize=8, loc="upper left")

    ax = visual(fig, (0.742, 0.5, 0.25, 0.5), "Average values by outcome")
    g = d.groupby("ActualStatus")[["Debt", "YearsEmployed", "CreditScore"]].mean().reindex(["Approved", "Rejected"])
    x = np.arange(3)
    for k, (status, c) in enumerate([("Approved", TEAL), ("Rejected", CORAL)]):
        bars = ax.bar(x + (k - 0.5) * 0.36, g.loc[status].values, 0.36, color=c, label=status)
        bar_labels(ax, bars, fmt="{:.1f}")
    ax.set_xticks(x, ["Debt", "Years empl.", "Credit score"]); ax.legend(frameon=False, fontsize=8)

    ax = visual(fig, (0.002, 0.0, 0.49, 0.48), "Feature importance (permutation, final model)")
    f = fi.head(10)[::-1]
    bars = ax.barh(f.Feature, f.Importance, color=TEAL, height=0.6)
    bar_labels(ax, bars, fmt="{:.1%}", horizontal=True)
    ax.set_xlim(0, f.Importance.max() * 1.15); ax.xaxis.set_major_formatter(PercentFormatter(1))

    # Key influencers style panel
    ax = visual(fig, (0.502, 0.0, 0.49, 0.48), "Key influencers: what makes Approved more likely")
    ax.axis("off")
    base = d.Approved.mean()
    conds = [
        ("A9 flag is True", d.PriorDefaultFlag == "True"),
        ("Employed is Yes", d.EmployedLabel == "Yes"),
        ("Income is above 500", d.Income > 500),
        ("Years employed is above 3", d.YearsEmployed > 3),
        ("Credit score is above 2", d.CreditScore > 2),
    ]
    infl = sorted(((name, d.loc[c, "Approved"].mean() / d.loc[~c, "Approved"].mean(), d.loc[c, "Approved"].mean())
                   for name, c in conds), key=lambda t: -t[1])
    top = max(t[1] for t in infl)
    for i, (name, ratio, rate) in enumerate(infl):
        y = 0.88 - i * 0.19
        ax.text(0.0, y, f"When {name}", fontsize=10, color="#252423", transform=ax.transAxes, va="center")
        ax.text(0.0, y - 0.075, f"approval rate {rate:.0%} vs {base:.0%} overall", fontsize=8, color=GREY,
                transform=ax.transAxes, va="center")
        ax.add_patch(Rectangle((0.52, y - 0.05), 0.36 * ratio / top, 0.1, color=TEAL, transform=ax.transAxes))
        ax.text(0.52 + 0.36 * ratio / top + 0.015, y, f"{ratio:.1f}x", fontsize=11, weight="bold", color=NAVY,
                transform=ax.transAxes, va="center")
    return fig


def page_model(d, mc, tm, meta):
    thr = meta["threshold"]
    fig = frame(2, [("Dataset", ["Test", "Train"]), ("Risk segment", ["High Risk", "Review", "Low Risk"]),
                    ("Threshold", [])])
    # slider in the filter pane
    fig.patches.append(Rectangle((0.014, 0.505), 0.13, 0.004, transform=fig.transFigure, color=LINE))
    pos = 0.014 + 0.13 * (thr - 0.05) / 0.9
    fig.patches.append(Rectangle((0.014, 0.505), pos - 0.014, 0.004, transform=fig.transFigure, color=TEAL))
    fig.patches.append(matplotlib.patches.Circle((pos, 0.507), 0.006, transform=fig.transFigure, color=TEAL))
    fig.text(0.014, 0.48, f"{thr:.2f}", fontsize=10, weight="bold", color=NAVY)

    cards = [("Accuracy", "Model Accuracy"), ("Precision", "Model Precision"), ("Recall", "Model Recall"),
             ("F1", "Model F1"), ("ROC AUC", "ROC AUC")]
    for i, (key, lab) in enumerate(cards):
        v = tm[key]
        kpi(fig, (i * 0.2 + 0.002, 0.82, 0.19, 0.17), f"{v:.3f}" if key == "ROC AUC" else f"{v:.1%}", lab)

    t = d[d.Dataset == "Test"]
    ax = visual(fig, (0.002, 0.4, 0.24, 0.4), "Confusion matrix (test set)")
    cm = pd.crosstab(t.ActualStatus, t.PredictedStatus).reindex(index=["Approved", "Rejected"],
                                                                 columns=["Approved", "Rejected"])
    colors = np.array([[TEAL, "#f6d5cc"], ["#f6d5cc", TEAL]])
    for i in range(2):
        for j in range(2):
            ax.add_patch(Rectangle((j, 1 - i), 1, 1, color=colors[i, j], ec="white", lw=3))
            ax.text(j + 0.5, 1.5 - i, cm.values[i, j], ha="center", va="center", fontsize=18, weight="bold",
                    color="white" if i == j else NAVY)
    ax.set_xlim(0, 2); ax.set_ylim(0, 2)
    ax.set_xticks([0.5, 1.5], ["Approved", "Rejected"]); ax.set_yticks([1.5, 0.5], ["Approved", "Rejected"])
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
    for s in ax.spines.values():
        s.set_visible(False)

    ax = visual(fig, (0.252, 0.4, 0.34, 0.4), "Model comparison (5x3 CV)",
                pad=(0.065, 0.045, 0.012, 0.075))
    mc = mc.sort_values("roc_auc")
    y = np.arange(len(mc))
    for k, (m, c) in enumerate([("roc_auc", NAVY), ("f1", TEAL), ("accuracy", GOLD)]):
        ax.barh(y + (k - 1) * 0.26, mc[m], 0.26, color=c, label={"roc_auc": "AUC"}.get(m, m.title()))
    names = {"GradientBoosting": "Gradient boost.", "LogisticRegression": "Logistic reg.",
             "RandomForest": "Random forest", "SVM": "SVM", "XGBoost": "XGBoost"}
    ax.set_yticks(y, mc.Model.map(names))
    ax.set_xlim(0.7, 0.95)
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 0.98))
    ax.tick_params(axis="y", labelsize=8)

    ax = visual(fig, (0.602, 0.4, 0.18, 0.4), "Risk segments")
    o = ["High Risk", "Review", "Low Risk"]
    v = d.RiskSegment.value_counts().reindex(o)
    ax.pie(v, colors=[CORAL, GOLD, TEAL], startangle=90, counterclock=False, wedgeprops=dict(width=0.38),
           autopct=lambda p: f"{p * len(d) / 100:.0f}", pctdistance=0.8,
           textprops=dict(color="white", fontsize=8, weight="bold"))
    ax.legend(o, loc="lower center", bbox_to_anchor=(0.5, -0.16), ncol=3, frameon=False, fontsize=7)

    # threshold simulator cards
    p, a = t.ApprovalProbability, t.Approved
    sim = [(f"{(d.ApprovalProbability >= thr).mean():.1%}", "Approval rate at threshold"),
           (f"{((p >= thr) == (a == 1)).mean():.1%}", "Accuracy at threshold"),
           (f"{((a == 1) & (p < thr)).sum()}", "Missed good applicants"),
           (f"{((a == 0) & (p >= thr)).sum()}", "Risky approvals")]
    for i, (val, lab) in enumerate(sim):
        ax = visual(fig, (0.792, 0.4 + (3 - i) * 0.1, 0.2, 0.095))
        ax.axis("off")
        ax.text(0.03, 0.5, val, fontsize=15, weight="bold", color=NAVY if i < 2 else CORAL,
                transform=ax.transAxes, va="center")
        ax.text(0.42, 0.5, lab, fontsize=8, color=GREY, transform=ax.transAxes, va="center")

    ax = visual(fig, (0.002, 0.0, 0.49, 0.38), "Distribution of approval probability")
    bins = np.linspace(0, 1, 11)
    ax.hist([d[d.Approved == 1].ApprovalProbability, d[d.Approved == 0].ApprovalProbability], bins=bins,
            stacked=True, color=[TEAL, CORAL], label=["Approved", "Rejected"], rwidth=0.85)
    ax.axvline(thr, color=NAVY, ls="--", lw=1.2)
    ax.text(thr + 0.015, ax.get_ylim()[1] * 0.9, f"threshold {thr:.2f}", fontsize=8, color=NAVY)
    ax.set_xlabel("Approval probability"); ax.legend(frameon=False, fontsize=8, loc="upper right")

    ax = visual(fig, (0.502, 0.0, 0.49, 0.38), "Review queue (probability 0.3 to 0.7)")
    ax.axis("off")
    q = d[d.RiskSegment == "Review"].sort_values("ApprovalProbability", ascending=False).head(7)
    cols = ["ApplicantID", "Age", "Income", "Debt", "CreditScore", "ApprovalProbability", "ActualStatus"]
    heads = ["ID", "Age", "Income", "Debt", "Credit score", "Probability", "Actual"]
    xs = [0.0, 0.1, 0.2, 0.33, 0.45, 0.62, 0.82]
    for x, h in zip(xs, heads):
        ax.text(x, 0.95, h, fontsize=9, weight="bold", color="#252423", transform=ax.transAxes)
    ax.plot([0, 1], [0.9, 0.9], color=LINE, transform=ax.transAxes, lw=1)
    for r, (_, row) in enumerate(q.iterrows()):
        yy = 0.8 - r * 0.115
        if r % 2 == 0:
            ax.add_patch(Rectangle((-0.01, yy - 0.045), 1.02, 0.11, color="#f7f7f7", transform=ax.transAxes))
        vals = [f"{row.ApplicantID}", f"{row.Age:.0f}" if pd.notna(row.Age) else "-", f"{row.Income:,}",
                f"{row.Debt:.2f}", f"{row.CreditScore}", f"{row.ApprovalProbability:.1%}", row.ActualStatus]
        for x, v in zip(xs, vals):
            color = (TEAL if v == "Approved" else CORAL) if x == 0.82 else "#323130"
            ax.text(x, yy, v, fontsize=9, color=color, transform=ax.transAxes, va="center")
    return fig


def render():
    d, fi, mc, tm, meta = load()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pages = [page_overview(d), page_drivers(d, fi), page_model(d, mc, tm, meta)]
    names = ["1_overview.png", "2_drivers.png", "3_model_and_risk.png"]
    for fig, name in zip(pages, names):
        fig.savefig(OUT_DIR / name, dpi=120, facecolor=CANVAS)
    # page 1 doubles as the README header image
    pages[0].savefig(FIGURES_DIR / "powerbi_dashboard_preview.png", dpi=110, facecolor=CANVAS)
    for fig in pages:
        plt.close(fig)


if __name__ == "__main__":
    render()
