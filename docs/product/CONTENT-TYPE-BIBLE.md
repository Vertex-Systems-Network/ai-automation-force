# Content Type Bible

## Purpose

Define how each registered media/content format behaves before implementation. A content format determines required planning structures, audio expectations, timeline behavior, QA focus and downstream generation requirements. Visual style is separate from content format.

## Universal fields

Every project/content item has:
- content format;
- working/final title;
- audience/policy profile;
- language;
- target duration;
- objective;
- premise/logline;
- structure map;
- character/world references where used;
- audio intent;
- visual intent;
- continuity level;
- originality record;
- QA state;
- rights/provenance state.

## Song

Required:
- song concept;
- lyrics;
- structure: intro/verse/pre-chorus/chorus/bridge/outro as applicable;
- hook/refrain;
- duration target;
- singer/voice direction;
- music direction;
- lyric timing or section timing;
- pronunciation notes where required.

Optional:
- call-and-response;
- educational objective;
- dance/action cues;
- instrumental sections;
- music-video narrative.

Primary QA:
- originality/lyric similarity;
- meter/repetition quality;
- intelligibility;
- age/audience fit;
- lyric/audio fidelity;
- melody/arrangement rights risk.

## Lullaby

Modes:
- sung lullaby;
- spoken lullaby;
- instrumental-supported narration.

Characteristics:
- low intensity;
- gentle pacing;
- low abruptness;
- predictable repetitions;
- safe calm imagery;
- softer visual motion when video exists.

For infant-oriented content, design primarily for parent-controlled listening rather than direct infant screen engagement.

## Poem

Modes:
- spoken poem;
- rhythmic poem;
- illustrated poem;
- cinematic poem;
- musicalized poem.

Required:
- poem text;
- stanza/section structure;
- delivery style;
- rhythm/pause markers where materially important.

Primary QA:
- language quality;
- cadence;
- originality;
- pronunciation;
- narrative/imagery coherence.

## Rhyme

Designed around compact repetition and participation.

Optional modes:
- chant;
- sung rhyme;
- movement/action rhyme;
- educational rhyme.

Require explicit repetition map to avoid accidental excessive looping or near-copying existing nursery material.

## Story

Required:
- premise;
- protagonist/POV;
- setup;
- conflict/problem/question;
- progression;
- resolution;
- scene/beat map;
- narration/dialogue model.

Options:
- narrated;
- dialogue-led;
- mixed;
- illustrated/storybook;
- animated;
- cinematic.

## Bedtime Story

Story subtype with:
- low-to-moderate emotional intensity;
- no abrupt unresolved threat near ending;
- slower pacing;
- calm closing sequence;
- narration-first audio design by default.

## Guided Imagination

Purpose:
- calm visualization;
- gentle exploration;
- educational visualization;
- relaxation.

Requires careful audience language and must not present therapeutic/medical claims unless separately validated under appropriate policy.

## Educational Video

Required:
- learning objective;
- prerequisite assumptions;
- factual claims;
- source/verification requirements;
- knowledge checks/examples where appropriate;
- age/knowledge-level adaptation.

Primary QA adds factual verification and misleading-education checks.

## Explainer

Audience may be general/adult/business/education.

Required:
- question/problem;
- key points;
- examples;
- conclusion/action summary;
- factual verification when claims are external/verifiable.

## Music Video

Audio master is typically timeline source.

Modes:
- performance;
- narrative;
- abstract/visualizer;
- hybrid.

Requires:
- section/beat timeline;
- visual motif map;
- performance character locks if recurring singer/avatar appears;
- beat-aware cuts where configured.

## Dialogue Scene

Required:
- characters;
- voice assignment;
- dialogue text;
- speaker turns;
- emotional intent;
- blocking;
- coverage plan;
- lip-sync requirement;
- reaction shots where useful.

Primary risks:
- voice mismatch;
- lip-sync drift;
- eyeline/screen-direction errors;
- identity inconsistency.

## Cinematic Sequence

Designed as a sequence rather than a full standalone narrative.

Requires:
- sequence objective;
- cinematic beat map;
- shot coverage;
- camera grammar;
- continuity state;
- sound design intent.

Useful for opening sequences, montage, action/event sequence, transitions or showcase scenes.

## Short Film

Recommended hierarchy:
`Project -> Act(s) -> Sequence -> Scene -> Shot -> Take`

Required:
- logline;
- characters;
- beginning/middle/end or justified alternative structure;
- script;
- scene breakdown;
- audio plan;
- editorial plan.

## Episode / Series Episode

Adds:
- series ID;
- season/episode number where relevant;
- recurring character/world version pins;
- continuity with prior episodes;
- episode-specific premise;
- unresolved/continuing arc metadata where appropriate.

Series memory must distinguish reusable canon from episode-local state.

## Movie

Target range may include long-form projects up to configured 3-hour maximum.

Requires:
- logline;
- synopsis;
- act/chapter architecture;
- sequences;
- scenes;
- character arcs;
- world/location continuity;
- screenplay/script;
- audio/dialogue/music plan;
- editorial rhythm plan;
- long-form context summaries/checkpoints;
- incremental render strategy;
- recovery strategy.

A movie is not generated as one model call.

## Documentary

Modes:
- narrated factual documentary;
- essay documentary;
- educational documentary;
- interview-led where legitimate source material exists;
- hybrid.

Requires:
- claims/sources;
- factual evidence;
- archival/source rights;
- quote/interview provenance;
- distinction between generated illustrative visuals and factual footage.

Do not fabricate documentary evidence.

## Compilation

Combines existing canonical segments/items.

Requires:
- source item IDs;
- rights compatibility;
- normalized audio/video specs;
- transition/intro/outro plan;
- duplicate-content/platform-quality review.

## Trailer / Teaser

Derived from or linked to a source project when possible.

Requires:
- source project/content;
- duration;
- selected beats;
- spoiler policy;
- title/card/CTA rules;
- music/audio treatment.

Must not invent finished-project scenes that materially misrepresent the underlying content unless explicitly created as conceptual/promotional material.

## Short / Social Video

Typical characteristics:
- vertical-first optional;
- shorter hook window;
- caption-safe framing;
- platform derivative of a larger project or standalone.

Do not let social optimization override audience safety or originality rules.

## Custom

Custom formats require:
- unique format name;
- definition;
- required structural fields;
- audio behavior;
- visual/timeline behavior;
- QA requirements;
- publishing implications;
- whether it may be reused as a registered preset later.

## Format vs treatment

Never encode treatment as format.

Example:
- Format: `movie`
- Genre: `fantasy adventure`
- Treatment: `cinematic`
- Visual style: `stylized 3D`

This allows the same format to support multiple styles and providers without schema churn.

## AI format selection

When `AI Decide` is enabled, selection should consider:
- user intent;
- audience;
- target duration;
- portfolio/memory state;
- available characters/worlds;
- production feasibility;
- budget/provider constraints;
- platform/output goal.

The AI stores the resolved concrete format and the rationale.

## Acceptance criteria

A format is development-ready when its required fields, optional fields, default audio route, timeline structure, key QA gates and long-form implications are defined without relying on provider-specific hidden behavior.
