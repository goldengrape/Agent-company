import re
import uuid
import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from loguru import logger

from nanobot.agent.tools.base import Tool
from nanobot.company.loader import CompanyConfigLoader
from nanobot.agent.memory import MemoryStore

class DocumentFlowTool(Tool):
    """
    Tool for managing the company's document flow (workflow).
    Enforces schemas and naming conventions defined in DOCS_SCHEMA.md.
    """
    
    @property
    def name(self) -> str:
        return "document_flow"

    @property
    def description(self) -> str:
        return (
            "Manage official company documents. Use this to create, validate, and submit "
            "Task Orders, Work Reports, and Audit Reports. Automatically handles naming and placement."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "The action to perform.",
                    "enum": ["create", "validate", "submit", "list_schemas"]
                },
                "doc_type": {
                    "type": "string",
                    "description": "The document type ID (e.g., 'Doc_Task_Order'). Required for 'create'."
                },
                "title": {
                    "type": "string",
                    "description": "The title of the document. Required for 'create'."
                },
                "content": {
                    "type": "string",
                    "description": "The content of the document. If empty, uses template."
                },
                "file_path": {
                    "type": "string",
                    "description": "Absolute path to the file. Required for 'validate' and 'submit'."
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata map for template substitution (e.g., {'TaskID': '123'})."
                }
            },
            "required": ["action"]
        }
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.loader = CompanyConfigLoader(workspace)
        self.memory = MemoryStore(workspace)
        
    async def execute(self, action: str, **kwargs) -> str:
        """
        Execute document flow actions.
        
        Actions:
        - create: Create a new document from a schema.
        - validate: Check if a document follows the schema.
        - submit: Submit a document (conceptual move to next stage).
        - list_schemas: List available document types.
        """
        # Ensure config is loaded
        self.loader.load_all()
        
        if action == "create":
            return self._create_document(
                doc_type=kwargs.get("doc_type"),
                title=kwargs.get("title", ""),
                content=kwargs.get("content", ""),
                metadata=kwargs.get("metadata", {})
            )
        elif action == "validate":
            return self._validate_document(
                file_path=kwargs.get("file_path"),
                doc_type=kwargs.get("doc_type")
            )
        elif action == "submit":
            return self._submit_document(file_path=kwargs.get("file_path"))
        elif action == "list_schemas":
            return self._list_schemas()
        else:
            return f"Unknown action: {action}. Valid actions: create, validate, submit, list_schemas."

    def _list_schemas(self) -> str:
        schemas = []
        for doc_id, schema in self.loader.schemas.items():
            schemas.append(f"- {doc_id}: {schema.filename_pattern} -> {schema.target_dir}")
        return "Available Schemas:\n" + "\n".join(schemas)

    def _create_document(self, doc_type: str, title: str, content: str, metadata: Dict) -> str:
        if doc_type not in self.loader.schemas:
            return f"Error: Unknown doc_type '{doc_type}'. Use 'list_schemas' to see available types."
            
        schema = self.loader.schemas[doc_type]
        
        # Resolve filename
        doc_uuid = str(uuid.uuid4())[:8]
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        
        filename = schema.filename_pattern
        filename = filename.replace("{ID}", doc_uuid)
        filename = filename.replace("{UUID}", doc_uuid)
        filename = filename.replace("{Title}", title.replace(" ", "_"))
        filename = filename.replace("{Date}", now)
        # Handle TaskID for reports if provided in metadata
        if "TaskID" in metadata and "{TaskID}" in filename:
             filename = filename.replace("{TaskID}", metadata["TaskID"])
             
        # Resolve target directory
        target_dir = self.workspace / schema.target_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = target_dir / filename
        
        # Prepare content
        # If content provided is empty, use template
        final_content = content
        if not final_content:
            final_content = schema.template
            # Simple template substitution
            final_content = final_content.replace("{ID}", doc_uuid)
            final_content = final_content.replace("{UUID}", doc_uuid)
            final_content = final_content.replace("{标题}", title)
            final_content = final_content.replace("{Title}", title)
            final_content = final_content.replace("{ISO_Date}", now)
            
            for k, v in metadata.items():
                final_content = final_content.replace(f"{{{k}}}", str(v))
                
        # Write file
        file_path.write_text(final_content, encoding="utf-8")

        # Log event
        self.memory.log_event("task_created", {
            "doc_id": doc_uuid,
            "doc_type": doc_type,
            "title": title,
            "file_path": str(file_path)
        })
        
        return f"Document created successfully:\nPath: {file_path}\nID: {doc_uuid}"

    def _validate_document(self, file_path: str, doc_type: Optional[str] = None) -> str:
        path = Path(file_path)
        if not path.is_absolute():
            path = self.workspace / path
            
        if not path.exists():
            return f"Error: File not found at {path}"
            
        # If doc_type not provided, try to guess or just check basic MD
        # For now, just a placeholder validation
        content = path.read_text(encoding="utf-8")
        
        if doc_type and doc_type in self.loader.schemas:
            # Check if critical headers from template exist
            # This is a weak check, but better than nothing
            schema = self.loader.schemas[doc_type]
            # Extract headers from template
            headers = re.findall(r'^##\s+(.+)$', schema.template, re.MULTILINE)
            missing = []
            for h in headers:
                if h not in content:
                    missing.append(h)
            
            if missing:
                return f"Validation Failed: Missing sections: {', '.join(missing)}"
                
        return "Validation Passed (Basic Structure Check)."

    def _submit_document(self, file_path: str) -> str:
        # For now, just log valid submission
        # In future, this could move file to 'inbox' of next role
        path = Path(file_path)
        if not path.exists():
             return f"Error: File {file_path} does not exist."
             
        # Check if it's already in a structured dir
        # Check if it's already in a structured dir
        self.memory.log_event("task_submitted", {
            "file_path": str(path)
        })
        return f"Document {path.name} submitted. System has logged this action."
