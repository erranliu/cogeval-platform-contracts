# Workbench Self-run Package Ingest — current contract

Data schema: `cogeval.package_import_result.v2`.

The `cogeval.package_import_result.v2` response is the only current self-run import response. Each result has
one of two independent meanings:

- an accepted/rejected import, represented by `accepted` and an optional
  self-contained `failure_reason`;
- a review or acceptance decision, represented by `decision_codes` and
  `queued_for_review`.

`failure_reason` is a `FailureReasonV1` occurrence. It is never reconstructed
from a status, message, or legacy reason-code list. An accepted result has no
failure reason. A rejected non-review result has a platform-owned failure
reason. A queued review result has no failure reason and must contain at least
one decision code.

Workbench and Website share only the wire schema. Owner-local failure
definitions remain in the producer that creates the fact.

Workbench producers import the package manifest, record, and evidence models
through `cogeval_platform_contracts.self_run_packages.current`; direct v1/v2
module imports are retired from the consumer boundary.
