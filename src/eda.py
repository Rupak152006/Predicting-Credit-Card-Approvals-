import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from src.config import FIGURES_DIR, NUMERIC_FEATURES

APPROVED, REJECTED = "#2a9d8f", "#e76f51"


def run_eda(df) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    label = df["Approved"].map({1: "Approved", 0: "Rejected"})
    palette = {"Approved": APPROVED, "Rejected": REJECTED}

    # 1. Class balance
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.countplot(x=label, hue=label, palette=palette, legend=False, ax=ax)
    ax.set(title="Application outcomes", xlabel="", ylabel="Applications")
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "01_class_balance.png", dpi=120); plt.close(fig)

    # 2. Numeric distributions by outcome
    fig, axes = plt.subplots(1, len(NUMERIC_FEATURES), figsize=(18, 4))
    for ax, col in zip(axes, NUMERIC_FEATURES):
        sns.boxplot(x=label, y=df[col], hue=label, palette=palette, legend=False, ax=ax, showfliers=False)
        ax.set(title=col, xlabel="", ylabel="")
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "02_numeric_by_outcome.png", dpi=120); plt.close(fig)

    # 3. Approval rate by key categorical drivers
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, col in zip(axes, ["PriorDefault", "Employed", "Citizen"]):
        rate = df.groupby(col)["Approved"].mean().mul(100).sort_values()
        rate.plot.barh(ax=ax, color=APPROVED)
        ax.set(title=f"Approval rate by {col}", xlabel="Approval rate (%)", ylabel="")
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "03_approval_by_category.png", dpi=120); plt.close(fig)

    # 4. Correlation heatmap
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(df[NUMERIC_FEATURES + ["Approved"]].corr(), annot=True, fmt=".2f",
                cmap="RdBu_r", center=0, ax=ax)
    ax.set_title("Correlation (numeric features)")
    fig.tight_layout(); fig.savefig(FIGURES_DIR / "04_correlation.png", dpi=120); plt.close(fig)
