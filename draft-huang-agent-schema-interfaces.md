---
title: "Schema Interfaces for Network Management Agent Skills"
abbrev: "Agent Schema Interfaces"
category: std

docname: draft-huang-agent-schema-interfaces-latest
submissiontype: IETF
number:
date:
consensus: false
v: 3
area: "Operations and Management"
keyword:
  - network management
  - network management agents
  - schema interfaces
  - interface retrieval
  - agent interoperability
venue:
  github: "agentic-network-management/agent-schema-interfaces"

author:
  -
    fullname: "Scott Huang"
    organization: "Cisco Systems, Inc."
    email: "scohuang@cisco.com"
  -
    fullname: "Fu Yu"
    organization: "China Telecom"
    email: "fuy44@chinatelecom.cn"
  -
    fullname: "Dan Voyer"
    organization: "Cisco Systems, Inc."
    email: "davoyer@cisco.com"

normative:
  A2A:
    title: "Agent2Agent Protocol Specification, Version 1.0.1"
    target: "https://a2a-protocol.org/v1.0.1/specification/"
  JCS:
    title: "JSON Canonicalization Scheme (JCS)"
    seriesinfo:
      RFC: 8785
  JSON-SCHEMA:
    title: "JSON Schema: A Media Type for Describing JSON Documents"
    target: "https://json-schema.org/draft/2020-12/json-schema-core.html"
  JSON-SCHEMA-VALIDATION:
    title: "JSON Schema Validation: A Vocabulary for Structural Validation of JSON"
    target: "https://json-schema.org/draft/2020-12/json-schema-validation.html"
  JSON-POINTER:
    title: "JavaScript Object Notation (JSON) Pointer"
    seriesinfo:
      RFC: 6901
  TIMESTAMP:
    title: "Date and Time on the Internet: Timestamps"
    seriesinfo:
      RFC: 3339

informative:
  IDL:
    title: "IDL: A Semantic Information Model for Agent Communication"
    target: "https://datatracker.ietf.org/doc/draft-feng-agentproto-idl-info-model/"

...

--- abstract

Network management agents can use an Agent-to-Agent protocol for task
exchange. The protocol alone does not define the application schemas used by
independently developed network management agent skills.

This document standardizes four components for schema-governed network
management agent skills: Schema References, per-skill Skill Interface
Documents, advertisement and retrieval through an A2A extension and
`describe_skill`, and the A2A mapping for interface version 1.0. Together,
they enable clients to retrieve and validate the application schemas used for
skill inputs, outputs, and supporting records.

--- middle

# Introduction {#intro}

Agent-to-Agent task exchange requires agreement at two different layers:

1. a protocol for agent discovery, task identity, lifecycle, streaming,
   polling, cancellation, and result transport; and
2. application schemas that define the meaning of the skill input, output,
   deliverables, and supporting records.

The Agent2Agent (A2A) protocol {{A2A}} defines agent discovery, message transport,
task lifecycle, streaming, polling, cancellation, and artifact delivery. It
does not define the domain-specific input, output, or supporting-record
schemas used by individual skills, nor a common interface for retrieving and
validating those schemas. This document addresses that application-schema gap
while leaving A2A task and transport semantics unchanged.

Network operations workflows may involve agents supplied by different
vendors, operating in different administrative domains, and implemented using
different model architectures. These agents may need to cooperate to
decompose, delegate, execute, and verify complex operational tasks. Such
cooperation requires exchanges of task objectives, operational context,
constraints, diagnostic requests, supporting records, and risk assessments
across agent boundaries. When independently implemented agents govern these
artifacts through bilateral assumptions rather than declared, machine-readable
per-skill interfaces, end-to-end workflows become fragile, difficult to
reproduce, and difficult to audit.

Agent discovery and the schema-interface procedure are distinct. Agent
discovery determines which agent to contact and how to reach it. The
schema-interface procedure defined in this document occurs after an agent has
been identified and provides the machine-readable interface for invoking one
of its advertised skills. This document does not define how agents are found,
selected, ranked, or matched to user intent.

A common protocol envelope can deliver a JSON object without making that
object semantically interoperable. If the original input and an upstream
agent's result are opaque text or unconstrained JSON, a downstream agent must
infer their meaning. Such inference may be useful for human-oriented content,
but it is not an adequate substitute for a declared interface when agents make
operational decisions or generate network changes.

The framework is intended to support independently developed agents from
different network-management domains without forcing their domain payloads
into one universal schema.

# Terminology {#terminology}

## Network Management Agent

A software component that performs or assists with network-management work,
including analysis, configuration, assurance, incident handling, validation,
simulation, or remediation.

## Client Agent

An A2A Client that identifies and contacts a remote agent, obtains and
validates its Skill Interface Documents, and delegates tasks on behalf of a
user or another system. This term describes a protocol role and does not imply
administrative control over the remote agent.

## Remote Agent

An A2A Server that publishes an Agent Card, exposes skills, receives delegated
tasks, and returns task status and results.

## Network-Management Domain

An application subject area, such as planning, assurance, configuration, or
incident analysis, whose owner defines the meaning of its skill inputs,
outputs, and supporting records. A domain is a schema-governance boundary; it
does not create a global namespace for skill identifiers.

## Delegation Hop

The relationship created when an agent handling one A2A Task invokes a skill
at another agent, thereby creating a distinct downstream A2A Task. The task
handled by the invoking agent is the upstream task, and the newly created task
is the downstream task.

## Schema Reference

A portable schema identity, integrity information, and inline schema content.
The identity and digest remain independent of any deployment-local mechanism
used to manage the schema before the Skill Interface Document is assembled.

## Version String

A canonical version identifier consisting of two dot-separated non-negative
decimal integers, `MAJOR.MINOR`. A component has no leading zero unless its
value is zero. Two versions are equal only when both numeric components are
equal; the canonical representation makes this equivalent to string equality.
A change that is not backward compatible with consumers of the prior version
increments `MAJOR` and resets `MINOR` to zero. A backward-compatible change
increments `MINOR`. This syntax and comparison rule apply to `skill_version`
and to the `version` in each Schema Reference. The version of the Skill
Interface Schema is separately identified by `interface_version`, which this
document fixes at `1.0`.

## Skill

A named capability advertised by an agent and invokable through an
Agent-to-Agent protocol. A skill identifier is scoped to the Agent Card in
which it is advertised and is not globally unique. Portable schema identity is
provided by the Schema Reference rather than by the skill identifier alone.

## Skill Interface Schema

The standardized, language-neutral schema that defines the permitted
structure and interpretation of a Skill Interface Document. An agent uses a
local or otherwise trusted copy of this schema to validate the documents it
publishes. A client agent uses the same schema version to validate retrieved
documents.

## Skill Interface Document

A machine-readable description of a skill's accepted input, produced output,
possible supporting records, interaction behavior, and applicable constraints.
It is an instance of the Skill Interface Schema. It contains domain-specific
Schema References supplied by the agent without modifying the standardized
Skill Interface Schema.

## Skill Interface Document Digest

The `interface_digest` value identifies the exact Skill Interface Document
selected by a client.  It is the string `sha256:` followed by the lowercase
hexadecimal representation of the SHA-256 digest of the UTF-8 encoding of the
complete Skill Interface Document serialized using the JSON Canonicalization
Scheme (JCS) {{JCS}}.

The digest covers every member of the Skill Interface Document, including its
inline domain schemas.  It does not cover the standardized Skill Interface
Schema used to validate the document, the Agent Card, a `describe_skill`
response wrapper, or a domain-skill invocation.  The `interface_digest` is
carried outside the Skill Interface Document so that the document does not
contain a digest of itself.

The same Skill Interface Document Digest MUST be carried in the Agent Card
extension advertisement, the `describe_skill` response, and each domain-skill
invocation that uses the document.  All three carried values and the digest
calculated from the returned document MUST match.

## Supporting Record

A domain-specific observation or artifact used to derive, validate, reproduce,
or audit a skill output. A supporting record is validated against the
applicable schema identified by the Skill Interface Document.

## A2A Artifact Identifier

The task-scoped `artifactId` assigned to an A2A Artifact as defined by A2A
{{A2A}}. It identifies an Artifact within an A2A Task and can be used by a
skill output to reference a supporting-record Artifact carried by that Task.
It is not a globally portable record identifier.

The following figure summarizes the structure of a Skill Interface Document:

```text
Skill Interface Document
|-- interface_version
|-- skill_id
|-- skill_version
|-- input_schema -------------------- Schema Reference
|   |-- schema_uri
|   |-- version
|   |-- dialect
|   |-- digest
|   `-- resolution
|       |-- type = "inline"
|       `-- schema
|-- output_schema ------------------- Schema Reference
|-- supporting_record_schemas[]
|   |-- kind
|   `-- schema_reference ------------ Schema Reference
|-- interaction
|   |-- supported_response_modes[]
|   `-- cancellable
`-- authority
    |-- default_mode
    `-- approval_may_be_required
```

# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Scope

This document standardizes:

- a common Schema Reference structure for identifying, verifying, and
  carrying inline schemas;
- a Skill Interface Schema and a conforming per-skill Skill Interface
  Document;
- a Skill Interface advertisement and retrieval procedure using an A2A
  extension and `describe_skill`; and
- an A2A mapping for carrying domain-skill inputs, outputs, supporting
  records, and machine-readable errors for interface version 1.0.

The mapping operates on top of A2A. It maps the fields defined by this
document to existing A2A Messages, Data Parts, Tasks, Artifacts, and status
messages without changing A2A operations, data objects, lifecycle semantics,
or protocol bindings. An implementation claiming conformance to interface
version 1.0 for exchanges over A2A MUST use this mapping.

This document does not define:

- the internal algorithm used by an agent;
- a universal schema for every network-management domain;
- a required schema-registry product or API;
- a globally centralized schema service;
- agent hosting, process lifecycle, or platform onboarding;
- an authorization policy model, including RBAC, ABAC, capabilities, policy
  engines, or approval workflows;
- a grant of authority based on schema or interface validation; or
- a new A2A transport or protocol binding.

# Relationship to Other Work

The "IDL: A Semantic Information Model for Agent Communication"
Internet-Draft {{IDL}} describes agent-wide identity, capabilities, autonomy
boundaries, context requirements, governance interfaces, and intent
participation. It includes optional input-context and output-schema
declarations, but it does not define a normative serialization or a per-skill
interface-retrieval procedure.

This document has a narrower scope. It defines a normative representation for
one version of one callable skill, including its input, output, and
supporting-record schemas, and defines the `describe_skill` retrieval and
validation procedure. The two models can be used together: an agent-wide
semantic description can identify a capability, while a Skill Interface
Document supplies the concrete application schemas used to invoke a selected
skill. A formal mapping between the two models is outside the scope of this
document.

# Design Principles

## Preserve task identity across delegation hops

When an agent handling an upstream A2A Task invokes another agent, the
downstream invocation creates a distinct A2A Task at the receiving agent. A
delegating component MUST NOT reuse the upstream task identifier as the
downstream protocol task identifier. Protocol task identifiers are interpreted
in the scope of the agent or endpoint that issued them; implementations MUST
NOT assume that they are globally unique. An implementation that needs to
correlate the two tasks MUST record their relationship using separately named
metadata rather than overloading either protocol task identifier.

## Standardize reusable structures, not all domain semantics

This framework standardizes reusable interface metadata, not the semantics of
every network-management domain. A vendor or domain owner defines the input,
output, and supporting-record schemas used by a particular skill and combines
them with the common structure; it does not redefine that structure. The
domain determines schema meaning and governance, while the skill identifier
selects one callable capability within an agent's advertised Agent Card.

## Distinguish structural conformance from semantic conformance

Matching Schema References establishes that communicating agents use the same
schema; it does not establish that the schema exposes sufficient semantics for
the intended operation. A schema that defines configuration only as a string
can validate the presence and type of that string but cannot by itself identify
affected resources, validate command dependencies, or establish that the
commands implement the requested intent.

When a skill-specific specification requires a receiving agent to inspect,
validate, transform, simulate, or apply a configuration change, that
specification MUST identify a machine-readable representation with sufficient
semantics for the required processing.  The applicable input, output, or
supporting-record schema describes that representation, and `describe_skill`
makes the schema available before delegation.  The receiving agent MUST
validate the representation and use a domain-specific implementation for
semantic validation, policy evaluation, simulation, or application, as
applicable.

## Deliver schemas inline in version 1.0

Every v1.0 Schema Reference returned by `describe_skill` MUST carry its schema
content inline. A client agent validates that embedded content against the
declared digest and does not contact an external service to complete the
interface.

An inline schema MAY be a compound schema document containing embedded schema
resources as defined by JSON Schema {{JSON-SCHEMA}}.  Every `$ref` and
`$dynamicRef` in `resolution.schema` MUST resolve to the root schema, one of
its subschemas, or an embedded schema resource contained within that same
`resolution.schema` value.  Each embedded schema resource used as a reference
target MUST identify itself with an absolute URI in `$id`.  References MAY
retain an absolute URI when that URI resolves to such an embedded resource;
an absolute URI does not permit external retrieval.

Validators MUST perform schema and instance validation with network and
filesystem schema retrieval disabled.  The only schema content a validator
may use from outside `resolution.schema` is a locally trusted copy of the
meta-schema identified by the Schema Reference's `dialect`.  Embedded schema
resources MUST use that same dialect.  A reference that cannot be resolved
under these rules, an attempted external retrieval, or an embedded resource
that selects another dialect makes the Skill Interface Document invalid and
MUST result in `interface_invalid`.

For interface version 1.0, a `format` value defined by JSON Schema Validation
{{JSON-SCHEMA-VALIDATION}} MUST be evaluated as an assertion during instance
validation. This is an additional interface version 1.0 conformance rule even
when the referenced JSON Schema dialect would otherwise treat `format` as an
annotation. In particular, an instance validated against `"format":
"date-time"` MUST conform to the Internet timestamp syntax defined by
{{TIMESTAMP}}.

Registries, bundles, caches, and agent packaging MAY be used locally to store,
govern, distribute, or prepare schemas. Their use does not alter the v1.0
wire representation, and a client agent is not required to know which local
mechanism supplied an inline schema. Version 1.0 does not require the schema to
originate in either an agent package or a central registry; either can be a
deployment-local source used before the complete inline document is served.

## Distinguish outputs from supporting records

The skill output states what the agent concluded or delivered. Supporting
records explain why that output can be trusted, reproduced, or audited. An
output and a supporting record use separate A2A Artifacts. An output that
depends on a supporting record SHOULD reference that record's task-scoped A2A
`artifactId` rather than duplicate its content.

## Assemble and validate before advertisement

An agent implementation owns its domain-specific input, output, and
supporting-record schemas. Its protocol service combines those schemas with a
trusted copy of the standardized Skill Interface Schema and applicable
interaction and authority declarations. The resulting Skill Interface
Document MUST be validated before it is advertised or returned.

An implementation SHOULD perform this assembly during agent initialization or
deployment configuration and retain an immutable validated document for each
skill version.
The `describe_skill` operation retrieves that document. It does not ask the
agent's domain logic to construct or alter an interface while processing the
interface request.

# Schema Reference

This document standardizes one Schema Reference structure for all schema
roles. Skill-input, skill-output, and supporting-record schemas do not
require different reference structures or delivery mechanisms.

A Schema Reference contains:

- `schema_uri`: stable portable identity;
- `version`: version meaningful to the schema publisher;
- `dialect`: schema language and version;
- `digest`: digest of the embedded schema content; and
- `resolution`: inline delivery information. In version 1.0 its `type` is
  `inline` and its `schema` member contains the schema content.

Version 1.0 fixes the digest algorithm to SHA-256.  To calculate `digest`, an
implementation MUST serialize the JSON value in `resolution.schema` using JCS
{{JCS}}, encode that canonical representation as UTF-8, and calculate SHA-256
over exactly those bytes.  The `digest` value MUST be the lowercase string
`sha256:` followed by exactly 64 lowercase hexadecimal digits representing
that result.  The digest covers only the `resolution.schema` value.  It does
not cover `resolution.type` or any other member of the enclosing Schema
Reference, including `schema_uri`, `version`, `dialect`, or `digest`.

This separation is intentional. The schema digest is a content digest for the
embedded JSON Schema value, while `schema_uri`, `version`, and `dialect`
provide identity and interpretation metadata. A conforming implementation
compares the complete Schema Reference, not the digest alone. The Skill
Interface Document Digest additionally covers the complete document, including
each Schema Reference's identity, version, dialect, digest, and inline content,
and therefore detects modification or substitution of that metadata.

The embedded schema MUST satisfy the JCS input requirements.  Differences in
insignificant JSON whitespace, object-member order, or a permitted alternate
JSON string escape do not change the digest because they produce the same JCS
representation.  A change to the JSON value represented by
`resolution.schema` changes the digest.  Version 1.0 does not define
digest-algorithm negotiation, and a value using another algorithm identifier
is invalid.

Version 1.0 Schema References MUST use `resolution.type` equal to `inline` and
MUST include the schema in `resolution.schema`. They MUST NOT contain an
external schema locator in place of the embedded content.

# Skill Interface Schema and Documents {#skill-interface-documents}

The Skill Interface Schema standardizes the structure shown in this section.
A Skill Interface Document is a conforming instance for one skill version. It
binds the domain schemas used by that skill to its input, output,
supporting-record, interaction, and authority characteristics.

The agent or domain owner supplies the skill identifier, skill version, and
domain input, output, and supporting-record schemas. The agent protocol
service assembles the complete document. Interaction declarations reflect the
agent implementation.
Authority declarations may additionally reflect deployment policy. Assembly
MUST NOT modify the standardized Skill Interface Schema.

The normative definitions of `authority`, `default_mode`, and
`approval_may_be_required` appear in {{skill-interface-json-schema}}. The
structural figure in {{terminology}} shows their location within a Skill
Interface Document.

The `authority` member is descriptive metadata about the operating posture an
agent advertises for a skill. `default_mode` describes that advertised default
posture; it does not grant the caller permission to use that mode.
`approval_may_be_required` indicates that an approval requirement may apply;
it does not assert that approval has been requested, granted, or remains
valid. The `authority` member is not a credential, capability, entitlement,
access-control decision, approval record, or authorization token. A client or
remote agent MUST NOT treat it as permission to execute a skill or cause a
side effect.

Version 1.0 defines the following `default_mode` values:

- `observe_only`: the default behavior reads or analyzes information and does
  not propose or apply an operational change;
- `recommend_only`: the default behavior may produce a proposed action or
  change but does not apply it; and
- `execute`: the default behavior may cause an operational side effect.

These values describe behavior, not authorization. In every mode, the agent
MUST perform the runtime authorization and approval checks required below.

Version 1.0 permits both a separate skill for each operation and multiple
operations within one skill. One operation per skill is preferred because it
gives each operation an independent interface and authority declaration.
Authors SHOULD expose operations with materially different effects or approval
requirements as separate skills. The `authority` member describes the skill as
a whole; it does not describe the effect of each operation selected within a
multi-operation skill. If one skill supports multiple operations, its
`input_schema` MUST require an unambiguous operation selector, enumerate the
permitted operations, and define any operation-specific input requirements.
Schema annotations SHOULD describe the effect of each operation so that a
caller can understand the requested action before invocation. If any operation
may require approval,
`approval_may_be_required` MUST be `true`. The receiving agent MUST still
authorize the selected operation and enforce its applicable approval policy
for every request.

For example, an agent that can read and delete a managed resource can
advertise separate `read_resource` and `delete_resource` skills. This is the
preferred design because reading and deleting have materially different
effects. Alternatively, the agent can advertise one `manage_resource` skill
whose `input_schema` requires a `resource_id` and an `operation` value of
either `read` or `delete`. That schema should describe the effect of each
value, and the skill must advertise `approval_may_be_required` as `true` if
deletion may require approval. In either design, the agent authorizes the
specific requested operation at invocation time.

The interface version 1.0 A2A mapping identifies the protocol elements
containing skill input, skill output, and supporting records. Those values
are validated against the corresponding domain schemas in the selected Skill
Interface Document.

Successful schema or Skill Interface validation does not authorize execution.
Before processing an invocation, the receiving agent or hosting platform MUST
authenticate the caller and perform a current authorization decision covering
the requested skill, resources, operation, and applicable constraints. Before
causing a side effect, it MUST also enforce any approval or execution-control
requirements imposed by current deployment policy. Advertised `authority`
metadata does not replace these runtime decisions.

The receiving agent or hosting platform remains authoritative for every
runtime authorization and approval decision. The `authority` member can help a
client understand a skill's advertised operating posture, but it is not an A2A
capability declaration and cannot establish what a particular caller is
permitted to do.

## Skill input

The skill input is the domain-specific application data submitted to a skill
invocation. The input MUST validate against the `input_schema` in the selected
Skill Interface Document. The interface version 1.0 A2A mapping carries that
input in the `arguments` member of its skill request object. As
specified in {{domain-skill-invocation}}, that object is the `data` value of
the A2A user Message's single Data Part.

Constraints that affect skill execution MUST be represented in and validated
by the skill's `input_schema`. A receiving agent MUST enforce a supplied
constraint or reject the invocation with the `constraint_rejected`
machine-readable error condition defined in {{error-conditions}}; it MUST NOT
silently ignore a valid constraint. Constraints enforced solely by a
delegating system need not be transmitted. The names, structures, and
semantics of transmitted constraints are defined by the domain-specific input
schema rather than by this framework. Protocol lifecycle and authorization
controls remain the responsibility of A2A and deployment policy.

Version 1.0 applies `input_schema` to the complete `arguments` value in the
initial domain-skill invocation. If an A2A Task enters
`TASK_STATE_INPUT_REQUIRED`, a caller's follow-up Message may contain only the
information requested by the agent. Version 1.0 does not define a schema for
such follow-up data, and the follow-up is not independently validated against
`input_schema`. A deployment that requires schema-governed multi-turn input
needs an additional profile or separately advertised skill for that exchange.
The combined intermediate-exchange example in {{domain-skill-invocation}}
illustrates an input-required request, the caller's partial reply, and the
separate task identifiers used when another agent is invoked.

## Skill output

The skill output is the domain-specific application data produced by a skill
invocation. The output MUST validate against the `output_schema` in the
selected Skill Interface Document. The interface version 1.0 A2A mapping
carries that output in the `result` member of its skill result object. As
specified in {{domain-skill-invocation}}, that object is the `data` value of
the primary A2A Artifact's single Data Part.

Protocol task status indicates whether protocol execution completed; it is
not part of the skill output. Completion of a protocol task does not by itself
establish that a requested downstream network operation completed
successfully. The domain output schema defines how the skill reports the
result of that operation.

Version 1.0 applies `output_schema` to the complete final `result`, after any
streamed Artifact updates have been assembled. It does not apply independently
to A2A status Messages, progress updates, or incomplete Artifact chunks.
Version 1.0 therefore defines no separate streaming-output schema: A2A governs
delivery of partial Artifact updates, while this document validates the
assembled final result and each complete supporting record. The schema boundary
for each intermediate exchange is summarized in
{{domain-skill-invocation}}.
Supporting records and the primary output are separate Artifacts within the
same A2A Task. An agent MAY stream zero or more complete supporting-record
Artifacts before it produces the primary result Artifact. Each supporting
record validates independently against its declared supporting-record schema,
while the complete primary result validates against `output_schema`. A
supporting record does not merge with or replace the primary result, and the
final result MAY reference it by its A2A `artifactId`. An early finding
intended for independent machine consumption SHOULD be published as such a
supporting record.

## Supporting-record schemas

A supporting record is a domain-specific observation or artifact used to
derive, validate, reproduce, or audit a skill output. Each entry in
`supporting_record_schemas` associates a `kind` with the Schema Reference for
the complete record. A produced record MUST validate against the schema for
its identified kind. A protocol progress update is not a supporting record
unless it is published in that form and passes this validation.

Each supporting-record `kind` in a Skill Interface Document MUST be unique and
MUST NOT equal that document's `skill_id`. This prevents a supporting-record
Artifact from being confused with the primary result Artifact, whose `name`
equals `skill_id`.

This framework does not define an additional common record envelope. The
domain schema defines any required record identifier, producer, source,
observation time, production time, integrity, derivation, classification, or
payload fields. Under this mapping, each supporting record is carried in an
A2A Artifact belonging to the same A2A Task, so the record's domain schema
need not repeat the A2A task or context identifier.

When supporting records justify a skill output, the domain `output_schema`
SHOULD define where the output carries their references. For records carried
by the same A2A Task, each reference SHOULD identify the corresponding A2A
Artifact by `artifactId`. This document does not mandate a common property
name or reference structure within every domain output.

The skill output is the answer, decision, or deliverable normally consumed by
the caller. Supporting records contain the observations and artifacts that
support that output. They MUST be published in separate Artifacts. The output
SHOULD reference a supporting record by its `artifactId` instead of embedding
a duplicate copy.

# A2A Mapping for Interface Version 1.0

This section defines how interface version 1.0 maps schema-interface
operations and data to A2A Messages, Data Parts, Tasks, Artifacts, and status
messages. An implementation MAY use any A2A protocol binding that preserves
these protocol elements and their semantics.

## Agent advertisement

An agent conforming to this framework MUST advertise `describe_skill` and each
schema-governed domain skill in its Agent Card.  It MUST also advertise the
following A2A extension in `AgentCapabilities.extensions`:

```text
https://agentic-network-management.github.io/agent-schema-interfaces/extensions/schema-interface/v1
```

The extension MAY be marked `required: false` so that extension-unaware
clients can continue to use the agent through base A2A procedures.  A client
using the procedure in this document MUST activate the extension for
`describe_skill` and domain-skill requests as specified by A2A {{A2A}}.
When the HTTP binding is used, the client requests activation by including
the extension URI in the `A2A-Extensions` request header.  An agent that
activates the extension SHOULD echo that URI in the `A2A-Extensions` response
header, as specified by A2A.  The A2A Message `extensions` list MUST also
include the URI when the Message carries a request object defined by this
document.  The header performs extension activation; the Message field
identifies the extension as relevant to that Message.

The extension `params` MUST contain `interface_version` with value `1.0` and a
`skills` array.  Each entry MUST contain `skill_id`, `skill_version`, and
`interface_digest`.  The `skill_id` MUST identify an `AgentSkill` in the same
Agent Card.  The `interface_digest` MUST be the Skill Interface Document
Digest for the document returned by `describe_skill` for that skill.  Version
1.0 permits exactly one advertised `skill_version` and `interface_digest`
binding for each `skill_id` in an Agent Card.

The following fragment illustrates the extension advertisement:

```json
{
  "uri": "https://agentic-network-management.github.io/agent-schema-interfaces/extensions/schema-interface/v1",
  "description": "Schema interfaces for advertised skills",
  "required": false,
  "params": {
    "interface_version": "1.0",
    "skills": [
      {
        "skill_id": "example_skill",
        "skill_version": "1.0",
        "interface_digest": "sha256:..."
      }
    ]
  }
}
```

The client selects the advertised `skill_id`, `skill_version`, and
`interface_digest` before calling `describe_skill`.  Version 1.0 does not
define request parameters for negotiating or selecting another interface or
skill version within `describe_skill`.  An agent that needs to advertise
concurrent incompatible versions in version 1.0 MUST expose them using
distinct skill identifiers. A client selects one of those identifiers from
the Agent Card; it MUST NOT infer a version range or negotiate an unadvertised
version.

When an agent replaces an advertised interface with a backward-compatible
revision, it increments the minor `skill_version` and advertises the new
version and digest. During a migration in which old and new incompatible
interfaces must remain callable concurrently, the agent advertises them under
distinct skill identifiers. Deprecation periods and removal policy are
deployment concerns, but removal of an advertised version MUST be reflected
in a newly retrieved Agent Card before clients can select it for new work.

The `describe_skill` skill MUST accept structured input identifying the
selected `skill_id` and MUST produce structured output containing the
corresponding Skill Interface Document and its `interface_digest`.

A caller MUST NOT assume that every Agent-to-Agent implementation conforms to
this framework. Absence of either the schema-interface extension or the
`describe_skill` skill from the Agent Card means that the agent does not
provide the schema-interface procedure defined here.
Such an agent MAY still be invoked using the base Agent-to-Agent protocol or an
explicitly configured out-of-band interface contract. The caller MUST NOT
infer or prescribe the remote skill's domain schemas from skill descriptions
or media types alone, and MUST NOT claim schema-interface conformance or
schema-governed compatibility for such an invocation. Supporting multiple
non-conforming agents requires separately configured contracts, adapters, or
other bilateral integration mechanisms. This is the scaling problem addressed
by this document: replacing an expanding collection of bilateral integrations
with one standardized interface-retrieval procedure.

## `describe_skill` request {#describe-skill-request}

The request identifies one advertised skill by `skill_id`. It does not carry
`interface_version`, `skill_version`, a version range, or another in-band
negotiation parameter.

The client MUST invoke the A2A Send Message or Send Streaming Message
operation with a user-role Message containing exactly one Data Part. The
Data Part's `data` value MUST be the following request object:

```json
{
  "skill": "describe_skill",
  "arguments": {
    "skill_id": "example_skill"
  }
}
```

## `describe_skill` response

On success, the A2A task MUST reach the completed state and contain exactly
one Artifact. The Artifact `name` MUST be `describe_skill`, and the Artifact
MUST contain exactly one Data Part. Its `data` value MUST be the following
object, where the notation in angle brackets represents the complete Skill
Interface Document rather than a JSON string:

```text
{
  "skill": "describe_skill",
  "result": {
    "interface_digest": "sha256:...",
    "interface": <Skill Interface Document>
  }
}
```

The `result.interface` value is a Skill Interface Document conforming to the
advertised and previously selected version of the standardized Skill
Interface Schema.  Its `skill_version` MUST equal the advertised
domain-skill version selected before the request.  The
`result.interface_digest` value MUST equal the `interface_digest` advertised
for the selected skill.  The client MUST calculate the Skill Interface
Document Digest of `result.interface` and verify that it equals both values.
In version 1.0, every Schema Reference in the document MUST contain the
complete domain schema inline in `resolution.schema` and MUST set
`resolution.type` to `inline`.

The response MUST be the previously assembled and validated document for the
selected skill version. The `describe_skill` operation MUST NOT redefine the
standard structure or invoke domain logic to construct or modify the document
while processing the request. The returned input, output, and
supporting-record schemas remain specific to the selected agent and skill.

The selected document and its calculated digest MUST correspond to the skill
version and digest advertised by the agent. If an advertised interface cannot
currently be returned, the agent MUST report `interface_unavailable`. If the
available document is malformed, inconsistent with the selected skill,
versions, or digest, or otherwise fails required validation, the agent MUST
report `interface_invalid`. It MUST NOT accept or return an unvalidated opaque
payload as a substitute.

## Domain-skill invocation {#domain-skill-invocation}

After validating the selected Skill Interface Document, a client invokes the
domain skill with the A2A Send Message or Send Streaming Message operation.
The user-role Message MUST contain exactly one Data Part. The Data Part's
`data` value MUST be this skill request object:

```json
{
  "skill": "example_skill",
  "skill_version": "1.0",
  "interface_digest": "sha256:...",
  "arguments": {
    "objective": "Evaluate the selected network resource"
  }
}
```

The `skill` value MUST equal the selected Agent Card skill identifier.  The
`skill_version` and `interface_digest` values MUST equal the values selected
from the Agent Card extension, returned by `describe_skill`, and validated by
the client.  Before validating `arguments` or invoking domain logic, the
receiving agent MUST compare both values with its currently active Skill
Interface Document for that skill.  It MUST reject the request with
`interface_mismatch` if either value differs.  The `arguments` value is the
complete domain input and MUST validate against the selected Skill Interface
Document's `input_schema`. The receiving agent MUST reject a nonconforming
input with `input_invalid` before invoking domain logic.

Base A2A does not assign a primary role to an Artifact. This profile uses the
term *primary result Artifact* for the one Artifact that carries the final
skill output. It is identified by an Artifact `name` equal to the selected
skill identifier and by a single Data Part containing the skill result object
defined below.

On success, the task MUST reach the completed state and contain exactly one
primary result Artifact:

```json
{
  "skill": "example_skill",
  "result": {
    "status": "succeeded"
  }
}
```

The `result` value is the complete domain output and MUST validate against the
selected Skill Interface Document's `output_schema`.

Each supporting record, when present, MUST be carried in a separate Artifact.
The Artifact `name` MUST equal the record `kind` declared in
`supporting_record_schemas`, and its single Data Part MUST contain the complete
record value that validates against the Schema Reference associated with that
kind. The record `kind`, and therefore the supporting Artifact `name`, MUST NOT
equal the selected `skill_id`. The Artifact `artifactId` provides a stable
task-scoped identifier that the domain output MAY reference. A record
transported or retrieved outside the task requires a stable reference
mechanism defined by its domain schema.

The same final Task and Artifact requirements apply whether the client uses
synchronous completion, streaming updates, or task retrieval and polling.
For streaming, A2A governs Artifact-update delivery through `artifactId`,
`append`, and `lastChunk` {{A2A}}. When `append` is `true`, the event content is
appended to previously delivered content for the same Artifact. This profile
does not assign additional semantics to `append` when it is `false` or absent,
and does not define independent schema conformance for a partial update. A
client MAY process the A2A updates incrementally or retrieve the completed Task
using the A2A Get Task operation. In either case, the complete primary result
MUST validate against `output_schema`.

The following summary shows the schema boundary for intermediate exchanges in
version 1.0:

| Exchange | Schema applied by this document |
| Initial skill request `arguments` | `input_schema` |
| `TASK_STATE_INPUT_REQUIRED` status Message | None |
| Caller follow-up Message answering that request | None |
| Incomplete primary result Artifact update or chunk | No independent v1.0 validation; A2A update semantics apply |
| Complete final primary result Artifact `result` | `output_schema` |
| Complete supporting-record Artifact | Matching entry in `supporting_record_schemas` |

The *primary result Artifact* is the profile-defined Artifact described in
{{domain-skill-invocation}}; base A2A does not assign a primary role to an
Artifact. The following example combines the intermediate exchanges described
above:

```text
1. Initial request
   arguments validates against input_schema.

2. Status update: TASK_STATE_INPUT_REQUIRED
   The agent requests one missing credential reference. No schema for this
   status Message is defined by version 1.0.

3. Caller follow-up Message
   The caller sends only the requested credential reference. The reply
   augments the Task interaction; it does not replace the original input and
   is not independently validated against input_schema.

4. Supporting-record Artifact update
   artifactId="record-1", name="observation-record"
   The complete record validates against the advertised observation-record
   schema.

5. Incomplete primary result Artifact update
   artifactId="result-1", name="example_skill", lastChunk=false
   This update lacks fields required in the final result. A2A governs its
   delivery, and version 1.0 does not validate it independently against
   output_schema.

6. Complete primary result Artifact update
   artifactId="result-1", name="example_skill", lastChunk=true
   This final update contains the complete primary result. It validates
   against output_schema and may reference "record-1" as supporting
   information. A client may instead retrieve this complete Artifact from the
   Task using the A2A Get Task operation.

7. Status update: TASK_STATE_COMPLETED
   The agent reports completion only after validating the complete result.
```

If the receiving agent delegates work to another agent during this sequence,
that delegation creates a distinct downstream A2A Task. An input-required
status or Artifact belongs to the Task that emitted it. The delegating
component records the association between the upstream and downstream task
identifiers, qualified by their respective agent identities or endpoints; it
does not reuse either identifier for the other Task.

All Artifacts in this sequence belong to the same A2A Task. The supporting
record and primary result remain separate and each is validated against its
own advertised schema. Version 1.0 does not define separate schemas for
partial primary results or input-required replies.

## Machine-readable error conditions {#error-conditions}

An error detected locally by a client before the remote agent creates a task
MUST NOT be represented as a state of a nonexistent remote task. The client
MUST stop the applicable procedure and report the machine-readable condition
locally or through the error mechanism of its enclosing system.

When the remote agent reports one of the conditions below through an A2A Task,
the Task's final status Message MUST contain exactly one Data Part whose
`data` value has this form:

```json
{
  "error": {
    "code": "interface_invalid",
    "message": "The selected interface document is invalid"
  }
}
```

The `code` value MUST be one of the machine-readable conditions below or an
additional value defined by a future profile. The human-readable `message`
MAY be omitted. A server-side error detected before task creation MUST be
carried using the error mechanism of the selected A2A protocol binding and
SHOULD expose the same machine-readable code when that binding permits it.
These conditions are not skill outputs and are not validated against the
selected skill's `output_schema`.

The `interface_invalid` condition identifies a defect in the Skill Interface
Document or an embedded schema. It MUST NOT be used when a valid interface
rejects a particular data instance. Such instance failures use
`input_invalid`, `output_invalid`, or `constraint_rejected`, as applicable.

A remote Task MUST reach `TASK_STATE_REJECTED` when the request is understood
but is not accepted for execution because of `interface_mismatch`,
`input_invalid`, `constraint_rejected`, or `authorization_failed`. A remote
Task MUST reach `TASK_STATE_FAILED` when an accepted operation cannot complete,
including when `describe_skill` cannot produce a valid advertised interface or
when domain processing cannot produce valid output. A
`resource_limit_exceeded` condition uses `TASK_STATE_REJECTED` when the limit
is checked before acceptance and `TASK_STATE_FAILED` when the limit is reached
during processing.

An implementation MUST distinguish at least the following conditions:

- `skill_not_advertised`: the requested `skill_id` is not advertised by the
  selected agent endpoint;
- `unsupported_interface_version`: the advertised or returned Skill Interface
  version is not supported by the client;
- `interface_unavailable`: the selected interface is advertised but cannot
  currently be returned;
- `interface_invalid`: a Skill Interface Document is malformed, does not match
  the selected skill, fails validation against the version 1.0 Skill
  Interface Schema, or contains an embedded schema that fails digest or
  schema validation;
- `interface_mismatch`: a domain-skill invocation carries a `skill_version` or
  `interface_digest` that does not match the receiving agent's currently
  active Skill Interface Document for that skill;
- `input_invalid`: the domain input does not validate against the selected
  Skill Interface Document's `input_schema`;
- `output_invalid`: the produced domain output does not validate against the
  selected Skill Interface Document's `output_schema`;
- `constraint_rejected`: a structurally valid requested constraint cannot be
  honored or enforced by the receiving agent;
- `authorization_failed`: authentication, authorization, or a required
  approval check does not permit the requested invocation or side effect; and
- `resource_limit_exceeded`: processing the interface, schema, input, output,
  or supporting records would exceed an implementation resource limit.

The `skill_not_advertised` condition can be detected by a client before it
sends `describe_skill`. A client MUST NOT send the request when the Agent Card
does not advertise the selected skill. A client detects
`unsupported_interface_version` when the extension advertisement or returned
document uses an interface version it does not support. Neither client-side
condition creates a remote failed Task. If a server receives a domain-skill
invocation based on a stale interface, it MUST report `interface_mismatch`
through the interface version 1.0 A2A mapping using `TASK_STATE_REJECTED`.

A client that detects `interface_invalid` locally MUST reject the document and
MUST NOT delegate the domain skill under this framework. An implementation
MAY include a `details` array for `input_invalid` and `output_invalid`. Each
entry MUST contain an `instance_path` identifying the invalid field using a
JSON Pointer {{JSON-POINTER}}. It MAY contain a `schema_path`, `keyword`,
`expected`, and `actual` value. These fields are diagnostic and do not replace
the machine-readable error `code`. For example:

```json
{
  "error": {
    "code": "input_invalid",
    "message": "The threshold must be numeric",
    "details": [
      {
        "instance_path": "/threshold",
        "schema_path": "/properties/threshold/type",
        "keyword": "type",
        "expected": "number",
        "actual": "string"
      }
    ]
  }
}
```

Diagnostic details MUST NOT disclose credentials, sensitive policy state,
input values prohibited by local security policy, or other information that
the caller is not authorized to receive.

The receiving agent MUST validate domain output before it reports
`TASK_STATE_COMPLETED`; invalid output results in `output_invalid` and
`TASK_STATE_FAILED`. A client MUST independently validate received output. If
it detects invalid output after the remote agent reported completion, it MUST
treat the output as unusable and report `output_invalid` locally; it cannot
retroactively change the remote Task state.

## Client-agent behavior {#client-behavior}

The following figure illustrates the conceptual inline flow between a client
agent and a remote network management agent. Inline delivery does not replace
Schema References. Each reference retains its stable identity, version,
dialect, and digest while carrying the schema content in its `resolution`
field.

~~~ ascii-art
       Client Agent                         Remote Agent
            |                                    |
            |------ Retrieve Agent Card -------->|
            |<-- Skills, versions, and interface |
            |    digests in A2A extension -------|
            |                                    |
            | Select advertised interface and    |
            | skill versions and digest          |
            |                                    |
            |--- describe_skill(skill_id) ------>|
            |<-- Document and interface_digest --|
            |       Schema References:           |
            |       - input schema               |
            |       - output schema              |
            |       - supporting records         |
            |       resolution.type = inline     |
            |       embedded schema content      |
            |                                    |
            | Validate document digest,          |
            | references, digests, and schemas   |
            |                                    |
            |--- Delegate request with version ->|
            |    and interface_digest            |
            |<--- Status, output, and records ---|
            | Validate response using cached     |
            | Schema References                  |
~~~

The client verifies each embedded schema against the digest declared by its
Schema Reference before using it. The following steps define the v1.0 client
behavior.

A client agent performs the following sequence:

1. retrieve the target Agent Card and obtain its A2A endpoint and schema-
   interface extension advertisement;
2. verify that both `describe_skill` and the selected domain skill are
   advertised, and select the advertised `skill_version` and
   `interface_digest` for that domain skill;
3. call `describe_skill` for the selected `skill_id` using the interface
   version 1.0 A2A mapping;
4. verify that the `interface_digest` returned by `describe_skill` equals the
   advertised value, calculate the digest of the returned Skill Interface
   Document, and verify that the calculated value also equals it;
5. validate the returned Skill Interface Document against a trusted local
   copy of the version 1.0 Skill Interface Schema, verify that its
   `interface_version` is `1.0`, and verify that its `skill_id` and
   `skill_version` identify the selected skill and version;
6. verify every embedded domain schema against its Schema Reference digest;
7. validate the outgoing skill input against `input_schema`;
8. delegate the task through the Agent-to-Agent protocol, carrying the
   selected `skill_version` and `interface_digest` in the skill request;
9. receive task status, typed skill output, and supporting records according
   to that mapping;
10. validate the skill output against `output_schema` and validate the
   supporting records; and
11. preserve, forward, display, or interpret them according to local policy.

Before delegating a domain skill under this framework, the client agent MUST
possess a successfully validated Skill Interface Document obtained from that
target's `describe_skill` skill. If `describe_skill` is absent, fails, returns
a document for a different skill or version, or returns a document that cannot
be validated, the client agent MUST NOT delegate the domain request using the
procedure defined in this document.

The client agent MAY reuse a cached Skill Interface Document without calling
`describe_skill` before every task when the cache entry is bound to the same
target identity, skill identifier, skill version, and interface digest
advertised by the current Agent Card. A change to any of those values
invalidates the entry and requires a new `describe_skill` exchange before the
next delegation.

A generic client agent can validate and route an unfamiliar vendor schema
without understanding its domain semantics. A domain-aware orchestrator may
install optional handlers keyed by stable schema URI to evaluate operational
thresholds, incident records, configuration policy, or other domain behavior.

A complete non-normative example is provided in {{end-to-end-example}}.

## Composition of consecutive skills

When the output of one skill becomes the input to another skill, the component
initiating the downstream delegation is the client agent for that interaction.
That component may be a centralized orchestrator or the upstream agent itself
communicating directly with the downstream agent. The same composition rules
apply in either topology.

The downstream delegation creates a new Agent-to-Agent task with its own task
identifier. The delegating component MUST retain the upstream and downstream
task identifiers as distinct values. It SHOULD preserve a correlation mapping
that includes the relevant agent identities or endpoints, skill identifiers,
task identifiers, and timestamps for observability, audit, and
troubleshooting. An implementation SHOULD define how this cross-hop
correlation metadata is carried or recorded. Fields such as `workflow_id`,
`step_id`, `attempt_id`, and `parent_a2a_task_id` may be
used when defined by the applicable domain schema or binding, but they do not
replace protocol task identifiers.

The following figure shows the reference comparison and validation decisions
performed by that delegating component.

~~~ ascii-art
 Upstream Agent                 Delegating Component
       |                                  |
       |-- Output payload ---------------->|
       |   output_schema reference        |
       |                                  |
       |                         Retrieve downstream
       |                         Skill Interface
       |                                  |
       |                                  v
       |                         Downstream input_schema
       |                              reference
       |                                  |
       |                    Compare URI, version,
       |                    dialect, and digest
       |                                  |
       |                +-----------------+----------------+
       |                |                                  |
       |              Match                         No exact match
       |                |                                  |
       |      Validate output against              Reject direct
       |      downstream input schema               composition
       |                |
       |                v
       |      Create new downstream A2A task
       |      and delegate validated input
       |                |
       |                v
       |        Downstream Agent
       |      validates and processes
~~~

The standardized Schema Reference allows an orchestrating system or delegating
agent to determine direct-composition eligibility without interpreting a
domain-specific schema. Direct composition MUST require the Schema Reference
for the transferred upstream output payload and the Schema Reference accepted
for the corresponding downstream input to have the same `schema_uri`,
`version`, `dialect`, and `digest`. Because version 1.0 carries schemas inline,
the delegating component also verifies that each embedded schema matches its
declared digest.

This exact-match rule is intentionally conservative. Two schemas can be
structurally similar, or can both accept a particular instance, while assigning
different meanings, units, defaults, constraints, or operational consequences
to the same fields. Inferring compatibility from shape or successful
validation alone could therefore connect semantically divergent interfaces.
Comparing the complete portable identity and content digest gives v1.0 a
deterministic composition decision without requiring domain interpretation,
schema negotiation, or a standardized compatibility algorithm. The rule does
not assert that only identical schemas can ever interoperate; it limits what
this specification treats as direct composition.

The orchestrating system or delegating agent MUST validate the transferred
instance mechanically against the downstream input schema before delegation,
and the receiving agent MUST validate the received instance before processing
it. Neither operation requires the orchestrating system or delegating agent to
understand the schema's domain semantics.

If those Schema Reference fields do not match, the delegating component MUST
NOT perform direct composition under this specification.

An implementation can use an out-of-band transformation mechanism before
delegation. Transformation discovery, trust, execution, and provenance are
outside the scope of this document. Any resulting payload enters this
procedure as a new input and is subject to ordinary input validation against
the downstream `input_schema`.

Matching Schema References and successful instance validation establish
structural compatibility, not operational correctness. The receiving agent
remains responsible for domain-semantic validation, authorization, policy
evaluation, and operational safety before acting on the input.

For example, an input schema can define a network measurement with a metric,
value, unit, observation window, observation time, and requested constraints.
An instance reporting link capacity of 100 Gbps can be structurally valid
while failing a request that requires available bandwidth measured over a
particular window and no older than a specified age.  Capacity and available
bandwidth are not interchangeable merely because their values use the same
unit.  A generic client can validate and route the instance without
understanding that distinction.  A domain-aware orchestrator MAY reject it
before delegation; otherwise, the downstream agent MUST enforce the window,
scope, unit, and freshness constraints represented by fields in its input
schema and supplied by the invocation.  The component that detects the
failure MUST reject the invocation with `constraint_rejected`.

# Schema Publication and Packaging

## Vendor release artifacts

Agent domain schemas are deployment-independent source artifacts. The
standardized Skill Interface Schema is a separately versioned common artifact;
an implementation packages an exact trusted copy rather than maintaining an
agent-specific variation. A vendor release pipeline SHOULD:

1. validate all schemas;
2. test representative inputs and outputs against them;
3. assign stable schema URIs and versions;
4. compute schema digests;
5. when publishing a schema bundle, produce a bundle manifest; and
6. sign or otherwise integrity-protect any published schema bundle.

Producing a schema bundle is optional. A bundle, registry, or agent package
may provide deployment-local source material for assembling a Skill Interface
Document. Regardless of that source, the resulting v1.0 document contains the
domain schemas inline. The release pipeline does not need access to a customer
registry.

## Agent initialization

Before advertising schema-interface support, an agent SHOULD:

1. load and integrity-check its packaged Skill Interface Schema;
2. load its domain input, output, and supporting-record schemas;
3. assemble a Skill Interface Document for each advertised skill version;
4. validate each document and each inline schema digest; and
5. calculate and retain the Skill Interface Document Digest for each immutable
   validated representation; and
6. advertise each skill version and digest through the schema-interface A2A
   extension.

Failure to load, assemble, or validate an interface prevents that skill
version from being advertised through this framework. An implementation MUST
NOT silently fall back to an opaque unconstrained payload.

# Schema Evolution and Compatibility

Schema publishers MUST treat a published schema version and digest as
immutable. A changed schema receives a new version and digest.

Compatibility policy SHOULD be applied to a governed schema family. Structural
compatibility checking is necessary but not sufficient. It cannot establish
that units, operational interpretation, authority, or supporting-record
quality remain compatible.

A breaking semantic change requires a new major version even if a structural
JSON Schema checker accepts the change. Examples include:

- changing a utilization value from percent to a fraction;
- changing a timestamp from observation time to processing time;
- changing a supporting-record classification from authoritative to inferred;
  or
- changing a configuration artifact from candidate to applied state.

The Skill Interface Document MUST identify the exact schema versions currently
used by the skill. When a registry is used as a deployment-local management
mechanism, the document assembler MUST select an exact version and digest; it
MUST NOT substitute a mutable `latest` value. A client validates and uses the
schema embedded in the accepted document.

# Security Considerations {#security}

## Schema trust

A syntactically valid schema is not necessarily trustworthy. A client agent
applies policy for trusted publishers, schema identities, digests, versions,
and dialects.

## Arbitrary retrieval

Following arbitrary schema URLs can expose a client agent to server-side
request forgery, credential leakage, malicious redirects, and availability
attacks. Version 1.0 Schema References contain inline schema content and MUST
NOT direct the client agent to retrieve a schema from an arbitrary URL.
Deployment-local schema-management tools that contact registries or other
services remain subject to administrator-configured trust and network policy.

## Resource limits

An implementation MUST enforce limits on schema size, nesting, reference
depth, reference cycles, compilation time, payload size, and cache
consumption. When an operation is rejected because one of these limits would
be exceeded, the implementation MUST report the `resource_limit_exceeded`
machine-readable condition defined in {{error-conditions}} through the
applicable binding. The error response need not disclose the configured
threshold or other sensitive implementation details.

Version 1.0 does not define numeric interoperability minima for these limits.
A future interface version MAY define minimum supported capacities or maximum
interoperable sizes for implementations that claim conformance to that
version.

## Schema validation and authorization

Schema validation establishes structural conformance, not caller authority,
operational safety, truth, or permission to modify a network. The `authority`
member of a Skill Interface Document is descriptive and MUST NOT be interpreted
as a permission grant or evidence that an approval has been obtained.

At invocation time, the receiving agent or hosting platform MUST authenticate
the caller and authorize the requested skill, resources, operation, and
applicable constraints under current local policy. It MUST repeat or refresh
the authorization decision when required by that policy before causing a side
effect. A cached Skill Interface Document, successful schema validation, or a
previous authorization decision MUST NOT substitute for a required current
decision. A denied authentication, authorization, or required approval check
MUST reject the invocation with the `authorization_failed` machine-readable
condition defined in {{error-conditions}}.

This document does not mandate an authorization model. Deployments may use
RBAC, ABAC, capability-based authorization, external policy decision points,
human or automated approval workflows, or another model that satisfies these
runtime requirements.

## Supporting-record integrity and provenance

Supporting records can be stale, replayed, forged, selectively omitted, or
derived from untrusted inputs. A supporting-record schema SHOULD require the
source, producer, relevant observation and production times, integrity data,
derivation, and classification needed by its domain. Deployments define
freshness and retention policy appropriate to the operation.

## Injection

Text, CLI configuration, tool output, model output, and supporting-record
payloads are untrusted data. An agent does not treat instructions embedded in
those artifacts as authorized task instructions unless the applicable schema
and policy explicitly assign them that role.

## Interface integrity and substitution

The remote agent and client agent MUST integrity-check the packaged Skill
Interface Schema before using it. A local implementation MUST NOT modify the
standardized schema while adding domain schemas.

A client agent verifies that a retrieved Skill Interface Document identifies
the requested agent skill and advertised skill version. It validates the
document against the selected Skill Interface Schema, verifies all embedded
schema digests, and verifies that the calculated Skill Interface Document
Digest equals the value carried in the Agent Card and `describe_skill`
response. A structurally valid document for a different skill, version, or
digest MUST NOT be accepted as a substitute.

The receiving agent verifies that the `skill_version` and `interface_digest`
carried by every domain-skill invocation identify its currently active Skill
Interface Document before it validates or acts on the domain input. This check
prevents a document change between interface retrieval and invocation from
silently changing the contract applied to a request.

# Operational Considerations

Interface retrieval and validation SHOULD NOT add a `describe_skill` exchange
to every task. A client agent caches validated Skill Interface Documents,
verified inline domain schemas, and compiled validators. A cache entry is
bound to the agent identity, skill identifier, skill version, interface
version, and interface digest. A changed advertised version or digest
invalidates the corresponding entry.

An implementation SHOULD expose diagnostics identifying:

- the Skill Interface Schema version, skill version, and interface digest
  selected;
- schema URIs, versions, and digests used;
- inline-schema digest verification results;
- validation failures;
- missing, malformed, or untrusted schemas;
- compatibility or policy failures; and
- upstream-to-downstream task mappings, qualified by agent identity or
  endpoint.

For each delegation hop, diagnostics SHOULD preserve the upstream and
downstream agent identities or endpoints, their distinct task identifiers,
the selected skill identifier and version, the interface digest, and the
observed terminal state. This information supports audit and troubleshooting
across multi-hop workflows. It does not define a distributed-tracing protocol;
an A2A extension or deployment-specific mechanism may carry additional trace
context.

Deployments using a registry or another management service SHOULD test that a
running agent can continue serving previously assembled and validated Skill
Interface Documents during temporary management-service unavailability. They
SHOULD also define cache refresh and schema-revocation behavior.

# IANA Considerations {#iana}

This early version does not request any IANA actions. A later version may
request identifiers for Skill Interface versions, media types, or URN
namespaces after the representation and protocol mapping stabilize.

--- back

# Skill Interface JSON Schema {#skill-interface-json-schema}

The following JSON Schema is the complete version 1.0 Skill Interface Schema
defined by this document.  The same machine-readable artifact is published in
the source repository as `schemas/skill-interface-v1.json`.

~~~ json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://agentic-network-management.github.io/agent-schema-interfaces/schemas/skill-interface-v1.json",
  "title": "Network Management Agent Skill Interface",
  "description": "Language-neutral schema interface for one agent skill.",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "interface_version",
    "skill_id",
    "skill_version",
    "input_schema",
    "output_schema",
    "supporting_record_schemas",
    "interaction",
    "authority"
  ],
  "properties": {
    "interface_version": {
      "const": "1.0"
    },
    "skill_id": {
      "type": "string",
      "pattern": "^[a-z][a-z0-9_-]*$"
    },
    "skill_version": {
      "$ref": "#/$defs/version"
    },
    "input_schema": {
      "$ref": "#/$defs/schemaReference"
    },
    "output_schema": {
      "$ref": "#/$defs/schemaReference"
    },
    "supporting_record_schemas": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/supportingRecordSchema"
      }
    },
    "interaction": {
      "$ref": "#/$defs/interaction"
    },
    "authority": {
      "$ref": "#/$defs/authority"
    }
  },
  "$defs": {
    "version": {
      "type": "string",
      "pattern": "^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)$"
    },
    "digest": {
      "type": "string",
      "pattern": "^sha256:[0-9a-f]{64}$"
    },
    "resolution": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "type",
        "schema"
      ],
      "properties": {
        "type": {
          "const": "inline"
        },
        "schema": {
          "type": "object"
        }
      }
    },
    "schemaReference": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "schema_uri",
        "version",
        "dialect",
        "digest",
        "resolution"
      ],
      "properties": {
        "schema_uri": {
          "type": "string",
          "minLength": 1
        },
        "version": {
          "$ref": "#/$defs/version"
        },
        "dialect": {
          "const": "https://json-schema.org/draft/2020-12/schema"
        },
        "digest": {
          "$ref": "#/$defs/digest"
        },
        "resolution": {
          "$ref": "#/$defs/resolution"
        }
      }
    },
    "supportingRecordSchema": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "kind",
        "schema_reference"
      ],
      "properties": {
        "kind": {
          "type": "string",
          "minLength": 1,
          "description": "Supporting-record kind; MUST NOT equal the containing Skill Interface Document's skill_id."
        },
        "schema_reference": {
          "$ref": "#/$defs/schemaReference"
        }
      }
    },
    "interaction": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "supported_response_modes",
        "cancellable"
      ],
      "properties": {
        "supported_response_modes": {
          "type": "array",
          "minItems": 1,
          "uniqueItems": true,
          "items": {
            "enum": [
              "sync",
              "stream",
              "poll"
            ]
          }
        },
        "cancellable": {
          "type": "boolean"
        }
      }
    },
    "authority": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "default_mode",
        "approval_may_be_required"
      ],
      "properties": {
        "default_mode": {
          "enum": [
            "observe_only",
            "recommend_only",
            "execute"
          ]
        },
        "approval_may_be_required": {
          "type": "boolean"
        }
      }
    }
  }
}
~~~

# Non-Normative End-to-End Example {#end-to-end-example}

This example follows one invocation from interface retrieval through output
validation. It uses a domain skill that evaluates whether an observed
resource metric satisfies a caller-supplied threshold and returns the
observation as a supporting record.

The interface version 1.0 mapping uses the following A2A structure for the
domain invocation:

~~~ ascii-art
 A2A user Message
 `-- Data Part
     `-- data: skill request object
         `-- arguments: domain input

 A2A completed Task
 |-- ordinary A2A Artifact carrying the primary skill output
 |   `-- Data Part
 |       `-- data: skill result object
 |           `-- result: domain output
 `-- ordinary A2A Artifact carrying one supporting record
     |-- name: supporting-record kind
     `-- Data Part
         `-- data: supporting-record value
~~~

A2A defines Message, Data Part, Task, and Artifact. The descriptions
"carrying the primary skill output" and "carrying one supporting record" are
roles assigned to ordinary A2A Artifacts by this mapping; they are not
distinct Artifact types defined by A2A.

Assume an Agent Card advertises `describe_skill`, the
`evaluate_resource_condition` skill, and the following schema-interface
extension.  The digest value is repeated below to show the required binding
among advertisement, interface retrieval, and invocation:

```json
{
  "uri": "https://agentic-network-management.github.io/agent-schema-interfaces/extensions/schema-interface/v1",
  "required": false,
  "params": {
    "interface_version": "1.0",
    "skills": [
      {
        "skill_id": "evaluate_resource_condition",
        "skill_version": "1.0",
        "interface_digest": "sha256:4dedea3f7ddf19e94d9fd0b30886624f50afb5aadc1b407508a05dd3c40f380d"
      }
    ]
  }
}
```

The client activates the extension.  With the HTTP binding, the request
includes:

```http
A2A-Extensions: https://agentic-network-management.github.io/agent-schema-interfaces/extensions/schema-interface/v1
```

The A2A Message also lists that URI in `extensions` and carries the following
skill request object as the Data Part's `data` value:

```json
{
  "skill": "describe_skill",
  "arguments": {
    "skill_id": "evaluate_resource_condition"
  }
}
```

The agent returns the complete `describe_skill` skill result object below.
Its `result.interface` member is the Skill Interface Document, and
`result.interface_digest` carries the advertised digest outside that
document:

```json
{
  "skill": "describe_skill",
  "result": {
    "interface_digest": "sha256:4dedea3f7ddf19e94d9fd0b30886624f50afb5aadc1b407508a05dd3c40f380d",
    "interface": {
    "interface_version": "1.0",
    "skill_id": "evaluate_resource_condition",
    "skill_version": "1.0",
    "input_schema": {
      "schema_uri": "urn:example:resource-condition:input:1.0",
      "version": "1.0",
      "dialect": "https://json-schema.org/draft/2020-12/schema",
      "digest": "sha256:a593fb695fd727eaa36602d9b539e53e54cde50aec6f4b7df5d624b70148f26a",
      "resolution": {
        "type": "inline",
        "schema": {
          "type": "object",
          "properties": {
            "resource_id": {
              "type": "string"
            },
            "condition": {
              "type": "object",
              "properties": {
                "metric": {
                  "type": "string"
                },
                "operator": {
                  "enum": [
                    "gt",
                    "gte",
                    "lt",
                    "lte"
                  ]
                },
                "threshold": {
                  "type": "number"
                },
                "unit": {
                  "type": "string"
                }
              },
              "required": [
                "metric",
                "operator",
                "threshold",
                "unit"
              ],
              "additionalProperties": false
            }
          },
          "required": [
            "resource_id",
            "condition"
          ],
          "additionalProperties": false
        }
      }
    },
    "output_schema": {
      "schema_uri": "urn:example:resource-condition:output:1.0",
      "version": "1.0",
      "dialect": "https://json-schema.org/draft/2020-12/schema",
      "digest": "sha256:11ee18a8c1ab8821e083d61298ef07c4f2ce2e29c3eafb82f4742f1e1e969bce",
      "resolution": {
        "type": "inline",
        "schema": {
          "type": "object",
          "properties": {
            "result": {
              "enum": [
                "condition_met",
                "condition_not_met"
              ]
            },
            "observed_value": {
              "type": "number"
            },
            "unit": {
              "type": "string"
            },
            "supporting_record_refs": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "minItems": 1,
              "uniqueItems": true
            }
          },
          "required": [
            "result",
            "observed_value",
            "unit",
            "supporting_record_refs"
          ],
          "additionalProperties": false
        }
      }
    },
    "supporting_record_schemas": [
      {
        "kind": "resource-observation",
        "schema_reference": {
          "schema_uri": "urn:example:resource-observation:1.0",
          "version": "1.0",
          "dialect": "https://json-schema.org/draft/2020-12/schema",
          "digest": "sha256:3cf0d51c1d6e97d03fa80d5b9435c55d955f824bc9e58d053bb2095e18a0a8c4",
          "resolution": {
            "type": "inline",
            "schema": {
              "type": "object",
              "properties": {
                "record_id": {
                  "type": "string"
                },
                "resource_id": {
                  "type": "string"
                },
                "metric": {
                  "type": "string"
                },
                "value": {
                  "type": "number"
                },
                "unit": {
                  "type": "string"
                },
                "observed_at": {
                  "type": "string",
                  "format": "date-time"
                }
              },
              "required": [
                "record_id",
                "resource_id",
                "metric",
                "value",
                "unit",
                "observed_at"
              ],
              "additionalProperties": false
            }
          }
        }
      }
    ],
    "interaction": {
      "supported_response_modes": [
        "sync",
        "stream"
      ],
      "cancellable": true
    },
    "authority": {
      "default_mode": "observe_only",
      "approval_may_be_required": false
    }
    }
  }
}
```

The client validates the document against the trusted version 1.0 Skill
Interface Schema, verifies `interface_version`, `skill_id`, and
`skill_version`, calculates its Skill Interface Document Digest, compares it
with the values in the Agent Card and `describe_skill` response, and verifies
all three inline-schema digests. It then validates the `arguments` value below
against `input_schema` and sends this domain-skill request object as the Data
Part's `data` value:

```json
{
  "skill": "evaluate_resource_condition",
  "skill_version": "1.0",
  "interface_digest": "sha256:4dedea3f7ddf19e94d9fd0b30886624f50afb5aadc1b407508a05dd3c40f380d",
  "arguments": {
    "resource_id": "network-resource-123",
    "condition": {
      "metric": "utilization",
      "operator": "gte",
      "threshold": 80,
      "unit": "percent"
    }
  }
}
```

The receiving agent first verifies that `skill_version` and
`interface_digest` identify its currently active Skill Interface Document. It
then validates the same input, performs the evaluation, and returns the
following completed A2A Task. The first ordinary Artifact carries the skill
result object. The second ordinary Artifact carries the supporting record:

```json
{
  "id": "task-123",
  "status": {
    "state": "TASK_STATE_COMPLETED"
  },
  "artifacts": [
    {
      "artifactId": "result-1",
      "name": "evaluate_resource_condition",
      "parts": [
        {
          "data": {
            "skill": "evaluate_resource_condition",
            "result": {
              "result": "condition_not_met",
              "observed_value": 42,
              "unit": "percent",
              "supporting_record_refs": ["observation-7"]
            }
          }
        }
      ]
    },
    {
      "artifactId": "observation-7",
      "name": "resource-observation",
      "parts": [
        {
          "data": {
            "record_id": "observation-7",
            "resource_id": "network-resource-123",
            "metric": "utilization",
            "value": 42,
            "unit": "percent",
            "observed_at": "2026-08-11T12:00:01Z"
          }
        }
      ]
    }
  ]
}
```

The client validates the output against `output_schema`, validates the record
against the schema selected by its kind, and resolves `observation-7` to that
record. The stable reference shows which observation supports the result
without requiring a common claim or record envelope. A missing `unit` in the
input, an output result outside the declared enumeration, or a record missing
`observed_at` fails domain-schema validation. A digest mismatch makes the
interface invalid and prevents delegation.

# Contributors
{:numbered="false"}

The following individuals made significant contributions to this document:

- Muthumayan Madhayyan, Cisco Systems, Inc., muthu@cisco.com
- David Chuck, Cisco Systems, Inc., dachuck@cisco.com
- Nirali Vasoya, Cisco Systems, Inc., nvasoya@cisco.com
- Sun Qiong, China Telecom, sunqiong@chinatelecom.cn
