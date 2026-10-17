
from pathlib import Path
from fastmcp import FastMCP
import pandas as pd
mcp = FastMCP("MCP Master")

# Resolve the project's data directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = (PROJECT_ROOT / "data").resolve()


@mcp.tool()
def fetch_data(path: str) -> str:
    """Read a UTF-8 text file from the project's data directory."""
    requested_path = Path(path)

    # Accept paths such as "sample.txt" or "data/sample.txt".
    if requested_path.is_absolute():
        return "Error: Use a relative path inside the data directory."

    if ".." in requested_path.parts:
        return "Error: Parent-directory paths are not allowed."

    if requested_path.parts and requested_path.parts[0].lower() == "data":
        requested_path = Path(*requested_path.parts[1:])

    file_path = (DATA_DIR / requested_path).resolve()

    # Prevent paths and symlinks from escaping DATA_DIR.
    if not file_path.is_relative_to(DATA_DIR):
        return "Error: Access outside the data directory is not allowed."

    if not file_path.is_file():
        return "Error: File not found in the data directory."

    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return "Error: This file is not valid UTF-8 text."
    except OSError:
        return "Error: The file could not be read."



@mcp.tool()
def process_data(path: str) -> str:
    """Analyze a CSV file inside the project's data directory."""
    requested_path = Path(path)

    if requested_path.is_absolute():
        return "Error: Use a relative path inside the data directory."

    if ".." in requested_path.parts:
        return "Error: Parent-directory paths are not allowed."

    if requested_path.parts and requested_path.parts[0].lower() == "data":
        requested_path = Path(*requested_path.parts[1:])

    file_path = (DATA_DIR / requested_path).resolve()

    if not file_path.is_relative_to(DATA_DIR):
        return "Error: Access outside the data directory is not allowed."

    if file_path.suffix.lower() != ".csv":
        return "Error: Only CSV files are supported."

    if not file_path.is_file():
        return "Error: File not found in the data directory."

    try:
        df = pd.read_csv(file_path)

        missing = df.isnull().sum()
        missing_report = ", ".join(
            f"{column}: {count}"
            for column, count in missing.items()
        )

        return (
            "CSV Analysis Report\n"
            f"Rows: {df.shape[0]}\n"
            f"Columns: {df.shape[1]}\n"
            f"Missing values per column: {missing_report}\n"
            f"Duplicate rows: {df.duplicated(subset=["Product", "City", "Sales", "Quantity"]).sum()}"
        )

    except pd.errors.EmptyDataError:
        return "Error: The CSV file is empty."
    except pd.errors.ParserError:
        return "Error: The CSV file could not be parsed."
    except UnicodeDecodeError:
        return "Error: The CSV file encoding is not supported."
    except OSError:
        return "Error: The CSV file could not be read."



if __name__ == "__main__":
    mcp.run(transport="stdio")
