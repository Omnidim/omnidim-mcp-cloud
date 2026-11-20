"""Hosted MCP server for OmniDimension."""
from importlib.metadata import version

# The only version source is pyproject.toml, which the release PR bumps.
__version__ = version("omnidim-mcp-cloud")
