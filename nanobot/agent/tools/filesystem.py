"""File system tools: read, write, edit."""

import os
from pathlib import Path
from typing import Any, List, Dict

from nanobot.agent.tools.base import Tool


def _is_subpath(target: Path, base: Path) -> bool:
    """Return True when target is inside base (or equal to base)."""
    try:
        target_norm = os.path.normcase(str(target.resolve()))
        base_norm = os.path.normcase(str(base.resolve()))
        return os.path.commonpath([target_norm, base_norm]) == base_norm
    except Exception:
        return False


def _resolve_path(path: str, allowed_dir: Path | None = None) -> Path:
    """Resolve path and optionally enforce directory restriction."""
    resolved = Path(path).expanduser().resolve()
    if allowed_dir and not _is_subpath(resolved, allowed_dir):
        raise PermissionError(f"Path {path} is outside allowed directory {allowed_dir}")
    return resolved


def _check_allowed_paths(
    resolved_path: Path,
    workspace: Path,
    allowed_paths: List[Dict[str, str]],
    mode: str = "r",
) -> None:
    """Check if resolved_path is within one of the allowed_paths entries.

    Args:
        resolved_path: Absolute resolved path to check.
        workspace: Workspace root for resolving relative allowed_paths.
        allowed_paths: List of {"path": "relative/dir/", "mode": "r"|"rw"} dicts.
        mode: Required access mode — "r" for read, "w" for write.

    Raises:
        PermissionError: If no allowed_path entry grants the required access.
    """
    if not allowed_paths:
        return  # No restrictions defined = allow all

    for entry in allowed_paths:
        entry_path = entry.get("path", "")
        entry_mode = entry.get("mode", "r")

        # Resolve allowed path relative to workspace
        abs_allowed = (workspace / entry_path).resolve()

        if _is_subpath(resolved_path, abs_allowed):
            # Path matches — check mode
            if mode == "r":
                return  # Read is always allowed if path matches
            if mode == "w" and "w" in entry_mode:
                return  # Write allowed
            raise PermissionError(
                f"Access denied: '{resolved_path.name}' is in a read-only path ({entry_path}). "
                f"Required: write, Granted: {entry_mode}"
            )

    # No matching path found
    allowed_list = ", ".join(e["path"] for e in allowed_paths)
    raise PermissionError(
        f"Access denied: path is outside allowed directories. "
        f"Allowed: [{allowed_list}]"
    )


class ReadFileTool(Tool):
    """Tool to read file contents."""

    def __init__(self, allowed_dir: Path | None = None,
                 allowed_paths: List[Dict[str, str]] | None = None,
                 workspace: Path | None = None):
        self._allowed_dir = allowed_dir
        self._allowed_paths = allowed_paths or []
        self._workspace = workspace

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file at the given path."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to read"
                }
            },
            "required": ["path"]
        }

    async def execute(self, path: str, **kwargs: Any) -> str:
        try:
            file_path = _resolve_path(path, self._allowed_dir)
            if self._allowed_paths and self._workspace:
                _check_allowed_paths(file_path, self._workspace, self._allowed_paths, mode="r")
            if not file_path.exists():
                return f"Error: File not found: {path}"
            if not file_path.is_file():
                return f"Error: Not a file: {path}"

            content = file_path.read_text(encoding="utf-8")
            return content
        except PermissionError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error reading file: {str(e)}"


class WriteFileTool(Tool):
    """Tool to write content to a file."""

    def __init__(self, allowed_dir: Path | None = None,
                 allowed_paths: List[Dict[str, str]] | None = None,
                 workspace: Path | None = None):
        self._allowed_dir = allowed_dir
        self._allowed_paths = allowed_paths or []
        self._workspace = workspace

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file at the given path. Creates parent directories if needed."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to write to"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write"
                }
            },
            "required": ["path", "content"]
        }

    async def execute(self, path: str, content: str, **kwargs: Any) -> str:
        try:
            file_path = _resolve_path(path, self._allowed_dir)
            if self._allowed_paths and self._workspace:
                _check_allowed_paths(file_path, self._workspace, self._allowed_paths, mode="w")
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            return f"Successfully wrote {len(content)} bytes to {path}"
        except PermissionError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error writing file: {str(e)}"


class EditFileTool(Tool):
    """Tool to edit a file by replacing text."""

    def __init__(self, allowed_dir: Path | None = None,
                 allowed_paths: List[Dict[str, str]] | None = None,
                 workspace: Path | None = None):
        self._allowed_dir = allowed_dir
        self._allowed_paths = allowed_paths or []
        self._workspace = workspace

    @property
    def name(self) -> str:
        return "edit_file"

    @property
    def description(self) -> str:
        return "Edit a file by replacing old_text with new_text. The old_text must exist exactly in the file."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to edit"
                },
                "old_text": {
                    "type": "string",
                    "description": "The exact text to find and replace"
                },
                "new_text": {
                    "type": "string",
                    "description": "The text to replace with"
                }
            },
            "required": ["path", "old_text", "new_text"]
        }

    async def execute(self, path: str, old_text: str, new_text: str, **kwargs: Any) -> str:
        try:
            file_path = _resolve_path(path, self._allowed_dir)
            if self._allowed_paths and self._workspace:
                _check_allowed_paths(file_path, self._workspace, self._allowed_paths, mode="w")
            if not file_path.exists():
                return f"Error: File not found: {path}"

            content = file_path.read_text(encoding="utf-8")

            if old_text not in content:
                return f"Error: old_text not found in file. Make sure it matches exactly."

            # Count occurrences
            count = content.count(old_text)
            if count > 1:
                return f"Warning: old_text appears {count} times. Please provide more context to make it unique."

            new_content = content.replace(old_text, new_text, 1)
            file_path.write_text(new_content, encoding="utf-8")

            return f"Successfully edited {path}"
        except PermissionError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error editing file: {str(e)}"


class ListDirTool(Tool):
    """Tool to list directory contents."""

    def __init__(self, allowed_dir: Path | None = None,
                 allowed_paths: List[Dict[str, str]] | None = None,
                 workspace: Path | None = None):
        self._allowed_dir = allowed_dir
        self._allowed_paths = allowed_paths or []
        self._workspace = workspace

    @property
    def name(self) -> str:
        return "list_dir"

    @property
    def description(self) -> str:
        return "List the contents of a directory."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The directory path to list"
                }
            },
            "required": ["path"]
        }

    async def execute(self, path: str, **kwargs: Any) -> str:
        try:
            dir_path = _resolve_path(path, self._allowed_dir)
            if self._allowed_paths and self._workspace:
                _check_allowed_paths(dir_path, self._workspace, self._allowed_paths, mode="r")
            if not dir_path.exists():
                return f"Error: Directory not found: {path}"
            if not dir_path.is_dir():
                return f"Error: Not a directory: {path}"

            items = []
            for item in sorted(dir_path.iterdir()):
                prefix = "📁 " if item.is_dir() else "📄 "
                items.append(f"{prefix}{item.name}")

            if not items:
                return f"Directory {path} is empty"

            return "\n".join(items)
        except PermissionError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error listing directory: {str(e)}"

