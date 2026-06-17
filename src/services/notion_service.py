"""
ARA - Notion Save Service
"""
import os
import re
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

try:
    from notion_client import Client
    _NOTION_AVAILABLE = True
except ImportError:
    _NOTION_AVAILABLE = False

def _get_client():
    if not _NOTION_AVAILABLE:
        return None
    token = os.getenv("NOTION_TOKEN")
    return Client(auth=token) if token else None

def _parse_inline(text: str) -> List[Dict]:
    parts = re.split(r"(\*\*[^*]+\*\*)", text)
    out = []
    for p in parts:
        if p.startswith("**") and p.endswith("**"):
            out.append({"type": "text", "text": {"content": p[2:-2]}, "annotations": {"bold": True}})
        else:
            out.append({"type": "text", "text": {"content": p}})
    return out

def _parse_blocks(md: str) -> List[Dict]:
    blocks = []
    for line in md.split("\n"):
        s = line.strip()
        if not s:
            continue
        if s.startswith("## ") or s.startswith("【"):
            t = s[3:] if s.startswith("## ") else s.strip("【】")
            blocks.append({"type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": t}}]}})
        elif s.startswith("### "):
            blocks.append({"type": "heading_3", "heading_3": {"rich_text": [{"type": "text", "text": {"content": s[4:]}}]}})
        elif s in ("---", "***"):
            blocks.append({"type": "divider", "divider": {}})
        elif s.startswith("- ") or s.startswith("• "):
            blocks.append({"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": _parse_inline(s[2:])}})
        elif re.match(r"^\d+\.\s+", s):
            blocks.append({"type": "numbered_list_item", "numbered_list_item": {"rich_text": _parse_inline(re.sub(r"^\d+\.\s+", "", s))}})
        elif s.startswith("> "):
            blocks.append({"type": "quote", "quote": {"rich_text": [{"type": "text", "text": {"content": s[2:]}}]}})
        else:
            blocks.append({"type": "paragraph", "paragraph": {"rich_text": _parse_inline(s)}})
    return blocks

def _chunk(blocks: List[Dict], n: int = 100):
    return [blocks[i:i+n] for i in range(0, len(blocks), n)]

def save_to_notion(title: str, markdown: str, parent_page_id: Optional[str] = None) -> Dict[str, Any]:
    client = _get_client()
    if not client:
        return {"success": False, "notion_url": None, "error": "Notion 未配置"}
    if not parent_page_id:
        parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID")
    if not parent_page_id:
        return {"success": False, "notion_url": None, "error": "Notion 父页面 ID 未配置"}
    try:
        blocks = _parse_blocks(markdown)
        if not blocks:
            return {"success": False, "notion_url": None, "error": "内容为空"}
        batches = _chunk(blocks)
        page = client.pages.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            properties={"title": {"title": [{"type": "text", "text": {"content": title}}]}},
            children=batches[0],
        )
        pid = page["id"]
        url = page.get("url", f"https://notion.so/{pid.replace('-', '')}")
        for b in batches[1:]:
            client.blocks.children.append(block_id=pid, children=b)
        return {"success": True, "notion_url": url, "error": None}
    except Exception as e:
        msg = str(e)
        if "401" in msg or "unauthorized" in msg.lower():
            return {"success": False, "notion_url": None, "error": "Notion Token 无效"}
        if "403" in msg or "restricted" in msg.lower():
            return {"success": False, "notion_url": None, "error": "Integration 未授权访问目标页面"}
        return {"success": False, "notion_url": None, "error": f"Notion API 错误: {msg[:200]}"}
