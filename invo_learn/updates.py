"""Read-only check against the public package; no learner data or code downloads."""
import re
from urllib.request import urlopen

VERSION_URL = "https://raw.githubusercontent.com/Matt-Salamone/invo-learn/main/VERSION"
CHANGELOG_URL = "https://github.com/Matt-Salamone/invo-learn/blob/main/CHANGELOG.md"


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
