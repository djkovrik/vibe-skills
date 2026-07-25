# Persistence testing

Cover:

- create/read/update/delete and constraints;
- transaction success and rollback;
- every migration from supported historical versions;
- adapter/codec round trips;
- deterministic ordering and reactive emissions;
- snapshot export/atomic replace;
- settings defaults, legacy, malformed, and observation;
- remote-apply suppression;
- driver closure and Android/iOS compilation.

Prefer the real generated schema and platform-equivalent test driver over mocks.

