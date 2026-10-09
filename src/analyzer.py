import logging
from pathlib import Path

import pandas as pd

from config import (
    DATA_DIR,
    REPORTS_DIR,
    LOGS_DIR,
    REPORT_FILE,
    ERROR_LOG,
    STATUS_COLUMN,
    DELIVERED_STATUS,
    TOTAL_AMOUNT_COLUMN,
    ENCODING,
)


class OrderAnalyzer:
    def __init__(self):
        self.data_dir = Path(DATA_DIR)
        self.reports_dir = Path(REPORTS_DIR)
        self.logs_dir = Path(LOGS_DIR)
        self.report_file = Path(REPORT_FILE)
        self.error_log = Path(ERROR_LOG)

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger("OrderAnalyzer")
        self.logger.setLevel(logging.ERROR)

        if not self.logger.handlers:
            file_handler = logging.FileHandler(self.error_log, encoding=ENCODING)
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def load_file(self, file_path: Path):
        """Читает CSV и проверяет обязательные колонки."""
        file_path = Path(file_path)

        try:
            df = pd.read_csv(file_path, encoding=ENCODING)
        except Exception as exc:
            self.logger.error("Ошибка чтения файла %s: %s", file_path, exc)
            return None

        if df.empty:
            self.logger.error("Файл %s пуст", file_path)
            return None

        required_columns = [STATUS_COLUMN, TOTAL_AMOUNT_COLUMN]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            self.logger.error(
                "В файле %s отсутствуют колонки: %s",
                file_path,
                missing_columns,
            )
            return None

        df[TOTAL_AMOUNT_COLUMN] = pd.to_numeric(
            df[TOTAL_AMOUNT_COLUMN], errors="coerce"
        )

        if df[TOTAL_AMOUNT_COLUMN].isna().any():
            self.logger.error(
                "В файле %s есть нечисловые значения в колонке %s",
                file_path,
                TOTAL_AMOUNT_COLUMN,
            )
            return None

        return df

    def filter_delivered(self, df: pd.DataFrame) -> pd.DataFrame:
        """Оставляет только доставленные заказы."""
        return df[df[STATUS_COLUMN] == DELIVERED_STATUS].copy()

    def calculate_metrics(self, df: pd.DataFrame):
        """Считает выручку, средний чек и количество заказов."""
        if df.empty:
            return 0.0, 0.0, 0

        total_revenue = df[TOTAL_AMOUNT_COLUMN].sum()
        average_check = df[TOTAL_AMOUNT_COLUMN].mean()
        orders_count = len(df)

        return total_revenue, average_check, orders_count

    def process_file(self, file_path: Path):
        """Обрабатывает один CSV-файл."""
        file_path = Path(file_path)

        df = self.load_file(file_path)
        if df is None:
            return None

        delivered_df = self.filter_delivered(df)
        total_revenue, average_check, orders_count = self.calculate_metrics(
            delivered_df
        )

        return {
            "file_name": file_path.name,
            "total_revenue": round(float(total_revenue), 2),
            "average_check": round(float(average_check), 2),
            "orders_count": int(orders_count),
        }

    def process_all(self):
        """Обрабатывает все CSV-файлы в папке data."""
        csv_files = sorted(self.data_dir.glob("*.csv"))

        results = []
        errors_count = 0

        for file_path in csv_files:
            result = self.process_file(file_path)

            if result is None:
                errors_count += 1
            else:
                results.append(result)

        report_df = pd.DataFrame(
            results,
            columns=[
                "file_name",
                "total_revenue",
                "average_check",
                "orders_count",
            ],
        )

        report_df.to_csv(self.report_file, index=False, encoding=ENCODING)

        return len(results), errors_count