# Job Hunt Copilot

A CLI tool that automates the repetitive parts of job hunting. Paste in a vacancy,
point it at your CV, and get a structured match analysis plus a tailored cover letter
— all in one command.

Built as a portfolio project demonstrating practical LangChain/LCEL patterns with
the Anthropic Claude API, targeting Junior AI Engineer roles.

---

## Features

- **Vacancy parsing** — extracts structured data from raw job postings (company,
  position, seniority, required skills, language requirements, work format) using
  a Claude LLM chain with `with_structured_output`
- **CV matching** — scores the candidate's CV against vacancy requirements and
  returns matched skills, missing skills, and hard disqualifiers
- **Cover letter generation** — produces a personalized, professional cover letter
  based on the match analysis, drawing on the full CV text for concrete details
  and matching the vacancy's language
- **Application history** — persists every run (company, position, score, cover
  letter text) to a local SQLite database via SQLAlchemy 2.0
- **CV indexing** — chunks and embeds the CV into a local ChromaDB vector store
  using HuggingFace sentence-transformers (no paid embedding API required)
- **Automatic retry with backoff** — transient failures (rate limits, connection
  errors) are retried up to 3 times with exponential backoff via `tenacity` before
  being surfaced as an error
- **Structured error handling** — raw Anthropic/LangChain exceptions are translated
  into a small custom exception hierarchy so callers can react to specific failure
  modes (rate limit, connection issue, bad structured output) instead of catching
  generic `Exception`
- **Colorized logging** — every module logs through the standard `logging` module;
  `main.py` wires it to a `rich.logging.RichHandler` for readable, color-coded
  console output and pretty tracebacks

---

## Architecture

```
vacancy.txt ──► vacancy_parser.py ──► VacancyRequirements
                                            │
cv.md ─────────────────────────────► matcher.py ──► MatchResult
      │                                     │
      └─────────────────────────► cover_letter.py ──► cover letter text
                                            │
                                        db.py ──► jobs.db

                     (all chain calls routed through llm_utils.py,
                      which retries transient failures and raises
                      typed exceptions from exceptions.py)
```

| Module | Responsibility |
|---|---|
| `config.py` | Pydantic Settings — loads `.env`, exposes typed paths and `SecretStr` API key |
| `models.py` | `VacancyRequirements` and `MatchResult` Pydantic models used for structured LLM output |
| `prompts.py` | All system and human prompt templates, centralized and separated from chain logic |
| `exceptions.py` | Custom exception hierarchy (`LLMCallError` and subclasses) for LLM failure modes |
| `llm_utils.py` | `invoke_chain_safely()` — wraps every chain call, retries transient errors (`tenacity`), logs and translates raw Anthropic/LangChain errors into `exceptions.py` types |
| `vacancy_parser.py` | LCEL chain: `ChatPromptTemplate | llm.with_structured_output(VacancyRequirements)` |
| `cv_store.py` | CV chunking, HuggingFace embeddings, ChromaDB indexing |
| `matcher.py` | LCEL chain: full CV text passed to Claude, returns `MatchResult` |
| `cover_letter.py` | LCEL chain: free-text generation from vacancy + match result + full CV text |
| `db.py` | SQLAlchemy 2.0 ORM — persists application records to SQLite |
| `cli.py` | Pipeline entry point — orchestrates all modules end to end, logs the run, and maps exceptions to user-facing error messages |
| `main.py` | Process entry point — configures colorized logging (`RichHandler`) before calling `cli.main()` |

---

## Project Structure

```
job-hunt-copilot/
├── src/
│   ├── config.py
│   ├── models.py
│   ├── prompts.py
│   ├── exceptions.py
│   ├── llm_utils.py
│   ├── vacancy_parser.py
│   ├── cv_store.py
│   ├── matcher.py
│   ├── cover_letter.py
│   ├── db.py
│   └── cli.py
├── inbox/
│   └── vacancy.txt          # paste the vacancy text here before each run
├── data/
│   └── cv.md                # your CV in Markdown (gitignored — stays local)
├── tests/
│   ├── test_vacancy_parser.py
│   └── test_matcher.py
├── .env.example
├── requirements.txt
├── main.py
└── README.md
```

---

## Setup

**Requirements:** Python 3.11+, an [Anthropic API key](https://console.anthropic.com/)

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/your-username/job-hunt-copilot.git
cd job-hunt-copilot
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> First run downloads the `all-MiniLM-L6-v2` sentence-transformers model (~90 MB).

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set your API key:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-6
```

The remaining settings have sensible defaults and can be left as-is.

### 4. Add your CV

Create `data/cv.md` and paste your CV in Markdown format. This file is gitignored
and will never leave your machine.

### 5. Index the CV into the vector store

```bash
python src/cv_store.py
```

This chunks the CV, embeds it with HuggingFace sentence-transformers, and stores
the vectors in `data/chroma/`. Re-run this step whenever you update your CV.

---

## Usage

### 1. Paste the vacancy

Copy the full job posting text into `inbox/vacancy.txt`.

### 2. Run the pipeline

```bash
python main.py
```

The tool will:
1. Parse the vacancy into structured data
2. Match it against your CV
3. Log the match score, matched/missing skills, and any red flags
4. Generate a cover letter and log it
5. Save the cover letter to `output/cover_letter.txt`
6. Persist the application record to `data/jobs.db`

All progress is reported through the standard `logging` module, rendered by
`rich.logging.RichHandler` — each line is timestamped and color-coded by level
(`INFO` in the default color, `WARNING` in yellow for red flags, `ERROR` in red
for failures).

### Example output

```
2026-07-03 16:20:11 INFO     src.cli: === JOB HUNT COPILOT ===
2026-07-03 16:20:11 INFO     src.vacancy_parser: Parsed vacancy: Acme Corp — Junior AI Engineer
2026-07-03 16:20:13 INFO     src.matcher: Match score: 78% | Good fit: True
2026-07-03 16:20:13 INFO     src.cli: Matched skills: Python, LangChain, FastAPI, PostgreSQL
2026-07-03 16:20:13 INFO     src.cli: Missing skills: Kubernetes, Go
2026-07-03 16:20:16 INFO     src.cover_letter: Generated cover letter (842 chars)
2026-07-03 16:20:16 INFO     src.cli: Saved to output/cover_letter.txt
2026-07-03 16:20:16 INFO     src.db: Saved application record id=1 for Acme Corp — Junior AI Engineer
```

If a vacancy has red flags, they are logged at `WARNING` level:

```
2026-07-03 16:20:13 WARNING  src.cli: Red flags:
2026-07-03 16:20:13 WARNING  src.cli:   - Requires on-call rotation not mentioned in CV
```

---

## Design Notes

### Full-context matching instead of RAG retrieval

The `matcher.py` module passes the full CV text directly to Claude rather than
retrieving relevant chunks from ChromaDB. This is a deliberate tradeoff:

- A single CV is small (typically 500–1500 tokens). Claude's context window handles
  it trivially, with no information loss from chunking.
- RAG retrieval adds a semantic search step that can drop relevant context if the
  query does not closely match the chunk's phrasing — a real risk when matching
  skills across different vocabulary.
- For this use case — one document, one query per run — retrieval adds latency and
  complexity without improving accuracy.

The ChromaDB and HuggingFace infrastructure in `cv_store.py` is retained to
demonstrate the retrieval pattern. At scale (multiple CVs, a large document corpus,
or high-frequency querying) the retrieval path would become the right choice.

### Local embeddings over a paid API

`cv_store.py` uses `sentence-transformers/all-MiniLM-L6-v2` via HuggingFace,
running locally. This means:
- No additional API key or cost beyond the Anthropic key
- No CV text sent to a third-party embedding service
- Reproducible embeddings — the model is version-pinned in `requirements.txt`

The tradeoff is a one-time ~90 MB model download and slightly lower embedding
quality compared to Voyage AI or OpenAI embeddings. For a single-user local tool
this is an acceptable tradeoff.

### Separating role fit from skill fit in `MatchResult`

`MatchResult` splits "is this the right *type* of role" from "does the
candidate have the specific required skills" into two independent fields:

- `role_alignment` — true if the position is fundamentally the kind of role
  the candidate is targeting (e.g. Python backend / AI engineering), regardless
  of how many specific frameworks match.
- `is_good_fit` — true only if the candidate meets enough of the *specific*
  technical requirements, independent of role type.

A Python backend vacancy missing a couple of libraries can be `role_alignment=True,
is_good_fit=False`; a web-scraping-only or QA vacancy is `role_alignment=False`
even if some listed tools overlap. Collapsing these into one score would hide
which of the two problems (wrong role vs. skill gap) actually applies.

### Modeling "or" requirements as skill alternatives

`VacancyRequirements.required_skill_alternatives` captures groups of
interchangeable skills — but only when the posting uses an explicit
alternative word ("or", "або", "чи", "либо"), e.g. "Django or FastAPI"
becomes `["Django", "FastAPI"]`. A skill lives in either `required_skills`
or one alternatives group, never both, so the matcher doesn't double-count
or unfairly penalize a candidate for lacking every option in an either/or
requirement. A plain comma-separated list without such a word (e.g.
"PostgreSQL, MySQL, MongoDB") is treated as all three being required, and
stays in `required_skills`.

### Retrying transient failures before giving up

`llm_utils.py` wraps every chain call in a `tenacity`-decorated retry
(`_invoke_with_retry`) that retries on `RateLimitError` and
`APIConnectionError` up to 3 attempts with exponential backoff (2s–10s).
The retry function must let these raw library exceptions propagate
unmodified — if it caught and re-raised them as a domain exception, tenacity's
`retry_if_exception_type` check would never see the original type again and
retries would silently stop working. Only after retries are exhausted does
`invoke_chain_safely()` translate the failure into a typed exception from
`exceptions.py`.

### Error handling: a typed exception hierarchy instead of bare `Exception`

Every LLM chain invocation goes through `invoke_chain_safely()` in `llm_utils.py`,
which retries transient failures, then catches the low-level
`anthropic`/`langchain_core` exceptions and re-raises them as one of the types
in `exceptions.py`:

| Exception | Raised when | Base |
|---|---|---|
| `LLMRateLimitError` | Anthropic API rate limit exceeded | `LLMCallError` |
| `LLMConnectionError` | Connection to the Anthropic API fails | `LLMCallError` |
| `LLMOutputError` | LLM response fails structured-output parsing | `LLMCallError` |
| `LLMCallError` | Any other unexpected API error (base class, also used directly) | `Exception` |

This keeps the failure modes explicit and catchable by name instead of forcing
every caller to inspect a generic `Exception` message. `cli.py` catches each
type separately at the top of the pipeline and logs an actionable message
without crashing the process; a final `except Exception` remains as a safety
net for anything truly unexpected, logged with a full traceback via
`logger.exception(...)`.

### Logging instead of `print`

All modules log through `logging.getLogger(__name__)` rather than calling
`print()`. This was a deliberate refactor with two goals:

- **Log at the source, not just in `main`.** Each module logs its own
  milestones and errors (e.g. `matcher.py` logs the computed match score,
  `db.py` logs the saved record id, `llm_utils.py` logs the raw error before
  translating it). This means the logs are useful even when a module is run
  standalone via its own `if __name__ == "__main__":` block, not only through
  the full `cli.py` pipeline.
- **`cli.py` only logs what's unique to orchestration** — the pipeline banner,
  the user-facing skills/red-flags summary, the generated cover letter, and
  the final exception mapping — instead of duplicating what the underlying
  functions already logged.

`main.py` configures the root logger once, at process start, with a
`rich.logging.RichHandler`. This gives color-coded, timestamped console output
(and readable tracebacks) without any module needing to know how logging is
displayed — modules just log; `main.py` decides how that looks.

### Temperature settings

| Chain | Temperature | Reason |
|---|---|---|
| `vacancy_parser.py` | 0 | Deterministic extraction — the same vacancy should always produce the same structured output |
| `matcher.py` | 0 | Consistent scoring — running the matcher twice on the same inputs should give the same result |
| `cover_letter.py` | 0.7 | Natural-sounding prose — some variation is desirable |

### API key security

`ANTHROPIC_API_KEY` is typed as `pydantic.SecretStr` in `AppSettings`. This
prevents the key from appearing in logs, `repr()` output, or `model_dump()` calls.

### Personal data stays local

`data/cv.md`, `data/chroma/`, `data/jobs.db`, and `output/` are all gitignored.
The repository ships only `inbox/vacancy.txt` as a placeholder. No personal or
sensitive data is ever committed.

---

## Running Tests

```bash
pytest
```

Tests use `unittest.mock.patch` to mock the LangChain chain at the module level,
so no API calls or local models are needed to run the test suite.

---

## Tech Stack

| Layer | Library |
|---|---|
| LLM provider | [Anthropic Claude](https://www.anthropic.com/) via `langchain-anthropic` |
| LLM orchestration | [LangChain](https://python.langchain.com/) / LCEL |
| Data validation | [Pydantic v2](https://docs.pydantic.dev/) + `pydantic-settings` |
| Vector store | [ChromaDB](https://www.trychroma.com/) via `langchain-chroma` |
| Embeddings | [HuggingFace sentence-transformers](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) |
| Database | SQLite via [SQLAlchemy 2.0](https://docs.sqlalchemy.org/) |
| Logging | Standard `logging` module + [Rich](https://rich.readthedocs.io/) (`RichHandler`) for colorized console output |
| Retry logic | [Tenacity](https://tenacity.readthedocs.io/) — exponential backoff on rate limit / connection errors |
| Testing | [pytest](https://pytest.org/) |
