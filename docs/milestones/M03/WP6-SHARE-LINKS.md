# M03-WP6 Durable Share-Link Authority

This slice makes share-link delivery authority durable without persisting raw bearer tokens.

## Security boundary

- Persist only a lowercase SHA-256 token digest; raw bearer tokens are never canonical data.
- Bind every link to one exact project and asset.
- Persist explicit download/stream permissions, expiry, revocation, optional maximum uses, and current use count.
- Authorize and increment `use_count` in the same PostgreSQL row-lock transaction.
- Treat signed object URLs as ephemeral capabilities, never as canonical authorization.
- Fail closed for wrong asset/project, wrong mode, expiry, revocation, invalid digest, or exhausted usage.

## Concurrency invariant

`PostgresShareLinkRepository.authorize_and_consume()` locks the selected share-link row with `FOR UPDATE` before evaluating the canonical delivery policy. A successful request increments `use_count` before the transaction commits. Concurrent requests competing for the final permitted use therefore serialize: only the first may consume the final use; later requests observe the exhausted count and are denied.

## Migration

Alembic revision `20260901_0013` adds `core.delivery_share_links` after the WP5 derivative migration and is reversible back to `20260831_0012`.
