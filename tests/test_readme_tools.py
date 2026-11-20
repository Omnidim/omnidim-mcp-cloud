"""The README tools table is what visitors and directory reviewers read first."""

import re
from pathlib import Path

from app.routes.mcp import _tools_for_listing

README = Path(__file__).resolve().parents[1] / 'README.md'


def test_readme_lists_exactly_the_served_tools() -> None:
    sections = re.split(r'^## ', README.read_text(), flags=re.M)
    tools_section = next((s for s in sections if s.startswith('Tools')), '')
    listed = sorted(re.findall(r'`([a-z][A-Za-z]+)`', tools_section))
    served = sorted(t['name'] for t in _tools_for_listing())
    assert served
    assert listed == served
