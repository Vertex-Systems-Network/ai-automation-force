# Asset & Media Library Specification

## Purpose

Define how the platform stores, versions, searches, reviews and reuses all media and reference assets without putting large binary files in ordinary Git history.

## Asset classes

Supported classes include:
- character reference image;
- character look reference;
- world/location reference;
- prop reference;
- style reference;
- keyframe;
- generated image;
- video take;
- approved shot;
- narration stem;
- dialogue stem;
- lead vocal;
- music/instrumental;
- ambience;
- SFX;
- final audio master;
- timeline/OTIO export;
- subtitle/caption;
- thumbnail/poster;
- final video master;
- proxy/preview;
- imported user/source asset;
- provider intermediate;
- rejected generation.

## Canonical asset record

Each asset should store:
- stable Asset ID;
- project/content/scene/shot/character links where applicable;
- media kind;
- canonical vs candidate vs rejected state;
- MIME/container;
- size;
- checksum/hash;
- duration where applicable;
- dimensions/FPS/channels/sample rate where applicable;
- storage URI;
- proxy/thumbnail URI;
- parent/source asset IDs;
- provider/model/generation attempt;
- prompt/version/hash;
- created timestamp;
- rights/provenance record;
- QA state;
- retention class;
- tags/semantic metadata.

## Storage classes

Suggested logical classes:
- `TEMPORARY` — provider uploads, intermediate scratch;
- `CANDIDATE` — generated/imported result awaiting QA;
- `REJECTED_HISTORY` — failed generation retained for learning/audit according to retention policy;
- `CANONICAL` — approved production asset;
- `MASTER` — approved final/near-final master;
- `PROXY` — lower-resolution derivative;
- `ARCHIVE` — long-term historical storage.

## Object storage

Large binary media belongs in S3-compatible/object storage or configured local development storage.

Git stores:
- code;
- policies;
- prompts;
- schemas;
- research;
- manifests;
- hashes;
- selected audit exports.

Normal project media must not bloat ordinary Git history.

## Import pipeline

Imported assets must pass:
- file-size policy;
- MIME/container detection;
- decode/probe validation;
- checksum;
- metadata extraction;
- malware/untrusted-file handling where applicable;
- rights/source declaration;
- canonical link assignment.

Do not trust filename extension alone.

## Versioning

A modified/regenerated asset creates a new Asset/version relationship rather than overwriting the only approved master.

Examples:
- new character reference pack;
- revised keyframe;
- remixed audio;
- re-encoded final master;
- regenerated video take.

Selection may move to the new version while history remains available.

## Derivatives

Derivatives should retain parent lineage:
- 4K master -> 1080p proxy;
- 16:9 master -> 9:16 derivative;
- WAV master -> AAC/MP3;
- image -> thumbnail;
- video -> poster frame.

Deterministic derivatives should record tool/version/settings where useful.

## Search/filter

Future library should support filtering by:
- project;
- asset type;
- character;
- world/location;
- shot/scene;
- provider/model;
- approved/rejected;
- rights state;
- date;
- language;
- tags;
- quality score;
- canonical state.

Semantic search may augment but not replace stable IDs and metadata.

## Asset graph

Every generated/derived asset should be traceable through parent IDs.

Example:
`ContentVersion -> AudioPrompt -> NarrationStem -> Timeline -> Keyframe -> GenerationAttempt -> VideoTake -> ApprovedShot -> FinalMaster`

Regeneration must not break lineage.

## Canonical selection

Only approved assets can be promoted to canonical production use.

Selection action records:
- previous selection;
- new selection;
- actor/AI role;
- reason;
- timestamp;
- downstream invalidation if needed.

## Invalidation

Changing upstream canonical assets may invalidate downstream state.

Examples:
- CharacterVersion changed -> affected future/unapproved shots may require re-plan;
- script changed -> narration/storyboard/timing may be stale;
- audio master duration changed -> storyboard/timeline timing may require rebuild;
- selected shot changed -> adjacent continuity QA may require re-run.

System should invalidate the smallest necessary dependency scope, not restart whole project blindly.

## Rejected assets

Rejected generations remain useful for:
- failure history;
- provider success statistics;
- duplicate retry prevention;
- QA training/evaluation;
- debugging.

Retention may eventually archive/delete large rejected binaries while preserving hashes/metadata/diagnosis according to configured policy.

## Privacy

Some imported assets may contain private people/voices/data. Asset metadata should support privacy/access classification and signed/limited access rather than public URLs.

## Acceptance criteria

Asset library planning is development-ready when every media artifact has stable identity, storage/probe/checksum requirements, version/lineage semantics, approval state and a clear rule for canonical selection and downstream invalidation.