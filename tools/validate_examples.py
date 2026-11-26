#!/usr/bin/env python3
"""Check the machine-readable artifacts of this repository.

Run from the repository root:

    pip install -r tools/requirements.txt
    python3 tools/validate_examples.py

Checks:

* schemas/skill-interface-v1.json is a valid JSON Schema 2020-12 document
  and is identical to the schema in the "Skill Interface JSON Schema"
  appendix of the draft;
* the Schema Reference digest test vectors (JCS serialization and digest);
* the Skill Interface Document digest test vectors;
* every Skill Interface example (examples/ and the end-to-end example of
  the draft) against the Skill Interface Schema, plus the v1.0 rules that
  the schema alone cannot express: inline schema digests, kind/skill_id
  uniqueness, local-only references and the declared dialect;
* the instances of the draft end-to-end example (arguments, output,
  supporting record) against the inline domain schemas, including the
  negative cases listed in the draft.

Schema retrieval is disabled and "format" is evaluated as an assertion,
as required for interface version 1.0.
"""

import copy
import hashlib
import json
import re
import sys
from pathlib import Path

import rfc8785
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry
from referencing.exceptions import NoSuchResource

ROOT = Path(__file__).resolve().parent.parent
DRAFT = ROOT / "draft-huang-ainetops-agent-schema-interfaces.md"
SCHEMA = ROOT / "schemas" / "skill-interface-v1.json"
EXAMPLES = ROOT / "examples"
DIALECT = "https://json-schema.org/draft/2020-12/schema"
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

FORMAT_CHECKER = FormatChecker()
failures = []


def check(condition, message):
    print(("ok   " if condition else "FAIL ") + message)
    if not condition:
        failures.append(message)
    return condition


def digest(value):
    return "sha256:" + hashlib.sha256(rfc8785.dumps(value)).hexdigest()


def no_retrieval(uri):
    raise NoSuchResource(ref=uri)


def validator(schema):
    """Validator with format assertion and no network or file retrieval."""
    return Draft202012Validator(
        schema,
        registry=Registry(retrieve=no_retrieval),
        format_checker=FORMAT_CHECKER,
    )


def errors(schema, instance):
    return sorted(validator(schema).iter_errors(instance), key=str)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def draft_json_blocks():
    """Return the JSON code blocks of the draft as (line, text) pairs."""
    blocks, current, start = [], None, 0
    for n, line in enumerate(DRAFT.read_text(encoding="utf-8").splitlines(), 1):
        if current is None and re.match(r"^~~~+ *json\s*$", line):
            current, start = [], n
        elif current is not None and re.match(r"^~~~+\s*$", line):
            blocks.append((start, "\n".join(current)))
            current = None
        elif current is not None:
            current.append(line)
    return blocks


def parsed_blocks():
    out = []
    for line, text in draft_json_blocks():
        try:
            out.append((line, json.loads(text)))
        except json.JSONDecodeError:
            pass  # blocks with "..." placeholders are illustrative only
    return out


def walk(node):
    yield node
    if isinstance(node, dict):
        for v in node.values():
            yield from walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk(v)


def check_local_refs(schema, label):
    """Every $ref/$dynamicRef must stay inside resolution.schema."""
    ids = {n["$id"].split("#")[0] for n in walk(schema)
           if isinstance(n, dict) and isinstance(n.get("$id"), str)}
    bad, dialects = [], set()
    for n in walk(schema):
        if not isinstance(n, dict):
            continue
        if isinstance(n.get("$schema"), str):
            dialects.add(n["$schema"])
        for key in ("$ref", "$dynamicRef"):
            ref = n.get(key)
            if isinstance(ref, str) and not ref.startswith("#") \
                    and ref.split("#")[0] not in ids:
                bad.append(ref)
    check(not bad, f"{label}: no external reference {bad or ''}".rstrip())
    check(dialects <= {DIALECT}, f"{label}: embedded resources use {DIALECT}")


def check_schema_reference(ref, label):
    check(ref["dialect"] == DIALECT, f"{label}: dialect is JSON Schema 2020-12")
    schema = ref["resolution"]["schema"]
    try:
        Draft202012Validator.check_schema(schema)
        ok = True
    except Exception as e:  # noqa: BLE001
        print(f"     {e}")
        ok = False
    check(ok, f"{label}: inline schema is a valid 2020-12 schema")
    check(digest(schema) == ref["digest"], f"{label}: digest {ref['digest']}")
    check_local_refs(schema, label)


def check_interface(doc, label, interface_schema):
    errs = errors(interface_schema, doc)
    for e in errs:
        print(f"     {e.json_path}: {e.message}")
    if not check(not errs, f"{label}: valid against skill-interface-v1.json"):
        return
    check_schema_reference(doc["input_schema"], f"{label} input_schema")
    check_schema_reference(doc["output_schema"], f"{label} output_schema")
    kinds = [r["kind"] for r in doc.get("supporting_record_schemas", [])]
    check(len(kinds) == len(set(kinds)), f"{label}: supporting record kinds are unique")
    check(doc["skill_id"] not in kinds, f"{label}: no kind equals skill_id")
    for r in doc.get("supporting_record_schemas", []):
        check_schema_reference(r["schema_reference"], f"{label} record '{r['kind']}'")


def main():
    interface_schema = load(SCHEMA)

    # 1. The Skill Interface Schema itself.
    Draft202012Validator.check_schema(interface_schema)
    check(interface_schema.get("$schema") == DIALECT,
          "skill-interface-v1.json is a valid JSON Schema 2020-12 document")
    blocks = parsed_blocks()
    appendix = [b for _, b in blocks
                if isinstance(b, dict) and b.get("$schema") == DIALECT
                and "interface_version" in b.get("properties", {})]
    check(len(appendix) == 1 and appendix[0] == interface_schema,
          "skill-interface-v1.json matches the schema appendix of the draft")

    # 2. Format assertion really works (missing optional dependency
    #    would silently turn "date-time" back into an annotation).
    check(bool(errors({"format": "date-time"}, "not-a-timestamp")),
          "format \"date-time\" is evaluated as an assertion")

    # 3. Schema Reference digest test vectors.
    for v in load(EXAMPLES / "schema-digest-test-vectors.json"):
        jcs = rfc8785.dumps(v["resolution_schema"])
        check(jcs == v["jcs_utf8"].encode("utf-8"), f"schema vector '{v['name']}': JCS")
        check(digest(v["resolution_schema"]) == v["digest"],
              f"schema vector '{v['name']}': digest")

    # 4. Skill Interface Document digest test vectors.
    for v in load(EXAMPLES / "interface-digest-test-vectors.json"):
        doc = load(EXAMPLES / v["document"])
        check(DIGEST_RE.match(v["interface_digest"]) is not None
              and digest(doc) == v["interface_digest"],
              f"interface vector '{v['name']}': {v['interface_digest']}")

    # 5. Skill Interface examples in examples/.
    for path in sorted(EXAMPLES.glob("*.json")):
        doc = load(path)
        if isinstance(doc, dict) and "interface_version" in doc:
            check_interface(doc, path.name, interface_schema)

    # 6. End-to-end example of the draft.
    described = [(n, b) for n, b in blocks
                 if isinstance(b, dict) and b.get("skill") == "describe_skill"
                 and "result" in b]
    if not check(len(described) == 1, "draft: one complete describe_skill result"):
        return
    line, wrapper = described[0]
    doc = wrapper["result"]["interface"]
    label = f"draft line {line}"
    check_interface(doc, label, interface_schema)
    check(digest(doc) == wrapper["result"]["interface_digest"],
          f"{label}: interface_digest {wrapper['result']['interface_digest']}")

    invocations = [b for _, b in blocks if isinstance(b, dict)
                   and b.get("skill") == doc["skill_id"] and "arguments" in b]
    tasks = [b for _, b in blocks if isinstance(b, dict) and "artifacts" in b]
    if not check(len(invocations) == 1 and len(tasks) == 1,
                 "draft: one invocation and one completed task"):
        return
    call, task = invocations[0], tasks[0]
    check(call["skill_version"] == doc["skill_version"]
          and call["interface_digest"] == wrapper["result"]["interface_digest"],
          "draft invocation echoes skill_version and interface_digest")

    in_schema = doc["input_schema"]["resolution"]["schema"]
    out_schema = doc["output_schema"]["resolution"]["schema"]
    records = {r["kind"]: r["schema_reference"]["resolution"]["schema"]
               for r in doc.get("supporting_record_schemas", [])}
    check(not errors(in_schema, call["arguments"]),
          "draft arguments are valid against input_schema")

    result, record_parts = None, []
    for artifact in task["artifacts"]:
        data = artifact["parts"][0]["data"]
        if data.get("skill") == doc["skill_id"]:
            result = data["result"]
        else:
            record_parts.append((artifact["name"], data))
    check(result is not None and not errors(out_schema, result),
          "draft output is valid against output_schema")
    for kind, record in record_parts:
        check(kind in records and not errors(records[kind], record),
              f"draft record '{kind}' is valid against its schema")
    refs = set((result or {}).get("supporting_record_refs", []))
    check(refs <= {r.get("record_id") for _, r in record_parts},
          "draft supporting_record_refs resolve to returned records")

    # Negative cases stated at the end of the draft example.
    bad = copy.deepcopy(call["arguments"])
    bad["condition"].pop("unit", None)
    check(bool(errors(in_schema, bad)), "draft: input without 'unit' is rejected")
    if result is not None:
        bad = dict(result, result="not_a_declared_value")
        check(bool(errors(out_schema, bad)), "draft: undeclared output result is rejected")
    for kind, record in record_parts:
        bad = {k: v for k, v in record.items() if k != "observed_at"}
        check(bool(errors(records[kind], bad)),
              f"draft: record '{kind}' without 'observed_at' is rejected")
        bad = dict(record, observed_at="yesterday")
        check(bool(errors(records[kind], bad)),
              f"draft: record '{kind}' with a non RFC 3339 'observed_at' is rejected")


if __name__ == "__main__":
    main()
    print()
    if failures:
        print(f"{len(failures)} check(s) failed")
        sys.exit(1)
    print("all checks passed")
