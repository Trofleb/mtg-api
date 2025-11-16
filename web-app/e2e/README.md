# End-to-End Tests

Playwright e2e tests for the MTG Card Search web application.

## Quick Start

### Recommended: VPS API (One Command)

```bash
# From project root - automatic tunnel setup and cleanup
just test-e2e-vps

# Interactive UI mode
just test-e2e-ui-vps
```

This automatically:
- Starts SSH tunnel to VPS API
- Runs all Playwright tests
- Cleans up tunnel when done

### Local API

```bash
# Terminal 1: Start API
docker-compose up api

# Terminal 2: Run tests
just test-e2e
```

### UI Tests Only (No API Required)

```bash
# From web-app directory
pnpm run test:e2e e2e/homepage.spec.ts
```

## Test Files

- **`homepage.spec.ts`** - UI-only tests (no API required) ✅ 6/6 passing
- **`card-search.spec.ts`** - Card search with API integration
- **`api.spec.ts`** - Direct API endpoint tests

## Common Commands

```bash
# VPS API tests (recommended)
just test-e2e-vps              # Run all tests
just test-e2e-vps e2e/api.spec.ts  # Run specific file
just test-e2e-ui-vps           # Interactive UI mode

# Local API tests
just test-e2e                  # All tests
just test-e2e-ui               # Interactive mode
just test-e2e-debug            # Debug with inspector

# From web-app directory
pnpm run test:e2e              # All tests
pnpm run test:e2e:ui           # Interactive mode
pnpm run test:e2e:debug        # Debug mode
pnpm run test:e2e e2e/homepage.spec.ts  # Specific file
```

## How It Works

### VPS Tunnel Setup

The `just test-e2e-vps` command:

1. Starts SSH tunnel container via `docker-compose.vps-dev.yml`
2. Tunnels VPS API to `localhost:8000`
3. Waits for API to respond
4. Runs Playwright tests with `--reporter=list` (non-blocking)
5. Automatically tears down tunnel

### Local API Setup

Requirements:
- Docker Compose
- API running on port 8000

```bash
# Start full stack
docker-compose up api

# Verify API is ready
curl http://localhost:8000/ping  # Should return: pong
```

## Debugging

### View Test Artifacts

Failed tests generate:
- Screenshots in `test-results/`
- Videos in `test-results/`
- Traces for retry attempts

### Trace Viewer

```bash
npx playwright show-trace path/to/trace.zip
```

### Common Issues

**Tunnel fails to start:**
```bash
# Check VPS connection in .env (VPS_HOST, VPS_USER, VPS_API_PORT)
# Verify 1Password SSH agent is running
```

**Tests timeout:**
```bash
# Verify API is accessible
curl http://localhost:8000/ping
```

**"Apply Filters" button ambiguity:**
- Use more specific selectors in tests
- This is a known issue being addressed

## Configuration

Playwright config (`playwright.config.ts`):
- Base URL: `http://localhost:3000`
- Browser: Chromium
- Timeout: 30s per test
- Retries: 2 in CI, 0 locally
- Reporters: List (non-blocking), JSON

Web server auto-start:
- Development: `pnpm run dev`
- CI: `pnpm run build && pnpm run start`
- Timeout: 120s

## Writing Tests

### Best Practices

```typescript
// Use semantic selectors
page.getByRole('button', { name: 'Search', exact: true })
page.getByLabel('Email')

// Wait explicitly
await expect(page.getByText('Results')).toBeVisible({ timeout: 10000 });

// Use data-testid for complex elements
page.locator('[data-testid="card-item"]')
```

### Test Structure

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

## Resources

- [Playwright Documentation](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Next.js Testing Guide](https://nextjs.org/docs/testing)
