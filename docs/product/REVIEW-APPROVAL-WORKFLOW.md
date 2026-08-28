# Review & Approval Workflow Specification

## Purpose

Define what AI may approve autonomously, what requires human review, how revisions are requested and how approved state is preserved without ambiguity.

## Review principles

- Approval is attached to a specific version/asset/state.
- Regeneration creates a new candidate; it does not erase prior approval history.
- Hard safety/rights/security/budget/publication gates override convenience settings.
- Review checkpoints should be configurable by project, but irreversible/high-impact actions remain protected.

## Reviewable stages

Potential checkpoints:
- project brief;
- audience/cast/content format;
- character creation/lock;
- script/lyrics/content;
- audio direction;
- audio master;
- visual/style bible;
- storyboard;
- keyframes;
- generated takes;
- scene assembly;
- final video master;
- thumbnail/metadata;
- private upload;
- public publish/schedule.

## Approval modes

### AI_AUTONOMOUS_WITH_HARD_GATES
AI may approve routine reversible outputs that pass configured QA. Human review remains for locked identities, unresolved rights, unconfigured spend and public publishing.

### STAGE_APPROVAL
Human approval at selected major stages, e.g. content -> audio -> storyboard -> final master.

### SCENE_APPROVAL
Human reviews every Scene after its Shots are assembled/QA-passed.

### TAKE_APPROVAL
Human selects/approves individual video/image/audio candidates.

### CUSTOM
Per-stage rules.

## Approval decision types

- APPROVE;
- APPROVE_WITH_NOTES;
- REQUEST_REVISION;
- REGENERATE;
- REJECT;
- LOCK;
- UNLOCK_REQUEST;
- DEFER;
- ESCALATE.

## Approval record

Store:
- Approval ID;
- target entity/asset ID;
- version/hash;
- stage;
- decision;
- actor/role;
- notes;
- timestamp;
- conditions;
- superseded approval ID where relevant.

## AI approval eligibility

AI may only auto-approve when:
- stage is configured as AI-approvable;
- all hard QA gates pass;
- rights/provenance required for that stage are sufficient;
- no locked operator choice is being changed;
- budget/spend is already authorized;
- output is not being publicly published unless policy explicitly allows it.

## Character approval

Creating a recurring canonical character should normally require explicit lock approval before production reuse.

After lock:
- AI may create scene expressions/poses within locked constraints;
- identity/look mutation beyond allowed variation creates a new CharacterVersion/Look proposal;
- AI cannot silently rewrite locked canonical identity.

## Content approval

Once script/lyrics/content version is approved:
- downstream systems reference that exact ContentVersion;
- material text change creates new version;
- minor pronunciation metadata can be updated separately if it does not change content meaning.

## Storyboard approval

Approval may occur at:
- whole storyboard;
- scene subset;
- keyframe subset.

Approved Shots can still produce multiple Takes. A change to the planned narrative purpose/camera/action beyond tolerance creates a Shot revision.

## Take comparison

Review UI should eventually support side-by-side candidate comparison with:
- provider/model;
- attempt cost;
- QA scores;
- continuity diagnosis;
- reference frame;
- prompt/version;
- generation time;
- rights/watermark state.

The cheapest or newest take is not automatically preferred.

## Revision requests

A revision should specify scope:
- text/content;
- voice;
- music;
- keyframe;
- one Shot;
- one Scene;
- visual style;
- whole stage only when necessary.

System should invalidate/regenerate only dependent downstream work.

## Approval invalidation

Approval may become stale if its dependencies materially change.

Examples:
- approved storyboard becomes stale after new audio duration;
- approved take requires adjacent continuity recheck after neighboring shot replacement;
- publishing approval becomes stale if final master changes;
- rights approval becomes stale if source/provider/tier changes.

Invalidation must be explicit and logged.

## Human override

Human may approve a secondary aesthetic QA failure when no hard safety/rights/integrity gate is violated, if project policy permits.

Human may not make an unresolved rights/safety block disappear without actually resolving/changing the underlying requirement.

## Public publishing

Default:
`Final Master Approved -> Upload Private -> Verify -> Publication Approval -> Schedule/Public`

Until policy explicitly changes, public publishing remains a human gate.

## Notifications

Future app may notify for:
- approval requested;
- budget approval required;
- locked identity change proposed;
- unresolved rights;
- final master ready;
- publish approval;
- repeated provider failure requiring decision.

## Auditability

Every approval/rejection/regeneration decision should be traceable. Do not encode critical approval state only in chat messages.

## Acceptance criteria

Review system is development-ready when each production stage can determine whether it may proceed automatically, must wait for approval, how approval attaches to a version, and what downstream state becomes invalid when an approved dependency changes.