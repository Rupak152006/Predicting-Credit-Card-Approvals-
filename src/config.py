"""Central configuration: paths, column names, and constants."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
FIGURES_DIR = ROOT / "reports" / "figures"
REPORTS_DIR = ROOT / "reports"
POWERBI_DIR = ROOT / "powerbi" / "data"

RAW_FILE = RAW_DIR / "crx.data"
DATA_URLS = [
    "https://archive.ics.uci.edu/ml/machine-learning-databases/credit-screening/crx.data",
    "https://raw.githubusercontent.com/PacktWorkshops/The-Data-Science-Workshop/master/Chapter15/Dataset/crx.data",
]

# The UCI dataset is anonymised (A1..A16). These are the widely used
# interpretations of each attribute; they are descriptive labels, not ground truth.
COLUMNS = [
    "Gender", "Age", "Debt", "Married", "BankCustomer", "EducationLevel",
    "Ethnicity", "YearsEmployed", "PriorDefault", "Employed", "CreditScore",
    "DriversLicense", "Citizen", "ZipCode", "Income", "Approved",
]
NUMERIC_FEATURES = ["Age", "Debt", "YearsEmployed", "CreditScore", "Income"]
CATEGORICAL_FEATURES = [
    "Gender", "Married", "BankCustomer", "EducationLevel", "Ethnicity",
    "PriorDefault", "Employed", "DriversLicense", "Citizen",
]
DROP_FEATURES = ["ZipCode"]  # high-cardinality identifier-like field, no signal
TARGET = "Approved"

RANDOM_STATE = 42
TEST_SIZE = 0.2
