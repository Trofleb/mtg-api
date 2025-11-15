# MTG API

A comprehensive Magic: The Gathering data API with card search, OCR capabilities, and event management features.

## Features

- **Card Search**: FastAPI backend with Meilisearch-powered full-text search
- **Multi-Frontend**: Streamlit and Next.js web interfaces
- **OCR Processing**: PDF and image text extraction for card recognition
- **MTG Events**: Fetch and format MTG tournament events with WhatsApp-ready messages
- **D&D Content**: Rules and content browser for D&D 5e
- **Background Tasks**: Huey-based task processing for data ingestion

## MTG Events CLI

The project includes a powerful command-line tool for fetching and formatting Magic: The Gathering events from Wizards' official API.

### Features

- Fetches events for organization 10933 (Xenomorphe)
- Multiple output formats: traditional French and WhatsApp-optimized
- Venue-based grouping for better readability
- Automatic pricing extraction from event descriptions
- Competitive event indicators (🏆)
- Rich terminal output with emoji support

### Quick Start

```bash
# List all upcoming events (default format)
uv run python scripts/mtg_events.py list-events

# WhatsApp format with venue grouping
uv run python scripts/mtg_events.py list-events --format whatsapp

# Compact format only (15 days)
uv run python scripts/mtg_events.py list-events --format compact

# Test API connection
uv run python scripts/mtg_events.py test-connection
```

### Using Just Commands

```bash
# Shortcut commands via Justfile
just events                # Complete message (compact + detailed)
just events-compact        # Compact format (15 days)
just events-whatsapp       # WhatsApp format with venue grouping
just events-test           # Test API connection
```

### Format Options

**Traditional Format** (`--format complete`):
- Compact section: Next 15 days with countdown format (`J-X Event Name - XX CHF NM`)
- Detailed section: Next 7 days with full emoji template

**WhatsApp Format** (`--format whatsapp`):
- Detailed section: Events grouped by date, then by venue with WhatsApp text formatting (`*bold*`, `_italic_`, `` `code` ``)
- Compact section: Days 8-15 in condensed venue-grouped format
- Competitive events marked with 🏆
- Clean attendance format: "Inscrits : X/Y"

**WhatsApp Detailed Only** (`--format whatsapp-detailed`):
- Only the detailed venue-grouped section (next 7 days)
- Perfect for quick announcements

### Advanced Options

```bash
# Custom organization and date ranges
uv run python scripts/mtg_events.py list-events \
  --org-id 10933 \
  --days 30 \
  --compact-days 20 \
  --detailed-days 10

# Debug mode with verbose output
uv run python scripts/mtg_events.py list-events --debug

# Show raw GraphQL responses
uv run python scripts/mtg_events.py list-events --show-raw-events
```

### Programmatic Usage

```python
from common.events import EventFetcher, EventFormatter

# Fetch events
fetcher = EventFetcher()
events = await fetcher.fetch_events(organization_id="10933")

# Traditional format
message = EventFormatter.format_complete_message(events)
print(message)

# WhatsApp format
whatsapp_message = EventFormatter.format_complete_message_whatsapp(events)
print(whatsapp_message)

# Custom grouping
venue_groups = EventFormatter.group_events_by_date_then_venue(events)
```

## Development

### Prerequisites

1. Install Python 3.13 (on Linux, use [pyenv](https://github.com/pyenv/pyenv))
2. Install [uv](https://docs.astral.sh/uv/) package manager
3. Install [Docker](https://docs.docker.com/get-docker/) and Docker Compose
4. Install [Just](https://github.com/casey/just) command runner (optional but recommended)

### Setup

```bash
# Install all dependencies
just install-all

# Or manually
uv sync --all-extras

# Start all services
docker-compose up

# Start specific services
docker-compose up api      # FastAPI on :8000
docker-compose up app      # Streamlit on :8501
docker-compose up web-app  # Next.js on :3000
```

### Available Services

- **API**: http://localhost:8000 (FastAPI with Swagger docs at /docs)
- **Streamlit App**: http://localhost:8501
- **Next.js Web App**: http://localhost:3000
- **MongoDB**: localhost:27017 (root/root)
- **Meilisearch**: http://localhost:7700
- **Redis**: localhost:6379
- **InfluxDB**: http://localhost:8181

### Development Commands

See the [Justfile](justfile) for all available commands, or run `just` to list them.

Key commands:
```bash
just dev              # Start FastAPI dev server
just dev-app          # Start Streamlit app
just test             # Run pytest
just lint             # Run ruff linter
just format           # Format code
just docker-up        # Start all Docker services
```

## Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Required
MEILI_MASTER_KEY=your_meilisearch_key
DATABASE_PASSWORD=your_db_password

# Optional (for OCR features)
API_KEY_OCR_LLM=your_runpod_api_key
MARKER_OCR_KEY=your_marker_key

# Optional (for cloud storage)
IK_API_KEY=your_infomaniak_key
IK_PRODUCT_ID=your_product_id
```

## Testing

```bash
# Run all tests
just test

# Run with coverage
just test-cov

# Run specific test file
just test-file tests/test_api.py
```

## Project Structure

```
mtg-api/
├── api/              # FastAPI backend
├── app/              # Streamlit frontend
├── web-app/          # Next.js frontend
├── common/           # Shared code and models
├── scripts/          # CLI tools (mtg_events.py)
├── tasks/            # Background job workers
├── notebooks/        # Jupyter notebooks for data processing
└── justfile          # Command runner recipes
```

## License

See [LICENSE](LICENSE) file for details.
