from __future__ import annotations

import pytest
from lineage_fixtures import full_lineage_bundle

from ai_automation_force_core import ProductionLineageBundle


def _revalidate(bundle: ProductionLineageBundle, assets: list[object]) -> None:
    candidate = bundle.model_copy(update={"assets": assets})
    ProductionLineageBundle.model_validate(candidate.model_dump())


def test_wp4_retains_canonical_asset_parent_cycle_rejection() -> None:
    """WP4 provenance persistence must not bypass the canonical lineage graph authority."""
    bundle = full_lineage_bundle()
    source = bundle.assets[0]
    derived = bundle.assets[1]

    cyclic_source = source.model_copy(update={"parent_asset_ids": [derived.asset_id]})
    cyclic_derived = derived.model_copy(update={"parent_asset_ids": [source.asset_id]})

    with pytest.raises(ValueError, match="parent cycle"):
        _revalidate(bundle, [cyclic_source, cyclic_derived, *bundle.assets[2:]])


def test_wp4_retains_project_boundary_rejection_for_asset_graph() -> None:
    """A provenance carrier cannot make an asset from another project part of this graph."""
    bundle = full_lineage_bundle()
    foreign_asset = bundle.assets[0].model_copy(update={"project_id": "PRJ-999999"})

    with pytest.raises(ValueError, match="belongs to another project"):
        _revalidate(bundle, [foreign_asset, *bundle.assets[1:]])
