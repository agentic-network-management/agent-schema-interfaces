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

normative:
  A2A:
    title: "Agent2Agent Protocol Specification, Version 1.0.1"
    target: "https://a2a-protocol.org/v1.0.1/specification/"
  JSON-SCHEMA:
    title: "JSON Schema: A Media Type for Describing JSON Documents"
    target: "https://json-schema.org/draft/2020-12/json-schema-core.html"

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
Documents, retrieval through `describe_skill`, and the A2A mapping for
interface version 1.0. Together, they enable clients to retrieve and validate
the application schemas used for skill inputs, outputs, and supporting
records.

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

# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Scope

This document standardizes:

- a common Schema Reference structure for identifying, verifying, and
  carrying inline schemas;
- a Skill Interface Schema and a conforming per-skill Skill Interface
  Document;
- a Skill Interface advertisement and retrieval procedure using
  `describe_skill`; and
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

# Terminology

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

## Schema Reference

A portable schema identity, integrity information, and inline schema content.
The identity and digest remain independent of any deployment-local mechanism
used to manage the schema before the Skill Interface Document is assembled.

## Schema Bundle

An optional, signed or otherwise integrity-protected collection of schemas and
a manifest distributed with an agent release. A bundle may supply schemas to
an agent during interface assembly, but it is not referenced on the v1.0 wire.

## Schema Registry

An optional deployment service that stores, versions, retrieves, and may
check compatibility among schemas. It is a deployment-local management and
governance mechanism, not a v1.0 schema-delivery mechanism between agents.
Registry-local identifiers are not portable schema identities.

## Skill

A named capability advertised by an agent and invokable through an
Agent-to-Agent protocol.

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

## Supporting Record

A domain-specific observation or artifact used to derive, validate, reproduce,
or audit a skill output. A supporting record is validated against the
applicable schema identified by the Skill Interface Document.

# Design Principles

## Preserve task identity across delegation hops

Each delegation hop creates a separate Agent-to-Agent task at the receiving
agent. A delegating component MUST NOT reuse an upstream task identifier as the
downstream protocol task identifier. Protocol task identifiers are interpreted
in the scope of the agent or endpoint that issued them; implementations MUST
NOT assume that they are globally unique. Cross-hop correlation MUST use
separately named metadata rather than overloading protocol task identifiers.

## Standardize reusable structures, not all domain semantics

This framework standardizes reusable interface metadata, not the semantics of
every network-management domain. A vendor or domain owner defines the input,
output, and supporting-record schemas used by a particular skill and combines
them with the common structure; it does not redefine that structure.

## Distinguish structural conformance from semantic conformance

Matching Schema References establishes that communicating agents use the same
schema; it does not establish that the schema exposes sufficient semantics for
the intended operation. A schema that defines configuration only as a string
can validate the presence and type of that string but cannot by itself identify
affected resources, validate command dependencies, or establish that the
commands implement the requested intent.

When a receiving agent is expected to inspect, validate, transform, simulate,
or apply a configuration change, the shared domain schema MUST define a
normalized structured representation of that change. The receiving agent MUST
validate the representation and use a domain-specific implementation for
semantic validation, policy evaluation, simulation, or application, as
applicable.

Device-specific rendering is a local implementation responsibility of the
agent that requires it. Rendered CLI is not part of the common operational
representation exchanged between agents, and communicating agents are not
required to agree on a rendered syntax or platform-specific command language.

The applicable input, output, or supporting-record schema defines the
normalized structure for a particular skill. The `describe_skill` operation
makes those requirements available before a client agent delegates work.

## Deliver schemas inline in version 1.0

Every v1.0 Schema Reference returned by `describe_skill` MUST carry its schema
content inline. A client agent validates that embedded content against the
declared digest and does not contact an external service to complete the
interface.

Registries, bundles, caches, and agent packaging MAY be used locally to store,
govern, distribute, or prepare schemas. Their use does not alter the v1.0
wire representation, and a client agent is not required to know which local
mechanism supplied an inline schema.

## Distinguish outputs from supporting records

The skill output states what the agent concluded or delivered. Supporting
records explain why that output can be trusted, reproduced, or audited. An
artifact MAY be both output and a supporting record; implementations SHOULD
avoid duplicating its content when the applicable domain schemas permit stable
references.

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

Version 1.0 fixes the digest algorithm to SHA-256. The `digest` value MUST be
the lowercase string `sha256:` followed by exactly 64 lowercase hexadecimal
digits representing the SHA-256 digest of the embedded schema content.
Version 1.0 does not define digest-algorithm negotiation, and a value using
another algorithm identifier is invalid.

Version 1.0 Schema References MUST use `resolution.type` equal to `inline` and
MUST include the schema in `resolution.schema`. They MUST NOT contain an
external schema locator in place of the embedded content.

# Skill Interface Schema and Documents

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

The `authority` member is descriptive metadata about the operating posture an
agent advertises for a skill. `default_mode` describes that advertised default
posture; it does not grant the caller permission to use that mode.
`approval_may_be_required` indicates that an approval requirement may apply;
it does not assert that approval has been requested, granted, or remains
valid. The `authority` member is not a credential, capability, entitlement,
access-control decision, approval record, or authorization token. A client or
remote agent MUST NOT treat it as permission to execute a skill or cause a
side effect.

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

## Supporting-record schemas

A supporting record is a domain-specific observation or artifact used to
derive, validate, reproduce, or audit a skill output. Each entry in
`supporting_record_schemas` associates a `kind` with the Schema Reference for
the complete record. A produced record MUST validate against the schema for
its identified kind. A protocol progress update is not a supporting record
unless it is published in that form and passes this validation.

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
support that output. An artifact MAY be both output and a supporting record;
implementations SHOULD publish it once and reference it rather than duplicate
its content when the applicable domain schemas permit that relationship.

# A2A Mapping for Interface Version 1.0

This section defines how interface version 1.0 maps schema-interface
operations and data to A2A Messages, Data Parts, Tasks, Artifacts, and status
messages. An implementation MAY use any A2A protocol binding that preserves
these protocol elements and their semantics.

## Agent advertisement

An agent conforming to this framework MUST advertise `describe_skill` as a
skill in its Agent Card. The Agent Card also advertises the domain skills that
can be selected in a `describe_skill` request. The `describe_skill` skill MUST
accept structured input identifying the selected `skill_id` and MUST produce
structured output containing the corresponding Skill Interface Document.
Advertising `describe_skill` signals support for the procedure and mapping
defined by this document. A conforming version 1.0 response MUST contain
`interface_version` with value `1.0`.

Version 1.0 does not define request parameters for negotiating or selecting an
interface version or skill version within `describe_skill`. A client using
this procedure requests the interface for one advertised `skill_id` and then
verifies that the returned document uses `interface_version` value `1.0`. The
returned document identifies the domain-skill version to which its schemas
apply.

A caller MUST NOT assume that every Agent-to-Agent implementation conforms to
this framework. Absence of the `describe_skill` skill from the Agent Card means
that the agent does not provide the schema-interface procedure defined here.
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
  "result": <Skill Interface Document>
}
```

The `result` value is a Skill Interface Document conforming to the advertised
and previously selected version of the standardized Skill Interface Schema.
Its `skill_version` MUST equal the advertised domain-skill version selected
before the request. In version 1.0, every Schema Reference in the response MUST
contain the complete domain schema inline in `resolution.schema` and MUST set
`resolution.type` to `inline`.

The response MUST be the previously assembled and validated document for the
selected skill version. The `describe_skill` operation MUST NOT redefine the
standard structure or invoke domain logic to construct or modify the document
while processing the request. The returned input, output, and
supporting-record schemas remain specific to the selected agent and skill.

The selected document MUST correspond to the skill version advertised by the
agent. If an advertised interface cannot currently be returned, the agent MUST
report `interface_unavailable`. If the available document is malformed,
inconsistent with the selected skill or versions, or otherwise fails required
validation, the agent MUST report `interface_invalid`. It MUST NOT accept or
return an unvalidated opaque payload as a substitute.

## Domain-skill invocation {#domain-skill-invocation}

After validating the selected Skill Interface Document, a client invokes the
domain skill with the A2A Send Message or Send Streaming Message operation.
The user-role Message MUST contain exactly one Data Part. The Data Part's
`data` value MUST be this skill request object:

```json
{
  "skill": "example_skill",
  "arguments": {
    "objective": "Evaluate the selected network resource"
  }
}
```

The `skill` value MUST equal the selected Agent Card skill identifier. The
`arguments` value is the complete domain input and MUST validate against the
selected Skill Interface Document's `input_schema`.

On success, the task MUST reach the completed state. It MUST contain one
primary Artifact whose `name` equals the selected skill identifier and whose
single Data Part contains this skill result object:

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
kind. The Artifact `artifactId` provides a stable task-scoped identifier that
the domain output MAY reference. A record transported or retrieved outside
the task requires a stable reference mechanism defined by its domain schema.

The same final Task and Artifact requirements apply whether the client uses
synchronous completion, streaming updates, or task retrieval and polling.
Streaming may deliver the Artifacts incrementally, but it MUST NOT change
their application-data structure or validation requirements.

## Machine-readable error conditions {#error-conditions}

When an error condition defined below is detected after an A2A task has been
created, the task MUST reach the failed state. Its final status Message MUST
contain exactly one Data Part whose `data` value has this form:

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
MAY be omitted. A failure detected before task creation MUST be carried using
the error mechanism of the selected A2A protocol binding and SHOULD expose the
same machine-readable code when that binding permits it. These conditions are
not skill outputs and are not validated against the selected skill's
`output_schema`.

An implementation MUST distinguish at least the following conditions:

- `skill_not_advertised`: the requested `skill_id` is not advertised by the
  selected agent endpoint;
- `unsupported_interface_version`: the returned Skill Interface version is
  not supported by the client;
- `interface_unavailable`: the selected interface is advertised but cannot
  currently be returned;
- `interface_invalid`: a Skill Interface Document is malformed, does not match
  the selected skill, fails validation against the version 1.0 Skill
  Interface Schema, or contains an embedded schema that fails digest or
  schema validation;
- `constraint_rejected`: a structurally valid requested constraint cannot be
  honored or enforced by the receiving agent;
- `authorization_failed`: authentication, authorization, or a required
  approval check does not permit the requested invocation or side effect; and
- `resource_limit_exceeded`: processing the interface, schema, input, output,
  or supporting records would exceed an implementation resource limit.

The `skill_not_advertised` condition can be detected by a client before it
sends `describe_skill`. A client MUST NOT send the request when the Agent Card
does not advertise the selected skill. A client detects
`unsupported_interface_version` when the returned document uses an interface
version it does not support. If a server receives a request based on stale or
inconsistent advertisement information, it MUST report the applicable
condition through the interface version 1.0 A2A mapping.

A client that detects `interface_invalid` locally MUST reject the document and
MUST NOT delegate the domain skill under this framework. An implementation
MAY include additional diagnostic details, but those details MUST NOT disclose
credentials, sensitive policy state, or information prohibited by local
security policy.

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
            |<----- Skills and A2A endpoint -----|
            |                                    |
            | Select advertised interface and    |
            | skill versions                     |
            |                                    |
            |--- describe_skill(skill_id) ------>|
            |<-- Skill Interface Document -------|
            |       Schema References:           |
            |       - input schema               |
            |       - output schema              |
            |       - supporting records         |
            |       resolution.type = inline     |
            |       embedded schema content      |
            |                                    |
            | Validate interface structure,      |
            | references, digests, and schemas   |
            |                                    |
            |--- Delegate validated request ---->|
            |<--- Status, output, and records ---|
            | Validate response using cached     |
            | Schema References                  |
~~~

The client verifies each embedded schema against the digest declared by its
Schema Reference before using it. The following steps define the v1.0 client
behavior.

A client agent performs the following sequence:

1. retrieve the target Agent Card and obtain its A2A endpoint, agent version,
   and advertised skill identifiers;
2. verify that both `describe_skill` and the selected domain skill are
   advertised;
3. call `describe_skill` for the selected `skill_id` using the interface
   version 1.0 A2A mapping;
4. validate the returned Skill Interface Document against a trusted local
   copy of the version 1.0 Skill Interface Schema, verify that its
   `interface_version` is `1.0`, and verify that its `skill_id` identifies the
   selected skill;
5. verify every embedded domain schema against its Schema Reference digest;
6. validate the outgoing skill input against `input_schema`;
7. delegate the task through the Agent-to-Agent protocol using that mapping;
8. receive task status, typed skill output, and supporting records according
   to that mapping;
9. validate the skill output against `output_schema` and validate the
   supporting records; and
10. preserve, forward, display, or interpret them according to local policy.

Before delegating a domain skill under this framework, the client agent MUST
possess a successfully validated Skill Interface Document obtained from that
target's `describe_skill` skill. If `describe_skill` is absent, fails, returns
a document for a different skill or version, or returns a document that cannot
be validated, the client agent MUST NOT delegate the domain request using the
procedure defined in this document.

The client agent MAY reuse a cached Skill Interface Document without calling
`describe_skill` before every task when the cache entry is bound to the same
target identity, agent version, skill identifier, skill version, and, when
advertised, interface-document digest. A change to any of those values
invalidates the entry and requires a new `describe_skill` exchange before the
next delegation.

A generic client agent can validate and route an unfamiliar vendor schema
without understanding its domain semantics. A domain-aware orchestrator may
install optional handlers keyed by stable schema URI to evaluate operational
thresholds, incident records, configuration policy, or other domain behavior.

## Non-normative end-to-end example

This example follows one invocation from interface retrieval through output
validation.

The profile uses the following A2A structure for the domain invocation:

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

Assume an Agent Card advertises `describe_skill` and the
`evaluate_resource_condition` skill. Using the procedure in
{{describe-skill-request}}, the client requests the interface for that skill.

The agent returns the following Skill Interface Document in the `result`
member of the `describe_skill` skill result object. The outer object is
omitted here to keep the example focused on the interface document:

```json
{
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
          "resource_id": { "type": "string" },
          "condition": {
            "type": "object",
            "properties": {
              "metric": { "type": "string" },
              "operator": { "enum": ["gt", "gte", "lt", "lte"] },
              "threshold": { "type": "number" },
              "unit": { "type": "string" }
            },
            "required": ["metric", "operator", "threshold", "unit"],
            "additionalProperties": false
          }
        },
        "required": ["resource_id", "condition"],
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
            "enum": ["condition_met", "condition_not_met"]
          },
          "observed_value": { "type": "number" },
          "unit": { "type": "string" },
          "supporting_record_refs": {
            "type": "array",
            "items": { "type": "string" },
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
              "record_id": { "type": "string" },
              "resource_id": { "type": "string" },
              "metric": { "type": "string" },
              "value": { "type": "number" },
              "unit": { "type": "string" },
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
    "supported_response_modes": ["sync", "stream"],
    "cancellable": true
  },
  "authority": {
    "default_mode": "observe_only",
    "approval_may_be_required": false
  }
}
```

The client validates the document against the trusted version 1.0 Skill
Interface Schema, verifies `interface_version`, `skill_id`, and
`skill_version`, and verifies all three inline-schema digests. It then
validates this domain input against `input_schema` before placing it in the
skill request object's `arguments` member:

```json
{
  "resource_id": "network-resource-123",
  "condition": {
    "metric": "utilization",
    "operator": "gte",
    "threshold": 80,
    "unit": "percent"
  }
}
```

The receiving agent validates the same input, performs the evaluation, and
places this domain output in the primary result Artifact's `result` member:

```json
{
  "result": "condition_not_met",
  "observed_value": 42,
  "unit": "percent",
  "supporting_record_refs": ["observation-7"]
}
```

It also produces a supporting-record Artifact named `resource-observation`
whose Data Part contains:

```json
{
  "record_id": "observation-7",
  "resource_id": "network-resource-123",
  "metric": "utilization",
  "value": 42,
  "unit": "percent",
  "observed_at": "2026-08-11T12:00:01Z"
}
```

The client validates the output against `output_schema`, validates the record
against the schema selected by its kind, and resolves `observation-7` to that
record. The stable reference shows which observation supports the result
without requiring a common claim or record envelope. A missing `unit` in the
input, an output result outside the declared enumeration, or a record missing
`observed_at` fails domain-schema validation. A digest mismatch makes the
interface invalid and prevents delegation.

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
5. retain an immutable validated representation for `describe_skill`.

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

A client agent verifies that a retrieved Skill Interface Document identifies the
requested agent skill and advertised skill version. It validates the document
against the selected Skill Interface Schema and verifies all embedded schema
digests. A structurally valid document for a different skill or version MUST
NOT be accepted as a substitute.

# Operational Considerations

Interface retrieval and validation SHOULD NOT add a `describe_skill` exchange
to every task. A client agent caches validated Skill Interface Documents,
verified inline domain schemas, and compiled validators. A cache entry is
bound to the agent identity, skill identifier, skill version, interface
version, and, when advertised, interface-document digest. A changed advertised
version or digest invalidates the corresponding entry.

An implementation SHOULD expose diagnostics identifying:

- the Skill Interface Schema version and skill version selected;
- schema URIs, versions, and digests used;
- inline-schema digest verification results;
- validation failures;
- missing, malformed, or untrusted schemas; and
- compatibility or policy failures; and
- upstream-to-downstream task mappings, qualified by agent identity or
  endpoint.

Deployments using a registry or another management service SHOULD test that a
running agent can continue serving previously assembled and validated Skill
Interface Documents during temporary management-service unavailability. They
SHOULD also define cache refresh and schema-revocation behavior.

# IANA Considerations {#iana}

This early version does not request any IANA actions. A later version may
request identifiers for Skill Interface versions, media types, or URN
namespaces after the representation and protocol mapping stabilize.

# Open Issues

The following issues require further review:

1. possible future in-band version-negotiation behavior when multiple
   interface versions are supported;
2. representation of confidential supporting records and access-controlled
   artifact references;
3. schema revocation and emergency withdrawal;
4. signature format for schema bundles and Skill Interface Documents;
5. a possible future interface version supporting non-inline schema delivery
   without making a registry API normative; and
6. possible future A2A mappings for later interface versions.

--- back

# Skill Interface JSON Schema

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
      "pattern": "^[0-9]+\\.[0-9]+(?:\\.[0-9]+)?$"
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
          "minLength": 1
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
          "type": "string",
          "minLength": 1
        },
        "approval_may_be_required": {
          "type": "boolean"
        }
      }
    }
  }
}
~~~

# Contributors
{:numbered="false"}

The following individuals made significant contributions to this document:

- Dan Voyer, Cisco Systems, Inc., davoyer@cisco.com
- Muthumayan Madhayyan, Cisco Systems, Inc., muthu@cisco.com
- David Chuck, Cisco Systems, Inc., dachuck@cisco.com
