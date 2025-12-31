from mcp_server.domain.value_objects.backend_source import BackendSource, BackendSourceType


class NamespaceGenerator:
    @staticmethod
    def generate(source: BackendSource, explicit_namespace: str | None = None) -> str:
        if explicit_namespace:
            return explicit_namespace

        if source.github_spec:
            return source.github_spec.infer_namespace()

        if source.package_name:
            name = source.package_name.split("/")[-1].lower()
            for prefix in ("mcp-", "server-", "mcp-server-"):
                if name.startswith(prefix):
                    return name[len(prefix) :]
            return name

        raise ValueError("Cannot auto-generate namespace for HTTP-only backend")
