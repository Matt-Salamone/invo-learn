"""Tracked, scoped Git attributes for immutable private record bytes."""
import datetime as dt
import subprocess
import tempfile
from pathlib import Path
import uuid

from .contracts import require

ROOTS = (".invo-learn", "tracks", "lessons", "reports", "inbox", "legacy", "migrations", "migration-records",
         ".agents/skills/invo-learn", ".agents/skills/invo-learn-setup",
         ".agents/skills/invo-learn-add-course", ".agents/skills/invo-learn-add-materials",
         ".agents/skills/invo-learn-update")
FILES = (".gitattributes", "state.json", "learn.py", "AGENTS.md", "START-HERE.md")
BEGIN = b"# BEGIN invo-learn byte preservation v1\n"
END = b"# END invo-learn byte preservation v1\n"
POLICY = BEGIN + b"# Preserve exact archives and installed files across Git checkout.\n" + b"".join(
    ("/" + name + "/** -text\n").encode() for name in ROOTS) + b"".join(
    ("/" + name + " -text\n").encode() for name in FILES) + END


def protected_paths(root):
    paths = {root / name for name in FILES if (root / name).is_file()}
    for name in ROOTS:
        directory = root / name
        if directory.is_dir():
            paths.update(p for p in directory.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    return sorted(p.relative_to(root).as_posix() for p in paths)


def portable_attributes(ws, names, cached):
    """Check the same tracked/worktree rules without local info/attributes overrides."""
    with tempfile.TemporaryDirectory(prefix="invo-git-attributes-") as folder:
        base = Path(folder)
        metadata = base / "metadata.git"
        initialized = subprocess.run(["git", "-c", "init.templateDir=", "init", "--bare", "--quiet", str(metadata)], capture_output=True)
        require(initialized.returncode == 0, "cannot verify portable Git attributes")
        tree = ws.root
        if cached:
            tree = base / "tree"
            tree.mkdir()
            indexed = subprocess.run(["git", "-C", str(ws.root), "ls-files", "-z"], capture_output=True)
            require(indexed.returncode == 0, "cannot inspect staged attribute files")
            for relative in indexed.stdout.decode("utf-8").split("\x00"):
                if relative and Path(relative).name == ".gitattributes":
                    destination = tree / relative
                    require(tree in destination.resolve().parents, "unsafe staged attribute path")
                    data = subprocess.run(["git", "-C", str(ws.root), "show", ":" + relative], capture_output=True)
                    require(data.returncode == 0, "cannot read staged attribute file")
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(data.stdout)
        result = subprocess.run(["git", "--git-dir", str(metadata), "--work-tree", str(tree), "-c", "core.bare=false",
                                 "check-attr", "--stdin", "-z", "text", "filter", "working-tree-encoding", "ident"],
                                input=b"\x00".join(name.encode("utf-8") for name in names) + b"\x00", capture_output=True)
        require(result.returncode == 0, "cannot verify portable checkout attributes")
        return result.stdout


def attribute_conflicts(output):
    fields = output.decode("utf-8").split("\x00")
    conflicts = []
    for n in range(0, len(fields) - 1, 3):
        name, attribute, value = fields[n:n + 3]
        if (attribute == "text" and value != "unset") or (attribute != "text" and value not in ("unspecified", "unset")):
            conflicts.append(f"{name}: {attribute}={value}")
    return conflicts


def verify_attributes(ws, cached=False):
    """Read effective attributes, including custom nested/global rules, without rewriting them."""
    if not (ws.root / ".git").exists():
        return {"verification": "no-git-workspace", "protected_files": len(protected_paths(ws.root))}
    names = protected_paths(ws.root)
    info = subprocess.run(["git", "-C", str(ws.root), "rev-parse", "--git-path", "info/attributes"], capture_output=True, text=True)
    require(info.returncode == 0, "cannot locate local Git attributes")
    local = ws.root / info.stdout.strip()
    local_overrides = local.is_file() and any(line.strip() and not line.lstrip().startswith(b"#") for line in local.read_bytes().splitlines())
    if cached:
        policy = subprocess.run(["git", "-C", str(ws.root), "show", ":.gitattributes"], capture_output=True)
        require(policy.returncode == 0 and POLICY in policy.stdout,
                "include the reviewed .gitattributes policy in this backup scope before publishing record bytes")
    command = ["git", "-C", str(ws.root), "check-attr"] + (["--cached"] if cached else []) + ["--stdin", "-z", "text", "filter", "working-tree-encoding", "ident"]
    result = subprocess.run(command,
                            input=b"\x00".join(name.encode("utf-8") for name in names) + b"\x00", capture_output=True)
    require(result.returncode == 0, "cannot verify effective Git byte attributes: " + result.stderr.decode("utf-8", errors="replace"))
    conflicts = attribute_conflicts(result.stdout)
    if local_overrides:
        conflicts.extend(attribute_conflicts(portable_attributes(ws, names, cached)))
    require(not conflicts, "custom Git attributes conflict with exact record bytes; preserve and review the rules: " + "; ".join(conflicts[:5]))
    return {"verification": "effective-git-attributes", "protected_files": len(names)}


def verify_archives(ws, today=None):
    from .workflow import doctor
    health = doctor(ws, today or dt.date.today().isoformat())
    for check in health["checks"]:
        if check["check"] in ("durable-artifacts", "active-release"):
            require(check["status"] == "ok", "existing archive integrity failed; restore original bytes, never rehash altered archives: " + check.get("reason", ""))


def protect(ws, today=None):
    from .engine import atomic, atomic_bytes, digest
    verify_archives(ws, today)
    path = ws.root / ".gitattributes"
    before = path.read_bytes() if path.exists() else None
    if before is not None and BEGIN.strip() in before:
        require(before.count(BEGIN.strip()) == 1 and POLICY in before,
                "managed Git byte-preservation block was customized; preserve and review it before maintenance")
        return {"status": "already-protected", "attributes": ".gitattributes", **verify_attributes(ws)}
    candidate = (before or b"")
    if candidate and not candidate.endswith(b"\n"):
        candidate += b"\n"
    candidate += POLICY
    backup = None
    if before is not None:
        backup = f".invo-learn/attribute-backups/{uuid.uuid4().hex}"
        atomic_bytes(ws.path(backup + "/attributes.before"), before)
        atomic(ws.path(backup + "/manifest.json"), {"path": ".gitattributes", "before_sha256": digest(before), "after_sha256": digest(candidate)})
    try:
        atomic_bytes(path, candidate)
        verification = verify_attributes(ws)
    except BaseException:
        if before is None:
            path.unlink(missing_ok=True)
        else:
            atomic_bytes(path, before)
        raise
    return {"status": "protected", "attributes": ".gitattributes", "backup": backup, **verification}
