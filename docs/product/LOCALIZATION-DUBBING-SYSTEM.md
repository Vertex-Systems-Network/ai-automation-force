# Localization & Dubbing System Specification

## Purpose

Define how canonical content, voices, songs, captions, visuals and metadata are adapted into additional languages while preserving meaning, timing, character identity, rights and lineage.

## Core rule

Localization is adaptation, not blind translation.

Each localized version is a derived canonical variant linked to a specific source ContentVersion/Project version.

## Language variant record

Store where applicable:
- source project/content version;
- target language;
- locale/region;
- translation/adaptation version;
- localized title;
- localized script/lyrics;
- pronunciation dictionary;
- voice assignments;
- subtitle/caption asset;
- dubbed audio assets;
- localized metadata;
- QA state;
- cultural review state;
- rights/provenance;
- timing strategy.

## Text localization modes

### Direct semantic adaptation
For narration/explainers where timing is flexible.

### Timing-constrained dubbing
Preserve scene/dialogue timing within configured tolerance.

### Lip-sync-constrained dubbing
Adjust wording/timing to fit visible mouth movement where needed.

### Song adaptation
Preserve:
- meaning/theme;
- meter;
- rhyme where practical;
- hook/refrain function;
- singability;
- section timing;
- audience naturalness.

Literal translation is not acceptable when it creates unnatural or unsingable lyrics.

## Voice strategy

Options:
- same canonical synthetic VoiceProfile with localized provider voice equivalent;
- language-specific VoiceProfile;
- original authorized voice clone where permitted;
- narrator re-casting;
- manual/imported dub.

Recurring character voice identity should remain perceptually consistent where possible, but exact provider voice IDs are not canonical identity.

## Pronunciation

Maintain per-language dictionary for:
- character names;
- invented words;
- locations;
- brands;
- technical terms;
- acronyms;
- culturally specific terms.

## Subtitle/caption system

Support:
- source transcript;
- translated subtitle;
- closed captions including SFX when needed;
- burn-in derivative only when requested;
- separate timed subtitle files as canonical text assets.

Caption timing should derive from approved localized audio, not only original-language timing when speech duration changes.

## Visual localization

Usually preserve video, but support localized variants for:
- on-screen deterministic text;
- titles/cards;
- UI/signage when editable and relevant;
- educational labels;
- culturally inappropriate/ambiguous imagery;
- region-specific legal/disclosure cards.

Avoid asking video AI to regenerate whole scenes merely to replace text when deterministic graphics can do it.

## RTL and typography

Future UI/render system should support RTL languages where applicable:
- correct text direction;
- punctuation;
- alignment;
- font coverage;
- subtitle positioning;
- title-card layout.

## Cultural adaptation

Review:
- idioms;
- humor;
- examples;
- gestures;
- holidays;
- food/clothing/context;
- age appropriateness;
- sensitive historical/religious/cultural references where relevant.

Do not erase source meaning unnecessarily, but do not assume literal equivalence across markets.

## QA

Localized variant reruns:
- semantic fidelity;
- naturalness;
- grammar;
- audience fit;
- cultural fit;
- pronunciation;
- subtitle timing;
- voice identity;
- lip sync where required;
- lyric meter/rhyme/singability;
- safety/factual checks;
- rights/provenance;
- metadata completeness.

## Source updates

If source ContentVersion changes after localization:
- mark affected variants potentially stale;
- compute/identify changed segments;
- re-localize only affected regions where possible;
- preserve previous localized versions/history.

## Analytics

Track localized variants separately while linking to source concept so analytics can compare language/market performance without mixing raw metrics blindly.

## Acceptance criteria

Localization is development-ready when a source project can create a language variant with explicit text/audio/subtitle/metadata lineage, timing strategy and QA without overwriting the original or depending on provider chat history.