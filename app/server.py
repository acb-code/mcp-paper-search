import os
import re
from pathlib import Path
from typing import List, Dict, Any

from mcp.server.fastmcp import FastMCP
from pypdf import PdfReader

from mcp.server.transport_security import TransportSecuritySettings

PAPER_ROOT = Path(os.environ.get("PAPER_ROOT", "/data")).resolve()


def _safe_path(user_path: str) -> Path:
    p = (PAPER_ROOT / user_path).resolve()
    # ensure resolved path stays under PAPER_ROOT
    if p != PAPER_ROOT and not str(p).startswith(str(PAPER_ROOT) + os.sep):
        raise ValueError("Path is outside PAPER_ROOT")
    return p


def _is_allowed_file(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in {".pdf", ".txt", ".md"}


def _read_text_file(p: Path, max_chars: int = 200_000) -> str:
    data = p.read_text(encoding="utf-8", errors="ignore")
    return data[:max_chars]


def _extract_pdf_text(p: Path, max_pages: int = 10, max_chars: int = 200_000) -> str:
    reader = PdfReader(str(p))
    chunks = []
    for page in reader.pages[:max_pages]:
        try:
            chunks.append(page.extract_text() or "")
        except Exception:
            chunks.append("")
    text = "\n".join(chunks)
    return text[:max_chars]


def _snippet(text: str, query: str, window: int = 180) -> str:
    m = re.search(re.escape(query), text, flags=re.IGNORECASE)
    if not m:
        return text[:window] + ("…" if len(text) > window else "")
    start = max(0, m.start() - window // 2)
    end = min(len(text), m.end() + window // 2)
    return ("…" if start > 0 else "") + text[start:end] + ("…" if end < len(text) else "")


mcp = FastMCP(
    "Paper Archive",
    instructions=(
        "Search and fetch papers from a local directory. "
        "Use search_papers to find relevant files, then fetch_paper to read content."
    ),
    stateless_http=True,
    json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,  # DEV: allow ngrok/forwarded hosts
    ),
)


@mcp.tool()
def list_papers(subdir: str = "") -> List[Dict[str, Any]]:
    root = _safe_path(subdir) if subdir else PAPER_ROOT
    if not root.exists():
        return []
    out: List[Dict[str, Any]] = []
    for p in sorted(root.rglob("*")):
        if _is_allowed_file(p):
            rel = p.relative_to(PAPER_ROOT).as_posix()
            out.append({"path": rel, "name": p.name, "bytes": p.stat().st_size})
    return out


@mcp.tool()
def search_papers(query: str, subdir: str = "", limit: int = 8) -> List[Dict[str, Any]]:
    root = _safe_path(subdir) if subdir else PAPER_ROOT
    if not root.exists() or not query.strip():
        return []

    results: List[Dict[str, Any]] = []
    q = query.strip()

    for p in sorted(root.rglob("*")):
        if not _is_allowed_file(p):
            continue

        try:
            if p.suffix.lower() == ".pdf":
                text = _extract_pdf_text(p)
            else:
                text = _read_text_file(p)
        except Exception:
            continue

        if re.search(re.escape(q), text, flags=re.IGNORECASE):
            rel = p.relative_to(PAPER_ROOT).as_posix()
            results.append({"path": rel, "name": p.name, "snippet": _snippet(text, q)})
            if len(results) >= max(1, limit):
                break

    return results


@mcp.tool()
def fetch_paper(path: str, max_chars: int = 60_000) -> Dict[str, Any]:
    p = _safe_path(path)
    if not _is_allowed_file(p):
        raise ValueError("Not an allowed file type (pdf/txt/md)")

    if p.suffix.lower() == ".pdf":
        text = _extract_pdf_text(p, max_pages=30, max_chars=max_chars)
    else:
        text = _read_text_file(p, max_chars=max_chars)

    return {"path": p.relative_to(PAPER_ROOT).as_posix(), "content": text}


def main() -> None:
    # mcp>=1.26 configures host/port via settings, not run() kwargs.
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8000
    # Streamable HTTP transport; FastMCP mounts on /mcp by default.
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
