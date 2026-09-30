"""Provided CSV logic. The workshop focuses on the interface in main.py."""
import csv
from pathlib import Path


class SummaryError(Exception):
    def __init__(self, message: str, hint: str):
        self.message, self.hint = message, hint
        super().__init__(message)


def summarize_csv(source: Path, encoding: str = "utf-8") -> dict:
    """Count nonblank data records and return the header names. Never writes files."""
    try:
        with source.open(encoding=encoding, newline="") as stream:
            reader = csv.reader(stream, strict=True)
            header = next(reader, None)
            if not header or not any(name.strip() for name in header):
                raise SummaryError(
                    "The CSV has no header row.",
                    "Add column names as the first row, then try again.",
                )
            rows = 0
            for row in reader:
                if not row:
                    continue
                if len(row) != len(header):
                    raise SummaryError(
                        f"CSV record ending on line {reader.line_num} has {len(row)} fields; "
                        f"the header has {len(header)}.",
                        "Check commas and quoting in that record.",
                    )
                rows += 1
    except (OSError, UnicodeError, LookupError, csv.Error) as exc:
        raise SummaryError(
            f"Cannot read {source}: {exc}",
            "Check the file, its CSV quoting and the selected encoding.",
        ) from None
    return {"rows": rows, "columns": header}
