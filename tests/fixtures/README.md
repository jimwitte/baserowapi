# Characterization fixtures

These fixtures contain sanitized Baserow field metadata and row response shapes
for credential-free characterization tests.

The field and row shapes were derived from the disposable hosted `baserow.io`
test database and its generated API documentation on 2026-09-01. Identifiers
are synthetic, collaborator details are fictitious, and no token,
authorization header, personal path, or unrelated user data is included.

The fixtures began with evidence available to release `0.1.0b5`. Computed,
UUID, and Autonumber shapes were refreshed from hosted `baserow.io` on
2026-09-02 during the `0.2.0b1` refactor. They are not a substitute for current
hosted compatibility tests and must not be treated as a complete Baserow
schema.
