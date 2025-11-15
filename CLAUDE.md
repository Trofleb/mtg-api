# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Container-Based Development
- `docker-compose up` - Start all services (API, app, web-app, database, cache, etc.)
- `docker-compose up api` - Start only the FastAPI service on port 8000
- `docker-compose up app` - Start only the Streamlit app on port 8501
- `docker-compose up web-app` - Start only the Next.js app on port 3000
- `docker-compose up huey` - Start only the background task worker
- `docker-compose logs -f <service>` - Follow logs for specific service

### Python Dependencies
- Uses `uv` package manager (configured in pyproject.toml)
- Core dependencies include FastAPI, MongoDB, Meilisearch, LangChain, httpx, typer, rich
- Optional groups: `tests` (pytest), `dev` (ruff, pre-commit), `app` (Streamlit), `notebooks` (Jupyter)
- Install with: `uv sync` (all), `uv sync --extra tests` (with tests), `uv sync --group app` (with Streamlit), `uv sync --group dev` (development tools)

### Task Runner (Just)
- `just` - Show all available commands
- `just install` - Install all dependencies (`uv sync`)
- `just install-dev` - Install with dev dependencies
- `just install-tests` - Install with test dependencies
- `just install-all` - Install all extras

#### Development Workflows
- `just dev` - Start FastAPI development server (install dev deps first)
- `just dev-api` - Start FastAPI dev server directly
- `just dev-app` - Start Streamlit app
- `just dev-huey` - Start background task worker

#### Docker Shortcuts
- `just docker-up` - Start all services
- `just docker-up-api` - Start only API service
- `just docker-up-app` - Start only Streamlit app
- `just docker-down` - Stop all services
- `just docker-logs <service>` - Follow logs for specific service

#### Testing & Quality
- `just test` - Run pytest with test dependencies
- `just test-cov` - Run tests with coverage report
- `just test-file <file>` - Run tests for specific file
- `just lint` - Run ruff linting
- `just lint-fix` - Run ruff with auto-fix
- `just format` - Format code with ruff
- `just pre-commit` - Run pre-commit hooks
- `just ci` - Run full CI pipeline (format-check, lint, test)

#### MTG Events Shortcuts
- `just events` - List all MTG events
- `just events-compact` - List events in compact format
- `just events-whatsapp` - List events in WhatsApp format
- `just events-test` - Test API connection

#### Utilities
- `just clean` - Remove build artifacts and cache
- `just info` - Show project information and service URLs
- `just health` - Check health of running services
- `just update` - Update dependencies

### Code Quality
- `ruff check` - Run linting
- `ruff format` - Format code
- `uv run pytest` - Run tests (requires `--extra tests`)
- `pre-commit run --all-files` - Run pre-commit hooks

### Key Services
- API: FastAPI application running on port 8000
- App: Streamlit application running on port 8501
- Web App: Next.js application running on port 3000 (modern card search interface)
- Database: MongoDB on port 27017 with username/password: root/root
- Cache: Redis on port 6379
- Search: Meilisearch on port 7700
- Timeseries: InfluxDB on port 8181

## Code Architecture

### Service Architecture
This is a multi-service application with separate containers for:
- **API**: FastAPI backend with MTG/D&D data endpoints
- **App**: Streamlit frontend for interactive data exploration
- **Huey**: Background task processor for data ingestion/processing
- **Database**: MongoDB for document storage
- **Cache**: Redis for caching and session storage
- **Search**: Meilisearch for full-text search capabilities
- **Timeseries**: InfluxDB for metrics and time-based data

### API Structure (`api/`)
- **Entry point**: `api/main.py` - FastAPI app with router includes
- **Routes**: `api/router/` contains modular routers:
  - `base.py`: Health checks and basic endpoints
  - `cards.py`: MTG card search and retrieval
  - `ocr.py`: PDF/image text extraction via RunPod
  - `dnd_rules.py`: D&D rules and content
  - `mtg_rules.py`: MTG rules and mechanics
  - `sets.py`: MTG set information
  - `sulapi.py`: SUL (external API) integration
- **Helpers**: `api/helpers/` contains database utilities
- **Dependencies**: `api/depedencies/` contains LangChain and embedding configs

### Frontend Structure

#### Streamlit App (`app/`)
- **Entry point**: `app/app.py` - Main Streamlit application
- **Pages**: `app/pages/` contains feature modules:
  - `card_search.py`: MTG card search interface
  - `file_ocr.py`: File upload and OCR processing
  - `deck_list.py`: Deck building and management
  - `mtg_db.py`: Database exploration tools
  - `mtg_rules.py`: Rules lookup interface
  - `dnd_rules.py`: D&D content browser
  - `sul.py`: External API interaction
- **Utils**: `app/utils/` contains shared utilities
- **Dialog**: `app/dialog/` contains UI event handling

#### Next.js Web App (`web-app/`)
- **Framework**: Next.js 16 with App Router, TypeScript (strict mode), Tailwind CSS 4
- **UI Components**: shadcn/ui for modern, accessible components
- **Code Quality**: Biome for linting and formatting
- **Testing**: Vitest with React Testing Library and jsdom
- **Package Manager**: pnpm for dependency management
- **Features**: Modern MTG card search with advanced filtering
- **Structure**:
  - `app/`: Next.js app router pages and layouts
  - `components/`: React components (card-search, card-grid, card-details-dialog)
  - `lib/`: Utility functions and API client
  - `components/ui/`: shadcn/ui components
  - `test/`: Testing utilities and custom render functions
- **Development**:
  - `pnpm dev` - Start development server on port 3000
  - `pnpm build` - Build for production
  - `pnpm lint` - Run Biome linter
  - `pnpm format` - Format code with Biome
  - `pnpm typecheck` - Run TypeScript type checking
  - `pnpm test` - Run Vitest in watch mode
  - `pnpm test:run` - Run tests once and exit
  - `pnpm test:ui` - Run tests with Vitest UI
  - `pnpm test:coverage` - Run tests with coverage report
- **Testing Setup**:
  - **Configuration**: `vitest.config.ts` with React plugin and path alias support
  - **Setup File**: `vitest.setup.ts` with Next.js mocks (navigation, Image, Link) and ResizeObserver
  - **Test Utils**: `test/test-utils.tsx` with custom render function including userEvent
  - **Coverage**: Configured with v8 provider, excludes config files and node_modules
  - **Test Files**: `*.test.ts` and `*.test.tsx` files located next to source files
- **Docker**: Standalone Dockerfile with multi-stage builds for production

### Background Tasks (`tasks/`)
- **Main**: `tasks/tasks.py` - Huey task definitions
- **Data fetching**: `tasks/fetch_dataset.py`, `tasks/ifetch_dataset.py`
- **Indexing**: `tasks/indexes.py` - Search index management
- **Utilities**: `tasks/obj_utils.py` - Object manipulation helpers

### CLI Scripts (`scripts/`)
- **MTG Events**: `scripts/mtg_events.py` - Command-line tool for fetching MTG events
  - Uses Typer for CLI interface with Rich for output formatting
  - Fetches events from Wizards' GraphQL API for organization 10933 (Xenomorphe)
  - Supports compact and detailed French formatting with emojis
  - **NEW**: WhatsApp-style formatting with venue-based grouping and competitive indicators
  - Usage: `uv run python scripts/mtg_events.py list-events --help`

### Shared Code (`common/`)
- **Models**: `common/scyfall_models.py` - Scryfall API data models
- **Constants**: `common/constants.py` - Shared configuration
- **Infomaniak**: `common/infomaniak/` - Swiss cloud provider integrations
- **Events**: `common/events/` - MTG event fetching and formatting
  - `models.py`: Pydantic models for Wizards' GraphQL API data
  - `fetcher.py`: HTTP client for Wizards' GraphQL endpoint with organization filtering
  - `formatter.py`: French message formatting with emoji templates and WhatsApp syntax support

### Data Science (`notebooks/`)
- Card database building: `build_card_db*.ipynb`
- OCR testing: `olmocr_test.ipynb`
- Dataset processing: `augment_dataset.ipynb`, `split_dataset_640.ipynb`
- Model training: `card_detection.ipynb`, `test_model.ipynb`
- Data ingestion: `push_data_mtg.ipynb`, `push_data_dnd.ipynb`

### OCR System Integration
- **Model**: AllenAI olmOCR-7B via RunPod serverless
- **Processing**: PyMuPDF for PDF text extraction + LLM enhancement
- **Computer Vision**: YOLO models for card detection, SAM2 for segmentation
- **Image Processing**: OpenCV, Kornia for image manipulation

### MTG Events System
The project includes a comprehensive system for fetching and formatting Magic: The Gathering events:

#### Organization Filtering
- **Target Organization**: 10933 (Xenomorphe)
- **Post-processing Filter**: Fetches all events geographically, then filters by organization ID
- **Location Strategy**: Uses broad Geneva coordinates (46.2043907, 6.1431577, 50km radius)

#### Venue Mapping
Known venue coordinates are mapped to full addresses:
- `46.2114995, 6.1206073` → "Espace Santé Esclarmonde, Avenue Soret 39, 1203 Genève"
- `46.20118, 6.13793` → "Clos Voltaire 49 rue de Lyon"

#### Pricing Extraction
- **Primary Source**: Event description field parsed for member/non-member pricing
- **Patterns**: "Membres XX CHF Non Membre YY CHF" and variations
- **Fallback**: Uses entryFee.amount for non-member pricing only

#### Message Formatting
**Traditional Format** - Two-section French format:
1. **Compact (15 days)**: `J-X Event Name - XX CHF NM (CODE)`
2. **Detailed (7 days)**: Emoji template with full event details

**WhatsApp Format** - Venue-grouped with WhatsApp text formatting:
1. **Detailed section** (7 days): Events grouped by venue with `*bold*`, `_italic_`, and `` `monospace` `` formatting
2. **Compact section** (8-15 days): Condensed venue-grouped format
3. **Competitive indicators**: 🏆 emoji for COMPETITIVE rules level events
4. **Simplified attendance**: "Inscrits : X/Y" format (removes "places disponibles" text)
5. **Event descriptions**: Included in detailed format with italic formatting

#### CLI Usage Examples
```bash
# List all events (complete format)
uv run python scripts/mtg_events.py list-events

# Compact format only
uv run python scripts/mtg_events.py list-events --format compact

# WhatsApp format with venue grouping
uv run python scripts/mtg_events.py list-events --format whatsapp

# WhatsApp detailed format only (7 days)
uv run python scripts/mtg_events.py list-events --format whatsapp-detailed

# Test API connection
uv run python scripts/mtg_events.py test-connection

# Debug mode with verbose output
uv run python scripts/mtg_events.py list-events --debug
```

#### Programmatic Usage
```python
from common.events import EventFetcher, EventFormatter

# Fetch events
fetcher = EventFetcher()
events = await fetcher.fetch_events(organization_id="10933")

# Format for display (traditional)
message = EventFormatter.format_complete_message(events)
print(message)

# Format for WhatsApp
whatsapp_message = EventFormatter.format_complete_message_whatsapp(events)
print(whatsapp_message)
```

### Environment Configuration
Required variables in `.env` (see `.env.example`):
- **Database**: `DATABASE`, `DATABASE_HOSTNAME`, `DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD`
- **Search**: `MEILI_MASTER_KEY`
- **OCR**: `API_KEY_OCR_MODEL`, `API_KEY_OCR_LLM`, `API_BASE_URL_OCR_MODEL`
- **Cloud**: `IK_API_KEY`, `IK_PRODUCT_ID` (Infomaniak)
- **External**: `MARKER_OCR_KEY` (alternative OCR service)
