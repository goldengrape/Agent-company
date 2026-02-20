import re
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict

@dataclass
class Post:
    title: str
    description: str
    skills: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    context_prompt: str = ""
    allowed_paths: List[Dict[str, str]] = field(default_factory=list)
    # 每项格式: {"path": "workspace/reports/", "mode": "rw"} 或 {"path": "workspace/tasks/", "mode": "r"}

@dataclass
class Schema:
    doc_type_id: str
    filename_pattern: str
    target_dir: str
    template: str

class CompanyConfigLoader:
    """Loads company configuration from markdown files."""
    
    def __init__(self, workspace_path: Path, company_name: str | None = None, company_path: str | None = None):
        self.workspace = workspace_path
        self.company_name = company_name
        self.company_path = company_path
        self.base_path = self._resolve_base_path()
        self.posts: Dict[str, Post] = {}
        self.schemas: Dict[str, Schema] = {}
        self.default_post: str | None = None
        self.default_task_template: str | None = None

    def _resolve_base_path(self) -> Path:
        """Resolve the base path for company configuration."""
        # 0. Explicit path provided (e.g. private company directory)
        if self.company_path:
            return Path(self.company_path)

        # 1. Explicit name provided
        if self.company_name:
            return self.workspace / "companies" / self.company_name
        
        # 2. Check for companies/default
        default_path = self.workspace / "companies" / "default"
        if default_path.exists():
            return default_path
            
        # 3. Fallback to legacy company/
        legacy_path = self.workspace / "company"
        return legacy_path

        
    def load_all(self):
        """Load all configuration files."""
        # Try loading from SKILL.md first
        if not self._load_from_skill_def():
            # Fallback to legacy default files
            self._load_posts()
            self._load_schemas()
            
        # self._load_workflows() # Placeholder

    def _load_from_skill_def(self) -> bool:
        """
        Try to load configuration from company/SKILL.md.
        Returns True if successful, False otherwise.
        """
        skill_file = self.base_path / "SKILL.md"
        if not skill_file.exists():
            return False
            
        try:
            # Use yaml.safe_load_all to correctly parse frontmatter
            # The first document in a YAML stream is typically the frontmatter
            frontmatter = next(yaml.safe_load_all(skill_file.read_text(encoding="utf-8")), None)
            
            if not frontmatter:
                return False
                
            self.default_post = frontmatter.get("default_post")
            self.default_task_template = frontmatter.get("default_task_template")
            
            components = frontmatter.get("components") or {}
            
            # Load components based on paths in SKILL.md
            # Note: paths in SKILL.md are relative to SKILL.md location (base_path)
            
            if "posts" in components:
                posts_path = self.base_path / components["posts"]
                if posts_path.exists():
                    self._parse_posts_content(posts_path.read_text(encoding="utf-8"))
                    
            if "docs_schema" in components:
                schema_path = self.base_path / components["docs_schema"]
                if schema_path.exists():
                    self._parse_schemas_content(schema_path.read_text(encoding="utf-8"))
            
            return True
        except Exception as e:
            print(f"Error loading SKILL.md: {e}")
            return False
        
    def _load_posts(self):
        """Parse POSTS.md and populate self.posts."""
        posts_file = self.base_path / "POSTS.md"
        if not posts_file.exists():
            return
            
        content = posts_file.read_text(encoding="utf-8")
        self._parse_posts_content(content)

        
    def _load_schemas(self):
        """Parse DOCS_SCHEMA.md and populate self.schemas."""
        schema_file = self.base_path / "DOCS_SCHEMA.md"
        if not schema_file.exists():
            return
            
        content = schema_file.read_text(encoding="utf-8")
        self._parse_schemas_content(content)

    def _parse_schemas_content(self, content: str):
        """
        Parse the content of DOCS_SCHEMA.md line by line to handle nested headers in code blocks.
        """
        lines = content.split('\n')
        current_schema = None
        in_code_block = False
        template_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # Check for code block toggle
            if stripped.startswith("```"):
                if not in_code_block and "markdown" in stripped:
                    in_code_block = True
                    continue
                elif in_code_block:
                    in_code_block = False
                    # Save template to current schema
                    if current_schema:
                        current_schema.template = "\n".join(template_lines)
                    template_lines = []
                    continue

            # If inside code block, just capture content
            if in_code_block:
                template_lines.append(line)
                continue

            # If not in code block, check for Section Header `##`
            if stripped.startswith("## ") and not in_code_block:
                # Save previous schema if exists
                if current_schema:
                    self.schemas[current_schema.doc_type_id] = current_schema
                    current_schema = None
                
                # Check for ID pattern: "## 1. Title (Doc_ID)" or "## 1. Title (`Doc_ID`)"
                id_match = re.search(r'\(`?(Doc_[a-zA-Z0-9_]+)`?\)', stripped)
                if id_match:
                    doc_id = id_match.group(1)
                    current_schema = Schema(
                        doc_type_id=doc_id,
                        filename_pattern="",
                        target_dir="",
                        template=""
                    )
                continue
                
            # Metadata parsing (only if we have a current schema)
            if current_schema:
                if stripped.startswith("**文件命名**:"):
                    match = re.search(r'`([^`]+)`', stripped)
                    if match:
                        current_schema.filename_pattern = match.group(1)
                elif stripped.startswith("**位置**:"):
                    match = re.search(r'`([^`]+)`', stripped)
                    if match:
                        current_schema.target_dir = match.group(1)
                        
        # Save last schema
        if current_schema:
            self.schemas[current_schema.doc_type_id] = current_schema

    def _parse_posts_content(self, content: str):

        """
        Parse the content of POSTS.md.
        
        Expected structure:
        ### 2.1 Title (ID)
        - **Description**: ...
        - **Skills**:
          - `skill`
        - **Tools**: `tool1`, `tool2`
        - **Context**:
          > prompt
        """
        # Split by level 3 headers which denote posts
        sections = re.split(r'^###\s+', content, flags=re.MULTILINE)[1:]
        
        for section in sections:
            lines = section.strip().split('\n')
            header = lines[0].strip()
            
            # Extract ID from header: "2.1 Title (Post_ID)" -> "Post_ID"
            # Allow optional backticks
            id_match = re.search(r'\(`?(Post_[a-zA-Z0-9_]+)`?\)', header)
            if not id_match:
                continue
            post_id = id_match.group(1)
            
            # Parse body
            description = ""
            skills = []
            tools = []
            context_lines = []
            allowed_paths = []
            
            current_mode = None
            
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith("- **Description**:"):
                    description = line.replace("- **Description**:", "").strip()
                    current_mode = "description"
                elif line.startswith("- **Skills**:"):
                    current_mode = "skills"
                elif line.startswith("- **Tools**:"):
                    # Tools are usually inline: "- **Tools**: `read_file`, `write_file`."
                    tools_str = line.replace("- **Tools**:", "").strip()
                    # Extract contents of backticks
                    tools = re.findall(r'`([^`]+)`', tools_str)
                    current_mode = "tools"
                elif line.startswith("- **Allowed Paths**:"):
                    current_mode = "allowed_paths"
                elif line.startswith("- **Context**:"):
                    current_mode = "context"
                
                elif current_mode == "skills":
                    # Parse bullet points: "  - `skill-name`"
                    skill_match = re.search(r'-\s+`([^`]+)`', line)
                    if skill_match:
                        skills.append(skill_match.group(1))

                elif current_mode == "allowed_paths":
                    # Parse: "  - `workspace/reports/` (读写)" or "  - `workspace/tasks/` (只读)"
                    path_match = re.search(r'-\s+`([^`]+)`\s*\(([^)]+)\)', line)
                    if path_match:
                        raw_path = path_match.group(1)
                        raw_mode = path_match.group(2).strip()
                        # 支持中文和英文模式标记
                        if raw_mode in ('读写', 'rw', 'read-write'):
                            mode = 'rw'
                        elif raw_mode in ('只读', 'r', 'read-only', 'readonly'):
                            mode = 'r'
                        else:
                            mode = 'r'  # 默认只读
                        allowed_paths.append({"path": raw_path, "mode": mode})
                        
                elif current_mode == "context":
                    # Parse blockquotes: "> Context line"
                    if line.startswith(">"):
                        context_lines.append(line[1:].strip())
            
            self.posts[post_id] = Post(
                title=post_id,
                description=description,
                skills=skills,
                tools=tools,
                context_prompt="\n".join(context_lines),
                allowed_paths=allowed_paths
            )
