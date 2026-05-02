# Claude Code adapter

Claude Code does not use Codex `SKILL.md` natively in the same way, so adapt this skill by:

1. copying the core guidance into the repository `CLAUDE.md`
2. linking the same architecture, sources, hardware, and gap-tracking docs
3. keeping the same product rules:
   - narrow MVP first
   - local-first architecture
   - open protocols
   - LLM as explainer, not numeric predictor
   - explicit note about missing real field data

Minimum instruction block for Claude Code:

- Build local-first agrotech MVPs around irrigation, pest risk, spreadsheet ingestion, and open sensor interoperability.
- Use Streamlit for the first UI, scikit-learn for baselines, DuckDB for messy file landing, and Postgres/PostGIS/TimescaleDB for operational storage.
- Use SensorThings/FROST when sensor interoperability matters.
- Treat Gemma or another local LLM as an explainer and cautious visual reviewer only.
- Always document missing data, validation gaps, hardware assumptions, and what is still demo-only.
