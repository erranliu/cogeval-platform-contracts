# <Integration Name>

Data schema: `<schema>`

Producer: `<system>`

Consumer: `<system>`

## Purpose

Describe why this integration exists and which product behavior depends on it.

## Producer API

- Method and path:
- Authentication:
- Response shape:
- Required fields beyond the base schema:
- Compatibility notes:

## Consumer Loader

- Default API path:
- Config override:
- Loader implementation:
- Validation:
- Cached or live behavior:

## Data Flow

Describe the producer-to-consumer flow, including any local projection model.

## Failure Behavior

- Platform not configured:
- Unauthorized:
- Unavailable or timeout:
- Invalid schema:
- Missing optional fields:
- Missing required integration fields:

## Required Tests

- Producer tests:
- Consumer loader tests:
- Consumer projection or product behavior tests:

## Minimal Payload

```json
{}
```

