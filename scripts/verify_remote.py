"""Verify that a deployed CURRENT•SEA endpoint is callable by an MCP client."""

import argparse
import asyncio

from mcp import Client


async def verify(base_url: str) -> None:
    mcp_url = f"{base_url.rstrip('/')}/mcp"
    async with Client(mcp_url) as client:
        tools = await client.list_tools()
        tool_names = {tool.name for tool in tools.tools}
        if "scan_ambiguity" not in tool_names:
            raise RuntimeError("The deployed server did not advertise scan_ambiguity.")

        call = await client.call_tool(
            "scan_ambiguity",
            {"text": "The deployment check might finish soon."},
        )
        result = call.structured_content or {}
        if result.get("source") != "mcp":
            raise RuntimeError("The machine invocation was not recorded as MCP.")

        print(f"Verified: {mcp_url}")
        print("Tool: scan_ambiguity")
        print(f"Request receipt: {result['request_id']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url", help="Deployed origin, such as https://example.com")
    arguments = parser.parse_args()
    asyncio.run(verify(arguments.base_url))


if __name__ == "__main__":
    main()
