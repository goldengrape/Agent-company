from pathlib import Path
from unittest.mock import MagicMock

import pytest

from nanobot.agent.subagent import SubagentManager
from nanobot.agent.tools.filesystem import _check_allowed_paths, _resolve_path
from nanobot.agent.tools.registry import ToolRegistry
from nanobot.company.loader import Post


def test_resolve_path_blocks_prefix_bypass(tmp_path: Path):
    allowed_dir = tmp_path / "workspace" / "reports"
    allowed_dir.mkdir(parents=True)

    inside = allowed_dir / "ok.txt"
    assert _resolve_path(str(inside), allowed_dir) == inside.resolve()

    # reports2 must NOT be treated as a child of reports
    bypass = tmp_path / "workspace" / "reports2" / "secret.txt"
    with pytest.raises(PermissionError):
        _resolve_path(str(bypass), allowed_dir)


def test_allowed_paths_blocks_prefix_bypass(tmp_path: Path):
    workspace = tmp_path
    allowed_root = workspace / "workspace" / "reports"
    allowed_root.mkdir(parents=True)

    # Allowed nested path
    nested = allowed_root / "team" / "report.md"
    nested.parent.mkdir(parents=True)
    _check_allowed_paths(
        nested.resolve(),
        workspace,
        [{"path": "workspace/reports/", "mode": "r"}],
        mode="r",
    )

    # Disallow sibling path with shared prefix (reports2)
    sibling = workspace / "workspace" / "reports2" / "report.md"
    with pytest.raises(PermissionError):
        _check_allowed_paths(
            sibling.resolve(),
            workspace,
            [{"path": "workspace/reports/", "mode": "r"}],
            mode="r",
        )


def test_subagent_tools_fail_closed_for_empty_post_tools(tmp_path: Path):
    provider = MagicMock()
    provider.get_default_model.return_value = "gpt-4"
    bus = MagicMock()
    manager = SubagentManager(provider=provider, workspace=tmp_path, bus=bus)

    post = Post(
        title="Post_Empty",
        description="no tools",
        skills=[],
        tools=[],
        context_prompt="",
        allowed_paths=[],
    )

    registry = ToolRegistry()
    manager._register_tools(registry, post)
    assert registry.tool_names == []

