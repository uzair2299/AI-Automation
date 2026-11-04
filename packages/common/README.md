# Smiota Common Library (`smiota-common`)

Shared foundational library for Smiota AI microservices, containing domain-agnostic logging, correlation tracking, exceptions, and API response models.

## Modules

- `smiota_common.logging`: Structured logging, Google Cloud / Datadog compliant `CloudJSONFormatter`, `CorrelationFilter`, and `setup_logging`.
- `smiota_common.middleware`: `CorrelationIdMiddleware` for FastAPI / Starlette distributed request tracing via `X-Correlation-ID`.
- `smiota_common.models`: Generic API response envelopes (`APIResponse[T]`) and error structures.
- `smiota_common.exceptions`: Enterprise base exception hierarchy (`SmiotaException`).

## Installation

For local development in editable mode:
```bash
pip install -e packages/common
```

In Docker builds:
```dockerfile
COPY packages/common /tmp/packages/common
RUN pip install /tmp/packages/common
```

