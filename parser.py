"""
parser.py  –  Parse LMS exports (CSV or XLSX) into a clean DataFrame.

The LMS format has 2 metadata rows at the top:
  Row 0: "Exercise Name : <name>"
  Row 1: "Course Name : <name>"
  Row 2: column headers
  Row 3+: data

For XLSX the same structure is expected on the first sheet.
"""

import re
import pandas as pd
import io


REQUIRED_COLS = {
    "Name", "UserName", "Registration Number", "Email",
    "Rank", "Total Attempts", "Marks Obtained", "Total Marks",
    "Percentage", "Grade", "Contact Number",
}


def _extract_meta(raw_value: str, key: str) -> str:
    """Pull the value after 'Key : ' from a metadata cell."""
    val = str(raw_value).strip().strip('"')
    match = re.search(rf"{re.escape(key)}\s*:\s*(.+)", val, re.IGNORECASE)
    return match.group(1).strip() if match else val


def _clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise column types and fill optional columns."""
    df = df.copy()
    # Strip whitespace from string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    # Coerce numeric columns
    for col in ["Rank", "Total Attempts", "Marks Obtained", "Total Marks",
                "Registration Number"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    if "Percentage" in df.columns:
        df["Percentage"] = pd.to_numeric(df["Percentage"], errors="coerce").fillna(0.0)

    # Fill optional columns if missing
    for col in ["Section", "Standards"]:
        if col not in df.columns:
            df[col] = "-"

    return df


def parse_lms_file(file_obj) -> tuple:
    """
    Parse an uploaded LMS file.

    Parameters
    ----------
    file_obj : file-like
        A Streamlit UploadedFile (or any BytesIO / file handle).

    Returns
    -------
    df : pd.DataFrame
        Clean student data.
    exercise : str
        Exercise name extracted from metadata.
    course : str
        Course name extracted from metadata.
    """
    name = getattr(file_obj, "name", "")
    ext  = name.rsplit(".", 1)[-1].lower() if "." in name else "csv"

    if ext == "xlsx":
        # ── XLSX branch ──────────────────────────────────────────────────────
        raw = pd.read_excel(file_obj, header=None, sheet_name=0)

        if len(raw) < 3:
            raise ValueError("File has fewer than 3 rows. Expected 2 metadata rows + header + data.")

        exercise = _extract_meta(str(raw.iloc[0, 0]), "Exercise Name")
        course   = _extract_meta(str(raw.iloc[1, 0]), "Course Name")

        header = raw.iloc[2].tolist()
        data   = raw.iloc[3:].copy()
        data.columns = header
        data = data.reset_index(drop=True)

    else:
        # ── CSV branch ───────────────────────────────────────────────────────
        content = file_obj.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="replace")

        lines = content.splitlines()
        if len(lines) < 3:
            raise ValueError("File has fewer than 3 rows. Expected 2 metadata rows + header + data.")

        # Extract metadata from first two lines
        exercise = _extract_meta(lines[0], "Exercise Name")
        course   = _extract_meta(lines[1], "Course Name")

        # Parse data starting from header row (line index 2)
        data_str = "\n".join(lines[2:])
        data = pd.read_csv(io.StringIO(data_str))
        data = data.reset_index(drop=True)

    # ── Shared validation & cleaning ─────────────────────────────────────────
    # Drop fully-empty rows
    data = data.dropna(how="all")

    missing = REQUIRED_COLS - set(data.columns)
    if missing:
        raise ValueError(
            f"File is missing required columns: {', '.join(sorted(missing))}\n"
            f"Found: {', '.join(str(c) for c in data.columns)}"
        )

    df = _clean_df(data)
    return df, exercise, course
