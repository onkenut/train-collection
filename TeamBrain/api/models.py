import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, Text, Boolean, Index, ForeignKey
from sqlalchemy.orm import relationship, DeclarativeBase


def _uuid() -> str:
    return uuid.uuid4().hex


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Base(DeclarativeBase):
    pass


class Notebook(Base):
    __tablename__ = "notebooks"

    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    icon = Column(String, nullable=False, default="\U0001f4d3")
    cover_color = Column(String, nullable=False, default="#10B981")
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(String, nullable=False, default=_now)
    updated_at = Column(String, nullable=False, default=_now)

    pages = relationship("Page", back_populates="notebook", cascade="all, delete-orphan")


class Page(Base):
    __tablename__ = "pages"
    __table_args__ = (
        Index("idx_pages_notebook", "notebook_id"),
        Index("idx_pages_parent", "parent_id"),
    )

    id = Column(String, primary_key=True, default=_uuid)
    notebook_id = Column(String, ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(String, ForeignKey("pages.id", ondelete="SET NULL"), nullable=True)
    title = Column(String, nullable=False, default="Untitled")
    icon = Column(String, nullable=False, default="\U0001f4c4")
    content = Column(Text, nullable=False, default="")
    ai_summary = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    is_template = Column(Boolean, nullable=False, default=False)
    metadata_ = Column("metadata", Text, nullable=False, default="{}")
    created_at = Column(String, nullable=False, default=_now)
    updated_at = Column(String, nullable=False, default=_now)

    notebook = relationship("Notebook", back_populates="pages")
    blocks = relationship("Block", back_populates="page", cascade="all, delete-orphan",
                          order_by="Block.sort_order")
    versions = relationship("PageVersion", back_populates="page", cascade="all, delete-orphan")
    share_links = relationship("ShareLink", back_populates="page", cascade="all, delete-orphan")
    page_tags = relationship("PageTag", back_populates="page", cascade="all, delete-orphan")


class Block(Base):
    __tablename__ = "blocks"
    __table_args__ = (
        Index("idx_blocks_page", "page_id"),
        Index("idx_blocks_parent", "parent_block_id"),
    )

    id = Column(String, primary_key=True, default=_uuid)
    page_id = Column(String, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)
    content = Column(Text, nullable=False, default="")
    properties = Column(Text, nullable=False, default="{}")
    sort_order = Column(Integer, nullable=False, default=0)
    parent_block_id = Column(String, ForeignKey("blocks.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(String, nullable=False, default=_now)
    updated_at = Column(String, nullable=False, default=_now)

    page = relationship("Page", back_populates="blocks")


class PageVersion(Base):
    __tablename__ = "page_versions"
    __table_args__ = (
        Index("idx_versions_page", "page_id"),
    )

    id = Column(String, primary_key=True, default=_uuid)
    page_id = Column(String, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    snapshot = Column(Text, nullable=False)
    char_count = Column(Integer, nullable=False, default=0)
    created_at = Column(String, nullable=False, default=_now)

    page = relationship("Page", back_populates="versions")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False, unique=True)
    color = Column(String, nullable=False, default="#10B981")
    created_at = Column(String, nullable=False, default=_now)

    page_tags = relationship("PageTag", back_populates="tag", cascade="all, delete-orphan")


class PageTag(Base):
    __tablename__ = "page_tags"
    __table_args__ = (
        Index("idx_page_tags_page", "page_id"),
        Index("idx_page_tags_tag", "tag_id"),
    )

    id = Column(String, primary_key=True, default=_uuid)
    page_id = Column(String, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(String, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(String, nullable=False, default=_now)

    page = relationship("Page", back_populates="page_tags")
    tag = relationship("Tag", back_populates="page_tags")


class ShareLink(Base):
    __tablename__ = "share_links"
    __table_args__ = (
        Index("idx_share_token", "token"),
    )

    id = Column(String, primary_key=True, default=_uuid)
    page_id = Column(String, ForeignKey("pages.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, nullable=False, unique=True, default=lambda: uuid.uuid4().hex[:16])
    password = Column(String, nullable=True)
    expires_at = Column(String, nullable=True)
    created_at = Column(String, nullable=False, default=_now)

    page = relationship("Page", back_populates="share_links")


class AIUsage(Base):
    __tablename__ = "ai_usage"

    id = Column(String, primary_key=True, default=_uuid)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False, default=0)
    budget_limit = Column(Integer, nullable=False, default=1000000)
    updated_at = Column(String, nullable=False, default=_now)

    request_logs = relationship("AIRequestLog", back_populates="usage", cascade="all, delete-orphan")


class AIRequestLog(Base):
    __tablename__ = "ai_request_logs"
    __table_args__ = (
        Index("idx_ai_logs_usage", "usage_id"),
    )

    id = Column(String, primary_key=True, default=_uuid)
    usage_id = Column(String, ForeignKey("ai_usage.id"), nullable=True)
    action = Column(String, nullable=False)
    tokens_used = Column(Integer, nullable=False, default=0)
    model = Column(String, nullable=False, default="gpt-3.5-turbo")
    cached = Column(Boolean, nullable=False, default=False)
    prompt_hash = Column(String, nullable=True)
    created_at = Column(String, nullable=False, default=_now)

    usage = relationship("AIUsage", back_populates="request_logs")


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(Text, nullable=False)
    updated_at = Column(String, nullable=False, default=_now)
