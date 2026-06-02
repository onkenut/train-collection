from __future__ import annotations

from typing import Optional, Any
from pydantic import BaseModel, Field


class NotebookCreate(BaseModel):
    name: str
    icon: str = "\U0001f4d3"
    cover_color: str = "#10B981"


class NotebookUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    cover_color: Optional[str] = None


class NotebookOut(BaseModel):
    id: str
    name: str
    icon: str
    cover_color: str
    sort_order: int
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class ReorderItem(BaseModel):
    id: str
    sort_order: int


class ReorderRequest(BaseModel):
    items: list[ReorderItem]


class PageCreate(BaseModel):
    title: str = "Untitled"
    icon: str = "\U0001f4c4"
    parent_id: Optional[str] = None
    is_template: bool = False
    metadata: dict[str, str] = Field(default_factory=dict)


class PageUpdate(BaseModel):
    title: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[str] = None
    is_template: Optional[bool] = None
    metadata: Optional[dict[str, str]] = None


class PageMove(BaseModel):
    notebook_id: str
    parent_id: Optional[str] = None
    sort_order: Optional[int] = None


class PageOut(BaseModel):
    id: str
    notebook_id: str
    parent_id: Optional[str]
    title: str
    icon: str
    content: str = ""
    sort_order: int
    is_template: bool
    metadata: dict[str, str]
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class BlockCreate(BaseModel):
    type: str
    content: str = ""
    properties: dict[str, Any] = Field(default_factory=dict)
    parent_block_id: Optional[str] = None
    sort_order: int = 0


class BlockUpdate(BaseModel):
    type: Optional[str] = None
    content: Optional[str] = None
    properties: Optional[dict[str, Any]] = None
    parent_block_id: Optional[str] = None
    sort_order: Optional[int] = None


class BlockOut(BaseModel):
    id: str
    page_id: str
    type: str
    content: str
    properties: dict[str, Any]
    sort_order: int
    parent_block_id: Optional[str]
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class PageSaveRequest(BaseModel):
    title: Optional[str] = None
    icon: Optional[str] = None
    content: Optional[str] = None
    blocks: list[BlockCreate] = []


class TagCreate(BaseModel):
    name: str
    color: str = "#10B981"


class TagOut(BaseModel):
    id: str
    name: str
    color: str
    created_at: str

    model_config = {"from_attributes": True}


class TagAssociate(BaseModel):
    tag_id: Optional[str] = None
    tag_name: Optional[str] = None
    color: str = "#10B981"


class ShareLinkCreate(BaseModel):
    password: Optional[str] = None
    expires_at: Optional[str] = None


class ShareLinkOut(BaseModel):
    id: str
    page_id: str
    token: str
    password: Optional[str]
    expires_at: Optional[str]
    created_at: str

    model_config = {"from_attributes": True}


class ShareAccessRequest(BaseModel):
    password: Optional[str] = None


class AIRequest(BaseModel):
    action: str = Field(..., pattern="^(continue|summarize|rewrite|translate|brainstorm)$")
    content: str
    context: Optional[str] = None
    params: Optional[dict[str, Any]] = None


class AIResponse(BaseModel):
    id: str
    generated_text: str
    tokens_used: int
    cached: bool


class AIUsageOut(BaseModel):
    month: int
    year: int
    total_tokens: int
    budget_limit: int


class AIConfigUpdate(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    monthly_budget: Optional[int] = None


class AIConfigOut(BaseModel):
    api_key: str
    base_url: str
    model: str
    monthly_budget: int


class VersionOut(BaseModel):
    id: str
    page_id: str
    snapshot: str
    char_count: int
    created_at: str

    model_config = {"from_attributes": True}


class VersionDiffOut(BaseModel):
    source_version_id: str
    target_version_id: str
    diff: list[str]


class SearchResult(BaseModel):
    page_id: str
    page_title: str
    notebook_id: str
    notebook_name: str
    snippet: str
    rank: float


class SearchResponse(BaseModel):
    results: list[SearchResult]
    total: int


class SyncPageItem(BaseModel):
    id: str
    title: str
    blocks: list[BlockCreate]
    updated_at: str
    checksum: str


class SyncPayload(BaseModel):
    pages: list[SyncPageItem]


class SyncChangeItem(BaseModel):
    id: str
    title: str
    updated_at: str
    action: str


class SyncChangesResponse(BaseModel):
    changes: list[SyncChangeItem]
    since: str


class FileUploadOut(BaseModel):
    id: str
    filename: str
    mime_type: str
    size: int
    url: str


class ExportTaskOut(BaseModel):
    task_id: str
    status: str
    download_url: Optional[str] = None
