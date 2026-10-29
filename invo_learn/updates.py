"""Read-only version checks and opt-out trusted updates before study."""
import re
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from urllib.request import urlopen

VERSION_URL = "https://raw.githubusercontent.com/Matt-Salamone/invo-learn/main/VERSION"
CHANGELOG_URL = "https://github.com/Matt-Salamone/invo-learn/blob/main/CHANGELOG.md"
TRUSTED_REPOSITORY = "https://github.com/Matt-Salamone/invo-learn.git"


def check_updates(installed):
    result = {"installed_version": installed, "version_url": VERSION_URL,
              "changelog_url": CHANGELOG_URL}
    try:
        with urlopen(VERSION_URL, timeout=5) as response:
            data = response.read(129)
        latest = data.decode("utf-8").strip()
        if len(data) > 128 or not re.fullmatch(r"\d+\.\d+\.\d+", latest):
            raise ValueError("GitHub returned an invalid package version")
        local_parts = tuple(map(int, installed.split(".")))
        latest_parts = tuple(map(int, latest.split(".")))
        status = "available" if latest_parts > local_parts else "current" if latest_parts == local_parts else "local-newer"
        return result | {"status": status, "latest_version": latest}
    except (OSError, ValueError) as exc:
        return result | {"status": "unavailable", "reason": str(exc),
                         "instruction": "Continue study with the installed version; update status is unknown."}


def study_update(ws, tid=None):
    """Fetch only the fixed trusted source; upgrade in a fresh interpreter.

    The active interpreter may be an older release. A subprocess also prevents
    module caching from mixing old code with a newly activated release.
    """
    from .engine import atomic, read_json
    from .contracts import Invalid
    prefs = ws.state["profile"]["preferences"]
    if tid:
        prefs = ws.effective_preferences(tid)
    if not prefs.get("auto_update", True):
        return {"status": "disabled"}
    if ws.pending_lessons():
        return {"status": "deferred", "reason": "Workspace handoff pending: ingest its returned report or explicitly abandon it before updating or preparing another lesson. Restage preserves the archived packet."}
    installed = read_json(ws.root / ".invo-learn/active.json")["version"]
    result = check_updates(installed)
    if result["status"] != "available":
        return result
    try:
        with tempfile.TemporaryDirectory(prefix="invo-learn-update-") as scratch:
            source = Path(scratch) / "source"
            config = subprocess.run(["git", "config", "--get-regexp", r"^url\."], cwd=scratch,
                                    capture_output=True, text=True, timeout=10)
            if config.returncode not in (0, 1) or config.stdout.strip():
                raise Invalid("Cannot verify direct trusted source: Git URL rewrites or unreadable configuration")
            fetch = subprocess.run(["git", "clone", "--config", "core.autocrlf=false", "--depth=1", "--single-branch", "--branch", "main",
                                    TRUSTED_REPOSITORY, str(source)], cwd=scratch,
                                   capture_output=True, text=True, timeout=60)
            if fetch.returncode:
                raise Invalid("Trusted release download failed: " + fetch.stderr.strip())
            # Refuse a race between the checked VERSION and the downloaded snapshot.
            if (source / "VERSION").read_text(encoding="utf-8").strip() != result["latest_version"]:
                raise Invalid("Trusted release changed during download; retry on the next preparation")
            from .install import layout_requirement, package
            migration = layout_requirement(ws, source)
            if migration is not None:
                return result | migration
            package(source)  # Validate compatibility before running trusted candidate code.
            upgraded = subprocess.run([sys.executable, "-m", "invo_learn", "--workspace", str(ws.root),
                                       "upgrade", "--source", str(source)], cwd=source,
                                      capture_output=True, text=True, timeout=60)
            if upgraded.returncode:
                raise Invalid(upgraded.stderr.strip() or "Upgrade failed")
            outcome = json.loads(upgraded.stdout)
            if outcome.get("status") == "migration-required":
                return result | outcome
            active = read_json(ws.root / ".invo-learn/active.json")
            if active["version"] != result["latest_version"]:
                raise Invalid("Upgrade activation could not be verified")
            # The temporary clone disappears; retain a usable trusted provenance.
            with ws.locked():
                active = read_json(ws.root / ".invo-learn/active.json")
                active["source"] = TRUSTED_REPOSITORY
                atomic(ws.root / ".invo-learn/active.json", active)
            return result | outcome
    except (OSError, ValueError, Invalid, subprocess.SubprocessError) as exc:
        return result | {"status": "failed", "reason": str(exc),
                         "instruction": "Records are preserved. Inspect activation and recovery guidance; continue on the installed release when safe."}
