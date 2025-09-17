import asyncio
import os
from typing import Any, Dict

import argparse
import httpx


def resolve_server_url() -> str:
    env_url = os.getenv("MCP_SERVER_URL")
    if env_url:
        return env_url
    return "https://ca3eda3eb9a9.ngrok-free.app"


async def call_send_gmail(server_url: str, name: str, email: str) -> Dict[str, Any]:
    url = f"{server_url.rstrip('/')}/tools/send_gmail"
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(url, json={"name": name, "email": email})
        response.raise_for_status()
        return response.json()


async def discover_tools(server_url: str) -> Dict[str, Any]:
    url = f"{server_url.rstrip('/')}/mcp/tools"
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def main() -> None:
    parser = argparse.ArgumentParser(description="MCP client: discover and call tools dynamically")
    parser.add_argument("--server-url", dest="server_url", default=resolve_server_url())
    parser.add_argument("--tool", dest="tool_name", default="send_gmail")
    parser.add_argument("--name", dest="name", default="John Doe")
    parser.add_argument("--email", dest="email", default="john.doe@example.com")
    args = parser.parse_args()

    # Discover available tools first
    discovery = await discover_tools(args.server_url)
    tools = {t["name"]: t for t in discovery.get("tools", [])}
    if args.tool_name not in tools:
        raise SystemExit(f"Tool '{args.tool_name}' not found. Available: {', '.join(tools.keys())}")

    selected = tools[args.tool_name]
    if selected["name"] == "send_gmail":
        result = await call_send_gmail(server_url=args.server_url, name=args.name, email=args.email)
    else:
        raise SystemExit(f"No caller implemented for tool '{selected['name']}'")

    print(result)


if __name__ == "__main__":
    asyncio.run(main())


