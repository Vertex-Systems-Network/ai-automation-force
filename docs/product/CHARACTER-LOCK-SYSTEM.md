# Character Library, Selection and Lock System

## Goal

Characters must be selectable before production, reusable across projects, lockable for continuity, and provider-independent. A provider's saved reference is an optimization, not the canonical identity.

## 1. Character library UX

Before storyboarding/video generation show a Character Library with:
- search/filter
- character type
- age category
- gender presentation
- human/non-human
- art/realism compatibility
- voice assignment
- locked status
- projects using the character
- last QA date
- canonical preview views

Actions:
- Select existing
- Create new
- Duplicate as variant
- Create wardrobe/look variant
- Lock
- Unlock with versioned change request
- Archive

## 2. Character lifecycle

`idea -> drafted -> reference-generated -> identity-qa -> locked -> active -> versioned -> archived`

Only `locked` or explicitly `one-off project locked` identities can be recurring production characters.

## 3. Canonical character record

Every character stores:
- character ID and version
- name/display name
- type/archetype
- age category / apparent age range
- gender presentation if applicable
- species/entity type
- height/proportion profile
- facial geometry descriptors
- hair/fur/material descriptors
- eye descriptors
- skin/fur/material palette
- body proportions
- signature features
- default wardrobe
- allowed wardrobe variants
- accessories
- personality/performance traits
- voice ID/profile
- motion/gesture traits
- expression set
- pose set
- front/3-quarter/profile/back references
- full-body and close-up references
- palette swatches
- forbidden mutations
- source/provenance/license
- canonical asset hashes

Do not depend on a single text prompt to reconstruct identity.

## 4. Lock modes

### Global hard lock
Use the same canonical identity across all projects. Changes require a new character version.

### Project lock
Identity is fixed inside one project but may differ from another project version.

### Look lock
Character identity remains stable while a named wardrobe/hair/accessory look is fixed for a sequence.

### Scene lock
Temporary state such as wet clothes, a hat, dirt, injury-free costume change, carried prop, etc. is preserved through linked shots.

### One-off lock
A newly generated one-project character still gets a minimal canonical identity package to prevent shot drift.

## 5. Reuse vs new behavior

Project option:
- `reuse_only`
- `new_only`
- `reuse_preferred`
- `new_preferred`
- `mixed`
- `ai_decide`

AI decision factors:
- story role fit
- age/audience fit
- recent character saturation
- series continuity
- originality
- visual compatibility
- production cost
- provider capability

Do not create new characters merely because generation is easy; recurring IP should gain value from controlled reuse.

## 6. Multi-character scenes

For every shot store:
- participating character IDs/versions
- screen position
- relative scale
- gaze target
- interaction partner
- speaking state
- pose/motion state
- wardrobe/look ID
- prop relationship

When a provider has a reference-count limit, the router must select a compatible generation technique rather than silently dropping a character reference.

## 7. Provider adapters

Adapter maps canonical identity to available mechanisms:
- saved reference
- multi-image reference
- subject reference
- image-to-video
- first-frame
- reference video
- trained avatar/digital twin when legitimately configured
- identity embedding/LoRA only where provider terms and project policy allow

Every generation attempt records which canonical references were actually supplied.

## 8. Continuity QA

Critical identity checks:
- face/head geometry
- body proportions
- apparent age
- species
- hair/fur/material
- eyes
- skin/palette
- wardrobe/look
- signature accessories
- scale relative to other characters

Secondary checks:
- expression accuracy
- pose plausibility
- style consistency
- lighting compatibility

Critical identity failures are hard failures; a visually attractive shot cannot pass by averaging these errors away.

## 9. Versioning

Never silently modify a locked character.

Example:
- `CHAR-0007@1.0` canonical original
- `LOOK-CHAR-0007-SLEEPWEAR@1.0` wardrobe look
- `CHAR-0007@2.0` intentional identity redesign

Existing projects remain pinned to their selected versions unless explicitly migrated.

## 10. Rights and real-person characters

For original generated characters, keep generation provenance and commercial-use status.

For real people/digital twins, require explicit rights/consent records and provider-compliant identity/voice workflows. Do not make a provider-generated resemblance the only proof of authorization.

## 11. Storage target

Suggested structure:

`characters/<character-id>/character.json`
`characters/<character-id>/references/`
`characters/<character-id>/looks/`
`characters/<character-id>/voices/`
`characters/<character-id>/qa/`

Large binaries live in object/media storage; Git stores manifests, hashes, metadata and appropriately sized canonical references only when repository policy permits.