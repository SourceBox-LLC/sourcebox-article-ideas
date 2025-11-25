import os
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY") or os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
NOTION_VERSION = os.getenv("NOTION_VERSION", "2022-06-28")

_title_property_name: Optional[str] = None


def _chunk_text(text: str, chunk_size: int = 1800) -> List[str]:
    if not text:
        return [""]
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def is_notion_configured() -> bool:
    return bool(NOTION_API_KEY and NOTION_DATABASE_ID)


def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def _get_title_property_name() -> Optional[str]:
    global _title_property_name

    if _title_property_name is not None:
        return _title_property_name

    if not is_notion_configured():
        return None

    try:
        response = requests.get(
            f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}",
            headers=_headers(),
            timeout=20,
        )
    except Exception as exc:
        print(f"Error fetching Notion database schema: {exc}")
        return None

    if response.status_code >= 400:
        print(
            f"Failed to fetch Notion database schema: {response.status_code} {response.text}"
        )
        return None

    data = response.json()
    properties = data.get("properties", {})
    for name, prop in properties.items():
        if prop.get("type") == "title":
            _title_property_name = name
            return _title_property_name

    print("No title property found in Notion database.")
    return None


def create_notion_page_for_draft(draft: Dict[str, Any]) -> None:
    if not is_notion_configured():
        print(
            "Notion not configured (missing NOTION_API_KEY or NOTION_DATABASE_ID); skipping Notion sync."
        )
        return

    title_property = _get_title_property_name()
    if not title_property:
        print("Could not determine Notion database title property; skipping Notion sync.")
        return

    title = draft.get("title") or "Untitled draft"
    description = draft.get("description") or ""
    content = draft.get("content") or ""

    children: List[Dict[str, Any]] = []

    if description:
        children.append(
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Description"},
                        }
                    ]
                },
            }
        )
        for chunk in _chunk_text(description):
            children.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": chunk},
                            }
                        ]
                    },
                }
            )

    if content:
        children.append(
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Draft"},
                        }
                    ]
                },
            }
        )
        for chunk in _chunk_text(content):
            children.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": chunk},
                            }
                        ]
                    },
                }
            )

    payload: Dict[str, Any] = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            title_property: {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": title},
                    }
                ]
            }
        },
    }

    if children:
        payload["children"] = children

    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            json=payload,
            headers=_headers(),
            timeout=20,
        )
        if response.status_code >= 400:
            print(
                f"Failed to create Notion page for '{title}': {response.status_code} {response.text}"
            )
        else:
            data = response.json()
            page_id = data.get("id")
            print(f"Created Notion page for '{title}' (page id: {page_id})")
    except Exception as exc:
        print(f"Error creating Notion page for '{title}': {exc}")
