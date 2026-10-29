"""Explicit, private, lossless rehearsals. Activation is a separate operation."""
import copy
import contextlib
import json
import os
from pathlib import Path
import shutil
import subprocess

from .contracts import fields, identifier, require
from .engine import Workspace, atomic, digest, no_links, read_json, within
from .legacy import read_snapshot


PRESENTATION = "Presentation override for newly issued lessons: self-contained teaching with no source commentary; retain provenance for explicit requests"


@contextlib.contextmanager
def stage_locked(stage):
    """Serialize explicit stage mutations outside its workspace inventory."""
    root = no_links(stage).resolve()
    path = root / "migration.lock"
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        from .contracts import Invalid
        raise Invalid("migration stage busy; verify no process is running before recovering a stale migration.lock") from exc
    try:
        os.write(fd, str(os.getpid()).encode())
        yield root
    finally:
        os.close(fd)
        path.unlink(missing_ok=True)


def origin_key(snapshot):
    return snapshot.kind + "-" + digest((snapshot.kind + ":" + snapshot.origin["id"]).encode())[:20]


def inventory(root):
    root = no_links(root).resolve()
    require(root.is_dir(), "inventory source directory is missing")
    files, directories = {}, []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_file():
            data = path.read_bytes()
            files[relative] = {"sha256": digest(data), "bytes": len(data)}
        elif path.is_dir():
            directories.append(relative)
        else:
            require(False, "unsupported filesystem entry: " + relative)
    return {"files": files, "directories": directories}


def check_history(root):
    """Full standalone Git directories can be copied without external dependencies."""
    for metadata in sorted({root / ".git", *root.rglob(".git")}):
        if not metadata.exists():
            continue
        require(metadata.is_dir(), "linked-worktree .git indirection requires a complete independent private repository copy before rehearsal")
        require(not (metadata / "commondir").exists() and not (metadata / "shallow").exists(),
                "shared or shallow Git history requires a complete independent private repository copy before rehearsal")
        alternates = metadata / "objects/info/alternates"
        require(not alternates.exists() or not alternates.read_text(encoding="utf-8").strip(),
                "Git object alternates require a complete independent private repository copy before rehearsal")
        checked = subprocess.run(["git", "--git-dir", str(metadata), "fsck", "--full", "--no-reflogs"],
                                 capture_output=True, text=True)
        require(checked.returncode == 0, "source Git history integrity check failed: " + checked.stderr.strip())


def _copy_tree(source, destination, include_git=True):
    require(not destination.exists(), "preserved destination already exists: " + str(destination))
    ignored = None if include_git else shutil.ignore_patterns(".git")
    shutil.copytree(source, destination, ignore=ignored)


def _canonical_materials(workspace, state, snapshot, key, tid):
    associations = {}
    materials = state["tracks"][tid]["materials"]
    for source in snapshot.state.get("intake", {}).get("sources", []):
        if not source.get("original"):
            continue  # Unavailable/external metadata remains in the exact legacy archive.
        mid = "legacy-" + digest((key + ":material:" + source["id"]).encode())[:20]
        require(mid not in materials, "origin-scoped legacy material ID collision")
        original = snapshot.path(source["original"])
        relative = f"tracks/{tid}/materials/originals/{mid}/{original.name}"
        destination = workspace / relative
        require(not destination.exists(), "legacy material destination conflicts with existing work")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(original.read_bytes())
        derived = []
        for cid, conversion in snapshot.state.get("conversions", {}).items():
            if conversion.get("source_id") != source["id"] or conversion.get("status") != "complete":
                continue
            output = snapshot.path(conversion["output"])
            did = "legacy-" + digest((key + ":conversion:" + cid).encode())[:20]
            output_relative = f"tracks/{tid}/materials/derived/{did}/{output.name}"
            target = workspace / output_relative
            require(not target.exists(), "legacy derivative destination conflicts with existing work")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(output.read_bytes())
            derived.append({"id": did, "path": output_relative, "sha256": digest(output.read_bytes()),
                            "approval_id": None, "note": "Preserved completed legacy conversion; actual consent retained in legacy archive",
                            "legacy_conversion": copy.deepcopy(conversion)})
        materials[mid] = {"id": mid, "name": original.name, "original": relative,
            "sha256": digest(original.read_bytes()), "role": "primary" if source["kind"] == "course" else "supplemental",
            "status": "usable" if source["status"] == "usable" or derived else "needs-transformation",
            "usability_note": "Preserved legacy intake status; see origin record",
            "derived": derived, "approvals": [], "origin": {"key": key, "source_id": source["id"], "reference": source["reference"]}}
        associations[source["id"]] = mid
    return associations


def _import_assignment(workspace, state, snapshot, key, tid):
    aid = "legacy-" + digest((key + ":assignment").encode())[:20]
    track = state["tracks"][tid]
    require(aid not in track.get("assignments", {}), "origin-scoped legacy assignment ID collision")
    archive = "legacy/" + key
    _copy_tree(snapshot.root, workspace / archive, include_git=False)
    material_ids = _canonical_materials(workspace, state, snapshot, key, tid)
    intake = snapshot.state.get("intake", {})
    specification = {"title": snapshot.state.get("name", "Legacy assignment"),
                     "requirements": copy.deepcopy(intake.get("constraints", [])),
                     "deliverables": copy.deepcopy(intake.get("deliverables", [])),
                     "criteria": copy.deepcopy(intake.get("grading_criteria", [])),
                     "material_ids": list(material_ids.values())}
    path = f"tracks/{tid}/assignments/{aid}/assignment.json"
    require(not (workspace / path).exists(), "legacy assignment requirements conflict with existing work")
    atomic(workspace / path, specification)
    record = {"id": aid, "track_id": tid, "spec": specification, "path": path,
              "sha256": digest((workspace / path).read_bytes()), "solution_choice": None,
              "plans": {}, "active_plan": None, "completion": "not-started",
              "legacy_context": {"origin_key": key, "assignment_id": snapshot.state["assignment_id"],
                  "origin_commit": snapshot.origin["commit"], "state_path": archive + "/.invo/state.json",
                  "solution_revision": snapshot.state.get("solution", {}).get("revision"),
                  "historical_exposure": "Existing reference retained; no new solution decision inferred",
                  "progress": copy.deepcopy(snapshot.state.get("plan", {})),
                  "evidence": copy.deepcopy(snapshot.state.get("evidence", []))}}
    track.setdefault("assignments", {})[aid] = record
    return {"track_id": tid, "assignment_id": aid, "material_ids": material_ids,
            "archive": archive, "original_assignment_id": snapshot.state["assignment_id"]}


def load_rehearsal(stage):
    root = no_links(stage).resolve()
    manifest = read_json(root / "migration-manifest.json")
    require(type(manifest.get("schema_version")) is int and manifest["schema_version"] == 1
            and isinstance(manifest.get("id"), str) and manifest["id"], "unsupported migration manifest")
    return root, manifest


def stage_path(root, relative):
    require(isinstance(relative, str) and relative and not Path(relative).is_absolute(),
            "rehearsal artifact path must be relative")
    path = (root / relative).resolve()
    require(within(path, root) and path != root, "artifact path escapes rehearsal")
    return no_links(path)


def verify_rehearsal(stage, verify_sources=True, verify_workspace=True):
    root, manifest = load_rehearsal(stage)
    for source in manifest["sources"].values():
        snapshot = stage_path(root, source["snapshot"])
        require(inventory(snapshot) == source["inventory"], "preserved source inventory/hash mismatch")
        if verify_sources:
            require(inventory(Path(source["source"])) == source["inventory"], "source changed since rehearsal; rehearse again before activation")
        if source.get("external_mailbox"):
            mailbox = source["external_mailbox"]
            require(inventory(stage_path(root, mailbox["snapshot"])) == mailbox["inventory"], "preserved external mailbox inventory/hash mismatch")
            if verify_sources:
                require(inventory(Path(mailbox["source"])) == mailbox["inventory"], "external mailbox changed since rehearsal")
    if verify_workspace:
        require(inventory(stage_path(root, manifest["workspace"])) == manifest["workspace_inventory"],
                "staged workspace inventory/hash mismatch; inspect staged changes")
    from .migration_projection import projection_current
    current_projection = (projection_current(Workspace(stage_path(root, manifest["workspace"])), manifest, root)
                          if verify_workspace else False)
    return {"status": "verified", "migration_id": manifest["id"], "activated": False,
            "stage": str(root), "workspace": str(stage_path(root, manifest["workspace"])),
            "destination": manifest["destination"], "manifest": manifest, "projection_current": current_projection}


def save_rehearsal(stage, manifest):
    """Later explicit projection/reconciliation operations record their new stage."""
    root = no_links(stage).resolve()
    manifest["workspace_inventory"] = inventory(stage_path(root, manifest["workspace"]))
    atomic(root / "migration-manifest.json", manifest)


def rehearse(plan):
    fields(plan, ("destination", "assignments", "stage"))
    require(isinstance(plan["assignments"], list), "assignments must be a list of source/course associations")
    destination = read_snapshot(plan["destination"])
    require(destination.kind == "course", "migration destination basis must be an existing course workspace")
    stage = no_links(plan["stage"]).resolve()
    requested = [(destination, None)]
    for selection in plan["assignments"]:
        fields(selection, ("source", "track_id"))
        identifier(selection["track_id"])
        require(selection["track_id"] in destination.state["tracks"], "associate the assignment with an existing destination course")
        snapshot = read_snapshot(selection["source"])
        require(snapshot.kind == "assignment", "assignment source must contain historical assignment state")
        requested.append((snapshot, selection["track_id"]))
    require(len({origin_key(s) for s, _ in requested}) == len(requested), "duplicate source identity; preserve one explicit origin association")
    for index, (snapshot, _) in enumerate(requested):
        for other, _ in requested[index + 1:]:
            require(not within(snapshot.root, other.root) and not within(other.root, snapshot.root),
                    "migration sources must be independent workspaces")
    for snapshot, _ in requested:
        require(not within(stage, snapshot.root) and not within(snapshot.root, stage), "rehearsal stage must be independent of all sources")
        require(not (snapshot.root / ".invo-learn/operation.lock").exists(), "source workspace is busy; retry when its writer finishes")
    for parent in stage.parents:
        require(not (parent / ".git").exists() and not (parent / "state.json").exists(),
                "private rehearsal stage must be outside enclosing repositories and learner workspaces")
    normalized = {"destination": str(destination.root), "assignments": [
        {"source": str(s.root), "track_id": tid} for s, tid in requested[1:]], "stage": str(stage)}
    request_id = digest(json.dumps(normalized, sort_keys=True).encode())
    if stage.exists():
        require((stage / "migration-manifest.json").is_file(), "stage already exists without a completed rehearsal; preserve it and choose an empty stage")
        _, prior = load_rehearsal(stage)
        require(prior.get("request_id") == request_id, "stage belongs to a different migration request")
        checked = verify_rehearsal(stage)
        return {key: value for key, value in checked.items() if key != "manifest"} | {"status": "already-rehearsed"}
    sources = {}
    for snapshot, tid in requested:
        problems = snapshot.integrity_problems()
        require(not problems, "source artifact integrity failure: " + str(problems))
        check_history(snapshot.root)
        key = origin_key(snapshot)
        sources[key] = {"kind": snapshot.kind, "source": str(snapshot.root), "origin": snapshot.origin,
                        "snapshot": "sources/" + key, "inventory": inventory(snapshot.root), "track_id": tid}
        if snapshot.kind == "course":
            box = Workspace(snapshot.root).mailbox()
            if not within(box, snapshot.root):
                require(not within(snapshot.root, box), "external mailbox cannot contain source workspace")
                require(not within(stage, box) and not within(box, stage), "rehearsal stage cannot overlap the external mailbox")
                sources[key]["external_mailbox"] = {"source": str(box), "snapshot": "external-mailboxes/" + key,
                                                     "inventory": inventory(box)}
    mid = "migration-" + digest(json.dumps({"request": request_id, "sources": sources}, sort_keys=True).encode())[:24]
    stage.mkdir(parents=True)
    atomic(stage / "rehearsal-operation.json", {"migration_id": mid, "status": "copying", "activated": False})
    for snapshot, _ in requested:
        source = sources[origin_key(snapshot)]
        _copy_tree(snapshot.root, stage / source["snapshot"])
        require(inventory(stage / source["snapshot"]) == source["inventory"], "source changed or copy failed; incomplete rehearsal preserved")
        if source.get("external_mailbox"):
            mailbox = source["external_mailbox"]
            _copy_tree(Path(mailbox["source"]), stage / mailbox["snapshot"])
            require(inventory(stage / mailbox["snapshot"]) == mailbox["inventory"], "external mailbox changed during copy")
    workspace = stage / "workspace"
    _copy_tree(stage / sources[origin_key(destination)]["snapshot"], workspace, include_git=False)
    state = copy.deepcopy(destination.state)
    associations = {origin_key(destination): {"tracks": {tid: tid for tid in state["tracks"]}}}
    for snapshot, tid in requested[1:]:
        key = origin_key(snapshot)
        preserved = read_snapshot(stage / sources[key]["snapshot"])
        associations[key] = _import_assignment(workspace, state, preserved, key, tid)
    state["profile"]["preferences"]["teaching_style"] = state["profile"]["preferences"].get("teaching_style", "") + "; " + PRESENTATION
    for track in state["tracks"].values():
        if "teaching_style" in track["preferences"]:
            track["preferences"]["teaching_style"] += "; " + PRESENTATION
    original_box = Path(destination.state["mailbox"]).resolve()
    if within(original_box, destination.root):
        box = workspace / original_box.relative_to(destination.root)
    else:
        box = workspace / ("migration-mailbox-" + mid[-8:])
        _copy_tree(stage / sources[origin_key(destination)]["external_mailbox"]["snapshot"], box)
    state["mailbox"] = str(box)
    atomic(box / ".invo-mailbox.json", {"workspace_id": state["workspace_id"], "path": str(box)})
    state["migration"] = {"id": mid, "status": "rehearsed", "destination": str(destination.root),
                          "intended_mailbox": str(original_box), "presentation_default": PRESENTATION,
                          "associations": associations}
    atomic(workspace / "state.json", state)
    Workspace(workspace).render()
    manifest = {"schema_version": 1, "id": mid, "request_id": request_id, "request": normalized,
                "status": "rehearsing", "activated": False, "destination": str(destination.root),
                "workspace": "workspace", "sources": sources, "associations": associations,
                "projection": {"status": "pending"}, "reconciliation": {"status": "pending"}}
    save_rehearsal(stage, manifest)
    verify_rehearsal(stage)
    manifest["status"] = "rehearsed"
    atomic(stage / "migration-manifest.json", manifest)
    atomic(stage / "rehearsal-operation.json", {"migration_id": mid, "status": "rehearsed", "activated": False})
    return {"status": "rehearsed", "migration_id": mid, "stage": str(stage), "workspace": str(workspace),
            "destination": str(destination.root), "manifest": str(stage / "migration-manifest.json"), "activated": False}
