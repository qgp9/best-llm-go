#!/usr/bin/env python3
"""
.github/scripts/send_discord.py
Sends formatted deployment notifications to Discord via webhook.
Distinguishes between git commit (push) and scheduled cron runs.
"""

import json
import os
import subprocess
import urllib.request


def get_commit_info():
    """Retrieve the current commit SHA and subject line."""
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:
        sha = os.environ.get("COMMIT_SHA", "").strip()

    try:
        subject = subprocess.check_output(
            ["git", "log", "-1", "--pretty=%s"], text=True
        ).strip()
    except Exception:
        subject = ""

    return sha, subject


def build_payload():
    event_name = os.environ.get("EVENT_NAME", "").strip().lower()
    repo_name = os.environ.get("REPO_NAME", "best-llm").strip()
    server_url = os.environ.get("SERVER_URL", "https://github.com").strip()
    run_id = os.environ.get("RUN_ID", "").strip()
    run_number = os.environ.get("RUN_NUMBER", "").strip()
    deploy_page_url = os.environ.get("DEPLOY_PAGE_URL", "").strip()

    # Determine Live Site URL
    if deploy_page_url:
        site_url = deploy_page_url
    else:
        owner = repo_name.split("/")[0] if "/" in repo_name else ""
        repo = repo_name.split("/")[1] if "/" in repo_name else repo_name
        site_url = f"https://{owner}.github.io/{repo}/"

    repo_url = f"{server_url}/{repo_name}"
    action_url = (
        f"{repo_url}/actions/runs/{run_id}" if run_id else f"{repo_url}/actions"
    )

    commit_sha, commit_title = get_commit_info()
    short_sha = commit_sha[:7] if commit_sha else ""
    commit_url = f"{repo_url}/commit/{commit_sha}" if commit_sha else repo_url

    # Event-specific styling and copy
    if event_name == "schedule":
        title = "⏰ [Schedule] Deployment Complete"
        desc = "Daily scheduled benchmark & model catalog sync."
        color = 0x3B82F6  # Blue
    elif event_name == "push":
        title = "📦 [Commit] Deployment Complete"
        desc = "New commit deployed to GitHub Pages."
        color = 0xD97757  # Brand Terracotta
    else:
        event_label = event_name.capitalize() if event_name else "Manual"
        title = f"⚡ [{event_label}] Deployment Complete"
        desc = "Workflow deployment complete."
        color = 0x10B981  # Emerald

    # Exactly requested fields:
    # 1. 사이트링크 2. GitHub 링크 3. Action 링크 4. 커밋이면 커밋 아이디/제목/링크 (스케줄이면 스케줄 정보)
    fields = [
        {
            "name": "🌐 Live Site",
            "value": f"[OpenCode & Free LLM Intel]({site_url})",
            "inline": False,
        },
        {"name": "📂 GitHub", "value": f"[{repo_name}]({repo_url})", "inline": True},
        {
            "name": "⚙️ Action Run",
            "value": f"[Run #{run_number}]({action_url})"
            if run_number
            else f"[View Run]({action_url})",
            "inline": True,
        },
    ]

    if event_name == "push":
        fields.append({
            "name": "📝 Commit",
            "value": (
                f"[`{short_sha}`]({commit_url}) {commit_title}".strip()
                if short_sha
                else (commit_title or "No commit details")
            ),
            "inline": False,
        })
    elif event_name == "schedule":
        fields.append({
            "name": "⏰ Schedule",
            "value": "Daily Sync (09:37 UTC)",
            "inline": False,
        })
    else:
        fields.append({
            "name": "⚡ Trigger",
            "value": f"Manual ({event_name or 'dispatch'})",
            "inline": False,
        })

    return {
        "embeds": [{
            "title": title,
            "description": desc,
            "color": color,
            "fields": fields,
            "footer": {"text": "100% Vibe-Coded with AI • Antigravity & Gemini"},
        }]
    }


def main():
    webhook_url = os.environ.get("DISCORD_WEBHOOK", "").strip()
    if not webhook_url:
        print(
            "DISCORD_WEBHOOK secret is not set. Skipping Discord notification."
        )
        return

    payload = build_payload()
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "GitHub-Actions-Discord-Notification",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(
                f"Discord notification sent successfully (HTTP {resp.status})."
            )
    except Exception as e:
        print(f"Failed to send Discord notification (non-critical): {e}")


if __name__ == "__main__":
    main()
