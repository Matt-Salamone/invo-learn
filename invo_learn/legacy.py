"""Read historical snapshots without executing their tools or changing their bytes.

Readers preserve original identities. They do not project learning credit or
authorize migration; those are separate operations on an explicit destination.
"""
from pathlib import Path
import subprocess

from .contracts import require, report as validate_course_report, string, strings
from .engine import digest, no_links, read_json, within


ASSIGNMENT_CONTEXT = ("assignment_id", "lesson_id", "packet_id", "contract_version", "solution_revision")


class LegacySnapshot:
    def __init__(self, source):
        self.root = no_links(source).resolve()
        require(self.root.is_dir(), "legacy source must be an existing directory")
        course = self.root / "state.json"
        assignment = self.root / ".invo/state.json"
        require(course.is_file() != assignment.is_file(),
                "source must contain exactly one supported course or assignment state")
        self.kind = "course" if course.is_file() else "assignment"
        self.state_path = course if self.kind == "course" else assignment
        self.state = read_json(self.state_path)
        require(isinstance(self.state, dict), "legacy state must be an object")
        marker, identity = (("schema_version", "workspace_id") if self.kind == "course"
                            else ("state_version", "assignment_id"))
        require(type(self.state.get(marker)) is int and self.state[marker] == 1
                and isinstance(self.state.get(identity), str) and self.state[identity].strip(),
                "unsupported or invalid legacy state identity")
        self.origin = {"kind": self.kind, "id": self.state[identity],
                       "commit": self._commit()}
        require(isinstance(self.packets, dict) and all(isinstance(packet, dict) for packet in self.packets.values()),
                "legacy packets must be keyed records")

    def _commit(self):
        # A detached filesystem snapshot may have no Git metadata. Never mistake
        # a containing repository's commit for the origin of such a snapshot.
        if not (self.root / ".git").exists():
            return None
        result = subprocess.run(["git", "-C", str(self.root), "rev-parse", "HEAD"],
                                capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None

    def path(self, relative):
        require(isinstance(relative, str) and relative.strip(), "legacy path must be nonempty text")
        require(not Path(relative).is_absolute(), "legacy artifact path must be relative")
        path = no_links(self.root / relative).resolve()
        require(within(path, self.root) and path != self.root, "legacy artifact path escapes source")
        return path

    @property
    def packets(self):
        return self.state.get("lessons" if self.kind == "course" else "packets", {})

    def status(self):
        pending_state = "prepared" if self.kind == "course" else "outstanding"
        return {"kind": self.kind, "source": str(self.root), "origin": self.origin,
                "state_path": self.state_path.relative_to(self.root).as_posix(),
                "pending": [key for key, value in self.packets.items()
                            if value.get("status") == pending_state],
                "packets": self.packets,
                "current_solution_revision": self.state.get("solution", {}).get("revision"),
                "tracks": self.state.get("tracks", {}),
                "imports": self.state.get("imports", {}),
                "reports": self.state.get("reports", {}),
                "supplemental_reports": self.state.get("supplemental_reports", {}),
                "evidence": self.state.get("evidence", []),
                "artifact_references": self.artifact_references(),
                "integrity_problems": self.integrity_problems(),
                "read_only": True}

    def artifact_references(self):
        """Known required files with their original checksums; no credit inference."""
        refs = []
        def add(path, role, checksum=None, size=None):
            refs.append({"path": path, "role": role, "sha256": checksum, "bytes": size})
        if self.kind == "assignment":
            for source in self.state.get("intake", {}).get("sources", []):
                if source.get("original"):
                    add(source["original"], "source", source.get("sha256"))
            for conversion in self.state.get("conversions", {}).values():
                if conversion.get("status") == "complete":
                    add(conversion["output"], "derived", conversion.get("sha256"))
            for reduction in self.state.get("reductions", {}).values():
                add(reduction["path"], "reduction", reduction.get("sha256"), reduction.get("bytes"))
            for packet in self.packets.values():
                base = packet["path"]
                add(base + "/manifest.json", "packet-manifest")
                for name in ("tutor.md", "report-template.json", "report-contract.json"):
                    add(base + "/" + name, "packet-instructions")
                for item in packet.get("included", []):
                    add(base + "/" + item["path"], "packet-context", item.get("sha256"), item.get("bytes"))
                for item in packet.get("upload_files", []):
                    add(packet["upload_path"] + "/" + item["name"], "upload", item.get("sha256"), item.get("bytes"))
            for record in self.state.get("imports", {}).values():
                add(record["raw_path"], "raw-report", record.get("sha256"))
            for path in self.state.get("solution", {}).get("artifacts", []):
                add(path, "current-solution")
        else:
            for track in self.state.get("tracks", {}).values():
                for material in track.get("materials", {}).values():
                    add(material["original"], "source", material.get("sha256"))
                    for derived in material.get("derived", []):
                        add(derived["path"], "derived", derived.get("sha256"))
            for key, packet in self.packets.items():
                add("lessons/" + key + "/packet/lesson.json", "course-packet-context")
                for name, checksum in packet.get("staged_files", {}).items():
                    add("lessons/" + key + "/packet/" + name, "packet", checksum)
            for record in self.state.get("reports", {}).values():
                add(record["path"], "report")
                if record.get("raw_path"):
                    add(record["raw_path"], "raw-report")
            for record in self.state.get("supplemental_reports", {}).values():
                add(record["path"], "supplemental-report")
                if record.get("raw_path"):
                    add(record["raw_path"], "raw-report")
        return refs

    def integrity_problems(self):
        problems = []
        for ref in self.artifact_references():
            try:
                path = self.path(ref["path"])
                content = path.read_bytes()
                require(ref["sha256"] is None or digest(content) == ref["sha256"],
                        "original checksum changed")
                require(ref["bytes"] is None or len(content) == ref["bytes"],
                        "original byte count changed")
                if ref["role"] == "packet-manifest":
                    manifest = read_json(path)
                    packet = next(p for p in self.packets.values() if p["path"] + "/manifest.json" == ref["path"])
                    require(all(field in manifest and manifest[field] == packet[field] for field in ASSIGNMENT_CONTEXT),
                            "manifest identifiers do not match original packet")
                elif ref["role"] == "course-packet-context":
                    snapshot = read_json(path)
                    packet = next(p for key, p in self.packets.items()
                                  if "lessons/" + key + "/packet/lesson.json" == ref["path"])
                    require(all(field in snapshot and snapshot[field] == packet[field]
                                for field in ("id", "track_id", "map_revision", "objective_ids")),
                            "snapshot context does not match original lesson")
            except (ValueError, TypeError, KeyError, OSError) as exc:
                problems.append({"path": ref["path"], "reason": str(exc)})
        return problems

    def inspect_report(self, returned, today=None):
        path = no_links(returned).resolve()
        raw = path.read_bytes()
        result = {"kind": self.kind, "origin": self.origin, "raw_path": str(path),
                  "raw_sha256": digest(raw), "raw_bytes": len(raw),
                  "read_only": True, "credit_applied": False}
        try:
            report = decode_report(raw)
        except (ValueError, TypeError, UnicodeError) as exc:
            return result | {"status": "malformed", "reason": str(exc)}
        result["report"] = report
        try:
            problems = self.integrity_problems()
            require(not problems, "legacy artifact integrity failure: " + str(problems))
            context, historical, packet = self.associate_report(report)
            result.update(context=context, historical_context=historical)
        except (ValueError, TypeError, KeyError) as exc:
            return result | {"status": "unresolved", "reason": str(exc)}
        try:
            self.validate_report(report, packet, today)
        except (ValueError, TypeError, KeyError) as exc:
            return result | {"status": "invalid", "reason": str(exc)}
        return result | {"status": "associated"}

    def associate_report(self, report):
        require(isinstance(report, dict), "legacy report must be an object")
        key = report.get("lesson_id" if self.kind == "course" else "packet_id")
        require(isinstance(key, str) and key in self.packets, "report has no matching original packet")
        packet = self.packets[key]
        if self.kind == "assignment":
            require(type(report.get("contract_version")) is int and report["contract_version"] == 1
                    and all(field in packet and report.get(field) == packet[field] for field in ASSIGNMENT_CONTEXT)
                    and report.get("assignment_id") == self.state["assignment_id"],
                    "report identifiers or solution revision do not match the issued packet")
            context = {field: packet[field] for field in ASSIGNMENT_CONTEXT}
            historical = packet["solution_revision"] != self.state.get("solution", {}).get("revision")
        else:
            require(report.get("lesson_id") == packet.get("id")
                    and report.get("track_id") == packet.get("track_id"),
                    "report identifiers do not match the issued lesson")
            if report.get("report_type") == "side-chat":
                require(type(report.get("schema_version")) is int and report["schema_version"] == 1,
                        "unsupported supplemental report schema")
                require(all(type(report.get(field)) is int and report[field] == packet.get(field, 0)
                            for field in ("map_revision", "content_revision")),
                        "supplemental revisions do not match the issued lesson")
            context = {"lesson_id": packet["id"], "track_id": packet["track_id"],
                       "map_revision": packet.get("map_revision")}
            historical = packet.get("map_revision") != self.state.get("tracks", {}).get(packet["track_id"], {}).get("map_revision")
        return context, historical, packet

    def validate_report(self, report, packet, today):
        report_type = report.get("report_type", "lesson")
        require(report_type in ("lesson", "side-chat"), "unsupported legacy report type")
        if report_type == "side-chat":
            string(report.get("report_id"), "supplemental report_id")
            require("observations" not in report and "objectives" not in report,
                    "supplemental discussion is not formal assessment")
            require(isinstance(report.get("discussions"), list) and report["discussions"],
                    "supplemental report needs actual discussions")
            for discussion in report["discussions"]:
                require(isinstance(discussion, dict), "discussion must be an object")
                for field in ("question", "explanation", "source_reference"):
                    string(discussion.get(field), field)
                require("learner_response" not in discussion or isinstance(discussion["learner_response"], str),
                        "learner_response must preserve actual text")
                if self.kind == "course":
                    strings(discussion.get("objective_ids", []), "discussion objectives")
                    require(set(discussion.get("objective_ids", [])) <= set(packet["objective_ids"]),
                            "discussion references unknown objective")
            strings(report.get("remaining_questions"), "remaining questions")
            require(isinstance(report.get("assessment_help"), list), "assessment_help must be a list")
            for help_item in report["assessment_help"]:
                require(isinstance(help_item, dict), "assessment help must be an object")
                for field in ("question", "help"):
                    string(help_item.get(field), field)
                require(help_item.get("timing") in ("before-answer", "after-answer", "unknown"),
                        "invalid assessment-help timing")
                if self.kind == "course":
                    require(help_item.get("objective_id") in packet["objective_ids"],
                            "assessment help references unknown objective")
            return
        if self.kind == "course":
            validate_course_report(report, packet, today or report.get("completed_on"))
            return
        require(isinstance(report.get("observations"), list) and report["observations"],
                "legacy main report needs actual observations")
        for observation in report["observations"]:
            require(isinstance(observation, dict), "observation must be an object")
            for field in ("criterion", "question", "learner_response", "assistance"):
                string(observation.get(field), field)
            require(observation.get("evidence_level") in ("covered", "assisted", "independent"),
                    "invalid legacy evidence level")
        strings(report.get("remaining_gaps"), "remaining gaps")
        require(isinstance(report.get("suspected_errors"), list), "suspected_errors must be a list")
        for concern in report["suspected_errors"]:
            require(isinstance(concern, dict), "suspected error must be an object")
            for field in ("claim", "reasoning", "source_reference"):
                string(concern.get(field), field)


def read_snapshot(source):
    return LegacySnapshot(source)


def decode_report(raw):
    """Strict JSON plus the complete fence accepted for pasted course reports."""
    import json
    clean = raw.decode("utf-8-sig").strip()
    lines = clean.splitlines()
    if len(lines) >= 3 and lines[0] in ("```json", "```") and lines[-1] == "```":
        clean = "\n".join(lines[1:-1]).strip()
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(clean, object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("invalid JSON number: " + value)))
