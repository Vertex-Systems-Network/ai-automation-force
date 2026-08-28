# Publishing System Specification

## Purpose

Define the publication pipeline from approved final master to platform-ready upload, verification, scheduling, publication and post-publish recordkeeping.

Initial platform: YouTube. Architecture remains adapter-based for future platforms.

## Core principle

Publishing is a separate stage from rendering. A final master is not automatically public.

Default flow:
`Final Master Approved -> Publish Package -> Upload Private -> Verify -> Publication Approval -> Schedule/Public -> Record Publication`

## Publish package

Contains:
- final video/audio master Asset ID;
- title;
- description;
- language/locale;
- thumbnail;
- captions/subtitles;
- playlist/category where relevant;
- audience/Made-for-Kids decision;
- synthetic-media/disclosure review;
- rights/provenance clearance;
- monetization/usage notes where applicable;
- scheduled time or privacy state;
- source project/version;
- publication policy/approval records.

## Metadata generation

AI Publishing Agent may propose:
- titles;
- descriptions;
- chapters/timestamps;
- tags/keywords where platform supports/benefits;
- playlist placement;
- thumbnail brief;
- localized metadata.

Metadata must remain truthful to actual content and must not use misleading claims/clickbait that materially misrepresents the media.

## Thumbnail workflow

Options:
- generated dedicated thumbnail;
- approved frame + deterministic text/graphics;
- character/world composition;
- manual/imported thumbnail.

Thumbnail goes through:
- identity/style QA;
- readability;
- unwanted text/logo checks;
- audience/platform policy;
- rights/provenance.

## Captions

Prefer captions from approved transcript/audio timing.

Support:
- source language captions;
- localized subtitles;
- accessibility captions including sound cues where relevant;
- platform upload as separate caption track;
- optional burned-in derivative only when requested.

## Audience classification

Project policy and final-content review determine audience flags. Child-directed projects require applicable platform review rather than relying only on channel defaults.

## Synthetic-media/disclosure review

Publishing stage should inspect current platform requirements and project content to determine whether disclosure/status fields are required.

Rules are mutable external facts and should be re-verified at implementation/publication time.

## Rights preflight

Before upload/publish:
- final master RightsRecord cleared for intended use;
- upstream source restrictions compatible;
- attribution ready;
- watermark restrictions resolved;
- real-person/voice consent resolved;
- platform-specific license restrictions reviewed.

Failure -> `BLOCKED_LICENSE` / review.

## Upload

Use resumable/chunked protocol where platform supports it.

Store:
- publication job ID;
- platform;
- platform asset/video ID;
- upload session/resume reference where safe;
- bytes/progress;
- result/status;
- checksum/verification;
- metadata version;
- upload timestamp.

Worker crash must reconcile existing upload/session before starting another duplicate upload.

## Privacy states

Normalized states:
- DRAFT_NOT_UPLOADED;
- UPLOADING;
- PRIVATE;
- UNLISTED;
- SCHEDULED;
- PUBLIC;
- FAILED;
- BLOCKED;
- REMOVED/ARCHIVED where applicable.

Default first upload is private unless project policy explicitly says otherwise.

## Post-upload verification

Verify:
- correct platform ID;
- duration;
- processing complete;
- thumbnail;
- metadata;
- captions;
- audience/disclosure state;
- privacy/schedule;
- no unexpected transcoding corruption;
- correct final-master lineage.

## Publication approval

Until explicitly changed by policy, public/scheduled publication requires human approval after private verification.

Approval attaches to:
- exact final master hash/version;
- metadata version;
- thumbnail version;
- audience/disclosure state;
- planned publish time/privacy.

Changing these materially may invalidate approval.

## Scheduling

Store desired publication timezone/time. Do not silently reinterpret timezone.

Future scheduler should handle:
- publish time;
- embargo;
- localization/channel strategy;
- platform delays/failures;
- rescheduling audit trail.

## Multi-platform future

Canonical publish package separates project metadata from platform adapters.

Future adapters may include:
- YouTube;
- short-form social platforms;
- podcast/audio feeds;
- music platforms;
- owned websites/apps.

Each adapter defines platform-specific constraints without mutating canonical final master.

## Failure behavior

Examples:
- auth expired -> block and request reconnection;
- upload interrupted -> resume/reconcile;
- metadata rejected -> fix metadata only;
- rights block -> do not upload/publicize;
- processing failure -> retry upload per bounded policy;
- duplicate platform asset detected -> reconcile, do not create another blindly.

## Publication history

Never overwrite historical publication records. Track changes to:
- title/description;
- thumbnail;
- privacy;
- scheduling;
- captions;
- platform asset status.

## Acceptance criteria

Publishing is development-ready when an approved final master can produce an auditable publish package, upload privately, verify platform state, wait for required approval and then publish/schedule without mixing publication state into creative generation jobs.