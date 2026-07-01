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
  based on the match analysis
- **Application history** — persists every run (company, position, score, cover
  letter text) to a local SQLite database via SQLAlchemy 2.0
- **CV indexing** — chunks and embeds the CV into a local ChromaDB vector store
  using HuggingFace sentence-transformers (no paid embedding API required)

---

## Architecture

```
vacancy.txt ──► vacancy_parser.py ──► VacancyRequirements
                                            │
cv.md ─────────────────────────────► matcher.py ──► MatchResult
                                            │
                             cover_letter.py ──► cover letter text
                                            │
                                        db.py ──► jobs.db
```

| Module | Responsibility |
|---|---|
| `config.py` | Pydantic Settings — loads `.env`, exposes typed paths and `SecretStr` API key |
| `models.py` | `VacancyRequirements` and `MatchResult` Pydantic models used for structured LLM output |
| `prompts.py` | All system and human prompt templates, centralized and separated from chain logic |
| `vacancy_parser.py` | LCEL chain: `ChatPromptTemplate | llm.with_structured_output(VacancyRequirements)` |
| `cv_store.py` | CV chunking, HuggingFace embeddings, ChromaDB indexing |
| `matcher.py` | LCEL chain: full CV text passed to Claude, returns `MatchResult` |
| `cover_letter.py` | LCEL chain: free-text generation from vacancy + match result |
| `db.py` | SQLAlchemy 2.0 ORM — persists application records to SQLite |
| `cli.py` | Pipeline entry point — orchestrates all modules end to end |

---

## Project Structure

```
job-hunt-copilot/
├── src/
│   ├── config.py
│   ├── models.py
│   ├── prompts.py
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
3. Print the match score, matched/missing skills, and any red flags
4. Generate a cover letter and print it to stdout
5. Save the cover letter to `output/cover_letter.txt`
6. Persist the application record to `data/jobs.db`

### Example output

```
=== JOB HUNT COPILOT ===
initializing database...

=== MATCH RESULT: Acme Corp — Junior AI Engineer ===
Score: 78% | Good fit: True

Matched skills: Python, LangChain, FastAPI, PostgreSQL
Missing skills: Kubernetes, Go

=== COVER LETTER ===

Dear Hiring Team at Acme Corp, ...

(saved to output/cover_letter.txt)
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
| Testing | [pytest](https://pytest.org/) |
