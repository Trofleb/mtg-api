# End-to-End Tests

This directory contains Playwright end-to-end tests for the MTG Card Search web application.

## Quick Start

### Option 1: VPS API with SSH Tunnel (Recommended)

**Automatic setup with Just:**
```bash
# From project root - automatically starts tunnel, runs tests, and cleans up
just test-e2e-vps

# Or for interactive UI mode
just test-e2e-ui-vps
```

**Manual setup:**
```bash
# 1. Start SSH tunnel to VPS API (from project root)
docker-compose -f docker-compose.vps-dev.yml up ssh-tunnel -d

# 2. Verify tunnel is working
curl http://localhost:8000/ping  # Should return: pong

# 3. Run tests (in web-app directory)
cd web-app
pnpm run test:e2e

# 4. Clean up tunnel
docker-compose -f docker-compose.vps-dev.yml down
```

### Option 2: Local API with Docker Compose

```bash
# 1. Start the API and dependencies (from project root)
docker-compose up api
# or: just docker-up-api

# 2. Wait for services to be healthy (~30-45 seconds)
# Watch for: ✅ API is healthy

# 3. Run all e2e tests (in another terminal)
cd web-app
pnpm run test:e2e
```

### Option 3: Homepage Tests Only (No API Required)

```bash
# From web-app directory
pnpm run test:e2e e2e/homepage.spec.ts
```

## Test Files

### `homepage.spec.ts`
Tests the main homepage UI elements and interactions without requiring the API:
- Page title and heading verification
- Scryfall attribution link
- Search input functionality
- Filter panel toggle
- All filter options display (colors, types, rarities, CMC slider)
- Form controls accessibility
- Button states (enabled/disabled)

**Status**: ✅ All tests passing (6/6)

### `card-search.spec.ts`
Tests the card search functionality that requires a running API:
- Basic card search
- Search on Enter key press
- Filter by card type, color, and rarity
- Load more pagination
- Card details dialog
- API error handling
- Loading states

**Status**: ⚠️ Requires API to be running at `http://localhost:8000`

### `api.spec.ts`
Direct API endpoint tests using Playwright's request fixture:
- `/ping` health check endpoint
- Card search endpoints
- Card retrieval by name and ID
- Pagination with cursor
- Error handling (404s, validation errors)
- Content-Type headers

**Status**: ⚠️ Requires API to be running at `http://localhost:8000`

## Running Tests

### Recommended: VPS API Tests (Automatic)

```bash
# From project root - handles tunnel setup and cleanup automatically
just test-e2e-vps

# Run specific test file
just test-e2e-vps e2e/homepage.spec.ts

# Interactive UI mode with VPS
just test-e2e-ui-vps
```

### Manual VPS Tunnel Setup

```bash
# Terminal 1: Start tunnel
just test-e2e-vps-tunnel

# Terminal 2: Run tests
cd web-app
pnpm run test:e2e

# When done, stop tunnel
just test-e2e-vps-tunnel-stop
```

### Local API Tests (Docker Compose)

```bash
# Terminal 1: Start services
docker-compose up api
# or: just docker-up-api

# Terminal 2: Run tests
just test-e2e
# or: cd web-app && pnpm run test:e2e
```

### Homepage Tests Only (No API Required)
```bash
# From web-app directory
pnpm run test:e2e e2e/homepage.spec.ts
```

### Specific Test File
```bash
pnpm run test:e2e e2e/homepage.spec.ts
```

### Interactive UI Mode
```bash
# From project root
just test-e2e-ui

# Or from web-app directory
pnpm run test:e2e:ui
```

### Debug Mode
```bash
# From project root
just test-e2e-debug

# Or from web-app directory
pnpm run test:e2e:debug
```

### With Visible Browser (Headed)
```bash
# From project root
just test-e2e-headed

# Or from web-app directory
pnpm run test:e2e:headed
```

### View Test Report
```bash
# From project root
just test-e2e-report

# Or from web-app directory
pnpm run test:e2e:report
```

## Prerequisites

### For Homepage Tests Only
- No external dependencies required
- Playwright automatically starts the Next.js dev server
- Run: `pnpm run test:e2e e2e/homepage.spec.ts`

### For Full Test Suite

#### Option 1: VPS API (Recommended - Easiest)

Uses SSH tunnel to connect to VPS API:

```bash
# Automatic - one command does everything
just test-e2e-vps
```

This command:
- Starts SSH tunnel to VPS API
- Runs Playwright tests
- Cleans up tunnel automatically

**Requirements:**
- VPS connection configured in `.env` (VPS_HOST, VPS_USER, VPS_API_PORT)
- 1Password SSH agent with VPS key
- VPS API running and accessible

#### Option 2: Local API (Full Docker Stack)

**Using Docker Compose:**

```bash
# From project root - Start API and all dependencies
docker-compose up api

# This starts:
# - API (FastAPI) on port 8000
# - MongoDB on port 27017
# - Redis on port 6379
# - Meilisearch on port 7700
```

**Or use Just commands:**
```bash
# From project root
just docker-up-api

# Check API health
just health
# Should show: ✅ API is healthy
```

**Verify API is ready:**
```bash
curl http://localhost:8000/ping
# Should return: pong
```

## Configuration

Test configuration is in `playwright.config.ts`:
- **Base URL**: `http://localhost:3000`
- **Browser**: Chromium (Firefox and WebKit available but commented out)
- **Timeout**: 30 seconds per test
- **Retries**: 2 retries in CI, 0 locally
- **Workers**: 1 in CI, unlimited locally
- **Reporters**: HTML, JSON, List
- **Artifacts**: Screenshots/videos on failure only, traces on first retry

## Web Server

Playwright automatically manages the Next.js development server:
- **Development**: `pnpm run dev`
- **CI**: `pnpm run build && pnpm run start`
- **Timeout**: 120 seconds for server startup
- **Reuse**: Existing server reused in local development

## Debugging Failed Tests

When a test fails, Playwright captures:
1. **Screenshot** - Visual state at failure
2. **Video** - Full test execution recording (on failure)
3. **Trace** - Detailed execution trace (on retry)

Access these in:
- `test-results/` directory
- HTML report: `playwright-report/index.html`

### View Trace Files
```bash
npx playwright show-trace path/to/trace.zip
```

## Writing New Tests

### Best Practices

1. **Use Semantic Selectors**
   ```typescript
   // Good
   page.getByRole('button', { name: 'Search' })
   page.getByLabel('Email')

   // Avoid
   page.locator('.btn-primary')
   ```

2. **Wait for Elements**
   ```typescript
   await expect(page.getByText('Results')).toBeVisible({ timeout: 10000 });
   ```

3. **Use data-testid for Complex Elements**
   ```typescript
   <div data-testid="card-item">...</div>

   page.locator('[data-testid="card-item"]')
   ```

4. **Group Related Tests**
   ```typescript
   test.describe('Feature Name', () => {
     test.beforeEach(async ({ page }) => {
       await page.goto('/');
     });

     test('specific behavior', async ({ page }) => {
       // test code
     });
   });
   ```

5. **Handle API Dependencies**
   ```typescript
   // Mock API responses when testing UI behavior
   await page.route('**/api/cards/search*', route =>
     route.fulfill({ json: mockData })
   );
   ```

## CI/CD Integration

Add to `.github/workflows/playwright.yml`:
```yaml
name: Playwright Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: lts/*
      - name: Install dependencies
        run: cd web-app && pnpm install
      - name: Install Playwright Browsers
        run: cd web-app && npx playwright install --with-deps
      - name: Run Playwright tests
        run: cd web-app && pnpm run test:e2e
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: web-app/playwright-report/
```

## Troubleshooting

### Tests Timing Out
- Increase timeout in test or config
- Check if API is running for API-dependent tests
- Verify network connectivity

### Strict Mode Violations
Use `exact: true` for buttons with similar names:
```typescript
page.getByRole('button', { name: 'Filters', exact: true })
```

### Flaky Tests
- Add explicit waits: `await page.waitForLoadState('networkidle')`
- Use `toBeVisible()` instead of truthy checks
- Ensure unique selectors with `exact: true`

### API Not Found Errors
Start the API before running API-dependent tests:
```bash
# From project root
docker-compose up api

# Verify API is responding
curl http://localhost:8000/ping
# Should return: pong

# Check service health
just health
```

### Port Already in Use
If port 8000 is already taken:
```bash
# Stop existing containers
docker-compose down

# Restart API
docker-compose up api
```

## Development Workflow

### Complete Testing Cycle

```bash
# Terminal 1: Start backend services
cd /path/to/mtg-api
docker-compose up api
# Wait for: "API is running on http://0.0.0.0:8000"

# Terminal 2: Develop and test
cd /path/to/mtg-api/web-app

# Run all tests
pnpm run test:e2e

# Or use interactive UI mode for development
pnpm run test:e2e:ui

# Or debug specific test
pnpm run test:e2e:debug e2e/homepage.spec.ts
```

### Using Just Commands

```bash
# Terminal 1: Start services
just docker-up-api

# Terminal 2: Run tests
just test-e2e

# Or interactive mode
just test-e2e-ui

# Check service health anytime
just health
```

### CI/CD Workflow

```bash
# This is what CI does automatically:
docker-compose up api &          # Start API in background
pnpm run build                   # Build Next.js app
pnpm run test:e2e                # Run all tests
docker-compose down              # Clean up
```

## Resources

- [Playwright Documentation](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Next.js Testing Guide](https://nextjs.org/docs/testing)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
