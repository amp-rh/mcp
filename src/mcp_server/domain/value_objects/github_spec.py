from dataclasses import dataclass


@dataclass(frozen=True)
class GitHubSpec:
    owner: str
    repo: str
    subpath: str | None = None

    @classmethod
    def from_url(cls, url: str) -> "GitHubSpec":
        if not url.startswith("github:"):
            raise ValueError(f"Invalid GitHub spec: {url}")

        path = url[7:]
        parts = path.split("/", 2)

        if len(parts) < 2:
            raise ValueError(f"GitHub spec must be owner/repo: {url}")

        return cls(
            owner=parts[0],
            repo=parts[1],
            subpath=parts[2] if len(parts) > 2 else None,
        )

    def to_package_name(self) -> str:
        return f"{self.owner}/{self.repo}"

    def infer_namespace(self) -> str:
        name = self.repo.lower()
        for prefix in ("mcp-", "server-", "mcp-server-"):
            if name.startswith(prefix):
                return name[len(prefix) :]
        return name
