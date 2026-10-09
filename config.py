from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

REPORT_FILE = REPORTS_DIR / "summary_report.csv"
ERROR_LOG = LOGS_DIR / "errors.log"

STATUS_COLUMN = "status"
DELIVERED_STATUS = "Delivered"
TOTAL_AMOUNT_COLUMN = "total_amount"
ENCODING = "utf-8"