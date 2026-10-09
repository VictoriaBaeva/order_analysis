from src.analyzer import OrderAnalyzer
from config import REPORT_FILE


def main():
    analyzer = OrderAnalyzer()
    processed_count, errors_count = analyzer.process_all()

    print(f"Обработано файлов: {processed_count}")
    print(f"Файлов с ошибками: {errors_count}")
    print(f"Итоговый отчёт: {REPORT_FILE}")


if __name__ == "__main__":
    main()