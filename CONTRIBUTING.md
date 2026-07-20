# Contributing to Farzana

Thanks for helping build a **read-only memory aide** that listens carefully.

## Before you start

1. Read [docs/STORY.md](docs/STORY.md), [docs/MOTIVATION.md](docs/MOTIVATION.md), [docs/RULES.md](docs/RULES.md).  
2. Read [SECURITY.md](SECURITY.md) — never commit secrets.  
3. Open an issue for large changes before a big PR.

## Development setup

```bash
git clone https://github.com/<org>/farzana.git
cd farzana
cp .env.example .env
# fill TELEGRAM_* and OPENAI_API_KEY locally only
uv sync
uv run farzana health
uv run farzana --no-webhook   # API only on :8000
```

Full setup (Telegram webhook, deploy): [docs/SETUP.md](docs/SETUP.md).

## Project layout

```text
src/farzana/     # application code
docs/            # product + architecture
deploy/          # EC2 / Terraform (no secrets)
```

## Coding rules (short)

- **Thin HTTP routes** — logic in `services/` / `workers/`.  
- **No external action tools** (email, calendar write, shell, browse).  
- **Markdown vault is truth** — no memory only inside the LLM.  
- Prefer small, reviewable PRs.  
- Update `docs/` when behavior or architecture changes.

See [docs/RULES.md](docs/RULES.md) and [AGENTS.md](AGENTS.md).

## Pull requests

1. Fork + branch from `main`.  
2. Keep commits focused.  
3. Describe **what** and **why**.  
4. Link related issues.  
5. Confirm: no `.env`, keys, or tokens in the diff.  
6. Pass local smoke: `uv run farzana health` and a quick import check.

### PR checklist

- [ ] No secrets  
- [ ] Docs updated if user-facing or architectural  
- [ ] Read-only product constraints respected  
- [ ] Still single-user (`TELEGRAM_USER_ID`); no multi-tenant paths  

## Issues

- Use issue templates when present.  
- Security → [SECURITY.md](SECURITY.md), not public issues.  
- Feature ideas → check existing roadmap issues first.

## Code of conduct

Be respectful. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

By contributing, you agree your contributions are licensed under the MIT License.
