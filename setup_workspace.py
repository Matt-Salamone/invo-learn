#!/usr/bin/env python3
"""Install or explicitly upgrade one learner workspace using a temporary trusted download."""
import argparse
import json
import os
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


def install(destination, name=None, mailbox=None, preferences=None, git=True, ref="main", upgrade_existing=False):
    if not upgrade_existing and not name:
        raise ValueError("name is required for a new workspace")
    url = "https://codeload.github.com/Matt-Salamone/invo-learn/zip/" + quote(ref, safe="")
    with tempfile.TemporaryDirectory(prefix="invo-learn-install-") as scratch:
        scratch = Path(scratch)
        archive = scratch / "package.zip"
        with urlopen(url, timeout=60) as response, archive.open("wb") as out:
            shutil.copyfileobj(response, out)
        source = unpack(archive, scratch / "source")
        # The child process needs no installed package or permanent source clone.
        import subprocess
        destination = Path(destination).resolve()
        command = ([sys.executable, "-m", "invo_learn", "--workspace", str(destination), "upgrade", "--source", str(source)]
                   if upgrade_existing else [sys.executable, "-m", "invo_learn", "bootstrap", str(destination), "--name", name])
        if not upgrade_existing and mailbox is not None:
            command.extend(["--mailbox", str(mailbox)])
        if not upgrade_existing and preferences is not None:
            command.extend(["--preferences", str(Path(preferences).resolve())])
        if not upgrade_existing and not git:
            command.append("--no-git")
        result = subprocess.run(command, cwd=source, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
        output = json.loads(result.stdout)
        # Keep a usable provenance URL after the temporary source is removed.
        if not upgrade_existing or output.get("status") in ("upgraded", "already-current"):
            activation = destination / ".invo-learn/active.json"
            active = json.loads(activation.read_text(encoding="utf-8"))
            active["source"] = url
            with tempfile.NamedTemporaryFile(dir=activation.parent, delete=False) as pending:
                pending.write((json.dumps(active, indent=2) + "\n").encode("utf-8"))
                pending.flush()
                os.fsync(pending.fileno())
                temporary = Path(pending.name)
            try:
                os.replace(temporary, activation)
            finally:
                temporary.unlink(missing_ok=True)
        return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--name")
    parser.add_argument("--upgrade", action="store_true", help="explicitly upgrade an existing workspace using the temporary trusted source")
    parser.add_argument("--mailbox", type=Path)
    parser.add_argument("--preferences", type=Path)
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--ref", default="main", help="trusted public branch, tag, or commit")
    args = parser.parse_args()
    if not args.upgrade and not args.name:
        parser.error("--name is required for a new workspace")
    if args.upgrade and (args.name or args.mailbox or args.preferences or args.no_git):
        parser.error("--upgrade preserves existing setup choices; omit new-workspace options")
    try:
        print(json.dumps(install(args.destination, args.name, args.mailbox, args.preferences,
                                 not args.no_git, args.ref, args.upgrade), indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
