"""Optional section inventory and observable objective criteria for v1 maps."""
from .contracts import fields, identifier, require, string, strings


def validate(ws, tid, spec):
    track = ws.track(tid)
    objectives = {o["id"]: o for o in spec["objectives"]}
    for obj in objectives.values():
        if "success_criteria" in obj:
            strings(obj["success_criteria"], "success criteria")
            require(obj["success_criteria"], "success criteria cannot be empty")
        old = track["objectives"].get(obj["id"])
        if old and old["evidence"]:
            require(old.get("success_criteria") == obj.get("success_criteria"),
                    "changing evidenced success criteria requires a new objective ID")
    if track.get("source_sections"):
        require("source_sections" in spec, "retain accepted section inventory in subsequent maps")
    if "source_sections" not in spec:
        require("section_inventory" not in spec, "section inventory needs source_sections")
        return
    require(isinstance(spec["source_sections"], list), "source_sections must be a list")
    require(isinstance(spec.get("section_inventory"), list), "section_inventory inspection records required")
    seen = set()
    for section in spec["source_sections"]:
        fields(section, ("id", "material_id", "locator", "objective_ids", "reason"))
        identifier(section["id"])
        require(section["id"] not in seen, "duplicate source section")
        seen.add(section["id"])
        material = track["materials"].get(section["material_id"])
        require(material and material["role"] == "primary", "source section needs primary material")
        string(section["locator"], "section locator")
        strings(section["objective_ids"], "section objectives")
        require(len(set(section["objective_ids"])) == len(section["objective_ids"])
                and set(section["objective_ids"]) <= objectives.keys(), "unknown/duplicate section objective")
        require(isinstance(section["reason"], str), "section reason must be text")
        if not section["objective_ids"]:
            string(section["reason"], "unmapped section needs a reason")
        for oid in section["objective_ids"]:
            require(any(r["material_id"] == section["material_id"] for r in objectives[oid]["sources"]),
                    "section objective must reference the same material")
    inventories = set()
    for inventory in spec["section_inventory"]:
        fields(inventory, ("material_id", "complete", "inspection_note"))
        require(inventory["material_id"] not in inventories, "duplicate material inventory")
        inventories.add(inventory["material_id"])
        require(type(inventory["complete"]) is bool, "inventory completeness must be boolean")
        string(inventory["inspection_note"], "source inspection and limitations")
        require(any(s["material_id"] == inventory["material_id"] for s in spec["source_sections"])
                or any(g["material_id"] == inventory["material_id"] for g in spec["source_gaps"]),
                "inventory needs sections or an explicit source gap")
    primary = {mid for mid, m in track["materials"].items() if m["role"] == "primary"}
    require(inventories == primary, "section inventory must account for every primary material")
    old_sections = {s["id"]: s for s in track.get("source_sections", [])}
    for section in spec["source_sections"]:
        old = old_sections.get(section["id"])
        if old:
            require((old["material_id"], old["locator"]) == (section["material_id"], section["locator"]),
                    "changed section identity needs a new ID")
    require(old_sections.keys() <= seen, "retain old sections and explain deferrals rather than deleting them")
