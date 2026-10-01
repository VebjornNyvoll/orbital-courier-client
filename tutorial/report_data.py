"""Ferdig CSV-leser. Vi jobber med CLI-et i main.py."""
import csv
from pathlib import Path


class SummaryError(Exception):
    def __init__(self, message: str, hint: str):
        self.message, self.hint = message, hint
        super().__init__(message)


def summarize_csv(source: Path, encoding: str = "utf-8") -> dict:
    """Tell datarader som ikke er tomme, og returner kolonnenavnene. Endrer ikke filer."""
    try:
        with source.open(encoding=encoding, newline="") as stream:
            reader = csv.reader(stream, strict=True)
            header = next(reader, None)
            if not header or not any(name.strip() for name in header):
                raise SummaryError(
                    "CSV-fila mangler en header.",
                    "Legg til kolonnenavn på første rad og prøv igjen.",
                )
            rows = 0
            for row in reader:
                if not row:
                    continue
                if len(row) != len(header):
                    raise SummaryError(
                        f"CSV-raden som slutter på linje {reader.line_num} har {len(row)} felt. "
                        f"Headeren har {len(header)}.",
                        "Sjekk kommaer og anførselstegn i raden.",
                    )
                rows += 1
    except (OSError, UnicodeError, LookupError, csv.Error) as exc:
        raise SummaryError(
            f"Kan ikke lese {source}: {exc}",
            "Sjekk fila, anførselstegnene og valgt enkoding.",
        ) from None
    return {"rows": rows, "columns": header}
