# M09 — Continuity and Generated Media QA

## Objective

Implement multimodal QA and take comparison so identity, environment, camera, action, style, anatomy, text, safety and continuity failures are detected, ranked and repaired at the smallest affected scope.

## Entry criteria

- P0 complete.
- M01–M08 accepted.
- Explicit M09 consent.
- Current multimodal evaluation model/provider options revalidated.

## Dependencies

`M04 entities + M07 continuity state + M08 generated takes -> M09`

## Work packages

### M09-WP1 — Canonical QA rubric engine
- QA dimension registry;
- hard vs soft thresholds;
- audience/policy profile;
- evaluator type (`DETERMINISTIC | MODEL | CV/MEDIA | HUMAN | HYBRID`);
- score/confidence/evidence;
- pass/fail/review state;
- versioned rubric.

### M09-WP2 — Identity/character QA
Compare approved take/keyframes against pinned CharacterVersion/Look/reference pack:
- face/shape;
- body/proportions;
- hair/eyes/skin/fur;
- wardrobe/accessories;
- distinctive marks/colors;
- voice identity linkage for multimodal scenes.

Locked attributes are hard failures according to policy.

### M09-WP3 — Environment/prop/style QA
- location/world identity;
- props/continuity;
- palette/style;
- lighting/time of day;
- unwanted text/logos/watermarks;
- composition/scene requirements.

### M09-WP4 — Camera/action/anatomy QA
- shot size/camera direction;
- movement intent;
- screen direction/eye-line;
- character position/pose;
- required action completion;
- anatomy/artifacts;
- temporal stability/flicker where detectable.

### M09-WP5 — Temporal continuity QA
Compare:
- previous approved outgoing state;
- current incoming/first frame;
- current end state;
- next-shot expected state where known.

Detect wardrobe/prop/location/pose/screen-direction/lighting discontinuity.

### M09-WP6 — Safety/text/rights technical QA
- content policy/safety hard gates;
- unwanted/incorrect on-screen text;
- platform/publishing technical eligibility hints;
- watermark/rights restrictions;
- malformed media/probe issues.

### M09-WP7 — Take ranking, compare and repair planner
- normalize QA records across takes;
- hard-fail exclusion;
- rank eligible candidates by quality/continuity/cost;
- human compare/override;
- generate scoped repair request;
- choose retry same provider/switch provider/re-reference/manual review;
- never regenerate already approved unaffected shots by default.

### M09-WP8 — Calibration/evaluation and acceptance
- golden continuity fixture set;
- known drift/failure fixtures;
- false-positive/false-negative calibration;
- AI evaluator regression suite;
- human-labeled calibration set;
- representative sequence with intentionally failed takes;
- prove only failed shots are regenerated and final accepted sequence retains continuity records.

## Expected modules/files

- QA rubric/evaluator services;
- multimodal evaluator adapters;
- continuity comparator;
- take ranking/repair planner;
- QA APIs and records;
- evaluation fixtures/tests.

## Data/migration impact

Adds QA rubric/version, QARecord/evidence/scores, take-ranking decisions, repair/regeneration requests and evaluator version references.

## API/UI impact

Adds take comparison, QA findings, approve/reject/repair APIs. Rich review UI is M11 but records are UI-ready.

## Security/cost/rights impact

- QA models receive only authorized tenant assets;
- provider/model evaluation cost budgeted;
- evaluator outputs untrusted/validated;
- safety/rights hard failures block approval;
- user/human override audited and cannot bypass non-overridable policy gates.

## Test/acceptance

Apply Master QA character/continuity/AI sections:
- reference drift;
- screen direction;
- prop/wardrobe mismatch;
- anatomy/text/watermark;
- evaluator malformed output;
- threshold regression;
- human override;
- cross-provider sequence;
- retry only failed scope.

## Rollout/rollback

QA rubric/evaluator versions are canaried. Previous known-good thresholds/evaluator stack retained. Historical approved QA records never silently rescore unless an explicit re-evaluation job is created.

## Exit criteria

A multi-shot, multi-provider sequence can automatically identify bad takes, compare alternatives and regenerate only affected shots while preserving approved work and a complete explainable QA history.

## Non-goals

- claim perfect visual understanding;
- automatic override of hard safety/rights policy;
- final timeline/render assembly;
- full review UI;
- biometric identification of real people beyond authorized project continuity use.
