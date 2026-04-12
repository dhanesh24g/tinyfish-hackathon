# Architecture

## Monorepo Layout

```text
apps/
  api/   # Python FastAPI backend
  web/   # Next.js frontend
docs/    # shared architecture and onboarding docs
```

## Backend Ownership

The backend owns:

- **Job extraction** - TinyFish web scraping + LLM metadata extraction
- **TinyFish orchestration** - Timeout handling (60s), failure detection, fallbacks
- **Question generation** - Research-based + JD-inferred questions
- **Question ranking** - Importance scoring and prioritization
- **Interview session state** - Turn management and transcript
- **Answer evaluation** - Real-time scoring with LLM
- **Final feedback reports** - Summary, scores, and preparation guidance

## Frontend Ownership

The frontend owns:

- **User flows** - Job input → Research → Interview → Feedback
- **Authentication UX** - API key validation
- **Session rendering** - Real-time progress updates with smooth animations
- **Audio capture UI** - Voice interview interface
- **Report presentation** - Feedback display and export

## Integration Boundary

The frontend should treat the backend as the system of record for interview workflow state.

### Core API Flows

1. **Create or extract a job target** - `POST /job-targets/extract`
   - TinyFish extracts job posting (60s timeout)
   - Metadata extraction uses TinyFish result directly (avoids re-processing)
   - Fallback: URL-derived metadata on timeout

2. **Trigger research** - `POST /research/run` (SSE streaming)
   - Builds targeted search queries (Glassdoor, Reddit, Blind)
   - TinyFish scrapes multiple sources in parallel
   - Detects failure signals (captcha, blocked, rate limits)
   - Streams progress updates to frontend

3. **Fetch ranked question bank** - `GET /question-bank/{job_target_id}`
   - Returns questions with importance scores
   - Fallback: LLM-inferred questions from JD if research fails

4. **Start interview session** - `POST /interview/session/start`
   - Creates session with ranked questions
   - Returns first question

5. **Send interview events** - `POST /interview/session/{id}/event`
   - User answers, clarifications, or skip actions
   - Real-time evaluation with gpt-4o-mini
   - Returns next question or completion signal

6. **Fetch feedback report** - `GET /interview/session/{id}/feedback`
   - Generates comprehensive feedback with Pydantic validation
   - Ensures all list fields (prep_guidance, strengths, etc.) are arrays

## Technical Implementation Details

### Job Extraction Flow

```
User submits URL
    ↓
TinyFish extracts (60s timeout)
    ↓ Returns: company_name, role_title, job_description
    ↓
Use TinyFish metadata directly (no LLM re-processing)
    ↓ Avoids: Greenhouse/Lever platform misidentification
    ↓
Fallback on timeout: URL-derived metadata (confidence: 0.3)
```

### Research Query Strategy

Targeted search queries to high-quality sources:
- **Company + Role**: `{company}+{role}+interview+questions+site:glassdoor.com`
- **Experiences**: `{company}+interview+experience+site:reddit.com+OR+site:blind.com`
- **Technical Fallback**: `{role}+technical+interview+questions+2026`

### Timeout & Error Handling

| Component           | Timeout | Fallback                       |
| ------------------- | ------- | ------------------------------ |
| Job Extraction      | 60s     | URL-derived metadata           |
| Research (per URL)  | 60s     | Skip URL, continue             |
| Research (all fail) | N/A     | LLM-inferred questions from JD |

**Failure Detection** (per TinyFish docs):
- Checks for: `captcha`, `blocked`, `access denied`, `rate limit`, `cloudflare`
- Logs warnings but continues with partial data

### LLM Configuration

- **Model**: `gpt-4o-mini` (fast, cost-effective, 128K context)
- **Cost**: ~$0.15 input / $0.60 output per 1M tokens
- **Use Cases**: Job metadata, question extraction, answer evaluation, feedback generation
- **Prompts**: Explicit instructions to avoid platform name confusion

### Data Validation

**Pydantic Validators** ensure type safety:
```python
@field_validator("prep_guidance", "strengths", "improvement_areas", mode="before")
def ensure_list(cls, v: str | list | None) -> list[str]:
    # Normalizes LLM string responses to arrays
```

**Database URL Normalization**:
```python
@field_validator("database_url", mode="after")
def normalize_database_url(cls, v: str) -> str:
    # Converts postgresql:// to postgresql+psycopg2://
    # Ensures compatibility with psycopg2-binary driver
```

### Frontend Progress Updates

**Smooth Progress Animation**:
- Uses `requestAnimationFrame` for 60fps updates
- Animates progress bar from current → target over 400-800ms
- User-friendly messages (no raw API endpoints shown)

**Status Messages**:
- ✓ "Found AI Engineer at Temus"
- ✓ "Analyzed glassdoor.com"
- ✓ "Research complete - 3 sources analyzed"

### Environment Variables

**Required for Production**:
```bash
OPENAI_API_KEY=sk-...           # OpenAI API key
TINYFISH_API_KEY=tf_...         # TinyFish API key
DATABASE_URL=postgresql://...   # Supabase/Postgres URL
BACKEND_CORS_ORIGINS=https://... # Frontend domain
```

**Optional Configuration**:
```bash
TINYFISH_TIMEOUT_SECONDS=60     # Default: 60s (per TinyFish docs)
TINYFISH_USE_MOCK=false         # Default: true (dev mode)
OPENAI_MODEL=gpt-4o-mini        # Default: gpt-4o-mini
```
