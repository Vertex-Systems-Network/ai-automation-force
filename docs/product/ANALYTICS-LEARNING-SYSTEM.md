# Analytics & Learning System Specification

## Purpose

Define how published performance data becomes structured learning for future planning without causing repetitive, manipulative or low-quality content cloning.

## Core principle

Analytics produces hypotheses and portfolio signals, not direct copy instructions.

## Canonical analytics dimensions

Link performance back to project attributes such as:
- project/content format;
- audience profile;
- duration;
- language/locale;
- character IDs;
- series/world;
- topic/theme;
- hook/opening type;
- narrative structure;
- music/audio style;
- voice profile;
- visual style;
- pacing profile;
- average shot length;
- provider mix;
- thumbnail style;
- title pattern;
- publication time/platform.

## Metrics

Platform-dependent metrics may include:
- impressions;
- CTR;
- views;
- unique/repeat viewers where available;
- average view duration;
- average percentage viewed;
- retention curve;
- early drop-off;
- completion rate;
- traffic sources;
- geography/language;
- engagement signals where available;
- subscriber/follow conversion where available;
- playlist/series progression;
- revenue/cost efficiency where applicable.

Do not assume all metrics are available for every platform/audience type.

## Cohorts

Compare like with like:
- same audience band;
- same content format;
- similar duration;
- same language/market;
- same publication period;
- same series/character when useful.

Avoid comparing a 30-second short directly with a 90-minute movie as if raw retention percentages mean the same thing.

## Hypothesis record

A learning hypothesis should include:
- hypothesis ID;
- observation window;
- supporting projects/items;
- audience/format cohort;
- measured effect;
- confidence;
- alternative explanations;
- proposed future test;
- originality/fatigue guard;
- status: proposed / testing / supported / rejected / inconclusive.

Example:
`Preschool animal call-and-response songs between 90–120 seconds show stronger first-30-second retention than comparable non-interactive songs.`

This does not authorize reusing the same melody, lyrics, plot or visual sequence.

## Portfolio feedback

Analytics may influence:
- format mix;
- duration ranges;
- character reuse frequency;
- pacing profiles;
- opening-hook design;
- series continuation;
- localization priority;
- thumbnail experimentation;
- production-budget allocation.

It should also include fatigue penalties so a winning pattern is not overproduced.

## Experiment system

Future controlled experiments may vary one or a small number of dimensions:
- thumbnail;
- title;
- opening structure;
- duration;
- visual pacing;
- music treatment;
- format variant.

Store experiment intent before observing outcome to reduce post-hoc story-telling.

## Quality constraints

Analytics must not override:
- child safety;
- rights/provenance;
- originality;
- truthful metadata;
- platform-quality requirements;
- locked identity/canon.

High CTR from misleading packaging is not considered a valid positive learning if it causes policy/quality harm.

## Cost/performance learning

Connect generation history to accepted-output economics:
- provider/model cost;
- free credits;
- retries;
- failure reason;
- accepted quality;
- manual effort;
- render duration.

This helps Provider Router learn actual project-specific success rates.

## Character/series learning

Track:
- character appearance frequency;
- audience response by character/series;
- novelty vs recurrence;
- episode progression;
- fatigue/saturation.

Do not automatically remove a character because of one low-performing item; use sufficient cohort evidence.

## Language learning

Localized variants are tracked separately and as related lineage so decisions can distinguish:
- content concept performance;
- translation quality;
- voice/dub quality;
- market/platform differences.

## Data freshness and attribution

Store:
- metric collection date;
- platform/source;
- project/publication ID;
- aggregation window;
- known data limitations.

Late/updating metrics should not silently rewrite prior analysis without versioning/snapshotting important decisions.

## Privacy

Do not build user-level profiling from data not legitimately available or necessary. Prefer aggregate platform analytics for content strategy.

## Acceptance criteria

Analytics learning is development-ready when platform metrics can be attributed to canonical project features, converted to versioned hypotheses, and fed into Portfolio/Provider routing without bypassing originality, fatigue, safety or rights gates.