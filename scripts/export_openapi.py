import json
import sys
from pathlib import Path

# Add the project root to Python's import path.
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.main import app  # noqa: E402

DOCS_DIR = ROOT_DIR / "docs"
DOCS_DIR.mkdir(exist_ok=True)

openapi_schema = app.openapi()

# Export OpenAPI specification.
openapi_path = DOCS_DIR / "openapi.json"

openapi_path.write_text(
    json.dumps(openapi_schema, indent=2),
    encoding="utf-8",
)

# Generate readable API reference.
lines = [
    "# API Reference",
    "",
    "Automatically generated from the FastAPI OpenAPI schema.",
    "",
    "Interactive documentation: `/docs`",
    "",
    "| Method | Endpoint | Summary | Tags |",
    "|---|---|---|---|",
]

supported_methods = {
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "options",
    "head",
}

endpoint_count = 0

for path, path_details in sorted(openapi_schema.get("paths", {}).items()):
    for method, details in sorted(path_details.items()):
        if method.lower() not in supported_methods:
            continue

        endpoint_count += 1

        summary = details.get("summary") or details.get("operationId", "Not specified")

        tags = ", ".join(details.get("tags", [])) or "General"

        lines.append(f"| `{method.upper()}` | `{path}` | {summary} | {tags} |")

lines.extend(
    [
        "",
        "## Authentication",
        "",
        "Protected endpoints use the configured authentication "
        "dependencies. Authenticate through the login endpoint and "
        "use the returned access token in the Swagger Authorize dialog.",
        "",
        "## Common Response Codes",
        "",
        "| Status | Meaning |",
        "|---|---|",
        "| 200 | Successful request |",
        "| 201 | Resource created or transaction completed |",
        "| 401 | Authentication required or invalid |",
        "| 403 | Insufficient privileges |",
        "| 404 | Resource not found or inaccessible |",
        "| 409 | Resource or idempotency conflict |",
        "| 422 | Request validation failed |",
        "| 500 | Unexpected server error |",
    ]
)

api_reference_path = DOCS_DIR / "API_REFERENCE.md"

api_reference_path.write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)

print("OpenAPI specification exported successfully.")
print("API reference generated successfully.")
print(f"Endpoints documented: {endpoint_count}")
print(f"OpenAPI file: {openapi_path}")
print(f"API reference: {api_reference_path}")
