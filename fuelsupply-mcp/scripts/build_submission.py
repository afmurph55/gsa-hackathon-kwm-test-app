# ruff: noqa: E501
# Long lines below are embedded report and slide prose.
"""Rebuild local documents from actual stored evaluation results."""

import json
from pathlib import Path

from docx import Document
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]


def main():
    summary = json.loads((ROOT / "eval/results/protocol.json").read_text())["summary"]
    latency = summary["latency_ms"]
    report = f"""# FuelSupply MCP evaluation document

Status: offline implementation verified; live market-data MVP and agent evaluation blocked.

## Methodology and inputs
Versioned protocol dataset: eval/cases.jsonl (26 cases). Test-only synthetic observations are isolated in tests/protocol_server.py and tests/fuel_fixtures.py; none are verified EIA mappings. Production sessions use the actual launch entry point and empty registry. Each fixture launches a subprocess, initializes MCP, lists all five tools, reads methodology, gets the briefing prompt and invokes tools. The installed MCP SDK uses snake_case client fields; protocol serialization is SDK-owned.

Layer A/B: 74 pytest cases pass (48 FuelSupply unit/API cases; 26 inherited template/security cases). Formula, calendar, missing/nonfinite values, compatible ratios, validation, seasonal history, reconciliation, pagination, concurrency, rate limiting, permanent errors, redirects, key redaction, timeout retry exhaustion, oversized responses and cache behavior are tested. Incompatible periods are tested directly in service tests. Layer C: real stdio protocol sessions against production and synthetic upstream fixture. Synthetic requests are in-memory MockTransport HTTP requests, never network calls.

Layer D: live EIA checks blocked, zero executed; eval/results/live.json records one skipped live-check group. EIA_API_KEY is absent and EIA hosts are not in the enforced network allowlist. The production registry has zero enabled bindings. No API route/facet/product/units combination is verified.

Layer E: attempted installed Codex CLI 0.167.0-alpha.4 using transient MCP configuration, read-only sandbox and ephemeral execution. Client initialization failed with a read-only filesystem error before any model/tool call. Logs: eval/results/agent-stderr.log and agent-events.jsonl. CLI authentication alone does not establish agent evaluation access. Agent tests executed: zero; tool-selection accuracy and model-answer correctness: unmeasured. No model configuration can be reported as executed.

## Actual results
- Pytest: 74 passed, 0 failed, 0 skipped; recorded in eval/results/pytest.txt. No separate live pytest tests are implied.
- Protocol: {summary["executed"]} executed, {summary["passed"]} passed, {summary["failed"]} failed, {summary["skipped"]} skipped. 15 production cases and 11 synthetic integration cases.
- Structured response validity: {summary["schema_valid_responses"]}/{summary["nonerror_responses"]} non-error responses = 100%. One additional case deliberately triggers MCP input validation and is excluded from that denominator.
- Calculation checks: custom coverage 100/100 = 1 day in synthetic protocol data, insufficient seasonal history and monthly residual_present all pass; unit tests also verify a zero residual, -1 residual, leap-February conversion, invalid/zero denominator and incompatible periods. No live calculation cross-check has run.
- Error paths: unsupported/blocked coverage, aliases, input validation, fake credential 401, rate limit Retry-After, missing/withheld values, stale periods and units behave as asserted. All 26 protocol responses are checked for the fake secret string; none expose it.
- End-to-end tool-call latency (session initialization excluded), n={latency["n"]}: minimum {latency["min"]:.3f} ms, median {latency["median"]:.3f} ms, p95 reported by harness {latency["p95_nearest_rank"]:.3f} ms, maximum {latency["max"]:.3f} ms. These small local samples are descriptive, not a performance guarantee or official GSA target.
- Production live-requested/no-observation responses: n=14, median {summary["production_live_latency_ms"]["median"]:.3f} ms. No upstream data were fetched. The validation error is excluded from mode groups.
- Synthetic uncached/live-requested responses (including error paths): n={summary["synthetic_live_latency_ms"]["n"]}, median {summary["synthetic_live_latency_ms"]["median"]:.3f} ms. Synthetic cached responses: n={summary["synthetic_cached_latency_ms"]["n"]}, median {summary["synthetic_cached_latency_ms"]["median"]:.3f} ms. Production cached measurements: n=0. These are not live EIA cold/cache benchmarks.
- Upstream request count: real EIA {summary["real_upstream_requests"]}; synthetic HTTP transport {summary["synthetic_upstream_requests"]}. Request counts do not count internal MCP calls as EIA requests.

## Environment and reproducibility
Python {summary["python"]}; dependencies {json.dumps(summary["dependencies"], sort_keys=True)}. Registry {summary["registry_version"]}. Base/template git revision {summary["base_revision"]}; runtime source SHA256 {summary["source_sha256"]}. Working tree contains the implementation; base revision is not falsely described as an implementation commit. uv.lock captures the full dependency set. Raw per-case tool outputs, latency and initialization timings are in eval/results/protocol.json. CI is defined but not run remotely; Python3.11 and container reproduction are unverified.

From /workspace/fuelsupply-mcp:

```bash
export UV_CACHE_DIR=/tmp/fuelsupply-uv-cache
export UV_PYTHON_INSTALL_DIR=/tmp/fuelsupply-python
uv sync --locked --group dev --python "$(command -v python)"
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/pytest tests -q
.venv/bin/python eval/run_protocol_eval.py
.venv/bin/python eval/run_live_checks.py
.venv/bin/python scripts/build_submission.py
```

Live-check exit 2 means blocked, not success. Protocol expectations intentionally target the empty production registry; version the dataset before enabling live coverage. The server launch is /workspace/fuelsupply-mcp/.venv/bin/fuelsupply-mcp and uses stdio independently of Codex.

## Security considerations
Fixed HTTPS EIA origin, relative-route validation and disabled redirects restrict outbound access. Server-side credentials are never tool inputs. Error bodies and request URLs are suppressed; numeric observations are sanitized. Timeouts, bounded concurrency/pages/retries, response-size cap and an expiring LRU limit resource use. Cache preserves retrieval timestamps and mode. No silent replay fallback, shell/file tool, purchasing operation or external tracing is enabled. Managed proxy trust is inherited. See docs/security.md for residual threats; no production, agency or compliance certification is claimed.

## Failures, lessons and recommendations
Initial protocol evaluation failed because the current SDK exposes snake_case client attributes; the harness was repaired against inspected SDK signatures. A fixture regenerated its verification timestamp between requests and accidentally bypassed the cache; it now reuses the same binding. Synthetic cutoff scenarios initially filtered their own test observations; the fixture was corrected to use periods preceding the cutoff. Initial failures remain in eval/results/initial-protocol-failures.json; final results supersede them.

The optional template Phoenix/LangChain guide was inspected; it is not an official mandatory harness. It would introduce model/tracing dependencies and was not enabled. Deterministic protocol testing does not replace agent usability testing.

Next: configure credentials and permitted EIA hosts, inspect a small metadata subset, validate each mapping and accounting component against authenticated responses/published tables, then run live protocol/calculation demos and an actual MCP-capable model client. Replace this deck with the official template after downloading it in a permitted environment. Do not deploy or submit without explicit authorization.

## Deliverable validation
A real local PPTX and DOCX are generated and reopened using their libraries. Rendering/visual QA is recorded separately in submission/artifact-validation.json; document reopen alone is not slide visual QA. Official PPTX/DOCX binary templates could not be downloaded here (proxy 403); local files do not claim template compliance. Requirements matrix and submission checklist list remaining gaps.
"""
    for destination in ["docs/evaluation.md", "submission/evaluation-document.md"]:
        (ROOT / destination).write_text(report)
    document = Document()
    for paragraph in report.split("\n\n"):
        if paragraph.startswith("# "):
            document.add_heading(paragraph[2:], 0)
        elif paragraph.startswith("## "):
            document.add_heading(paragraph[3:], 1)
        else:
            document.add_paragraph(paragraph)
    docx_path = ROOT / "submission/evaluation-document.docx"
    document.save(docx_path)
    assert Document(docx_path).paragraphs

    slides = [
        (
            "FuelSupply MCP",
            "Government fuel briefings, with evidence and limits",
            [
                "Dataset Access Server | Local sandbox prototype",
                "Intended users: transportation, aviation, logistics and energy analysts",
                "Proposed use case; no agency adoption claimed",
                "Offline implementation tested. Live-data MVP blocked.",
            ],
        ),
        (
            "The analyst's problem",
            "One briefing, incompatible datasets",
            [
                "Compare distillate, gasoline and kerosene-type jet fuel",
                "Understand inventories, implied demand and regional sourcing",
                "Preserve definitions, units, frequency and observation periods",
                "Public EIA data only; no procurement or operational files",
            ],
        ),
        (
            "Tools follow analyst goals",
            "Coverage → conditions → inventory → structure",
            [
                "discover_fuel_coverage: choose exact product and supported scope",
                "assess_fuel_supply_conditions: production, stocks, demand, trade",
                "compare_inventory_buffer: compatible ratios and seasonal evidence",
                "explain_regional_supply_balance / assess_historical_sourcing",
            ],
        ),
        (
            "Architecture",
            "Client-independent MCP over stdio",
            [
                "Pydantic models → one tool per file → orchestration",
                "Verified registry → fixed-origin EIA client → bounded cache",
                "Deterministic normalization, coverage and reconciliation",
                "Methodology resource and reusable briefing prompt",
            ],
        ),
        (
            "Analytical safeguards",
            "Make uncertainty visible",
            [
                "Distillate ≠ ULSD; finished gasoline ≠ components; jet ≠ avgas",
                "Monthly totals use calendar days; stocks remain quantities",
                "Demand is product supplied, an accounting-based proxy",
                "Missing terms yield insufficient_components; never force a balance",
            ],
        ),
        (
            "Security and reliability",
            "Read-only behavior enforced in implementation",
            [
                "Environment key; fixed EIA origin; validated routes; no redirects",
                "2 concurrent fetches; 3 pages; 3 eligible attempts; 2 MiB response cap",
                "Timeouts, Retry-After handling, duplicate and missing-value checks",
                "Timestamped cache; stderr logs; no external tracing or deployment",
            ],
        ),
        (
            "Demonstrated functionality",
            "Actual local calls; synthetic data labeled",
            [
                "Real MCP initialize, list tools, resource/prompt retrieval and calls",
                "Production: blocked coverage and product clarification work",
                "Synthetic: inventory ratio, monthly residual and upstream failures",
                "Real national briefing and East Coast data demo remain blocked",
            ],
        ),
        (
            "Actual evaluation results",
            "Evidence, not a claim of agent performance",
            [
                f"74 pytest passes | {summary['passed']}/26 MCP cases pass | 25/25 structured results",
                f"Local tool latency: n=26; median {latency['median']:.2f} ms; p95 {latency['p95_nearest_rank']:.2f} ms",
                "Synthetic uncached n=9; cached n=2; 72 mock upstream requests",
                "0 real EIA requests; Codex client initialization blocked",
            ],
        ),
        (
            "What public data cannot establish",
            "The boundary is part of the briefing",
            [
                "How many gallons can we buy next week? EIA cannot establish that.",
                "No uncommitted quantity, quotes, airport availability or delivery guarantee",
                "Utilization is not spare product capacity; yields do not prove switching",
                "Historical receipts are not confirmed replacement supply",
            ],
        ),
        (
            "Next steps and local deliverables",
            "Verify live coverage before claiming MVP completion",
            [
                "Configure key and EIA network access; verify curated metadata/samples",
                "Run live calculation checks, real-data demos and a model client",
                "Code + lockfile + CI + docs + PPTX + evaluation MD/DOCX prepared",
                "Official templates blocked; no push, publication or submission",
            ],
        ),
    ]
    (ROOT / "submission/deck-outline.md").write_text(
        "\n\n".join(
            "## "
            + title
            + "\n\n"
            + subtitle
            + "\n\n"
            + "\n".join("- " + b for b in bullets)
            for title, subtitle, bullets in slides
        )
    )
    presentation = Presentation()
    presentation.slide_width, presentation.slide_height = Inches(13.333), Inches(7.5)
    navy, white, teal, muted = "102437", "F6F8FA", "53D8BB", "B7C8D7"

    def text(slide, x, y, width, height, content, size, color, bold=False):
        box = slide.shapes.add_textbox(
            Inches(x), Inches(y), Inches(width), Inches(height)
        )
        frame = box.text_frame
        frame.word_wrap = True
        for i, line in enumerate(content.split("\n")):
            p = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
            p.text = line
            p.font.size = Pt(size)
            p.font.name = "Aptos"
            p.font.bold = bold
            p.font.color.rgb = RGBColor.from_string(color)
            p.space_after = Pt(20)
        return box

    for index, (title, subtitle, bullets) in enumerate(slides, 1):
        slide = presentation.slides.add_slide(presentation.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = RGBColor.from_string(navy)
        text(
            slide, 0.65, 0.35, 12, 0.4, "FUELSUPPLY / GSA MCP HACKATHON", 12, teal, True
        )
        text(slide, 0.65, 1.05, 12, 1.05, title, 34, white, True)
        text(slide, 0.65, 2.05, 12, 0.7, subtitle, 23, teal)
        text(
            slide, 0.8, 3.0, 11.8, 3.6, "\n".join("•  " + b for b in bullets), 22, white
        )
        text(
            slide,
            0.65,
            6.95,
            11.5,
            0.3,
            "Public EIA data · Sandbox only · Offline evidence / live coverage blocked",
            10,
            muted,
        )
        text(slide, 12, 6.9, 0.6, 0.4, f"{index:02}", 12, muted)
    path = ROOT / "submission/presentation.pptx"
    presentation.save(path)
    reopened = Presentation(path)
    assert len(reopened.slides) == 10
    validation = {
        "pptx_reopened": True,
        "slides": 10,
        "docx_reopened": True,
        "official_template_used": False,
        "visual_qa": "pending_renderer",
        "limitations": "Official binary templates blocked by network policy; rendering status updated after conversion.",
    }
    (ROOT / "submission/artifact-validation.json").write_text(
        json.dumps(validation, indent=2)
    )
    print(json.dumps(validation))


if __name__ == "__main__":
    main()
