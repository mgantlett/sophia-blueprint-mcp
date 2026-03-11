"""
Sophia Labs — MCP Knowledge Server
Blueprint-as-a-Service for Coding Agents

Serves Architecture Blueprint content via MCP tools.
Coding agents (Cursor, Claude Code, Windsurf) connect and query
battle-tested cognitive agent architecture patterns in real-time.

Transport: Streamable HTTP (MCP standard, Cloud Run compatible)
Embedding: Google GenAI text-embedding-004
"""

import os
import re
import glob
import time
import logging
import numpy as np
import urllib.request
import urllib.parse
import json
from typing import Optional

from mcp.server.fastmcp import FastMCP
from google import genai

# ─── Logging ────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("SophiaKnowledge")

# ─── Config ─────────────────────────────────────────────────────────────────

PORT = int(os.environ.get("PORT", "8080"))
CHAPTERS_DIR = os.path.join(os.path.dirname(__file__), "knowledge", "chapters")
EMBEDDING_MODEL = "text-embedding-004"

# ─── License / Auth Config ──────────────────────────────────────────────────

GUMROAD_PRODUCT_ID = os.environ.get("GUMROAD_PRODUCT_ID", "")  # Set in Cloud Run
FREE_CHAPTERS = {1, 3}  # Ch 1: Bio-Digital Metaphor (hook) + Ch 3: Multi-Tier Routing (lead magnet)
KEY_CACHE_TTL = 3600  # Cache valid keys for 1 hour


class LicenseVerifier:
    """Verifies Gumroad license keys with in-memory caching."""

    def __init__(self):
        self._cache: dict[str, float] = {}  # key -> expiry timestamp

    def is_valid(self, key: str) -> bool:
        """Check if a key is valid (cache-first, then Gumroad API)."""
        if not key:
            return False

        # Check cache
        if key in self._cache:
            if time.time() < self._cache[key]:
                return True
            else:
                del self._cache[key]

        # Verify with Gumroad
        if not GUMROAD_PRODUCT_ID:
            logger.warning("GUMROAD_PRODUCT_ID not set — all keys rejected")
            return False

        try:
            data = urllib.parse.urlencode({
                "product_id": GUMROAD_PRODUCT_ID,
                "license_key": key,
                "increment_uses_count": "false",
            }).encode()

            req = urllib.request.Request(
                "https://api.gumroad.com/v2/licenses/verify",
                data=data,
                method="POST",
            )
            resp = urllib.request.urlopen(req, timeout=5)
            result = json.loads(resp.read())

            if result.get("success"):
                self._cache[key] = time.time() + KEY_CACHE_TTL
                logger.info(f"License verified: {key[:8]}...")
                return True
            else:
                logger.info(f"License rejected: {key[:8]}...")
                return False

        except Exception as e:
            logger.error(f"Gumroad API error: {e}")
            return False


license_verifier = LicenseVerifier()

# Async-safe context variable for current request's API key
import contextvars
_api_key_var: contextvars.ContextVar[str] = contextvars.ContextVar('api_key', default='')


def require_key(chapter_num: int) -> Optional[str]:
    """Returns an error message if the chapter is gated and no valid key is present."""
    if chapter_num in FREE_CHAPTERS:
        return None  # Free chapter

    if not GUMROAD_PRODUCT_ID:
        return None  # Auth not configured — allow everything (dev mode)

    if _api_key_var.get() and license_verifier.is_valid(_api_key_var.get()):
        return None  # Valid key

    return (
        f"🔒 **Chapter {chapter_num} requires an API key.**\n\n"
        f"Chapter 3 (Multi-Tier Routing) is free — try it now!\n\n"
        f"To unlock all 10 chapters:\n"
        f"1. Get your key at [sophialabs.gumroad.com](https://sophialabs.gumroad.com)\n"
        f"2. Add it to your MCP config:\n\n"
        f'```json\n'
        f'{{\n'
        f'  "mcpServers": {{\n'
        f'    "sophia-blueprint": {{\n'
        f'      "url": "https://sophialabs.gantlett.io/blueprint/mcp",\n'
        f'      "headers": {{"Authorization": "Bearer YOUR_KEY"}}\n'
        f'    }}\n'
        f'  }}\n'
        f'}}\n'
        f'```'
    )

# ─── Knowledge Base ─────────────────────────────────────────────────────────

class KnowledgeBase:
    """Loads blueprint chapters, computes embeddings, and provides search."""

    def __init__(self):
        self.chapters: list[dict] = []          # {number, title, content, sections}
        self.chunks: list[dict] = []            # {chapter, section, content}
        self.chunk_embeddings: np.ndarray = None
        self.client: genai.Client = None

    def load_chapters(self):
        """Load all markdown chapter files."""
        pattern = os.path.join(CHAPTERS_DIR, "*.md")
        files = sorted(glob.glob(pattern))

        if not files:
            logger.error(f"No chapters found in {CHAPTERS_DIR}")
            return

        for filepath in files:
            filename = os.path.basename(filepath)
            # Extract chapter number from filename like "01_bio_digital_metaphor.md"
            match = re.match(r"(\d+)_(.+)\.md", filename)
            if not match:
                continue

            number = int(match.group(1))
            slug = match.group(2).replace("_", " ").title()

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract title from first H1
            title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
            title = title_match.group(1) if title_match else slug

            # Extract subtitle from first italic line
            subtitle_match = re.search(r"^\*(.+)\*$", content, re.MULTILINE)
            subtitle = subtitle_match.group(1) if subtitle_match else ""

            self.chapters.append({
                "number": number,
                "title": title,
                "subtitle": subtitle,
                "slug": slug,
                "content": content,
                "filepath": filepath,
            })

            # Split into sections (by H2 headers) for granular search
            sections = re.split(r"^## ", content, flags=re.MULTILINE)
            for i, section in enumerate(sections):
                if not section.strip():
                    continue
                # Reconstruct the ## header
                section_text = section if i == 0 else f"## {section}"
                # Extract section title
                sec_title_match = re.match(r"## (.+)", section_text)
                sec_title = sec_title_match.group(1) if sec_title_match else f"Section {i}"

                self.chunks.append({
                    "chapter_number": number,
                    "chapter_title": title,
                    "section_title": sec_title.strip(),
                    "content": section_text.strip(),
                })

        logger.info(f"Loaded {len(self.chapters)} chapters, {len(self.chunks)} sections")

    async def compute_embeddings(self):
        """Compute embeddings for all chunks using Google GenAI."""
        if not self.chunks:
            logger.warning("No chunks to embed")
            return

        # ADC on Cloud Run, API key for local dev
        api_key = os.environ.get("GOOGLE_GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
            logger.info("GenAI client: using API key")
        else:
            self.client = genai.Client()
            logger.info("GenAI client: using ADC")

        # Batch embed all chunk contents
        texts = [c["content"][:2000] for c in self.chunks]  # Truncate to 2000 chars
        logger.info(f"Computing embeddings for {len(texts)} sections...")

        # Batch in groups of 100 (API limit)
        all_embeddings = []
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            result = self.client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=batch,
            )
            for emb in result.embeddings:
                all_embeddings.append(emb.values)

        self.chunk_embeddings = np.array(all_embeddings)
        logger.info(f"Embeddings computed: {self.chunk_embeddings.shape}")

    async def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Semantic search across all chapter sections."""
        if self.chunk_embeddings is None:
            # Fallback: keyword search
            return self._keyword_search(query, top_k)

        # Embed query
        result = self.client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=[query],
        )
        query_emb = np.array(result.embeddings[0].values)

        # Cosine similarity
        norms = np.linalg.norm(self.chunk_embeddings, axis=1) * np.linalg.norm(query_emb)
        similarities = np.dot(self.chunk_embeddings, query_emb) / (norms + 1e-8)

        # Top-K
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            chunk = self.chunks[idx]
            results.append({
                "chapter": chunk["chapter_number"],
                "chapter_title": chunk["chapter_title"],
                "section": chunk["section_title"],
                "score": float(similarities[idx]),
                "content": chunk["content"],
            })

        return results

    def _keyword_search(self, query: str, top_k: int = 3) -> list[dict]:
        """Fallback keyword search when embeddings aren't available."""
        query_lower = query.lower()
        scored = []
        for chunk in self.chunks:
            score = chunk["content"].lower().count(query_lower)
            if score > 0:
                scored.append((score, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "chapter": c["chapter_number"],
                "chapter_title": c["chapter_title"],
                "section": c["section_title"],
                "score": s,
                "content": c["content"],
            }
            for s, c in scored[:top_k]
        ]

    def get_chapter(self, identifier: str | int) -> Optional[dict]:
        """Get a chapter by number or topic keyword."""
        # Try numeric
        try:
            num = int(identifier)
            for ch in self.chapters:
                if ch["number"] == num:
                    return ch
        except (ValueError, TypeError):
            pass

        # Try keyword match on title
        query = str(identifier).lower()
        for ch in self.chapters:
            if query in ch["title"].lower() or query in ch["slug"].lower():
                return ch

        return None

    def get_pattern(self, pattern_name: str) -> Optional[dict]:
        """Find a specific pattern by name across all chapters."""
        pattern_lower = pattern_name.lower()

        # Map common pattern names to likely sections
        pattern_keywords = {
            "heartbeat": ["heartbeat", "30-second", "cycle"],
            "dual-layer": ["dual-layer", "core vs evolved", "core.*evolved"],
            "identity": ["identity", "archetype", "genome"],
            "routing": ["routing", "3-tier", "cascade", "semantic router"],
            "escalation": ["escalation", "chat escalation"],
            "dreamer": ["dream", "creative synthesis"],
            "healer": ["healer", "self-repair"],
            "fleet bridge": ["fleet bridge", "fleet.db", "shared consciousness"],
            "zone": ["zone", "prime-only", "shared zone"],
            "registry": ["registry", "agent registry", "declarative"],
            "shadow": ["shadow", "shadow comparison"],
            "cost governor": ["cost", "budget", "governor"],
            "engram": ["engram", "vector memory"],
        }

        # Find best matching chunk
        best_chunk = None
        best_score = 0

        for chunk in self.chunks:
            content_lower = chunk["content"].lower()
            section_lower = chunk["section_title"].lower()

            # Score based on keyword presence
            score = 0
            if pattern_lower in content_lower:
                score += 10
            if pattern_lower in section_lower:
                score += 20

            # Check mapped keywords
            for key, keywords in pattern_keywords.items():
                if pattern_lower in key or key in pattern_lower:
                    for kw in keywords:
                        if kw in content_lower:
                            score += 5

            if score > best_score:
                best_score = score
                best_chunk = chunk

        if best_chunk and best_score > 0:
            return {
                "pattern": pattern_name,
                "chapter": best_chunk["chapter_number"],
                "chapter_title": best_chunk["chapter_title"],
                "section": best_chunk["section_title"],
                "content": best_chunk["content"],
            }

        return None

    def list_chapters(self) -> list[dict]:
        """Return chapter index with titles and descriptions."""
        return [
            {
                "number": ch["number"],
                "title": ch["title"],
                "subtitle": ch["subtitle"],
            }
            for ch in self.chapters
        ]


# ─── Initialize ─────────────────────────────────────────────────────────────

kb = KnowledgeBase()
kb.load_chapters()

# ─── MCP Server ─────────────────────────────────────────────────────────────

mcp = FastMCP(
    "SophiaBlueprint",
    host="0.0.0.0",
    port=PORT,
    stateless_http=True,
    streamable_http_path="/blueprint/mcp",
)

_embeddings_ready = False


@mcp.tool()
async def sophia_blueprint_list() -> str:
    """
    List all available chapters in the Sophia Architecture Blueprint.
    Returns chapter numbers, titles, and descriptions.
    Use this first to discover what knowledge is available.
    """
    chapters = kb.list_chapters()
    telemetry.track_tool("blueprint_list")
    has_key = _api_key_var.get() and license_verifier.is_valid(_api_key_var.get())
    auth_active = bool(GUMROAD_PRODUCT_ID)

    lines = ["# Sophia Architecture Blueprint — Chapter Index\n"]
    for ch in chapters:
        num = ch['number']
        if auth_active and num not in FREE_CHAPTERS and not has_key:
            lock = " 🔒"
        elif num in FREE_CHAPTERS and auth_active:
            lock = " 🆓"
        else:
            lock = ""
        lines.append(f"**Chapter {num}**: {ch['title']}{lock}")
        if ch["subtitle"]:
            lines.append(f"  *{ch['subtitle']}*")
        lines.append("")

    lines.append(f"\n*{len(chapters)} chapters, ~22,000 words, 50+ code examples*")
    if auth_active and not has_key:
        lines.append("\n🆓 = Free chapter | 🔒 = Requires API key")
        lines.append("Get your key at [sophialabs.gumroad.com](https://sophialabs.gumroad.com)")
    lines.append("\n*Use `sophia_blueprint_chapter(N)` to read a specific chapter.*")
    lines.append("*Use `sophia_blueprint_search(query)` for semantic search.*")

    return "\n".join(lines)


@mcp.tool()
async def sophia_blueprint_chapter(chapter: str) -> str:
    """
    Get the full content of a blueprint chapter by number (1-9) or topic keyword.

    Examples:
    - sophia_blueprint_chapter("3") → Multi-Tier Routing (FREE)
    - sophia_blueprint_chapter("identity") → Identity & Personality
    - sophia_blueprint_chapter("heartbeat") → Autonomic Systems
    """
    ch = kb.get_chapter(chapter)
    if not ch:
        available = ", ".join(f"{c['number']}: {c['title']}" for c in kb.chapters)
        return f"Chapter not found for '{chapter}'. Available: {available}"

    telemetry.track_tool("blueprint_chapter")
    telemetry.track_chapter(ch["number"])

    # Check access
    gate_msg = require_key(ch["number"])
    if gate_msg:
        return gate_msg

    return ch["content"]


@mcp.tool()
async def sophia_blueprint_search(query: str) -> str:
    """
    Semantic search across all blueprint chapters.
    Returns the most relevant sections with chapter context.

    Examples:
    - sophia_blueprint_search("how to add a new agent") → Ch 4 registry pattern
    - sophia_blueprint_search("memory zone governance") → Ch 5 zone taxonomy
    - sophia_blueprint_search("reduce API costs") → Ch 9 model tiering
    """
    global _embeddings_ready
    if not _embeddings_ready:
        try:
            await kb.compute_embeddings()
            _embeddings_ready = True
        except Exception as e:
            logger.warning(f"Embedding computation failed, using keyword fallback: {e}")

    results = await kb.search(query, top_k=3)
    telemetry.track_tool("blueprint_search")
    telemetry.track_search(query)

    if not results:
        return f"No results found for '{query}'. Try a different search term."

    output = [f"# Search Results for: \"{query}\"\n"]
    for i, r in enumerate(results, 1):
        score_str = f" (score: {r['score']:.2f})" if isinstance(r['score'], float) else ""
        output.append(f"## Result {i}: Chapter {r['chapter']} — {r['chapter_title']}{score_str}")
        output.append(f"**Section:** {r['section']}\n")
        # Truncate long content
        content = r["content"]
        if len(content) > 3000:
            content = content[:3000] + "\n\n...[truncated — use `sophia_blueprint_chapter` for full content]"
        output.append(content)
        output.append("\n---\n")

    return "\n".join(output)


@mcp.tool()
async def sophia_blueprint_pattern(pattern_name: str) -> str:
    """
    Look up a specific architectural pattern from the blueprint.

    Examples:
    - sophia_blueprint_pattern("heartbeat loop")
    - sophia_blueprint_pattern("dual-layer identity")
    - sophia_blueprint_pattern("fleet bridge")
    - sophia_blueprint_pattern("chat escalation")
    - sophia_blueprint_pattern("shadow comparison")
    - sophia_blueprint_pattern("cost governor")
    """
    result = kb.get_pattern(pattern_name)
    telemetry.track_tool("blueprint_pattern")

    if not result:
        patterns = [
            "heartbeat loop", "dual-layer identity", "routing cascade",
            "chat escalation", "dream synthesis", "self-repair / healer",
            "fleet bridge", "zone governance", "agent registry",
            "shadow comparison", "cost governor", "engram / vector memory"
        ]
        return (
            f"Pattern '{pattern_name}' not found.\n\n"
            f"Known patterns: {', '.join(patterns)}\n\n"
            f"Try `sophia_blueprint_search(\"{pattern_name}\")` for a broader search."
        )

    output = [
        f"# Pattern: {result['pattern']}",
        f"**Source:** Chapter {result['chapter']} — {result['chapter_title']}",
        f"**Section:** {result['section']}\n",
        result["content"],
    ]

    return "\n".join(output)


# ─── Telemetry ───────────────────────────────────────────────────────────────

from collections import defaultdict
import threading

STATS_TOKEN = os.environ.get("STATS_TOKEN", "")
BOOT_TIME = time.time()


class TelemetryStore:
    """Thread-safe in-memory metrics. Logs to Cloud Run structured logging.
    
    Tracks: page views, CTA clicks, MCP tool calls, referrers, countries.
    All data is ephemeral (resets on deploy) — persistent data lives in Cloud Logging.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self.page_views = 0
        self.mcp_requests = 0
        self.events: dict[str, int] = defaultdict(int)       # event_name → count
        self.referrers: dict[str, int] = defaultdict(int)     # domain → count
        self.tools: dict[str, int] = defaultdict(int)         # tool_name → count  
        self.chapters: dict[int, int] = defaultdict(int)      # chapter_num → count
        self.searches: list[str] = []                         # recent search queries
        self.countries: dict[str, int] = defaultdict(int)     # country → count
        self.errors = 0

    def track_pageview(self, referrer: str = "", country: str = ""):
        with self._lock:
            self.page_views += 1
            if referrer:
                self.referrers[referrer] += 1
            if country:
                self.countries[country] += 1

    def track_event(self, name: str):
        with self._lock:
            self.events[name] += 1

    def track_mcp(self, path: str, latency_ms: float, status: int, user_agent: str = ""):
        with self._lock:
            self.mcp_requests += 1
            if status >= 400:
                self.errors += 1

    def track_tool(self, tool_name: str):
        with self._lock:
            self.tools[tool_name] += 1

    def track_chapter(self, chapter_num: int):
        with self._lock:
            self.chapters[chapter_num] += 1

    def track_search(self, query: str):
        with self._lock:
            self.searches.append(query)
            if len(self.searches) > 200:
                self.searches = self.searches[-100:]

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "uptime_seconds": int(time.time() - BOOT_TIME),
                "page_views": self.page_views,
                "mcp_requests": self.mcp_requests,
                "errors": self.errors,
                "events": dict(self.events),
                "top_referrers": dict(sorted(self.referrers.items(), key=lambda x: -x[1])[:20]),
                "top_countries": dict(sorted(self.countries.items(), key=lambda x: -x[1])[:20]),
                "tool_calls": dict(self.tools),
                "chapter_requests": dict(sorted(self.chapters.items())),
                "recent_searches": list(self.searches[-20:]),
            }


telemetry = TelemetryStore()

# ─── Landing Page ────────────────────────────────────────────────────────────

from starlette.responses import HTMLResponse, JSONResponse

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


# ─── Auth Middleware ─────────────────────────────────────────────────────────

class AuthASGIMiddleware:
    """Raw ASGI middleware — extracts API key without buffering responses.
    
    BaseHTTPMiddleware wraps response bodies and breaks SSE streaming.
    This passes through cleanly.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            auth = headers.get(b"authorization", b"").decode()
            key = auth.replace("Bearer ", "").strip() if auth.startswith("Bearer ") else ""
            token = _api_key_var.set(key)
            try:
                await self.app(scope, receive, send)
            finally:
                _api_key_var.reset(token)
        else:
            await self.app(scope, receive, send)


# ─── Main ───────────────────────────────────────────────────────────────────

def _get_header(scope, name: bytes) -> str:
    """Extract a header value from ASGI scope."""
    for k, v in scope.get("headers", []):
        if k == name:
            return v.decode("utf-8", errors="replace")
    return ""


def _get_query_param(scope, name: str) -> str:
    """Extract a query parameter from ASGI scope."""
    qs = scope.get("query_string", b"").decode()
    for part in qs.split("&"):
        if "=" in part:
            k, v = part.split("=", 1)
            if k == name:
                return urllib.parse.unquote(v)
    return ""


async def _read_body(receive) -> bytes:
    """Read the full request body from ASGI receive."""
    body = b""
    while True:
        msg = await receive()
        body += msg.get("body", b"")
        if not msg.get("more_body", False):
            break
    return body


class LandingAndRedirectMiddleware:
    """ASGI middleware: landing page, /track beacon, /stats, /health, /mcp redirect.
    
    FastMCP natively handles /blueprint/mcp via streamable_http_path.
    This adds telemetry endpoints and the landing page.
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "/")
        method = scope.get("method", "GET")

        # ── Landing page ──
        if path == "/":
            html_path = os.path.join(STATIC_DIR, "index.html")
            with open(html_path, "r", encoding="utf-8") as f:
                resp = HTMLResponse(f.read())
            await resp(scope, receive, send)
            return

        # ── Beacon: POST /track ──
        if path == "/track" and method == "POST":
            body = await _read_body(receive)
            try:
                data = json.loads(body) if body else {}
            except (json.JSONDecodeError, ValueError):
                data = {}

            event = data.get("event", "pageview")
            referrer = data.get("referrer", "")
            # Cloud Run sets X-Appengine-Country or we can parse from CF headers
            country = (
                _get_header(scope, b"x-appengine-country")
                or _get_header(scope, b"cf-ipcountry")
                or ""
            )

            if event == "pageview":
                telemetry.track_pageview(referrer=referrer, country=country)
            else:
                telemetry.track_event(event)

            # Structured log for Cloud Logging
            logger.info(json.dumps({
                "type": "track",
                "event": event,
                "referrer": referrer,
                "country": country,
                "page": data.get("page", "/"),
                "user_agent": _get_header(scope, b"user-agent"),
                "timestamp": time.time(),
            }))

            resp = JSONResponse({"ok": True}, status_code=204)
            await resp(scope, receive, send)
            return

        # ── Health check ──
        if path == "/health":
            resp = JSONResponse({
                "status": "ok",
                "uptime": int(time.time() - BOOT_TIME),
                "chapters": len(kb.chapters),
                "page_views": telemetry.page_views,
                "mcp_requests": telemetry.mcp_requests,
            })
            await resp(scope, receive, send)
            return

        # ── Stats (token-protected) ──
        if path == "/stats":
            token = _get_query_param(scope, "token")
            if STATS_TOKEN and token != STATS_TOKEN:
                resp = JSONResponse({"error": "unauthorized"}, status_code= 401)
                await resp(scope, receive, send)
                return
            resp = JSONResponse(telemetry.snapshot())
            await resp(scope, receive, send)
            return

        # ── Redirect old /mcp → /blueprint/mcp ──
        if path == "/mcp" or path.startswith("/mcp/"):
            from starlette.responses import RedirectResponse
            new_path = path.replace("/mcp", "/blueprint/mcp", 1)
            resp = RedirectResponse(url=new_path, status_code=307)
            await resp(scope, receive, send)
            return

        # ── MCP requests — log telemetry ──
        if path.startswith("/blueprint/mcp"):
            start_t = time.time()
            # Capture status code from the response
            status_code = 200
            original_send = send

            async def capturing_send(message):
                nonlocal status_code
                if message.get("type") == "http.response.start":
                    status_code = message.get("status", 200)
                await original_send(message)

            await self.app(scope, receive, capturing_send)

            latency_ms = (time.time() - start_t) * 1000
            user_agent = _get_header(scope, b"user-agent")
            telemetry.track_mcp(path, latency_ms, status_code, user_agent)

            logger.info(json.dumps({
                "type": "mcp_request",
                "method": method,
                "path": path,
                "status": status_code,
                "latency_ms": round(latency_ms, 1),
                "user_agent": user_agent,
                "timestamp": time.time(),
            }))
            return

        await self.app(scope, receive, send)


if __name__ == "__main__":
    logger.info(f"Starting Sophia Blueprint MCP server on port {PORT}...")
    logger.info(f"Chapters loaded: {len(kb.chapters)}, Sections: {len(kb.chunks)}")
    logger.info(f"Auth: {'ENABLED (Gumroad)' if GUMROAD_PRODUCT_ID else 'DISABLED (dev mode)'}")
    logger.info(f"Free chapters: {FREE_CHAPTERS}")
    logger.info(f"Telemetry: /track (beacon), /health, /stats{'(token-protected)' if STATS_TOKEN else ' (open — set STATS_TOKEN to protect)'}")

    # FastMCP handles /blueprint/mcp natively (streamable_http_path setting)
    starlette_app = mcp.streamable_http_app()
    # Add landing page, telemetry endpoints, /mcp redirect
    app = LandingAndRedirectMiddleware(starlette_app)
    # Auth extraction
    app = AuthASGIMiddleware(app)

    logger.info(f"MCP endpoint: /blueprint/mcp (legacy /mcp redirects)")

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
