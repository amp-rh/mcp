from dataclasses import dataclass
from enum import Enum

from mcp_server.domain.value_objects.github_spec import GitHubSpec
from mcp_server.domain.value_objects.process_config import ProcessConfig


class BackendSourceType(Enum):
    HTTP = "http"
    GITHUB = "github"
    PACKAGE = "package"


@dataclass(frozen=True)
class BackendSource:
    source_type: BackendSourceType
    http_url: str | None = None
    github_spec: GitHubSpec | None = None
    package_name: str | None = None
    process_config: ProcessConfig | None = None

    def __post_init__(self) -> None:
        if self.source_type == BackendSourceType.HTTP and not self.http_url:
            raise ValueError("HTTP source requires http_url")
        if self.source_type == BackendSourceType.GITHUB and not self.github_spec:
            raise ValueError("GitHub source requires github_spec")
        if self.source_type == BackendSourceType.PACKAGE and not self.package_name:
            raise ValueError("Package source requires package_name")
