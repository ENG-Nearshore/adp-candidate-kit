"""Repositories that can be documented and the request templates users can pick."""

import json
from dataclasses import dataclass
from pathlib import Path

CLASSIFICATIONS = ("public", "internal", "confidential")


@dataclass(frozen=True)
class Repository:
    id: str
    name: str
    description: str
    language: str
    owner: str
    classification: str
    path: Path
    docs_paths: tuple[Path, ...]

    def summary(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "language": self.language,
            "owner": self.owner,
            "classification": self.classification,
            "has_docs": bool(self.docs_paths),
        }


@dataclass(frozen=True)
class Template:
    id: str
    title: str
    path: Path

    def text(self) -> str:
        return self.path.read_text(encoding="utf-8")


class Catalog:
    def __init__(self, repositories: list[Repository], templates: list[Template]):
        self._repositories = {r.id: r for r in repositories}
        self._templates = {t.id: t for t in templates}

    @classmethod
    def load(cls, catalog_path: Path) -> "Catalog":
        data = json.loads(catalog_path.read_text(encoding="utf-8"))
        base = catalog_path.parent
        repositories = []
        for item in data["repositories"]:
            if item["classification"] not in CLASSIFICATIONS:
                raise ValueError(f"Unknown classification for {item['id']}: {item['classification']}")
            repositories.append(
                Repository(
                    id=item["id"],
                    name=item["name"],
                    description=item.get("description", ""),
                    language=item.get("language", ""),
                    owner=item.get("owner", ""),
                    classification=item["classification"],
                    path=(base / item["path"]).resolve(),
                    docs_paths=tuple((base / p).resolve() for p in item.get("docs", [])),
                )
            )
        templates = [
            Template(id=t["id"], title=t["title"], path=(base / t["path"]).resolve())
            for t in data["templates"]
        ]
        return cls(repositories, templates)

    def repositories(self) -> list[Repository]:
        return list(self._repositories.values())

    def repository(self, repo_id: str) -> Repository | None:
        return self._repositories.get(repo_id)

    def templates(self) -> list[Template]:
        return list(self._templates.values())

    def template(self, template_id: str) -> Template | None:
        return self._templates.get(template_id)
