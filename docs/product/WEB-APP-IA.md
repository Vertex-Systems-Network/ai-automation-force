# Web Application Information Architecture

## Purpose

Define the future web application's navigation, screens, responsibilities and major interaction states before frontend implementation.

The web app is a control/review/editor surface over the same provider-neutral backend contracts; provider secrets never live in the browser.

## Primary navigation

Recommended top-level areas:
- Dashboard
- Projects
- Characters
- Worlds & Locations
- Props & Styles
- Assets
- Production Queue
- Providers & Costs
- Publishing
- Analytics
- Admin / Settings

Project-level secondary navigation:
- Overview
- Brief / Content
- Cast / Characters
- Audio
- Storyboard
- Timeline
- Scenes
- Shots / Takes
- Assets
- QA / Review
- Costs
- Publishing
- History

## Dashboard

Show:
- active projects;
- blocked jobs;
- awaiting approvals;
- current generation queue;
- provider health/quota summary;
- recent final masters;
- publication status;
- budget alerts;
- recent failures;
- recommended next action.

Dashboard must not require loading large media/timelines to be useful.

## Projects list

Capabilities:
- search;
- filter by status, audience, format, language, duration, character, owner/workspace later;
- sort by updated/status/priority;
- create new project;
- duplicate as new project/template without duplicating canonical IDs;
- archive;
- resume blocked/incomplete project.

Project cards/table should surface:
- title;
- format;
- duration;
- stage;
- progress;
- active characters;
- next block/action;
- cost to date;
- last updated.

## New Project Wizard

Implements `NEW-PROJECT-WIZARD.md` with:
- Quick;
- Guided;
- Advanced modes;
- preflight summary;
- AI Decide decisions and explanations;
- save draft;
- no provider spend merely by creating project.

## Project Overview

Summary panels:
- creative brief;
- audience/cast;
- format/duration;
- characters/worlds;
- current stage;
- timeline progress;
- cost/budget;
- QA/rights state;
- publication state;
- activity/history.

Primary action should be context-aware: `Continue Production`, `Review Audio`, `Approve Storyboard`, `Fix Shot`, etc.

## Content / Script Editor

Features:
- structured script/lyrics/story document;
- version history;
- AI suggestion vs approved text distinction;
- section/scene markers;
- pronunciation notes;
- source/research references where appropriate;
- originality/QA panel;
- approve/request revision.

Do not hide canonical version changes inside autosave without version semantics.

## Character Library

Views:
- card/list;
- search/filter by type, age, gender/species, reusable, rights, tags;
- character detail;
- versions;
- looks;
- reference pack;
- voice association;
- project usages;
- lock state;
- create new;
- propose new version/look.

Locked identity indicators must be visually obvious.

## Worlds / Locations / Props / Styles

Reusable library behavior similar to characters:
- list/search;
- canonical version/details;
- reference media;
- project usage;
- rights;
- versioning;
- create/select.

## Audio Workspace

Areas:
- script/lyrics timing;
- voice assignments;
- music direction;
- waveform/player;
- stems;
- dialogue lines;
- ambience/SFX list;
- candidate renders;
- QA results;
- cost/provider details;
- mix controls for safe deterministic parameters;
- approve/regenerate affected segment.

Future UI should avoid pretending to be a full DAW initially; focus on production decisions and deterministic mix controls.

## Storyboard

Card/grid view by Scene/Shot showing:
- keyframe/reference;
- shot purpose;
- duration;
- characters/location;
- camera/action;
- status;
- risk;
- provider requirement;
- QA state.

Actions:
- reorder within allowed hierarchy;
- edit shot plan;
- create/split/merge shot plan;
- approve scene/storyboard;
- generate keyframes after authorized scope.

## Timeline Editor

Desktop-oriented editing surface.

Tracks may include:
- primary video;
- B-roll/overlays;
- narration;
- dialogue;
- lead vocal;
- music;
- ambience;
- SFX;
- captions;
- graphics;
- beat/marker lanes.

Initial editor should support production-level operations needed by the platform, not attempt to clone every feature of Premiere/Resolve.

Key capabilities:
- zoom/scroll;
- virtualized long timelines;
- clip/shot selection;
- trim handles;
- markers;
- transition intent;
- audio alignment;
- locked regions;
- proxy playback;
- jump to Scene/Shot;
- non-destructive changes;
- OTIO mapping.

## Scene View

Scene-focused production page:
- script excerpt;
- scene state;
- characters/location/props;
- audio;
- shot list;
- selected takes;
- continuity panel;
- scene preview;
- QA;
- cost;
- approval.

Useful for long-form production without loading entire movie timeline.

## Shot / Take Inspector

Show:
- canonical Shot plan;
- first/end keyframes;
- references;
- all Takes;
- side-by-side compare;
- provider/model;
- prompt version;
- cost/credits;
- QA/continuity scores;
- failure reasons;
- select canonical Take;
- regenerate with constrained change;
- revise Shot plan.

## Production Queue

Show durable jobs:
- queued;
- running;
- waiting provider;
- waiting quota;
- waiting approval;
- manual handoff;
- failed/retryable;
- completed.

Actions:
- inspect;
- cancel where safe;
- retry;
- choose fallback when operator intervention required;
- import manual-free output;
- view lineage/log summary.

## Providers & Costs

Provider dashboard:
- enabled/evaluation providers;
- current model capabilities;
- free quota if known;
- paid price metadata;
- health/circuit state;
- success/rejection rate;
- spend by provider/project;
- current budget caps;
- manual-free routes;
- evidence freshness.

Secrets configured server-side only.

## QA / Review

Unified review queue:
- stage approvals;
- rights blocks;
- character lock changes;
- failed continuity;
- candidate Take comparison;
- final master review;
- publication approval.

Filters by project/stage/severity.

## Publishing

Show:
- final master;
- thumbnail;
- title/description;
- captions;
- audience/disclosure state;
- rights clearance;
- private upload status;
- verification;
- schedule/public approval;
- publication history.

## Analytics

Views:
- project/publication performance;
- content cohorts;
- retention;
- character/series performance;
- language variants;
- hypotheses/experiments;
- provider accepted-output economics.

Avoid presenting correlation as causal fact without context.

## Admin / Settings

Covers:
- general defaults;
- provider credentials/status;
- budgets;
- storage;
- language/voice defaults;
- policy presets;
- publication accounts;
- runner/worker status;
- templates;
- feature flags/evaluation providers;
- audit logs later.

## Global interaction states

Every screen should design for:
- loading;
- empty;
- error;
- blocked;
- offline/network loss;
- retry;
- long-running progress;
- cancellation;
- approval waiting;
- stale/version-conflict;
- permission denied later;
- destructive confirmation.

## Long-form UI scaling

For 3-hour projects use:
- pagination;
- scene/sequence scoped views;
- virtualized lists/timeline;
- proxies/thumbnails;
- incremental data loading;
- search/jump by ID/scene/character;
- background job progress.

Do not load thousands of shots/full-resolution assets into browser memory at once.

## Accessibility

Plan for:
- keyboard navigation;
- focus management;
- semantic controls;
- accessible labels;
- contrast;
- non-color-only status indicators;
- captioned preview where appropriate;
- reduced-motion consideration for UI animations.

## Responsive strategy

Desktop is primary for timeline/storyboard production.

Tablet/mobile web may support monitoring/review/approval, while future native mobile app focuses on status and approval rather than full professional timeline editing.

## Acceptance criteria

Web IA is development-ready when every major backend domain/workflow has a defined user surface, state/error/review behavior, and the UI does not require provider-specific business logic or expose provider secrets.