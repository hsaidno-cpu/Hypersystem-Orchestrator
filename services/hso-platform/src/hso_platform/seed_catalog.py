from __future__ import annotations

import json
from pathlib import Path

from .database import build_engine, build_session_factory
from .models import Plugin
from .settings import Settings


def seed_catalog(repository_root: Path, session_factory) -> dict:
    plugin_path = repository_root / "catalog" / "plugins.json"
    repository_path = repository_root / "catalog" / "repositories.json"
    plugins = json.loads(plugin_path.read_text(encoding="utf-8"))["plugins"]
    repositories = json.loads(repository_path.read_text(encoding="utf-8"))["repositories"]
    repository_index = {item["repository_id"]: item for item in repositories}

    created = 0
    updated = 0
    with session_factory() as session, session.begin():
        for source in plugins:
            repository = repository_index.get(source.get("source_repository_id"), {})
            existing = session.get(Plugin, source["plugin_key"])
            values = {
                "display_name": source["display_name"],
                "source_state": source["source_state"],
                "source_url": repository.get("url"),
                "source_commit": repository.get("pinned_commit"),
                "owner_reference": repository.get("full_name"),
                "metadata_json": {
                    "primary_domain": source.get("primary_domain"),
                    "release_version": source.get("release_version"),
                    "platform_package_version": source.get("platform_package_version"),
                    "source_repository_id": source.get("source_repository_id"),
                    "instruction_snapshot_path": source.get("instruction_snapshot_path"),
                    "source_instruction_parity_status": source.get("source_instruction_parity_status"),
                    "source_classification": source.get("source_classification"),
                },
            }
            if existing:
                for field, value in values.items():
                    setattr(existing, field, value)
                # Reseeding never overwrites human-reviewed rights decisions.
                updated += 1
            else:
                session.add(Plugin(
                    plugin_key=source["plugin_key"],
                    execution_rights_status="NOT_ASSESSED",
                    distribution_rights_status="NOT_ASSESSED",
                    **values,
                ))
                created += 1
    return {"created": created, "updated": updated, "total": len(plugins)}


def main() -> int:
    settings = Settings.from_env()
    settings.validate()
    root = Path(__file__).resolve().parents[4]
    engine = build_engine(settings)
    try:
        result = seed_catalog(root, build_session_factory(engine))
        print(json.dumps(result, sort_keys=True))
        return 0
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
