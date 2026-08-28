# Project Presets & Admin Settings Specification

## Purpose

Define reusable project templates and the administrative/default settings that control platform behavior without hard-coding creative/provider choices into application code.

## Project preset principles

A preset is a starting configuration, not a locked project.

Presets may define:
- audience;
- content format;
- duration/range;
- cast defaults;
- character strategy;
- visual profile;
- audio profile;
- pacing;
- output/aspect/FPS;
- review policy;
- provider/cost policy;
- publishing defaults;
- required wizard steps.

Creating from a preset resolves a normal Project record; later edits do not silently change the preset itself.

## Initial recommended presets

### 2-Minute Kids Song
- Audience: Preschool/Child configurable;
- Format: Song;
- Duration: 90–150 sec default target 120;
- Character strategy: existing locked or create+lock;
- Visual: stylized 3D/2D configurable;
- Audio: full song, AI Music Director;
- Pacing: music-synced;
- Output: 16:9 1080p + optional vertical derivative;
- Review: content/audio/storyboard/final master;
- Provider: HYBRID_SMART.

### Bedtime Story
- Audience: child-directed selected band;
- Format: Bedtime Story;
- Duration: 3–10 min default;
- Audio: gentle narration + optional music bed;
- Visual: gentle storybook/animation;
- Pacing: very gentle/gentle;
- strict low-intensity child policy;
- review: content/audio/final.

### Educational Explainer
- Audience: child/general configurable;
- Format: Educational Video/Explainer;
- factual verification required;
- narration-first;
- deterministic labels/graphics preferred;
- citations/research where claims are external.

### Music Video
- Format: Music Video;
- audio master required before final shot timing;
- beat/section grid;
- performance/narrative/abstract mode;
- strong keyframe/storyboard flow.

### Cinematic Short Film
- Format: Short Film;
- Duration: 3–15 min;
- Act/sequence/scene structure;
- cinematic camera/coverage;
- dialogue/score optional;
- strict character/world continuity.

### Series Episode
- Format: Series Episode;
- reusable series/character/world canon required;
- duration configurable;
- prior episode continuity memory;
- episode-local state.

### 90-Minute Movie
- Format: Movie;
- Duration: 5400 sec default;
- long-form hierarchical planning;
- Act/Sequence/Scene checkpoints;
- scene-based generation/review;
- incremental rendering;
- project-level budget forecast required before provider spend.

### Documentary
- Format: Documentary;
- factual/source verification;
- archival/imported asset rights;
- generated illustration disclosure distinction;
- narration/interview modes.

### Social Short
- Format: Short/Social;
- vertical-first optional;
- hook/caption safe zones;
- may derive from canonical long-form asset;
- no safety/originality shortcuts.

## Preset lifecycle

States:
- DRAFT;
- ACTIVE;
- DEPRECATED;
- ARCHIVED.

Presets are versioned. Existing projects retain the preset version they were created from for audit but are independent thereafter.

## User/custom presets

Future users/workspaces may save a Project configuration as a reusable preset, excluding:
- provider secrets;
- one-off generated assets unless explicitly referenced;
- publication tokens;
- private consent documents.

## Admin settings groups

### General
- platform name/logo later;
- default timezone;
- default language;
- default project autonomy level;
- default output profile;
- default storage retention.

### Audience / Policy
- enabled policy profiles;
- default kids/general policies;
- hard safety gates;
- public publishing default;
- required review checkpoints.

Machine-read policy changes that affect runtime behavior require development/change governance and must not be casually edited as documentation.

### AI / Providers
For each provider:
- enabled/disabled/evaluation;
- allowed capabilities;
- preferred model(s);
- blocked model(s);
- credentials configured status;
- endpoint/region where applicable;
- quota metadata;
- privacy restrictions;
- provider-specific concurrency limits;
- manual-free eligibility.

Secrets are stored server-side/secret manager, never shown in full or committed to Git.

### Cost / Budget
- currency;
- default execution mode;
- per-attempt cap;
- per-shot cap;
- per-project cap;
- daily/monthly cap;
- provider-specific cap;
- approval thresholds;
- free-credit preferences;
- cost alert thresholds.

### Audio Defaults
- narrator voice profile;
- singer preference;
- language/accent defaults;
- output sample/container settings;
- loudness target;
- music-bed defaults;
- SFX/ambience defaults.

### Visual Defaults
- style profile;
- aspect ratio;
- resolution;
- FPS;
- camera/pacing defaults;
- caption-safe margins;
- strict continuity default;
- reference strategy.

### Character Defaults
- recurring character lock behavior;
- new-character review requirement;
- reference-pack minimums;
- voice association policy;
- versioning behavior.

### Storage
- local/S3-compatible backend;
- bucket/container;
- region;
- signed URL expiration;
- temp retention;
- rejected asset retention;
- proxy policy;
- archive policy.

### Workers / Runtime
- worker pools/classes;
- concurrency limits;
- FFmpeg worker limit;
- provider task limit;
- long-form scene parallelism;
- retry defaults;
- circuit-breaker thresholds.

Exact runtime values belong to implementation/operations, but UI should expose safely configurable settings later.

### Publishing Accounts
- connected platforms;
- channel/account identity;
- default privacy;
- default language/category;
- publication approval requirement;
- playlist mappings;
- credential status.

### Localization
- enabled languages;
- default locales;
- preferred voices per language;
- subtitle defaults;
- translation review requirement;
- RTL support settings.

### Notifications
Future configurable events:
- approval requested;
- final master ready;
- budget threshold;
- provider outage/quota exhaustion;
- rights block;
- publication success/failure;
- daily/weekly production summary.

### Provider Scout
- enabled/disabled;
- research model;
- schedule;
- official source list;
- safe auto-merge classes;
- review policy.

Changing executable scout settings still follows development/change governance.

## Settings precedence

Recommended precedence:
1. hard system/safety/security constraints;
2. project explicit locks;
3. project-specific settings;
4. selected preset;
5. workspace/user defaults later;
6. global defaults.

AI-generated recommendations never override a higher-precedence locked setting silently.

## Settings audit

Material changes should record:
- setting;
- old/new value;
- actor;
- timestamp;
- reason where important;
- affected future jobs/projects.

Existing approved outputs should not be silently reinterpreted under new defaults.

## Acceptance criteria

Presets/admin planning is development-ready when project creation can start from reusable versioned configurations, and every operational default has a clear precedence, secret-handling rule, audit behavior and separation between safe user configuration and hard policy/security constraints.