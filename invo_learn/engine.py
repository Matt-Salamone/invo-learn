"""Inspectable JSON state, atomic writes, guarded staging and evidence projection."""
import contextlib
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import uuid

from .contracts import Invalid, KINDS, date, evidence_outcome, fields, identifier, preferences, require, report, string, strings

STATE_SCHEMA = 1
DEFAULTS = {"teaching_style": "brief explanation, attempt, feedback",
            "supplemental_research": False, "remediation": "recommend prerequisite repair; advancement is advisory",
            "schedule": None}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(Invalid(f"invalid JSON number: {value}")))


def atomic(path, value):
    data = (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    atomic_bytes(path, data)


def atomic_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        with temp.open("wb") as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def is_link(path):
    if path.is_symlink():
        return True
    # lstat exposes junction tags on Windows, including Python 3.10/3.11,
    # which do not yet provide Path.is_junction().
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return getattr(info, "st_reparse_tag", None) == getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003)


def no_links(path):
    path = Path(os.path.abspath(path))
    for p in (path, *path.parents):
        require(not is_link(p), f"symlink/junction paths are not allowed: {p}")
    if path.is_dir():
        for root, dirs, files in os.walk(path, followlinks=False):
            for name in dirs + files:
                require(not is_link(Path(root) / name), "symlink/junction inside managed directory")
    return path


def within(path, root):
    return path == root or root in path.parents


def safe_mailbox(root, mailbox):
    root, mailbox = root.resolve(), no_links(mailbox).resolve()
    require(mailbox != Path(mailbox.anchor), "mailbox cannot be a filesystem root")
    require(not within(root, mailbox), "mailbox cannot contain the workspace")
    require(mailbox.name.lower() not in ("tracks", "materials", "sources", "source", "archive", "archives",
            "originals", "derived", "reports", "lessons", "inbox", ".invo-learn", ".agents", ".cursor", ".git"),
            "mailbox cannot be a source, archive or managed-record folder")
    if within(mailbox, root):
        require(mailbox.parent == root and mailbox.name not in
                ("tracks", "reports", "lessons", "inbox", ".invo-learn", ".agents", ".cursor", ".git"),
                "internal mailbox must be a dedicated top-level folder")
    return mailbox


class Workspace:
    def __init__(self, root):
        self.root = no_links(Path(root)).resolve()
        self.state_path = self.root / "state.json"
        self.state = read_json(self.state_path)
        require(self.state["schema_version"] == STATE_SCHEMA, "unsupported workspace schema; use compatible harness")

    @contextlib.contextmanager
    def locked(self):
        path = self.root / ".invo-learn" / "operation.lock"
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise Invalid("workspace busy; if an interrupted process left operation.lock, verify no process is running before removing it") from exc
        try:
            os.write(fd, str(os.getpid()).encode())
            self.state = read_json(self.state_path)
            yield
        finally:
            os.close(fd)
            path.unlink(missing_ok=True)

    def save(self, action, details):
        self.state["events"].append({"action": action, "details": details,
                                     "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat()})
        atomic(self.state_path, self.state)
        self.render()

    def track(self, tid):
        require(tid in self.state["tracks"], f"unknown track: {tid}")
        return self.state["tracks"][tid]

    def path(self, relative):
        p = no_links(self.root / relative).resolve()
        require(within(p, self.root), "path escapes workspace")
        return p

    def mailbox(self):
        box = safe_mailbox(self.root, Path(self.state["mailbox"]))
        require(box.is_dir(), "configured mailbox missing")
        marker = read_json(box / ".invo-mailbox.json")
        require(marker == {"workspace_id": self.state["workspace_id"], "path": str(box)},
                "mailbox ownership marker mismatch")
        return box

    def add_track(self, tid, title, prefs=None):
        identifier(tid)
        string(title, "track title")
        prefs = prefs or {}
        preferences(prefs)
        require(tid not in self.state["tracks"], "track already exists")
        self.state["tracks"][tid] = {"title": title, "preferences": copy.deepcopy(prefs), "active": True,
            "materials": {}, "objectives": {}, "proposals": {}, "map_revision": 0,
            "overrides": [], "notes": []}
        self.save("add-track", {"track_id": tid})
        return {"track_id": tid, "preferences": self.effective_preferences(tid)}

    def effective_preferences(self, tid):
        return self.state["profile"]["preferences"] | self.track(tid)["preferences"]

    def set_preferences(self, tid, prefs):
        preferences(prefs)
        target = self.track(tid)["preferences"] if tid else self.state["profile"]["preferences"]
        target.update(prefs)
        self.save("preferences", {"track_id": tid, "changes": prefs})
        return target

    def add_material(self, tid, source, role="primary"):
        track = self.track(tid)
        require(role in ("primary", "supplemental"), "invalid source role")
        require(role == "primary" or self.effective_preferences(tid)["supplemental_research"],
                "supplemental research is disabled for this track")
        source = no_links(source).resolve()
        require(source.is_file(), "material must be a file; archive directory inputs first")
        from_mailbox = within(source, self.mailbox())
        require(not (from_mailbox and source.name == ".invo-mailbox.json"), "mailbox ownership marker is not learning material")
        data = source.read_bytes()
        # Keep the drop-off in place until guarded staging snapshots the mailbox.
        # Retrying an intake must not register the same upload twice for a course.
        if from_mailbox:
            checksum = digest(data)
            for material in track["materials"].values():
                if material["sha256"] == checksum and material["role"] == role:
                    original = self.path(material["original"])
                    require(original.is_file() and digest(original.read_bytes()) == checksum,
                            "durable original checksum mismatch; restore it before retrying intake")
                    return material
        mid = "m-" + uuid.uuid4().hex[:12]
        dest = self.root / "tracks" / tid / "materials" / "originals" / mid / source.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        try:
            text = data.decode("utf-8-sig")
            usable = bool(text.strip()) and all(ord(c) >= 32 or c in "\n\r\t" for c in text)
        except UnicodeDecodeError:
            usable = False
        track["materials"][mid] = {"id": mid, "name": source.name, "original": dest.relative_to(self.root).as_posix(),
            "sha256": digest(data), "role": role, "status": "usable" if usable else "needs-transformation",
            "usability_note": "UTF-8 text" if usable else "agent inspection or approved transformation required",
            "derived": [], "approvals": []}
        self.save("add-material", {"track_id": tid, "material_id": mid})
        return track["materials"][mid]

    def inspect_material(self, tid, mid, note):
        m = self.track(tid)["materials"][mid]
        string(note, "inspection evidence/tool and limitations")
        m.update(status="usable", usability_note=note)
        self.save("material-inspected", {"track_id": tid, "material_id": mid, "note": note})
        return m

    def approve_transformation(self, tid, mid, workflow, consent):
        m = self.track(tid)["materials"][mid]
        string(workflow, "workflow (tools, operations, outputs, fidelity limitations)")
        string(consent, "learner's explicit permission")
        aid = "a-" + uuid.uuid4().hex[:12]
        m["approvals"].append({"id": aid, "workflow": workflow, "consent": consent,
                              "scope": "this material only; local tools; no external upload", "used": False})
        self.save("transformation-approved", {"track_id": tid, "material_id": mid, "approval_id": aid})
        return m["approvals"][-1]

    def add_derived(self, tid, mid, source, aid, note):
        m = self.track(tid)["materials"][mid]
        approval = next((a for a in m["approvals"] if a["id"] == aid), None)
        require(approval is not None and not approval["used"], "unused material-specific transformation approval required")
        string(note, "conversion provenance and fidelity limitations")
        source = no_links(source).resolve()
        require(source.is_file(), "derived artifact must be a file")
        data = source.read_bytes()
        require(bool(data), "derived artifact is empty")
        did = "d-" + uuid.uuid4().hex[:12]
        dest = self.root / "tracks" / tid / "materials" / "derived" / did / source.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        m["derived"].append({"id": did, "path": dest.relative_to(self.root).as_posix(), "sha256": digest(data),
                             "approval_id": aid, "note": note})
        approval["used"] = True
        m["status"] = "usable"
        m["usability_note"] = note
        self.save("derived-material", {"track_id": tid, "material_id": mid, "derived_id": did})
        return m

    def propose_map(self, tid, spec):
        t = self.track(tid)
        fields(spec, ("objectives", "source_gaps", "rationale"))
        string(spec["rationale"], "map rationale")
        require(isinstance(spec["objectives"], list) and spec["objectives"], "map needs objectives")
        require(isinstance(spec["source_gaps"], list), "source_gaps must be a list")
        ids, referenced = set(), set()
        for obj in spec["objectives"]:
            fields(obj, ("id", "title", "kind", "sources", "prerequisites", "scope", "reason"))
            identifier(obj["id"])
            require(obj["id"] not in ids, "duplicate map objective")
            ids.add(obj["id"])
            string(obj["title"], "objective title")
            require(obj["kind"] in KINDS, "objective kind must be fact, concept or skill")
            require(obj["scope"] in ("included", "deferred"), "invalid objective scope")
            require(isinstance(obj["reason"], str), "scope reason must be text")
            if obj["scope"] == "deferred":
                string(obj["reason"], "deferral reason")
            strings(obj["prerequisites"], "prerequisites")
            require(isinstance(obj["sources"], list) and obj["sources"], "source-backed objectives required")
            for ref in obj["sources"]:
                fields(ref, ("material_id", "locator"))
                require(ref["material_id"] in t["materials"], "unknown map source")
                require(t["materials"][ref["material_id"]]["role"] == "primary", "uploaded primary materials define scope")
                string(ref["locator"], "source locator (page, section, timestamp, etc.)")
                referenced.add(ref["material_id"])
            old = t["objectives"].get(obj["id"])
            if old:
                require(old["kind"] == obj["kind"], "changing objective kind requires a new objective ID")
                if old["evidence"]:
                    require(old["title"] == obj["title"] and old["sources"] == obj["sources"],
                            "evidenced objective meaning is immutable; defer it and add a new ID")
        require(set(t["objectives"]) <= ids, "retain old objectives; defer rather than delete evidence")
        for obj in spec["objectives"]:
            require(set(obj["prerequisites"]) <= ids and obj["id"] not in obj["prerequisites"], "unknown/self prerequisite")
        graph = {o["id"]: o["prerequisites"] for o in spec["objectives"]}
        def visit(oid, stack):
            require(oid not in stack, "prerequisite cycle")
            for parent in graph[oid]:
                visit(parent, stack | {oid})
        for oid in graph:
            visit(oid, set())
        gaps = set()
        for gap in spec["source_gaps"]:
            fields(gap, ("material_id", "reason"))
            require(gap["material_id"] in t["materials"] and gap["material_id"] not in gaps, "unknown/duplicate source gap")
            string(gap["reason"], "source gap reason")
            gaps.add(gap["material_id"])
        primary = {mid for mid, m in t["materials"].items() if m["role"] == "primary"}
        require(primary <= referenced | gaps, "map must account for every primary material through objectives or explicit gaps")
        pid = "map-" + uuid.uuid4().hex[:12]
        t["proposals"][pid] = {"spec": copy.deepcopy(spec), "base_revision": t["map_revision"],
                               "material_ids": sorted(t["materials"]), "status": "pending"}
        self.save("map-proposed", {"track_id": tid, "proposal_id": pid})
        return {"proposal_id": pid, **t["proposals"][pid]}

    def accept_map(self, tid, pid, approval):
        t = self.track(tid)
        string(approval, "learner map approval")
        require(pid in t["proposals"], "unknown proposal")
        p = t["proposals"][pid]
        require(p["status"] == "pending" and p["base_revision"] == t["map_revision"]
                and p["material_ids"] == sorted(t["materials"]), "stale/accepted proposal; propose current materials again")
        for obj in p["spec"]["objectives"]:
            old = t["objectives"].get(obj["id"], {})
            t["objectives"][obj["id"]] = copy.deepcopy(obj) | {"coverage": old.get("coverage", "unassessed"),
                "understanding": old.get("understanding", "unassessed"), "retention": old.get("retention", "unassessed"),
                "evidence": old.get("evidence", []), "uncertainties": old.get("uncertainties", []),
                "review": old.get("review", None)}
        t["source_gaps"] = p["spec"]["source_gaps"]
        t["map_revision"] += 1
        p.update(status="accepted", approval=approval)
        self.save("map-accepted", {"track_id": tid, "proposal_id": pid})
        return {"revision": t["map_revision"]}

    def override(self, tid, oids, reason):
        t = self.track(tid)
        require(set(oids) <= t["objectives"].keys(), "unknown override objective")
        string(reason, "explicit learner override")
        t["overrides"].append({"objective_ids": oids, "reason": reason})
        self.save("learner-override", {"track_id": tid, "objective_ids": oids, "reason": reason})
        return t["overrides"][-1]

    def prepare(self, tid, spec, today):
        t = self.track(tid)
        date(today)
        fields(spec, ("objective_ids", "mode", "context", "attachments", "supplemental_context"))
        strings(spec["objective_ids"], "objective_ids")
        require(spec["objective_ids"] and len(set(spec["objective_ids"])) == len(spec["objective_ids"]), "unique lesson objectives required")
        require(set(spec["objective_ids"]) <= t["objectives"].keys(), "lesson requires accepted map objectives")
        for oid in spec["objective_ids"]:
            require(all(t["materials"][r["material_id"]]["status"] == "usable" for r in t["objectives"][oid]["sources"]),
                    "assigned objective has unreadable sources; inspect or transform with permission first")
        require(spec["mode"] in ("lesson", "review"), "mode must be lesson or review")
        string(spec["context"], "source-grounded teaching context")
        require(isinstance(spec["supplemental_context"], str), "supplemental_context must be text")
        require(not spec["supplemental_context"] or self.effective_preferences(tid)["supplemental_research"], "supplemental research disabled")
        require(isinstance(spec["attachments"], list), "attachments must be a list")
        active = self.state["active_lesson"]
        require(not active or self.state["lessons"][active]["status"] in ("reported", "abandoned"),
                "current handoff awaits report; ingest it or explicitly abandon before reusing mailbox")
        box = self.mailbox()  # Preflight before writing any lesson artifacts.
        selected = []
        for a in spec["attachments"]:
            fields(a, ("material_id",), ("derived_id",))
            require(a["material_id"] in t["materials"], "unknown attachment")
            m = t["materials"][a["material_id"]]
            require(m["status"] == "usable", "attachment needs inspection/approved transformation")
            if "derived_id" in a:
                d = next((d for d in m["derived"] if d["id"] == a["derived_id"]), None)
                require(d is not None, "unknown derived artifact")
                rel, checksum = d["path"], d["sha256"]
            else:
                rel, checksum = m["original"], m["sha256"]
            src = self.path(rel)
            require(digest(src.read_bytes()) == checksum, "source checksum changed")
            selected.append((src, checksum, rel))
        lid = "lesson-" + uuid.uuid4().hex[:12]
        folder = self.root / "lessons" / lid
        packet = folder / "packet"
        packet.mkdir(parents=True)
        objectives = [copy.deepcopy(t["objectives"][oid]) for oid in spec["objective_ids"]]
        lesson = {"id": lid, "track_id": tid, "prepared_on": today, "mode": spec["mode"],
                  "sequence": len(self.state["lessons"]),
                  "objective_ids": spec["objective_ids"], "map_revision": t["map_revision"],
                  "status": "prepared", "report_id": None, "spec": copy.deepcopy(spec),
                  "preferences": copy.deepcopy(self.effective_preferences(tid)),
                  "objective_snapshot": objectives, "staged_files": {}}
        source_lines = []
        for n, (src, checksum, rel) in enumerate(selected, 1):
            name = f"source-{n:02d}-{src.name}"
            shutil.copyfile(src, packet / name)
            source_lines.append({"upload": name, "workspace_path": rel, "sha256": checksum})
        atomic(packet / "lesson.json", lesson | {"sources": source_lines})
        template = (Path(__file__).parent / "templates" / "chatbot.md").read_text(encoding="utf-8")
        text = template + "\n\n## Assigned lesson\n\n" + json.dumps({
            "lesson_id": lid, "track_id": tid, "mode": spec["mode"], "prepared_on": today,
            "learner_preferences": lesson["preferences"], "objectives": objectives,
            "source_attachments": source_lines}, indent=2, ensure_ascii=False)
        text += "\n\n## Uploaded-source teaching context\n\n" + spec["context"]
        if spec["supplemental_context"]:
            text += "\n\n## Optional supplemental context (outside uploaded scope)\n\n" + spec["supplemental_context"]
        (packet / "START-HERE.md").write_text(text + "\n", encoding="utf-8")
        shutil.copyfile(Path(__file__).parent / "templates" / "report.schema.json", packet / "report.schema.json")
        for p in packet.iterdir():
            lesson["staged_files"][p.name] = digest(p.read_bytes())
        self.state["lessons"][lid] = lesson
        self.state["active_lesson"] = lid
        self.save("lesson-prepared", {"lesson_id": lid})
        self.stage(lid, box)
        return {"lesson_id": lid, "mailbox": str(box), "instruction": "Upload every visible file into a fresh chatbot conversation; start with START-HERE.md", "warnings": self.lesson_warnings(tid, spec["objective_ids"])}

    def lesson_warnings(self, tid, oids):
        t = self.track(tid)
        warnings = []
        for oid in oids:
            for pre in t["objectives"][oid]["prerequisites"]:
                if t["objectives"][pre]["understanding"] != "demonstrated":
                    warnings.append(f"{oid}: prerequisite {pre} unresolved; recommend repair, allow learner override")
        return warnings

    def stage(self, lid, box=None):
        require(lid == self.state["active_lesson"], "can only restage the active lesson")
        lesson = self.state["lessons"][lid]
        require(lesson["status"] == "prepared", "only prepared lessons can be staged")
        box = box or self.mailbox()
        packet = self.path(f"lessons/{lid}/packet")
        require({p.name: digest(p.read_bytes()) for p in packet.iterdir()} == lesson["staged_files"], "durable packet checksum changed")
        # Preserve EVERYTHING before clearing, including unexpected downloaded/pasted reports.
        contents = [p for p in box.iterdir() if p.name != ".invo-mailbox.json"]
        if contents:
            snapshot = self.root / "inbox" / "mailbox-snapshots" / uuid.uuid4().hex
            payload = snapshot / "contents"
            payload.mkdir(parents=True)
            for p in contents:
                if p.is_dir():
                    shutil.copytree(p, payload / p.name)
                else:
                    shutil.copy2(p, payload / p.name)
            atomic(snapshot / "snapshot.json", {"reason": "mailbox reuse; unparsed returns preserved", "next_lesson": lid})
            # Recheck ownership and links immediately before destructive operations.
            self.mailbox()
            for p in contents:
                require(p.parent.resolve() == box, "unsafe mailbox child")
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
        for p in packet.iterdir():
            shutil.copyfile(p, box / p.name)
        return {"lesson_id": lid, "mailbox": str(box)}

    def abandon(self, lid, reason):
        string(reason, "explicit abandonment reason")
        require(lid == self.state["active_lesson"], "only active lesson can be abandoned")
        lesson = self.state["lessons"][lid]
        require(lesson["status"] == "prepared", "lesson already finalized")
        lesson.update(status="abandoned", abandonment_reason=reason)
        self.save("lesson-abandoned", {"lesson_id": lid, "reason": reason})
        return {"status": "abandoned"}

    def ingest(self, raw, today):
        date(today)
        # Durably retain input even when parsing, validation or state commit fails.
        rid = digest(raw.encode("utf-8"))
        path = self.root / "inbox" / "reports" / (rid + ".txt")
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            atomic_bytes(path, raw.encode("utf-8"))
        clean = raw.strip().lstrip("\ufeff")
        lines = clean.splitlines()
        if len(lines) >= 3 and lines[0] in ("```json", "```") and lines[-1] == "```":
            clean = "\n".join(lines[1:-1]).strip()
        # Use the same strict JSON loader for pasted input without arbitrary extraction.
        parsed = self.root / "inbox" / (rid + ".parse.json")
        try:
            parsed.write_text(clean, encoding="utf-8")
            obj = read_json(parsed)
        finally:
            parsed.unlink(missing_ok=True)
        require(isinstance(obj, dict), "report must be an object")
        lid = obj.get("lesson_id")
        require(isinstance(lid, str) and lid in self.state["lessons"], "unknown lesson; raw report preserved in inbox")
        lesson = self.state["lessons"][lid]
        report(obj, lesson, today)
        normalized = digest(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode())
        report_id = obj["report_id"]
        existing = self.state["reports"].get(report_id)
        if existing:
            require(existing["sha256"] == normalized, "report_id conflict; do not overwrite earlier evidence")
            return {"status": "duplicate", "report_id": report_id}
        for previous in self.state["reports"].values():
            require(previous["lesson_id"] != lid, "lesson already has a report; record a dispute instead of a second import")
        require(lesson["status"] == "prepared", "cannot import abandoned/finalized lesson")
        dest = self.root / "reports" / (report_id + ".json")
        atomic(dest, obj)
        self.state["reports"][report_id] = {"sha256": normalized, "lesson_id": lid,
            "path": dest.relative_to(self.root).as_posix(), "raw_path": path.relative_to(self.root).as_posix(),
            "report": obj, "invalidated": False}
        lesson.update(status="reported", report_id=report_id)
        self.recompute(lesson["track_id"])
        self.save("report-ingested", {"report_id": report_id, "lesson_id": lid})
        return {"status": "imported", "report_id": report_id, "track_id": lesson["track_id"],
                "recommended_next_steps": obj["recommended_next_steps"], "prerequisite_gaps": obj["prerequisite_gaps"]}

    def dispute(self, report_id, reason):
        require(report_id in self.state["reports"], "unknown report")
        string(reason, "dispute/invalid assessment reason")
        r = self.state["reports"][report_id]
        r.update(invalidated=True, invalidation_reason=reason)
        tid = r["report"]["track_id"]
        self.recompute(tid)
        self.save("report-invalidated", {"report_id": report_id, "reason": reason})
        return {"status": "invalidated", "next": "prepare a fresh assessment; original report is retained"}

    def recompute(self, tid):
        t = self.track(tid)
        intervals = self.state["review_policy"]["interval_days"]
        for o in t["objectives"].values():
            o.update(coverage="unassessed", understanding="unassessed", retention="unassessed",
                     evidence=[], uncertainties=[], review=None)
        # Chronological projection makes late imports and withdrawal deterministic.
        reports = sorted((r for r in self.state["reports"].values() if r["report"]["track_id"] == tid),
                         key=lambda r: (r["report"]["completed_on"], self.state["lessons"][r["lesson_id"]]["prepared_on"],
                                        self.state["lessons"][r["lesson_id"]]["sequence"]))
        for record in reports:
            r = record["report"]
            lesson = self.state["lessons"][r["lesson_id"]]
            for item in r["objectives"]:
                o = t["objectives"][item["objective_id"]]
                o["evidence"].append({"report_id": r["report_id"], "lesson_id": r["lesson_id"],
                    "completed_on": r["completed_on"], "mode": lesson["mode"], "invalidated": record["invalidated"],
                    **copy.deepcopy(item)})
                if record["invalidated"]:
                    o["uncertainties"].append(f"{r['report_id']}: withdrawn: {record['invalidation_reason']}")
                    continue
                if item["coverage"] == "covered":
                    o["coverage"] = "covered"
                assessments = item["assessments"]
                success, contradiction, cold_success = evidence_outcome(assessments, KINDS[o["kind"]])
                eligible = success and not contradiction and item["coverage"] == "covered" and item["judgment"] == "demonstrated"
                if item["judgment"] == "demonstrated" and not eligible:
                    o["uncertainties"].append(f"{r['report_id']}: claimed demonstration lacks consistent fresh unaided evidence")
                if contradiction and success:
                    o["uncertainties"].append(f"{r['report_id']}: conflicting pass/fail; use fresh reassessment")
                if r["misconceptions"] or r["prerequisite_gaps"]:
                    o["uncertainties"].extend(f"{r['report_id']}: {x}" for x in r["misconceptions"] + r["prerequisite_gaps"])
                old = o["review"]
                when = date(r["completed_on"])
                delayed = old is not None and when >= date(old["due_on"]) and when > date(old["last_on"])
                if eligible:
                    o["understanding"] = "demonstrated"
                    step = old["step"] if old else 0
                    if lesson["mode"] == "review" and delayed and cold_success:
                        step = min(step + 1, len(intervals) - 1)
                        o["retention"] = "demonstrated"
                    elif lesson["mode"] == "review" and not cold_success:
                        o["retention"] = "needs-review"
                        o["uncertainties"].append(f"{r['report_id']}: performance after repair is relearning, not delayed retention")
                        step = 0
                    elif lesson["mode"] == "review":
                        o["uncertainties"].append(f"{r['report_id']}: early review establishes performance, not delayed retention")
                        # An early review does not postpone a due review or advance its interval.
                        if old:
                            continue
                    o["review"] = {"step": step, "last_on": r["completed_on"],
                        "due_on": (when + dt.timedelta(days=intervals[step])).isoformat(), "kind": KINDS[o["kind"]],
                        "last_result": "independent-pass", "lapses": (old["lapses"] if old else 0)
                        + int(lesson["mode"] == "review" and not cold_success)}
                elif item["coverage"] == "covered" or assessments:
                    o["understanding"] = "uncertain" if success or item["judgment"] == "uncertain" else "needs-practice"
                    if lesson["mode"] == "review" or o["retention"] == "demonstrated":
                        o["retention"] = "needs-review"
                    o["review"] = {"step": 0, "last_on": r["completed_on"],
                        "due_on": (when + dt.timedelta(days=intervals[0])).isoformat(), "kind": KINDS[o["kind"]],
                        "last_result": "not-demonstrated", "lapses": (old["lapses"] if old else 0) + (lesson["mode"] == "review")}

    def set_policy(self, intervals):
        require(isinstance(intervals, list) and intervals and all(type(x) is int and x > 0 for x in intervals)
                and intervals == sorted(set(intervals)), "interval_days must be increasing positive integers")
        self.state["review_policy"]["interval_days"] = intervals
        for tid in self.state["tracks"]:
            self.recompute(tid)
        self.save("review-policy", {"interval_days": intervals})
        return self.state["review_policy"]

    def status(self, today):
        date(today)
        tracks, due = {}, []
        for tid, t in self.state["tracks"].items():
            tracks[tid] = {"title": t["title"], "active": t["active"], "preferences": self.effective_preferences(tid),
                           "materials": t["materials"], "objectives": t["objectives"], "source_gaps": t.get("source_gaps", []),
                           "pending_maps": [pid for pid, p in t["proposals"].items() if p["status"] == "pending"],
                           "overrides": t["overrides"]}
            mapped = {ref["material_id"] for o in t["objectives"].values() for ref in o["sources"]}
            tracks[tid]["unmapped_primary_materials"] = [mid for mid, m in t["materials"].items()
                if m["role"] == "primary" and mid not in mapped]
            for oid, o in t["objectives"].items():
                if t["active"] and o["scope"] == "included" and o["review"] and o["review"]["due_on"] <= today:
                    due.append({"track_id": tid, "objective_id": oid, **o["review"]})
        return {"learner": self.state["profile"], "mailbox": self.state["mailbox"], "tracks": tracks, "due_reviews": sorted(due, key=lambda r: (r["due_on"], r["track_id"], r["objective_id"])),
                "active_lesson": self.state["active_lesson"], "review_policy": self.state["review_policy"]}

    def render(self):
        lines = ["# Learner overview", "", f"Learner: {self.state['profile']['name']}", "",
                 f"Mailbox (drop off materials and pick up lessons): {self.state['mailbox']}", "",
                 "Generated from state.json. Agent-owned plans live in track plan.md files; use tools to change records.", ""]
        for tid, t in self.state["tracks"].items():
            lines.extend([f"## {t['title']} ({tid})", "", f"Preferences: {json.dumps(self.effective_preferences(tid), ensure_ascii=False)}", ""])
            track_lines = [f"# Coverage: {t['title']}", "", f"Accepted revision: {t['map_revision']}", ""]
            for oid, o in t["objectives"].items():
                refs = "; ".join(f"{r['material_id']} — {r['locator']}" for r in o["sources"])
                line = f"- {oid}: {o['title']} | scope={o['scope']} | coverage={o['coverage']} | understanding={o['understanding']} | retention={o['retention']}"
                lines.append(line)
                track_lines.extend([line, f"  Sources: {refs}", f"  Prerequisites: {', '.join(o['prerequisites']) or 'none'}",
                                    f"  Deferral: {o['reason'] or 'none'}", f"  Review: {json.dumps(o['review'])}"])
                for note in o["uncertainties"]:
                    track_lines.append(f"  Unresolved/evidence note: {note}")
            for mid, m in t["materials"].items():
                track_lines.append(f"- Source {mid}: [{m['name']}]({Path(m['original']).relative_to(Path('tracks') / tid).as_posix()}) ({m['role']}, {m['status']})")
            for gap in t.get("source_gaps", []):
                track_lines.append(f"- Unmapped source gap: {gap['material_id']}: {gap['reason']}")
            for override in t["overrides"]:
                track_lines.append(f"- Learner override (gaps retained): {json.dumps(override, ensure_ascii=False)}")
            for pid, p in t["proposals"].items():
                if p["status"] == "pending":
                    track_lines.append(f"- Pending map for learner review: {pid}")
            folder = self.root / "tracks" / tid
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "coverage.md").write_text("\n".join(track_lines) + "\n", encoding="utf-8")
            plan = folder / "plan.md"
            if not plan.exists():
                plan.write_text("# Study plan\n\nAgent: record source coverage rationale, next lessons, unresolved prerequisites, priorities and any learner-supplied scheduling constraints here.\n", encoding="utf-8")
            lines.append("")
        (self.root / "OVERVIEW.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def initial_state(root, mailbox, name, prefs=None):
    string(name, "learner name")
    prefs = prefs or {}
    preferences(prefs)
    return {"schema_version": STATE_SCHEMA, "workspace_id": uuid.uuid4().hex, "mailbox": str(mailbox),
            "profile": {"name": name, "preferences": DEFAULTS | prefs}, "tracks": {}, "lessons": {},
            "reports": {}, "active_lesson": None, "events": [],
            "review_policy": {"interval_days": [1, 3, 7, 14, 30, 60], "policy": "fresh unaided success; delayed reviews expand, other attempts reset"}}
