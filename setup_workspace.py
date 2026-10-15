#!/usr/bin/env python3
"""Install one learner workspace using a temporary public-package download."""
import argparse
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import tempfile
from urllib.parse import quote
from urllib.request import urlopen
import zipfile


def unpack(archive, destination):
    """Validate all paths before extracting a GitHub source archive."""
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        roots = set()
        for entry in entries:
            path = PurePosixPath(entry.filename)
            if (not path.parts or path.is_absolute() or ".." in path.parts
                    or "\\" in entry.filename or ":" in entry.filename
                    or stat.S_ISLNK(entry.external_attr >> 16)):
                raise ValueError("Unsafe package archive path")
            roots.add(path.parts[0])
        if len(roots) != 1:
            raise ValueError("Expected one package directory in the archive")
        bundle.extractall(destination)
    return destination / roots.pop()


def install(destination, name, mailbox=None, preferences=None, git=True, ref="main"):
    url = "https://codeload.github.com/Matt-Salamone/invo-learn/zip/" + quote(ref, safe="")
    with tempfile.TemporaryDirectory(prefix="invo-learn-install-") as scratch:
        scratch = Path(scratch)
        archive = scratch / "package.zip"
        with urlopen(url, timeout=60) as response, archive.open("wb") as out:
            shutil.copyfileobj(response, out)
        source = unpack(archive, scratch / "source")
        # The child process needs no installed package or permanent source clone.
        import subprocess
        command = [sys.executable, "-m", "invo_learn", "bootstrap", str(Path(destination).resolve()),
                   "--name", name]
        if mailbox is not None:
            command.extend(["--mailbox", str(mailbox)])
        if preferences is not None:
            command.extend(["--preferences", str(Path(preferences).resolve())])
        if not git:
            command.append("--no-git")
        result = subprocess.run(command, cwd=source, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
        output = json.loads(result.stdout)
        # Keep a usable provenance URL after the temporary source is removed.
        activation = Path(output["workspace"]) / ".invo-learn/active.json"
        active = json.loads(activation.read_text(encoding="utf-8"))
        active["source"] = url
        activation.write_text(json.dumps(active, indent=2) + "\n", encoding="utf-8")
        return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--mailbox", type=Path)
    parser.add_argument("--preferences", type=Path)
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--ref", default="main", help="trusted public branch, tag, or commit")
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.destination, args.name, args.mailbox, args.preferences,
                                 not args.no_git, args.ref), indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
