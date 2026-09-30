from pathlib import Path

from report_data import summarize_csv


def summarize(source: Path):
    report = summarize_csv(source)
    print(f"Rows: {report['rows']}")
    print(f"Columns: {', '.join(report['columns'])}")


if __name__ == "__main__":
    summarize(Path(__file__).parent / "data" / "tickets.csv")
