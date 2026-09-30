"""Export only participant-authored CLI files, never credentials or infrastructure."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).parent


def export(output: Path = ROOT / "submission.zip"):
    files = [ROOT / "cli.py", ROOT / "USAGE.md"]
    # Optional modules must live in commands/. No arbitrary filesystem traversal.
    commands = ROOT / "commands"
    if commands.exists() and not commands.is_symlink():
        files.extend(
            p
            for p in commands.rglob("*.py")
            if not p.is_symlink()
            and not any(parent.is_symlink() for parent in p.parents if parent != ROOT.parent)
        )
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for file in files:
            if file.exists() and not file.is_symlink():
                archive.write(file, file.relative_to(ROOT))
    return output


if __name__ == "__main__":
    print(export())
