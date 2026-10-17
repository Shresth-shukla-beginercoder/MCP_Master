# MCP Master Toolkit

A Python-based Model Context Protocol (MCP) server that lets AI applications read text files and analyze and clean CSV datasets through MCP tools.

**PyPI:** [mcp-master-toolkit-2026](https://pypi.org/project/mcp-master-toolkit-2026/)  
**Version:** 0.1.0  
**Python:** 3.13+

## Features

- **Text File Reader:** Read UTF-8 text files from a configured data directory.
- **CSV Analysis:** Inspect row counts, columns, missing values, and duplicate rows.
- **Data Cleaning:** Fill missing numeric values using column means.
- **Cleaned CSV Export:** Save cleaned datasets separately from the originals.
- **Streamable HTTP Transport:** Connect compatible MCP clients to the server.
- **Authentication:** Protect HTTP access with a bearer token.

## Installation

Install and launch the published package using [uv](https://docs.astral.sh/uv/):

```bash
uvx --from mcp-master-toolkit-2026 mcp-master-http
```

The server listens locally at:

```text
http://127.0.0.1:8000/mcp
```

## Configuration

The HTTP server requires an `MCP_AUTH_TOKEN`.

### PowerShell

Set the token before starting the server:

```powershell
$env:MCP_AUTH_TOKEN = "your-secret-token"
uvx --from mcp-master-toolkit-2026 mcp-master-http
```

Use a long, randomly generated secret. Never commit tokens, API keys, or `.env` files to GitHub.

### Data directory

By default, the server looks for a `data` directory in its current working directory. You can specify a different directory using `MCP_MASTER_DATA_DIR`.

```powershell
$env:MCP_MASTER_DATA_DIR = "C:\path\to\your\data"
```

Example directory structure:

```text
data/
├── sample.txt
├── sales.csv
└── cleaned/
```

The server creates the `cleaned` directory when a CSV is processed, if needed.

## Available MCP Tools

### `fetch_data`

Reads a UTF-8 text file from the configured data directory.

Example input:

```json
{
  "path": "sample.txt"
}
```

### `process_data`

Analyzes a CSV, reports missing values and duplicate rows, fills missing numeric values with column means, and saves a cleaned CSV.

Example input:

```json
{
  "path": "sales.csv"
}
```

The cleaned output is saved in the `cleaned` directory using the filename pattern:

```text
sales_cleaned.csv
```

Original CSV files are not overwritten.

## Connect with MCP Inspector

1. Start the server using the installation command above.
2. Open [MCP Inspector](https://github.com/modelcontextprotocol/inspector).
3. Select **Streamable HTTP** as the transport.
4. Enter the server URL:

   ```text
   http://127.0.0.1:8000/mcp
   ```

5. Configure the following custom header:

   ```text
   Authorization: Bearer YOUR_MCP_AUTH_TOKEN
   ```

6. Connect and list the available tools.

Replace the placeholder with the same token configured in `MCP_AUTH_TOKEN`.

## Development Setup

Clone your repository and enter its directory:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd MCP_MASTER
```

Install dependencies using uv:

```bash
uv sync
```

Configure the required environment variables, then start the development server:

```bash
uv run mcp-master-http
```

Compile-check the server source:

```bash
uv run python -m py_compile src/servers/http_server.py
```

Build and validate distribution files:

```bash
uv build
uvx --from twine twine check dist/*
```

**Note:** Before publishing a new release, remove stale distribution files from `dist` and verify that only the intended package files are present.

## Security Notes

- Keep `MCP_AUTH_TOKEN` and other secrets out of source control.
- Do not expose the server publicly without appropriate network security and HTTPS.
- Use a separate, strong token for MCP authentication rather than your PyPI upload token.
- Restrict file access to trusted users and data.

## Project Structure

```text
MCP_MASTER/
├── data/
│   ├── sample.txt
│   ├── sales.csv
│   └── cleaned/
├── src/
│   ├── servers/
│   │   ├── __init__.py
│   │   ├── http_server.py
│   │   └── stdio_server.py
│   ├── clients/
│   └── agents/
├── tests/
├── .env
├── .gitignore
├── README.md
├── pyproject.toml
└── uv.lock
```

## License

Choose and add an appropriate open-source license before distributing the project under a specific license.

## Author

**Shresth Shukla**

Explore the repository, try the MCP tools, and contribute improvements.
