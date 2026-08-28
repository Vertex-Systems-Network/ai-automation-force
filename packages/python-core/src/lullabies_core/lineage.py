from __future__ import annotations

from collections import defaultdict

from pydantic import Field, model_validator

from .aggregate import ProjectBundle
from .common import CommercialUseStatus, LockScope, StrictModel
from .content import Content, ContentVersion
from .production import Asset, CostRecord, GenerationAttempt, Job, QARecord, RightsRecord
from .timeline import Take


class ProductionLineageBundle(StrictModel):
    """Complete provider-neutral production lineage for one canonical project.

    `ProjectBundle` owns editorial graph validation. This aggregate adds only lineage and
    ownership invariants already represented by M01 contracts: content ownership, jobs,
    attempts, generated assets, QA, costs and rights. It intentionally does not add
    provider execution or advanced editorial semantics.
    """

    project_bundle: ProjectBundle
    content: Content
    content_version: ContentVersion
    jobs: list[Job] = Field(default_factory=list)
    attempts: list[GenerationAttempt] = Field(default_factory=list)
    assets: list[Asset] = Field(default_factory=list)
    qa_records: list[QARecord] = Field(default_factory=list)
    cost_records: list[CostRecord] = Field(default_factory=list)
    rights_records: list[RightsRecord] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_lineage(self) -> ProductionLineageBundle:
        self._validate_content()
        self._validate_character_locks()
        self._validate_jobs_and_attempts()
        self._validate_assets()
        self._validate_takes_and_qa()
        self._validate_costs()
        self._validate_rights()
        return self

    def _validate_content(self) -> None:
        project = self.project_bundle.project
        timeline = self.project_bundle.timeline
        if project.content_id != self.content.content_id:
            raise ValueError("project.content_id must reference lineage content")
        if self.content.project_id != project.project_id:
            raise ValueError("content.project_id must equal project.project_id")
        if self.content.active_version_id != self.content_version.content_version_id:
            raise ValueError("content.active_version_id must reference lineage content version")
        if self.content_version.content_id != self.content.content_id:
            raise ValueError("content version belongs to another content identity")
        if project.active_timeline_id != timeline.timeline_id:
            raise ValueError("project.active_timeline_id must reference lineage timeline")

        character_ids = {item.character_id for item in self.project_bundle.characters}
        world_ids = {item.world_id for item in self.project_bundle.worlds}
        prop_ids = {item.prop_id for item in self.project_bundle.props}
        missing_characters = set(self.content_version.character_ids) - character_ids
        missing_worlds = set(self.content_version.world_ids) - world_ids
        missing_props = set(self.content_version.prop_ids) - prop_ids
        if missing_characters:
            raise ValueError(
                f"content version references missing characters: {sorted(missing_characters)}"
            )
        if missing_worlds:
            raise ValueError(f"content version references missing worlds: {sorted(missing_worlds)}")
        if missing_props:
            raise ValueError(f"content version references missing props: {sorted(missing_props)}")

    def _validate_character_locks(self) -> None:
        project_id = self.project_bundle.project.project_id
        scenes = {scene.scene_id for scene in self.project_bundle.scenes}
        versions = {
            version.character_version_id: version
            for version in self.project_bundle.character_versions
        }
        for character in self.project_bundle.characters:
            lock = character.lock
            if lock.scope == LockScope.PROJECT and lock.project_id != project_id:
                raise ValueError(f"character {character.character_id} lock belongs to another project")
            if lock.scope == LockScope.SCENE and lock.scene_id not in scenes:
                raise ValueError(f"character {character.character_id} lock references missing scene")
            if lock.scope == LockScope.LOOK and lock.pinned_look_id is not None:
                pinned = lock.pinned_character_version_id
                if pinned is None or pinned not in versions:
                    raise ValueError(f"character {character.character_id} look lock version is missing")
                look_ids = {look.look_id for look in versions[pinned].looks}
                if lock.pinned_look_id not in look_ids:
                    raise ValueError(f"character {character.character_id} look lock is not in pinned version")

    def _validate_jobs_and_attempts(self) -> None:
        project = self.project_bundle.project
        shots = {shot.shot_id for shot in self.project_bundle.shots}
        assets = {asset.asset_id for asset in self.assets}
        jobs = self._unique_jobs()
        attempts = self._unique_attempts()
        attempts_by_job: dict[str, set[str]] = defaultdict(set)
        attempt_numbers_by_job: dict[str, set[int]] = defaultdict(set)

        for job in self.jobs:
            if job.project_id != project.project_id:
                raise ValueError(f"job {job.job_id} belongs to another project")
            if job.shot_id is not None and job.shot_id not in shots:
                raise ValueError(f"job {job.job_id} references missing shot")
            if job.content_id is not None and job.content_id != self.content.content_id:
                raise ValueError(f"job {job.job_id} references another content identity")

        for attempt in self.attempts:
            if attempt.job_id not in jobs:
                raise ValueError(f"attempt {attempt.attempt_id} references missing job")
            job = jobs[attempt.job_id]
            attempts_by_job[attempt.job_id].add(attempt.attempt_id)
            if attempt.attempt_number in attempt_numbers_by_job[attempt.job_id]:
                raise ValueError(f"job {attempt.job_id} has duplicate attempt_number")
            attempt_numbers_by_job[attempt.job_id].add(attempt.attempt_number)

            request = attempt.request
            if request.project_id != project.project_id:
                raise ValueError(f"attempt {attempt.attempt_id} request belongs to another project")
            if job.shot_id is not None and request.shot_id != job.shot_id:
                raise ValueError(f"attempt {attempt.attempt_id} request shot differs from job")
            if request.shot_id is not None and request.shot_id not in shots:
                raise ValueError(f"attempt {attempt.attempt_id} request references missing shot")
            if job.content_id is not None and request.content_id != job.content_id:
                raise ValueError(f"attempt {attempt.attempt_id} request content differs from job")
            if request.content_id is not None and request.content_id != self.content.content_id:
                raise ValueError(f"attempt {attempt.attempt_id} request references another content")
            missing_inputs = set(request.input_asset_ids) - assets
            if missing_inputs:
                raise ValueError(
                    f"attempt {attempt.attempt_id} references missing input assets: "
                    f"{sorted(missing_inputs)}"
                )

        for job in self.jobs:
            loaded = attempts_by_job.get(job.job_id, set())
            if set(job.attempt_ids) != loaded:
                raise ValueError(f"job {job.job_id} attempt membership is inconsistent")
            if job.selected_attempt_id is not None and job.selected_attempt_id not in attempts:
                raise ValueError(f"job {job.job_id} selected attempt is not loaded")

    def _validate_assets(self) -> None:
        project_id = self.project_bundle.project.project_id
        attempts = self._unique_attempts()
        assets = self._unique_assets()

        for asset in self.assets:
            if asset.project_id is not None and asset.project_id != project_id:
                raise ValueError(f"asset {asset.asset_id} belongs to another project")
            if asset.asset_id in asset.parent_asset_ids:
                raise ValueError(f"asset {asset.asset_id} cannot parent itself")
            missing_parents = set(asset.parent_asset_ids) - set(assets)
            if missing_parents:
                raise ValueError(
                    f"asset {asset.asset_id} references missing parents: {sorted(missing_parents)}"
                )
            if asset.generation_attempt_id is not None:
                if asset.generation_attempt_id not in attempts:
                    raise ValueError(f"asset {asset.asset_id} references missing generation attempt")
                attempt = attempts[asset.generation_attempt_id]
                if asset.asset_id not in attempt.output_asset_ids:
                    raise ValueError(f"asset {asset.asset_id} is not an output of its generation attempt")
                if asset.provider_id is not None and asset.provider_id != attempt.provider.provider_id:
                    raise ValueError(f"asset {asset.asset_id} provider differs from generation attempt")
                if (
                    asset.model_provider_id is not None
                    and asset.model_provider_id != attempt.provider.model_provider_id
                ):
                    raise ValueError(
                        f"asset {asset.asset_id} model provider differs from generation attempt"
                    )
                if (
                    asset.provider_model_id is not None
                    and asset.provider_model_id != attempt.provider.model_id
                ):
                    raise ValueError(f"asset {asset.asset_id} model differs from generation attempt")

        for attempt in self.attempts:
            missing_outputs = set(attempt.output_asset_ids) - set(assets)
            if missing_outputs:
                raise ValueError(
                    f"attempt {attempt.attempt_id} references missing output assets: "
                    f"{sorted(missing_outputs)}"
                )
            for asset_id in attempt.output_asset_ids:
                if assets[asset_id].generation_attempt_id != attempt.attempt_id:
                    raise ValueError(
                        f"attempt {attempt.attempt_id} output asset points to another attempt"
                    )

        self._validate_asset_parent_cycles(assets)

    def _validate_takes_and_qa(self) -> None:
        attempts = self._unique_attempts()
        assets = self._unique_assets()
        qa_records = self._unique_qa_records()

        for take in self.project_bundle.takes:
            self._validate_take_lineage(take, attempts, assets)
            for qa_id in take.qa_record_ids:
                if qa_id not in qa_records:
                    raise ValueError(f"take {take.take_id} references missing QA record")
                qa = qa_records[qa_id]
                valid_subject = qa.subject_type == "take" and qa.subject_id == take.take_id
                valid_subject = valid_subject or (
                    qa.subject_type == "asset"
                    and take.asset_id is not None
                    and qa.subject_id == take.asset_id
                )
                if not valid_subject:
                    raise ValueError(f"take {take.take_id} QA record belongs to another subject")

        takes_by_attempt: dict[str, set[str]] = defaultdict(set)
        for take in self.project_bundle.takes:
            if take.attempt_id is not None:
                takes_by_attempt[take.attempt_id].add(take.take_id)

        for attempt in self.attempts:
            for qa_id in attempt.qa_record_ids:
                if qa_id not in qa_records:
                    raise ValueError(f"attempt {attempt.attempt_id} references missing QA record")
                qa = qa_records[qa_id]
                valid_subject = qa.subject_type in {"attempt", "generation-attempt"} and (
                    qa.subject_id == attempt.attempt_id
                )
                valid_subject = valid_subject or (
                    qa.subject_type == "asset" and qa.subject_id in attempt.output_asset_ids
                )
                valid_subject = valid_subject or (
                    qa.subject_type == "take"
                    and qa.subject_id in takes_by_attempt.get(attempt.attempt_id, set())
                )
                if not valid_subject:
                    raise ValueError(
                        f"attempt {attempt.attempt_id} QA record belongs to another subject"
                    )

    def _validate_take_lineage(
        self,
        take: Take,
        attempts: dict[str, GenerationAttempt],
        assets: dict[str, Asset],
    ) -> None:
        if take.attempt_id is not None:
            if take.attempt_id not in attempts:
                raise ValueError(f"take {take.take_id} references missing attempt")
            attempt = attempts[take.attempt_id]
            if attempt.request.shot_id != take.shot_id:
                raise ValueError(f"take {take.take_id} attempt belongs to another shot")
        if take.asset_id is not None:
            if take.asset_id not in assets:
                raise ValueError(f"take {take.take_id} references missing asset")
            if take.attempt_id is not None:
                asset = assets[take.asset_id]
                if asset.generation_attempt_id != take.attempt_id:
                    raise ValueError(f"take {take.take_id} asset belongs to another attempt")
                if take.asset_id not in attempts[take.attempt_id].output_asset_ids:
                    raise ValueError(f"take {take.take_id} asset is not an attempt output")

    def _validate_costs(self) -> None:
        project_id = self.project_bundle.project.project_id
        jobs = self._unique_jobs()
        attempts = self._unique_attempts()
        for cost in self.cost_records:
            if cost.project_id != project_id:
                raise ValueError(f"cost {cost.cost_record_id} belongs to another project")
            if cost.job_id is not None and cost.job_id not in jobs:
                raise ValueError(f"cost {cost.cost_record_id} references missing job")
            if cost.attempt_id is None:
                if not cost.estimated:
                    raise ValueError(f"actual cost {cost.cost_record_id} requires attempt_id")
                continue
            if cost.attempt_id not in attempts:
                raise ValueError(f"cost {cost.cost_record_id} references missing attempt")
            attempt = attempts[cost.attempt_id]
            if cost.job_id is not None and cost.job_id != attempt.job_id:
                raise ValueError(f"cost {cost.cost_record_id} job differs from attempt")
            if cost.provider_id != attempt.provider.provider_id:
                raise ValueError(f"cost {cost.cost_record_id} provider differs from attempt")
            if cost.model_provider_id != attempt.provider.model_provider_id:
                raise ValueError(f"cost {cost.cost_record_id} model provider differs from attempt")
            if cost.model_id != attempt.provider.model_id:
                raise ValueError(f"cost {cost.cost_record_id} model differs from attempt")

    def _validate_rights(self) -> None:
        assets = self._unique_assets()
        rights = self._unique_rights_records()
        for asset in self.assets:
            if asset.rights_record_id is None:
                continue
            if asset.rights_record_id not in rights:
                raise ValueError(f"asset {asset.asset_id} references missing rights record")
            record = rights[asset.rights_record_id]
            if record.subject_type != "asset" or record.subject_id != asset.asset_id:
                raise ValueError(f"asset {asset.asset_id} rights record belongs to another subject")

        for record in self.rights_records:
            if record.subject_type == "asset" and record.subject_id not in assets:
                raise ValueError(f"rights {record.rights_record_id} references missing asset")
            if (
                record.commercial_use != CommercialUseStatus.ALLOWED
                and not record.publication_blocked
            ):
                raise ValueError(
                    f"rights {record.rights_record_id} must remain publication-blocked"
                )

    def _validate_asset_parent_cycles(self, assets: dict[str, Asset]) -> None:
        visited: set[str] = set()
        active: set[str] = set()

        def visit(asset_id: str) -> None:
            if asset_id in active:
                raise ValueError(f"asset lineage contains a parent cycle at {asset_id}")
            if asset_id in visited:
                return
            active.add(asset_id)
            for parent_id in assets[asset_id].parent_asset_ids:
                visit(parent_id)
            active.remove(asset_id)
            visited.add(asset_id)

        for asset_id in assets:
            visit(asset_id)

    def _unique_jobs(self) -> dict[str, Job]:
        values = {job.job_id: job for job in self.jobs}
        if len(values) != len(self.jobs):
            raise ValueError("duplicate Job IDs")
        return values

    def _unique_attempts(self) -> dict[str, GenerationAttempt]:
        values = {attempt.attempt_id: attempt for attempt in self.attempts}
        if len(values) != len(self.attempts):
            raise ValueError("duplicate GenerationAttempt IDs")
        return values

    def _unique_assets(self) -> dict[str, Asset]:
        values = {asset.asset_id: asset for asset in self.assets}
        if len(values) != len(self.assets):
            raise ValueError("duplicate Asset IDs")
        return values

    def _unique_qa_records(self) -> dict[str, QARecord]:
        values = {record.qa_record_id: record for record in self.qa_records}
        if len(values) != len(self.qa_records):
            raise ValueError("duplicate QARecord IDs")
        return values

    def _unique_rights_records(self) -> dict[str, RightsRecord]:
        values = {record.rights_record_id: record for record in self.rights_records}
        if len(values) != len(self.rights_records):
            raise ValueError("duplicate RightsRecord IDs")
        return values
