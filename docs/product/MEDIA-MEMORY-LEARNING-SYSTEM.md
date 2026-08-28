# Media Memory & Learning System Specification

## Purpose

Generalize the original content memory bank into the persistent memory system for the full AI-native media platform. The system must remember what was planned, generated, approved, rejected, published, learned and why—without depending on chat history or any provider's internal history.

## Memory layers

### 1. Canonical project memory
Stores current approved project truth:
- Project settings/version;
- audience/cast/format;
- content/script version;
- character/world/location/prop/style versions;
- approved audio;
- storyboard/timeline;
- selected Takes;
- approvals;
- final master;
- publishing state.

### 2. Creative originality memory
Stores fingerprints and prior concepts for:
- titles;
- topics;
- premises;
- hooks;
- lyrics/refrains;
- plots;
- structures;
- learning goals;
- creative devices;
- character situations;
- visual concepts.

Used to reject duplicates/derivative ideas before full production.

### 3. Canon / continuity memory
Stores persistent facts about:
- characters and looks;
- worlds/locations;
- props;
- series canon;
- episode/movie state changes;
- scene/sequence continuity checkpoints.

### 4. Generation history
Stores every meaningful provider attempt:
- request/attempt IDs;
- provider/model;
- prompt/version/hash;
- input assets;
- output asset/hash;
- cost/quota;
- duration;
- result state;
- QA scores;
- failure/rejection reason;
- retry strategy.

Rejected attempts are memory, not garbage.

### 5. Provider performance memory
Aggregates by provider/model/task class:
- accepted-output rate;
- common failure categories;
- average retries;
- latency;
- cost;
- continuity success;
- manual effort;
- recent health.

Used by Provider Router.

### 6. Research memory
Stores:
- research query/objective;
- dated source/evidence;
- extracted claims;
- freshness;
- confidence;
- related decisions.

Mutable technical/provider facts are re-verified when stale.

### 7. Rights/provenance memory
Stores rights state and evidence references for source/provider/identity usage and downstream propagation.

### 8. Analytics learning memory
Stores:
- publication metric snapshots;
- cohorts;
- hypotheses;
- experiments;
- supported/rejected learnings;
- fatigue/saturation signals.

Analytics learning feeds future planning only through quality/originality gates.

### 9. Operational memory
Stores:
- active jobs;
- workflow references;
- checkpoints;
- locks/leases;
- waiting reasons;
- budget reservations;
- manual handoffs;
- last completed production unit.

This belongs in runtime persistence once PostgreSQL/Temporal are introduced, not only flat Git files.

## Source-of-truth transition

Repository-first phase:
- Git stores canonical engineering policy, planning docs, prompts, research evidence, schemas and current simple memory ledgers.

Application phase:
- PostgreSQL becomes canonical operational state for live projects/jobs/assets/approvals;
- object storage holds binary media;
- Git remains canonical for engineering/configuration/versioned prompt/policy/research artifacts and selected audit exports.

Migration must be explicit; do not silently maintain two conflicting masters.

## Stable IDs and references

Memory uses stable external IDs for audit/cross-system references, e.g. Project/Character/Shot/Take/Asset IDs.

Database internal keys may use UUID/ULID-like identifiers, but external stable IDs remain unique and durable.

## Fingerprints

Originality/semantic memory may use:
- normalized text hashes;
- title/premise/hook hashes;
- keyphrase sets;
- structured concept fingerprint;
- embeddings/vector similarity;
- plot/creative-device classification;
- character/setting usage counts.

Embeddings are one signal, not the sole originality verdict.

## Retrieval scoping

Do not retrieve the entire platform memory for every prompt.

Use task-scoped retrieval:
- current project/canon;
- relevant adjacent continuity;
- closest originality matches;
- prior provider failures for same task type;
- relevant research;
- applicable analytics hypotheses.

## Rejected history

Preserve enough rejected history to avoid:
- recreating duplicate concepts;
- repeating the same provider failure;
- retrying the same prompt/reference combination blindly;
- forgetting why an asset/idea was rejected.

Large rejected media may be archived/expired later while metadata/hash/diagnosis remains according to retention policy.

## Memory consistency

Audit should detect:
- dangling IDs;
- selected asset missing;
- canonical item pointing to rejected output;
- character lock version missing;
- stale approval after upstream version change;
- orphaned generation attempt;
- project timeline mismatch;
- published item without final-master lineage;
- duplicate stable IDs.

## Invalidation

Upstream changes mark only affected downstream memory stale.

Examples:
- script change -> audio/storyboard may stale;
- character version change -> affected unapproved shots/keyframes stale;
- audio duration change -> timing/storyboard stale;
- shot replacement -> adjacent continuity QA stale;
- final master change -> publication approval stale.

Never delete old history merely to make current state appear consistent.

## AI context handoff

Every AI role should receive:
- task-specific canonical state;
- relevant locked decisions;
- relevant prior failures/memory;
- applicable policies;
- explicit requested output schema.

The AI should not infer important state from chat memory when repository/runtime evidence exists.

## Learning governance

Memory can improve decisions but may not self-modify hard policy invisibly.

Examples:
- provider history can adjust routing score;
- retention pattern can influence pacing experiment;
- originality history can suppress repeated theme;
- no memory signal may bypass rights/safety/security/budget gates.

## Audit/export

Important project state should be exportable as an audit manifest including:
- canonical versions;
- asset graph;
- generation attempts;
- approvals;
- costs;
- rights summary;
- publication lineage;
- key learning/hypothesis references.

## Acceptance criteria

Memory system is development-ready when a new AI worker/session can reconstruct the current safe next action, relevant canon, prior failures and approval state from persisted evidence without relying on earlier conversation history.