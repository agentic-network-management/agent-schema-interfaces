# Meeting Review Guide

## Schema Interfaces for Network Management Agent Skills

This guide provides a concise narrative for presenting and reviewing the
Internet-Draft. It is supporting material and is not part of the normative
specification.

## Opening

Agent-to-Agent protocols provide agent advertisement, task submission,
lifecycle state, streaming, polling, cancellation, and result transport. They
do not define the domain-specific input and output schemas used by individual
skills.

This draft fills that gap by defining how a client agent retrieves and
validates a versioned, machine-readable skill interface before delegating
work. The objective is to replace an expanding collection of bilateral,
vendor-specific integrations with one predictable schema-interface
procedure.

## 1. Problem statement

An Agent Card can identify an available skill, but it does not provide enough
information for a client to determine:

- the exact application data accepted by the skill;
- the structure and meaning of the skill output;
- the supporting records that may accompany the output;
- how those inputs, outputs, and records are versioned; or
- how to validate them before they are consumed or acted upon.

Without a standardized interface-retrieval procedure, an orchestrator needs a
separate configured contract or adapter for every remote agent and skill.
That approach becomes difficult to govern and scale across independently
developed agents and multiple vendors.

## 2. Three standardized components

The draft standardizes three reusable components.

### Schema Reference

A Schema Reference provides:

- a stable schema URI;
- a schema version;
- the JSON Schema dialect;
- a SHA-256 content digest; and
- the inline schema content.

The common reference structure is used for input, output, and
supporting-record schemas.

### Skill Interface Document

A Skill Interface Document describes one version of one skill. It combines:

- the skill's domain-specific input schema;
- its domain-specific output schema;
- its supporting-record schemas;
- supported interaction modes; and
- descriptive authority metadata.

The standardized structure does not standardize every domain payload. Vendors
and domain organizations continue to own their domain schemas.

### `describe_skill`

An agent advertises `describe_skill` in its Agent Card. A client uses this
skill to retrieve the previously assembled and validated Skill Interface
Document for an advertised domain skill.

## 3. End-to-end flow

The main client flow is:

1. Retrieve the target Agent Card.
2. Confirm that `describe_skill` and the desired domain skill are advertised.
3. Select the advertised Skill Interface and domain-skill versions.
4. Call `describe_skill` with the selected `skill_id`.
5. Validate the returned document against the trusted Skill Interface Schema.
6. Confirm that the returned interface and skill versions match the versions
   selected before the request.
7. Verify every inline domain schema against its SHA-256 digest.
8. Validate the domain input against `input_schema`.
9. Delegate the task through A2A.
10. Validate the returned domain output and supporting records.

The remote agent also validates the input before processing it. Validation is
therefore performed at both trust boundaries.

Input constraints are specified by the skill's domain-specific
`input_schema`; the common framework does not define a universal constraint
vocabulary. A receiving agent must enforce a transmitted constraint or reject
the invocation with `constraint_rejected`. It must not silently ignore a valid
constraint. Constraints enforced solely by the orchestrator do not need to be
transmitted, and runtime authorization and deployment policy remain separate
from input constraints.

## 4. Deliberately narrow version 1.0 scope

Version 1.0 intentionally chooses a small, deterministic starting point:

- schemas are delivered inline;
- SHA-256 is the only digest algorithm;
- interface and skill versions are selected before `describe_skill`;
- `describe_skill` does not perform in-band version negotiation;
- registries, bundles, packaging, and caches are deployment-local management
  mechanisms;
- no registry product or registry API is required; and
- the draft does not define the concrete mapping to A2A messages, Parts,
  artifacts, metadata, or extensions.

An A2A Binding Profile or deployment specification defines that final wire
mapping. Conformance to this draft establishes schema-interface conformance;
it does not by itself establish complete A2A wire interoperability.

## 5. Structural validation is not authorization

Schema validation establishes structural conformance. It does not establish:

- caller identity;
- permission to execute a skill;
- approval for a side effect;
- semantic correctness;
- operational safety; or
- the truth of an output or supporting record.

The Skill Interface `authority` member is descriptive metadata. It is not a
credential, entitlement, capability, approval record, or authorization token.

At runtime, the receiving agent or hosting platform must authenticate the
caller and authorize the requested skill, resources, operation, and applicable
constraints. Deployments may use RBAC, ABAC, capabilities, external policy
decision points, or human or automated approval workflows.

## 6. Outputs and supporting records

The skill output is the result, decision, or deliverable normally consumed by
the caller. Supporting records are domain-specific observations or artifacts
used to derive, validate, reproduce, or audit that output.

The draft does not define a universal claim, output, or supporting-record
envelope. Each domain schema defines its own record structure, including any
identifier, source, producer, observation time, integrity, derivation, or
classification fields it requires.

When particular supporting records justify a result, the domain output schema
should define stable references to those records. References should survive
retransmission and later task-result retrieval. Array positions, message
ordering, and other transient transport locations should not be used as
provenance links.

## 7. Multi-agent composition

When an upstream output becomes a downstream input, the delegating component
may be a centralized orchestrator or the upstream agent itself.

Version 1.0 permits direct composition only when the upstream output Schema
Reference and downstream input Schema Reference have exactly the same:

- `schema_uri`;
- `version`;
- `dialect`; and
- `digest`.

This is intentionally conservative. Two schemas can have similar structures,
or both accept the same instance, while assigning different meanings, units,
defaults, constraints, or operational consequences to their fields. Exact
matching provides a deterministic decision without requiring domain
interpretation, in-band negotiation, or a common compatibility algorithm.

The rule does not assert that different schemas can never interoperate. It
only limits what version 1.0 recognizes as direct composition. Transformation
between different schemas is outside the direct-composition procedure.

Each downstream delegation creates a new A2A task. The upstream task ID must
not be reused as the downstream task ID. The delegating component should keep
a correlation mapping containing the participating agent identities or
endpoints, skill IDs, task IDs, and timestamps for observability, audit, and
troubleshooting.

## 8. Machine-readable failure conditions

The draft defines these failure conditions:

- `skill_not_advertised`;
- `unsupported_interface_version`;
- `interface_unavailable`;
- `interface_invalid`;
- `constraint_rejected`;
- `authorization_failed`; and
- `resource_limit_exceeded`.

The applicable A2A Binding Profile or deployment specification defines the
actual error envelope and whether a condition is represented as a protocol
error, failed task, structured message, or another A2A element. Error
conditions are not domain skill outputs and are not validated against the
skill's `output_schema`.

## 9. Security and implementation limits

Implementations must treat schemas, model output, CLI text, tool output, and
supporting records as untrusted data. They must also enforce limits on:

- schema and payload size;
- nesting and reference depth;
- reference cycles;
- schema compilation time; and
- cache consumption.

Version 1.0 does not define numeric interoperability minima. A Binding Profile
or deployment specification may define minimum supported capacities or
maximum interoperable sizes.

## 10. Implementation experience

The framework has been exercised using an orchestrating client and multiple
independently implemented domain agents. The prototype demonstrates that a
single client can:

- retrieve interfaces through `describe_skill`;
- validate the common interface structure;
- verify inline schemas and digests;
- validate domain requests and responses; and
- interact with agents that expose different domain skills.

Product-specific examples are useful implementation evidence but remain
outside the vendor-neutral draft.

## Questions for reviewers

The meeting should seek feedback on the following decisions:

1. Is advertising `describe_skill` as an A2A skill the right interface
   retrieval mechanism?
2. Should the concrete A2A binding be part of this document or a separate
   Binding Profile?
3. How should supported Skill Interface and domain-skill versions be
   represented in an Agent Card?
4. Is exact-match direct composition appropriate for version 1.0?
5. Should a future interface version support registry or agent-hosted schema
   delivery?
6. Should the draft define a canonical JSON serialization for calculating
   schema digests?
7. Are the machine-readable error conditions sufficient?
8. Are additional privacy requirements needed for supporting records and
   their stable references?
9. Which numeric resource limits, if any, belong in a future A2A Binding
   Profile?

The digest-serialization question deserves particular attention. Version 1.0
fixes SHA-256, but fully interoperable verification also requires agreement on
the exact serialized bytes over which the digest is calculated.

## Suggested closing

This proposal does not attempt to standardize every network-management
payload. It standardizes how an agent declares, retrieves, verifies, and uses
the schemas for a particular skill. The intended outcome is one predictable
schema-interface procedure that can replace a growing collection of bilateral
agent integrations.
