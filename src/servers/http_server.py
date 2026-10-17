
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth import StaticTokenVerifier

# Load environment variables from the current working directory's .env,
# if one exists. Environment variables already set take precedence.
load_dotenv()

# Require authentication instead of accidentally starting an
# unauthenticated HTTP server.
AUTH_TOKEN = os.environ.get("MCP_AUTH_TOKEN")

if not AUTH_TOKEN or not AUTH_TOKEN.strip():
    raise RuntimeError(
        "MCP_AUTH_TOKEN is required. Set it in your environment "
        "or in a .env file before starting the HTTP server."
    )

auth = StaticTokenVerifier(
    tokens={
        AUTH_TOKEN: {
            "sub": "mcp-master-user",
            "client_id": "mcp-master-client",
        }
    }
)

mcp = FastMCP("MCP Master HTTP", auth=auth)

# Use the working directory by default, or allow users to configure
# a dedicated data directory with MCP_MASTER_DATA_DIR.
PROJECT_ROOT = Path.cwd().resolve()

DATA_DIR = Path(
    os.environ.get("MCP_MASTER_DATA_DIR", str(PROJECT_ROOT / "data"))
).resolve()

CLEANED_DIR = (DATA_DIR / "cleaned").resolve()

# Prevent an existing "cleaned" symlink from redirecting output outside
# the configured data directory.
if not CLEANED_DIR.is_relative_to(DATA_DIR):
    raise RuntimeError(
        "The cleaned directory must remain inside the data directory."
    )


def get_safe_file_path(path: str) -> Path:
    """Resolve a relative path safely inside the configured data directory."""
    requested_path = Path(path)

    if requested_path.is_absolute() or ".." in requested_path.parts:
        raise ValueError(
            "Use a safe relative path inside the data directory."
        )

    # Accept both "sales.csv" and "data/sales.csv".
    if requested_path.parts and requested_path.parts[0].lower() == "data":
        requested_path = Path(*requested_path.parts[1:])

    file_path = (DATA_DIR / requested_path).resolve()

    if not file_path.is_relative_to(DATA_DIR):
        raise ValueError(
            "Access outside the data directory is not allowed."
        )

    return file_path


@mcp.tool()
def fetch_data(path: str) -> str:
    """Read a UTF-8 text file inside the configured data directory."""
    try:
        file_path = get_safe_file_path(path)

        if not file_path.is_file():
            return "Error: File not found."

        return file_path.read_text(encoding="utf-8")

    except ValueError as error:
        return f"Error: {error}"
    except (OSError, UnicodeDecodeError):
        return "Error: The file could not be read as UTF-8 text."


@mcp.tool()
def process_data(path: str) -> str:
    """Analyze a CSV, fill missing numeric values with column means,
    and save a separate cleaned CSV file.
    """
    try:
        file_path = get_safe_file_path(path)

        if file_path.suffix.lower() != ".csv":
            return "Error: Only CSV files are supported."

        if not file_path.is_file():
            return "Error: CSV file not found."

        df = pd.read_csv(file_path)

        # Capture statistics before cleaning.
        original_rows, original_columns = df.shape
        missing_before = df.isnull().sum()
        duplicates_before = int(df.duplicated().sum())

        # Fill missing values in numeric columns with their column mean.
        numeric_columns = df.select_dtypes(include="number").columns

        for column in numeric_columns:
            column_mean = df[column].mean()

            # An entirely empty numeric column has no mean to use.
            if pd.notna(column_mean):
                df[column] = df[column].fillna(column_mean)

        # Calculate statistics after cleaning.
        missing_after = df.isnull().sum()
        duplicates_after = int(df.duplicated().sum())

        # Save separately, preserving the original CSV.
        CLEANED_DIR.mkdir(parents=True, exist_ok=True)

        cleaned_file = (
            CLEANED_DIR / f"{file_path.stem}_cleaned.csv"
        ).resolve()

        if not cleaned_file.is_relative_to(CLEANED_DIR):
            return "Error: Invalid output file path."

        df.to_csv(cleaned_file, index=False)

        return (
            "CSV Analysis and Cleaning Report\n"
            "================================\n"
            f"Original file: {file_path.name}\n"
            f"Rows: {original_rows}\n"
            f"Columns: {original_columns}\n\n"
            "Missing values BEFORE cleaning:\n"
            f"{missing_before.to_string()}\n\n"
            "Missing values AFTER cleaning:\n"
            f"{missing_after.to_string()}\n\n"
            f"Duplicate rows before cleaning: {duplicates_before}\n"
            f"Duplicate rows after cleaning: {duplicates_after}\n\n"
            "Cleaning method: Mean imputation for numeric columns\n"
            f"Cleaned file saved to: {cleaned_file}"
        )

    except ValueError as error:
        return f"Error: {error}"
    except (
        OSError,
        UnicodeDecodeError,
        pd.errors.ParserError,
        pd.errors.EmptyDataError,
    ) as error:
        return f"Could not process CSV: {error}"


def main():
    """Start the authenticated Streamable HTTP server."""
    mcp.run(
        transport="streamable-http",
        host=os.environ.get("MCP_HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "8000")),
        path="/mcp",
    )


if __name__ == "__main__":
    main()
