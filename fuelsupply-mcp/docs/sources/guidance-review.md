# Guidance review — November 11, 2026

Official event: https://www.gsa.gov/artificial-intelligence/ai-community-of-practice/events-and-training/mcp-server-and-ai-agent-government-hackathon
Official starter: https://github.com/GSA-TTS/mcp-hackathon-template, commit `f39249f1768309e3ef8b31742390a4f3a656b5f3`.

Read the event's track, sandbox scope, rubric and deliverable sections using web access. Read local README, QUICKSTART, SECURITY, docs/README, eval/README, eval/databricks/README and .agents/skills/mcp-eval/SKILL.md. Inspected workspace for AGENTS and participant/rubric files: none were found before this project was created. Existing unrelated repository was preserved.

The event describes Dataset Access Server, requires public-data sandbox prototypes, and expects code, a deck and evaluation documentation. The rubric includes maintainable design, reliability evidence, agent-oriented interfaces, mission value, innovation and presentation. No scoring weights have been invented. Eligibility or registration is not asserted for this project. Participant-specific instructions remain unavailable and must be checked before actual submission.

No conflict requiring consequential action was identified. The starter contains public-hosting instructions, but vendor educational material does not override the event sandbox boundary. No hosting action was taken.

Official binary references located:
- https://www.gsa.gov/system/files/MCP-hackathon-sample-deck.pptx
- https://www.gsa.gov/system/files/MCP-hackathon-sample-evaluation-document.docx

Web access could identify these files but could not parse their binary content. An ordinary sandbox curl to the deck returned proxy CONNECT 403. GSA is absent from the environment network allowlist. Local replacement PPTX/DOCX files are explicitly not claimed to use the official templates. No bypass was attempted.

EIA sources reviewed via web access (not authenticated API discovery):
- https://www.eia.gov/opendata/
- https://www.eia.gov/opendata/documentation.php
- https://www.eia.gov/petroleum/supply/weekly/
- https://www.eia.gov/petroleum/supply/monthly/
- https://www.eia.gov/petroleum/supply/monthly/pdf/psmnotes.pdf
- https://www.eia.gov/petroleum/supply/weekly/pdf/appendixb.pdf

Methodological takeaway: demand is calculated from supply/disposition accounting; PADD receipts, production types, transfers and adjustments can matter. Weekly data include estimation and differ from monthly structures. These sources establish methodological context, not verified API routes/facets. No exact route, series ID, frequency/facet combination or unit was inferred from memory.

Codex reference reviewed: https://developers.openai.com/codex/extend/mcp (web resolver redirected to current learn.chatgpt.com documentation). Installed CLI help/version was inspected separately; no global settings were changed.
