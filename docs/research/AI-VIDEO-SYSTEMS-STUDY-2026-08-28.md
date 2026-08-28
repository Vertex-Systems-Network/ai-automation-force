# AI Video Systems Study — 2026-08-28

## Purpose

Record architecture lessons from current production/orchestration systems. This is not a feature-copy list. The goal is to identify proven patterns and translate them into a provider-neutral architecture.

## LTX Studio

Official product material emphasizes:
- reusable AI Characters, Objects, Locations and other Elements;
- consistency across scenes;
- keyframes and references;
- camera control;
- dynamic storyboard;
- timeline editor;
- sound design.

Source: https://website.ltx.studio/

Lesson for this project:
Treat Characters, Locations, Props and Styles as canonical reusable entities. Storyboard and timeline are first-class objects, not temporary prompts.

## Runway

Gen-4 References supports saved references for persistent reuse and up to multiple references per generation, with guidance around consistent characters/scenes. Runway also exposes reference media concepts across images/video/audio.

Sources:
- https://help.runwayml.com/hc/en-us/articles/40042718905875-Creating-with-Gen-4-Image-References
- https://help.runwayml.com/hc/en-us/articles/52963720640275-Using-reference-media-to-guide-your-generations

Lesson:
Canonical references must be named, versioned and reusable. Provider-specific saved references should map back to provider-independent entity IDs.

## Adobe Firefly Boards

Firefly Boards supports moodboards/storyboards, generated images/videos, style references and composition references. Adobe also highlights Content Credentials/provenance concepts.

Sources:
- https://helpx.adobe.com/firefly/web/create-mood-boards/firefly-boards/about-firefly-boards.html
- https://www.adobe.com/learn/firefly/web/create-commercial-storyboard-firefly-boards
- https://helpx.adobe.com/firefly/web/work-with-audio-and-video/work-with-video/use-video-as-composition-reference.html

Lesson:
Separate style reference from composition reference, keep storyboard collaboration/editability, and store provenance rather than treating generated media as context-free files.

## HeyGen

Current HeyGen products emphasize persistent avatars, scene-level script/voice control, long-form identity consistency and multi-angle/avatar looks. This is particularly relevant for presenter/dialogue formats.

Sources:
- https://www.heygen.com/avatars/avatar-v
- https://help.heygen.com/en/articles/11049655-overview-our-new-ai-studio
- https://help.heygen.com/en/articles/11049837-create-your-first-video-in-our-studio

Lesson:
For human-presenter projects, trained/persistent avatar providers can be a specialized adapter. The core system still stores identity/consent/versioning independently.

## Temporal

Temporal describes durable execution that resumes workflows after crashes, network failures or infrastructure outages, including long-running AI-agent workflows.

Source: https://docs.temporal.io/

Lesson:
This project's multi-stage renders, provider waits, quota resets, retries and manual handoffs are durable workflows. Do not depend solely on in-process background tasks for production orchestration.

## FastAPI

FastAPI documents in-process BackgroundTasks for small jobs but explicitly notes that heavier computation/multi-process work benefits from larger queue/orchestration systems.

Source: https://fastapi.tiangolo.com/tutorial/background-tasks/

Lesson:
FastAPI should be the API/control surface, not the durable media-job execution engine.

## FFmpeg

FFmpeg supports concat mechanisms and complex filtergraphs for deterministic audio/video processing.

Sources:
- https://ffmpeg.org/faq.html
- https://ffmpeg.org/ffmpeg.html

Lesson:
Use generative AI for creative assets; use deterministic media tooling for timeline assembly, overlays, audio mixing, subtitles and deliverable encodes.

## GitHub Actions

Scheduled workflows run from the default branch using cron/timezone configuration. Standard runners are free for public repositories; private repositories use the account/organization included minute quota. GitHub Free organizations currently include 2,000 hosted-runner minutes/month; self-hosted runners are free from GitHub Actions billing.

Sources:
- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- https://docs.github.com/en/actions/concepts/billing-and-usage
- https://docs.github.com/en/billing/concepts/product-billing/github-actions

Lesson:
A short daily provider-research job is practical, but the repository is private so hosted minutes are quota-backed rather than unlimited. Keep the scout lightweight or use a self-hosted runner if continuous free execution is required.

## GitHub PR safety

GitHub protected branches/rulesets can require checks/reviews before merge. Auto-merge merges after configured requirements pass.

Sources:
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches
- https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/automatically-merging-a-pull-request

Lesson:
Daily research may auto-merge low-risk registry/research/docs updates after validation. Architecture/code/schema/security changes should not be blindly self-merged by the discovering agent.

## Search/research adapters

Current official pricing pages show API-search free capacity that can support a daily scout, subject to provider terms and future changes:
- Tavily: 1,000 free API credits/month.
- Brave Search API: monthly free credits.
- Gemini API supports Google Search grounding and URL context on supported models; pricing/free quotas vary by model/tier and must be refreshed.

Sources:
- https://www.tavily.com/pricing
- https://brave.com/search/api/
- https://ai.google.dev/gemini-api/docs/google-search
- https://ai.google.dev/gemini-api/docs/url-context
- https://ai.google.dev/gemini-api/docs/pricing

Lesson:
The scout must have pluggable discovery/search adapters. It cannot assume one free search service exists forever.

## Architecture conclusions

Adopt these patterns:
1. Entity Library: Character, Location, Prop, Style, Voice.
2. Hierarchical project structure: Project -> Act -> Sequence -> Scene -> Shot -> Take.
3. Editable storyboard and timeline as canonical state.
4. Reference/keyframe-based continuity.
5. Provider-neutral intent translated by adapters.
6. Durable workflow engine for long-running/resumable jobs.
7. Deterministic final media assembly.
8. Provenance, rights, cost and QA attached to every asset/take.
9. Daily capability research with controlled PR-based updates.
10. Human/policy gates around risky automatic changes and public publication.

## Rejected architectural shortcut

Do not implement a system whose primary data model is:
`prompt -> provider -> output file`.

That model cannot reliably support character continuity, three-hour productions, provider switching, memory, cost optimization, revisions, licensing or future mobile/API clients.