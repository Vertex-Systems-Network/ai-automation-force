from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from lullabies_core import (
    Act,
    Asset,
    AssetKind,
    AttemptStatus,
    AudienceProfile,
    CanonicalStatus,
    CastProfile,
    Character,
    CharacterLock,
    CharacterVersion,
    Content,
    ContentObjective,
    ContentVersion,
    CostRecord,
    GenerationAttempt,
    GenerationRequest,
    Job,
    JobStatus,
    LockScope,
    ProductionLineageBundle,
    Project,
    ProjectBundle,
    ProviderModelRef,
    QARecord,
    RightsRecord,
    Scene,
    Sequence,
    Shot,
    Take,
    Timeline,
    TimeRange,
)
from lullabies_core.common import AuditFields

NOW = datetime(2026, 8, 29, 12, 0, tzinfo=UTC)


def audit() -> AuditFields:
    return AuditFields(created_at=NOW, updated_at=NOW)


def full_lineage_bundle() -> ProductionLineageBundle:
    project = Project(
        project_id="PRJ-000500",
        title="Full lineage fixture",
        audience=AudienceProfile(
            kind="preschool",
            age_min_years=2,
            age_max_years=5,
            child_directed=True,
            policy_profile="kids",
        ),
        cast=CastProfile(ages=["child"], genders=["mixed"], ai_may_decide=False),
        content_format="song",
        language="en",
        target_duration_seconds=120,
        character_ids=["CHR-000500"],
        content_id="CNT-000500",
        active_timeline_id="TML-000500",
        audit=audit(),
    )
    content = Content(
        content_id="CNT-000500",
        active_version_id="CTV-000500",
        project_id=project.project_id,
        status="approved",
        audit=audit(),
    )
    content_version = ContentVersion(
        content_version_id="CTV-000500",
        content_id=content.content_id,
        version=1,
        title="Count the Stars",
        content_format="song",
        language="en",
        target_duration_seconds=120,
        objective=ContentObjective(
            primary="Teach counting through an original preschool song",
            learning="Count from one to five",
            emotional="Calm confidence",
        ),
        premise="A recurring child character counts friendly stars.",
        hook="Each star joins the chorus.",
        script_or_lyrics="One little star, two little stars, count with me.",
        character_ids=["CHR-000500"],
        originality_fingerprint="fixture-count-stars-v1",
        audit=audit(),
    )

    pinned_version = CharacterVersion(
        character_version_id="CHV-000500",
        character_id="CHR-000500",
        version=1,
        display_name="Mira",
        character_type="human-child",
        apparent_age="5",
        gender_presentation="female",
        personality_traits=["curious", "gentle"],
        identity_constraints=["round face", "dark bob haircut"],
        status=CanonicalStatus.APPROVED,
        audit=audit(),
    )
    active_version = CharacterVersion(
        character_version_id="CHV-000501",
        character_id="CHR-000500",
        version=2,
        display_name="Mira",
        character_type="human-child",
        apparent_age="5",
        gender_presentation="female",
        personality_traits=["curious", "gentle"],
        identity_constraints=["round face", "dark bob haircut", "yellow cardigan"],
        status=CanonicalStatus.APPROVED,
        audit=audit(),
    )
    character = Character(
        character_id="CHR-000500",
        name="Mira",
        active_version_id=active_version.character_version_id,
        lock=CharacterLock(
            scope=LockScope.PROJECT,
            pinned_character_version_id=pinned_version.character_version_id,
            project_id=project.project_id,
        ),
        audit=audit(),
    )

    timeline = Timeline(
        timeline_id="TML-000500",
        project_id=project.project_id,
        duration_seconds=120,
        act_ids=["ACT-000500"],
        audit=audit(),
    )
    act = Act(
        act_id="ACT-000500",
        project_id=project.project_id,
        order=1,
        title="Song",
        sequence_ids=["SEQ-000500"],
        target_duration_seconds=120,
        audit=audit(),
    )
    sequence = Sequence(
        sequence_id="SEQ-000500",
        act_id=act.act_id,
        order=1,
        title="Counting chorus",
        scene_ids=["SCN-000500"],
        target_duration_seconds=120,
        audit=audit(),
    )
    scene = Scene(
        scene_id="SCN-000500",
        sequence_id=sequence.sequence_id,
        order=1,
        title="Star meadow",
        character_ids=[character.character_id],
        shot_ids=["SHT-000500"],
        target_duration_seconds=120,
        audit=audit(),
    )
    take = Take(
        take_id="TAK-000500",
        shot_id="SHT-000500",
        attempt_id="ATT-000500",
        asset_id="AST-000501",
        canonical_status=CanonicalStatus.APPROVED,
        continuity_score=98,
        qa_record_ids=["QAR-000500"],
        audit=audit(),
    )
    shot = Shot(
        shot_id="SHT-000500",
        scene_id=scene.scene_id,
        order=1,
        time_range=TimeRange(start_seconds=0, duration_seconds=8),
        purpose="Opening counting beat",
        action="Mira points to the first star.",
        character_ids=[character.character_id],
        take_ids=[take.take_id],
        selected_take_id=take.take_id,
        audit=audit(),
    )
    project_bundle = ProjectBundle(
        project=project,
        timeline=timeline,
        acts=[act],
        sequences=[sequence],
        scenes=[scene],
        shots=[shot],
        takes=[take],
        characters=[character],
        character_versions=[pinned_version, active_version],
    )

    source_asset = Asset(
        asset_id="AST-000500",
        project_id=project.project_id,
        kind=AssetKind.IMAGE,
        uri="s3://fixture/reference/mira.png",
        sha256="a" * 64,
        mime_type="image/png",
        size_bytes=1024,
        canonical_status=CanonicalStatus.APPROVED,
        audit=audit(),
    )
    generated_asset = Asset(
        asset_id="AST-000501",
        project_id=project.project_id,
        kind=AssetKind.VIDEO,
        uri="s3://fixture/generated/shot-500.mp4",
        sha256="b" * 64,
        mime_type="video/mp4",
        size_bytes=4096,
        duration_seconds=8,
        width=1920,
        height=1080,
        parent_asset_ids=[source_asset.asset_id],
        provider_id="fixture-provider",
        model_provider_id="fixture-provider",
        provider_model_id="fixture-video-v1",
        generation_attempt_id="ATT-000500",
        rights_record_id="RGT-000500",
        canonical_status=CanonicalStatus.APPROVED,
        audit=audit(),
    )
    qa_record = QARecord(
        qa_record_id="QAR-000500",
        subject_type="asset",
        subject_id=generated_asset.asset_id,
        gate="continuity",
        passed=True,
        critical=True,
        score=98,
        created_at=NOW,
    )
    job = Job(
        job_id="JOB-000500",
        project_id=project.project_id,
        job_type="video-shot-generation",
        status=JobStatus.COMPLETED,
        idempotency_key="fixture-job-000500",
        shot_id=shot.shot_id,
        content_id=content.content_id,
        attempt_ids=["ATT-000500"],
        selected_attempt_id="ATT-000500",
        retry_budget_remaining=2,
        audit=audit(),
    )
    attempt = GenerationAttempt(
        attempt_id="ATT-000500",
        job_id=job.job_id,
        attempt_number=1,
        provider=ProviderModelRef(
            provider_id="fixture-provider",
            model_id="fixture-video-v1",
            capability="image-to-video",
            access_class="test",
            registry_verified_at=NOW,
        ),
        request=GenerationRequest(
            capability="image-to-video",
            project_id=project.project_id,
            shot_id=shot.shot_id,
            content_id=content.content_id,
            input_asset_ids=[source_asset.asset_id],
            target_duration_seconds=8,
            requires_commercial_rights=True,
            requires_character_continuity=True,
            idempotency_key="fixture-attempt-request-000500",
        ),
        provider_generation_id="provider-job-500",
        started_at=NOW,
        finished_at=NOW,
        output_asset_ids=[generated_asset.asset_id],
        status=AttemptStatus.SUCCEEDED,
        paid_cost=Decimal("0.42"),
        qa_record_ids=[qa_record.qa_record_id],
    )
    cost_record = CostRecord(
        cost_record_id="CST-000500",
        project_id=project.project_id,
        job_id=job.job_id,
        attempt_id=attempt.attempt_id,
        provider_id=attempt.provider.provider_id,
        model_provider_id=attempt.provider.model_provider_id,
        model_id=attempt.provider.model_id,
        paid_cost=Decimal("0.42"),
        recorded_at=NOW,
    )
    rights_record = RightsRecord(
        rights_record_id="RGT-000500",
        subject_type="asset",
        subject_id=generated_asset.asset_id,
        provider_id=attempt.provider.provider_id,
        model_provider_id=attempt.provider.model_provider_id,
        model_id=attempt.provider.model_id,
        plan_or_tier="fixture",
        source_basis="provider-terms-unresolved-fixture",
        publication_blocked=True,
        notes=["Commercial rights intentionally unresolved for fail-closed fixture."],
    )

    return ProductionLineageBundle(
        project_bundle=project_bundle,
        content=content,
        content_version=content_version,
        jobs=[job],
        attempts=[attempt],
        assets=[source_asset, generated_asset],
        qa_records=[qa_record],
        cost_records=[cost_record],
        rights_records=[rights_record],
    )
