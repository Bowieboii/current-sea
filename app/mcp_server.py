"""The machine-native doorway into CURRENT•SEA."""

from typing import Annotated

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from app import __version__
from app.service import AssetService, InvalidAssetInput, InvocationLimitReached


def build_mcp_server(service: AssetService) -> MCPServer:
    server = MCPServer(
        name="current-sea",
        title="CURRENT SEA — Ambiguity Scan",
        description=(
            "A deterministic, explainable wording check with no submitted-text "
            "retention."
        ),
        instructions=(
            "Use scan_ambiguity when vague timing, quantities, references, "
            "commitments, or standards could make text harder to act on."
        ),
        version=__version__,
    )

    @server.tool(name="scan_ambiguity")
    def scan_ambiguity(
        text: Annotated[
            str,
            Field(
                min_length=1,
                max_length=10_000,
                description="Text to inspect; it is processed but not retained.",
            ),
        ],
    ) -> dict[str, object]:
        """Find wording that may need clarification.

        Use this when an agent needs an inexpensive, deterministic, explainable
        check for vague timing, quantities, references, commitments, or
        standards. The service retains invocation metadata but never the
        submitted text. Signals are possible issues, not proof of ambiguity.
        """
        try:
            return service.invoke(text, source="mcp")
        except (InvalidAssetInput, InvocationLimitReached) as error:
            raise ToolError(str(error)) from error

    return server
