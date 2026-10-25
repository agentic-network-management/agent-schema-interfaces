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
  CONFLUENT:
    title: "Confluent Schema Registry Documentation"
    target: "https://docs.confluent.io/platform/current/schema-registry/"

...

--- abstract

Network management agents can use an Agent-to-Agent protocol to discover
peers, delegate work, observe task state, receive results, and cancel work.
The protocol alone does not define the application schemas used by an analysis
agent, incident-analysis agent, configuration agent, or other independently
developed network management agent.

This document standardizes three components for the machine-readable schema
interfaces of network management agent skills: a Schema Reference structure
for identifying, verifying, and resolving schemas; a Skill Interface Schema
and conforming per-skill Skill Interface Document; and a Skill Interface
advertisement and retrieval procedure using `describe_skill`. The Skill
Interface combines common Skill Request, Skill Outcome, and Supporting Record
Envelopes with the input, output, and supporting-record schemas defined by
the agent's vendor or domain owner.

Schema identity is portable, while schema resolution is deployment-specific.
Schemas may be returned inline, served by the agent, installed as an offline
bundle, or resolved through an optional customer-operated schema registry.
The design does not require a public registry or make a registry a runtime
dependency for every task.

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

The three standardized components define a framework in which:

- common Skill Request, Skill Outcome, Supporting Record, and Skill Interface
  structures are standardized without standardizing every domain payload;
- each skill declares versioned input, output, and supporting-record schemas;
- vendors and domain owners define the schemas specific to their agents;
- an agent assembles and validates a Skill Interface Document from the common
  structure and its domain schemas before advertising that document;
- a client agent retrieves and validates the selected Skill Interface before
  delegation;
- schemas can be resolved without assuming a particular registry product; and
- skill outcomes cite the supporting records used to derive, validate, or
  audit them.

The framework is intended to support independently developed agents from
different network-management domains without forcing their domain payloads
into one universal schema.

# Conventions and Definitions

{::boilerplate bcp14-tagged}

# Scope

This document standardizes:

- a common Schema Reference structure for identifying, verifying, and
  resolving schemas;
- a Skill Interface Schema and a conforming per-skill Skill Interface
  Document; and
- a Skill Interface advertisement and retrieval procedure using
  `describe_skill`.

In support of those three components, this document also defines:

- the relationship among skill requests, skill outcomes, deliverables, and
  supporting records;
- schema identity, integrity, versioning, and resolution behavior;
- the relationship between these interfaces and Agent-to-Agent task state; and
- requirements for validation, caching, trust, and failure handling.

This document does not define:

- the internal algorithm used by an agent;
- a universal schema for every network-management domain;
- a required schema-registry product or API;
- a globally centralized schema service;
- agent hosting, process lifecycle, or platform onboarding;
- authorization merely by successful schema validation; or
- the semantics of vendor-specific analysis, incident, or configuration data.

# Standardized Components

## Schema Reference Structure

The Schema Reference is a common structure for identifying a schema by stable
URI and version, declaring its schema dialect, verifying its content by
digest, and providing deployment-specific resolution information. The same
structure is used for request, input, output, and supporting-record schemas.
The structure is standardized so that a client can identify, retrieve, and
verify every schema in a Skill Interface without agent-specific or
registry-specific interpretation. The referenced domain schemas and the
deployment's choice of resolution mechanism are not standardized by the
Schema Reference structure.

A standardized Schema Reference also enables composition across independently
developed agents. An orchestrating system or delegating agent can compare the
Schema Reference of an upstream outcome payload with the Schema Reference
accepted for a downstream input without interpreting either schema's domain
semantics. Matching schema identity, version, dialect, and digest provides a
deterministic basis for deciding whether direct composition is permitted.

## Skill Interface

The Skill Interface Schema defines the common structure of a Skill Interface
Document. A conforming document describes one version of one skill and binds
the common envelope schemas to the domain-specific input, output, and
supporting-record schemas used by that skill.

## Skill Interface Advertisement and Retrieval

An agent advertises `describe_skill` in its Agent Card. A client invokes
`describe_skill` to retrieve the validated Skill Interface Document for a
selected advertised skill. The operation retrieves the interface document;
schema content identified by its Schema References is then obtained through
the applicable schema-resolution mechanism.

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

A portable schema identity plus integrity and resolution information. A
Schema Reference identifies schema content independently of the mechanism
used by a particular deployment to retrieve it.

## Schema Bundle

A signed or otherwise integrity-protected collection of schemas and a
manifest distributed with an agent release.

## Schema Registry

An optional deployment service that stores, versions, retrieves, and may
check compatibility among schemas. Registry-local identifiers are not
portable schema identities.

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

A machine-readable description of a skill's accepted input, produced outcome,
possible supporting records, interaction behavior, and applicable constraints.
It is an instance of the Skill Interface Schema. It contains domain-specific
Schema References supplied by the agent without modifying the standardized
Skill Interface Schema.

## Skill Request Envelope

The application-level request for invoking a skill, including its goal, typed
input, constraints, and workflow correlation. The Agent-to-Agent protocol
remains authoritative for protocol task identity and lifecycle state.

## Skill Outcome Envelope

The typed claims and deliverables produced by a skill invocation. A claim is a
conclusion intended to be consumed or acted upon. A deliverable is an artifact
the invocation was requested to produce.

## Supporting Record Envelope

A provenance-bearing observation or artifact used to derive, validate, or
audit a Skill Outcome.

# Design Principles

## Separate transport from application semantics

The Agent-to-Agent protocol owns task submission, protocol task identifiers,
context identifiers, lifecycle state, streaming, polling, and cancellation.
The schema-interface framework owns the structure and meaning of the
application payload.

An application payload MUST NOT redefine an Agent-to-Agent task identifier as
another unqualified `task_id`. An application MAY carry a `workflow_id`,
`step_id`, `attempt_id`, or explicitly named `parent_a2a_task_id` for
correlation.

## Standardize reusable structures, not all domain semantics

The common standard defines the Skill Request Envelope, Skill Outcome
Envelope, Supporting Record Envelope, Skill Interface Schema, and Schema
Reference. A vendor or domain owner defines the input, output, and
supporting-record payload schemas used by a particular skill. A conforming
implementation combines those domain schemas with the common structure to
produce a Skill Interface Document; it does not redefine the common structure.

## Distinguish envelope conformance from semantic conformance

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

## Treat schema resolution as deployment-specific

The stable schema identity and digest remain the same across deployments. A
customer deployment may resolve that identity from a registry, offline
bundle, agent endpoint, inline schema, or trusted local cache.

## Keep the registry optional

The remote agent and client agent MUST be capable of interoperating without a
schema registry when the necessary schemas are supplied through another
supported resolution mechanism.

## Distinguish outcomes from supporting records

The Skill Outcome states what the agent concluded or delivered. Supporting
records explain why that outcome can be trusted, reproduced, or audited. An
artifact MAY be both a deliverable and a supporting record; it is stored once
and referenced by its artifact or supporting-record identifier from each
applicable role.

## Assemble and validate before advertisement

An agent implementation owns its domain-specific input, output, and
supporting-record schemas. Its protocol service combines those schemas with a
trusted copy of the standardized Skill Interface Schema and applicable
interaction and authority declarations. The resulting Skill Interface
Document MUST be validated before it is advertised or returned.

An implementation SHOULD perform this assembly during agent initialization or
onboarding and retain an immutable validated document for each skill version.
The `describe_skill` operation retrieves that document. It does not ask the
agent's domain logic to construct or alter an interface while processing the
interface request.

## Inline schema-interface flow

The following figure shows the initial inline flow between a client agent and
a remote network management agent.  Inline delivery does not replace Schema
References.  Each reference retains its stable identity, version, dialect,
and digest while carrying the schema content in its `resolution` field.

~~~ ascii-art
       Client Agent                         Remote Agent
            |                                    |
            |------ Retrieve Agent Card -------->|
            |<----- Skills and A2A endpoint -----|
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

After identifying a remote agent and retrieving its Agent Card, the client
agent obtains the selected skill's validated Skill Interface Document through
`describe_skill`.  For the inline flow, the client validates the document
against its trusted copy of the Skill Interface Schema, verifies each Schema
Reference and embedded schema against the declared digest, validates the skill
request, and exchanges the task directly with the target through the
Agent-to-Agent protocol.

Other deployments may resolve the same stable Schema References through:

- a trusted cache;
- a customer-operated schema registry;
- a platform-installed or offline schema bundle; or
- an authenticated agent-hosted schema endpoint.

These mechanisms change how schema content is obtained; they do not change
the Skill Interface Document or carry the delegated task or its result.

# Schema Reference

This document standardizes one Schema Reference structure for all schema
roles. Skill-request, skill-output, and supporting-record schemas do not
require different reference structures, registries, or resolution mechanisms.

A Schema Reference contains:

- `schema_uri`: stable portable identity;
- `version`: version meaningful to the schema publisher;
- `dialect`: schema language and version;
- `digest`: digest of the resolved schema content; and
- `resolution`: deployment-selected resolution information.

```json
{
  "schema_uri": "urn:example:network-management:skill-input:1.0",
  "version": "1.0",
  "dialect": "https://json-schema.org/draft/2020-12/schema",
  "digest": "sha256:abc123...",
  "resolution": {
    "type": "inline",
    "schema": {
      "type": "object",
      "properties": {
        "objective": {
          "type": "string"
        }
      },
      "required": [
        "objective"
      ],
      "additionalProperties": false
    }
  }
}
```

When registry resolution is used, registry-local numeric identifiers MUST NOT
be treated as globally portable schema identities. Two registries may assign
the same numeric identifier to different schema content. A registry reference
therefore includes the stable schema URI and digest.

# Skill Interface Schema and Documents

The Skill Interface Schema standardizes the structure shown in this section.
A Skill Interface Document is a conforming instance for one skill version. It
binds common envelopes to the domain schemas used by that skill and identifies
the request, input, output, supporting-record, interaction, and authority
characteristics.

The agent or domain owner supplies the skill identifier, skill version, and
domain input, output, and supporting-record schemas. The agent protocol
service supplies the common envelope reference and assembles the complete
document. Interaction declarations reflect the agent implementation.
Authority declarations may additionally reflect deployment policy. Assembly
MUST NOT modify the standardized Skill Interface Schema.

The following non-normative example illustrates a conforming Skill Interface
Document using inline schema resolution:

```json
{
  "interface_version": "1.0",
  "skill_id": "example_skill",
  "skill_version": "1.0",
  "request_envelope": {
    "schema_uri": "urn:example:agent:skill-request-envelope:1.0",
    "version": "1.0",
    "dialect": "https://json-schema.org/draft/2020-12/schema",
    "digest": "sha256:a2c799262a3ce3c19ef5cdd983bf3d12b43ab3c426227091b909dcb7054738c0",
    "resolution": {
      "type": "inline",
      "schema": {
        "type": "object"
      }
    }
  },
  "input_schema": {
    "schema_uri": "urn:example:network-management:example-skill-input:1.0",
    "version": "1.0",
    "dialect": "https://json-schema.org/draft/2020-12/schema",
    "digest": "sha256:8d076361c4dcc79f0dbf1afa4dbe864e6318a88e4a8e6d9441c7cc99a5837aeb",
    "resolution": {
      "type": "inline",
      "schema": {
        "type": "object",
        "properties": {
          "objective": {
            "type": "string"
          }
        },
        "required": [
          "objective"
        ]
      }
    }
  },
  "output_schema": {
    "schema_uri": "urn:example:network-management:example-skill-output:1.0",
    "version": "1.0",
    "dialect": "https://json-schema.org/draft/2020-12/schema",
    "digest": "sha256:9a16baf78ac2b47ca47423709257463d3d315b3e35be9b5d72b9fb0b1a9910ed",
    "resolution": {
      "type": "inline",
      "schema": {
        "type": "object",
        "properties": {
          "status": {
            "type": "string"
          }
        },
        "required": [
          "status"
        ]
      }
    }
  },
  "supporting_record_schemas": [
    {
      "kind": "observation-record",
      "schema_uri": "urn:example:network-management:observation-record:1.0",
      "version": "1.0",
      "dialect": "https://json-schema.org/draft/2020-12/schema",
      "digest": "sha256:a2c799262a3ce3c19ef5cdd983bf3d12b43ab3c426227091b909dcb7054738c0",
      "resolution": {
        "type": "inline",
        "schema": {
          "type": "object"
        }
      }
    }
  ],
  "interaction": {
    "supported_response_modes": [
      "sync",
      "stream",
      "poll"
    ],
    "cancellable": true
  },
  "authority": {
    "default_mode": "read-only",
    "approval_may_be_required": true
  }
}
```

The inline schemas above are domain content populated into the standardized
document. They are not additions to or replacements for the Skill Interface
Schema. A deployment may instead populate the same Schema References with an
agent-hosted, bundle, or registry resolution mechanism supported by the
selected interface version.

Request validation is logically performed in two stages: the complete request
is validated against the common Skill Request Envelope, and the envelope's
typed input is validated against the domain `input_schema`. Outcome and
supporting-record validation follow the same composition model. An
implementation MAY compile these stages into an equivalent composed validator.

Successful schema validation does not authorize execution. The receiving
agent and hosting platform MUST independently authenticate the caller and
authorize the requested skill, resources, and operation.

# Skill Interface Advertisement and Retrieval

This section defines the standardized procedure for advertising
`describe_skill` and retrieving a Skill Interface Document for a selected
skill.

## Agent advertisement

An agent conforming to this framework MUST advertise `describe_skill` as a
skill in its Agent Card. The Agent Card also advertises the domain skills that
can be selected in a `describe_skill` request. The `describe_skill` skill MUST
accept structured input identifying the selected `skill_id` and MUST produce
structured output containing the corresponding Skill Interface Document.

The advertisement identifies the supported profile version and advertised
skill versions. It SHOULD also provide an interface-document digest when the
Agent Card representation permits that binding.

A caller MUST NOT assume that every Agent-to-Agent implementation conforms to
this framework. Absence of the `describe_skill` skill from the Agent Card means
that the agent does not provide the schema-interface procedure defined here.

## `describe_skill` request

The request selects one advertised skill:

```json
{
  "skill": "describe_skill",
  "arguments": {
    "skill_id": "example_skill"
  }
}
```

## `describe_skill` response

The response is a Skill Interface Document conforming to the advertised
version of the standardized Skill Interface Schema. It MAY contain complete
domain schemas inline or MAY contain Schema References resolved through
another supported mechanism.

The response MUST be the previously assembled and validated document for the
selected skill version. The `describe_skill` operation MUST NOT redefine the
standard structure or invoke domain logic to construct or modify the document
while processing the request. The returned input, output, and
supporting-record schemas remain specific to the selected agent and skill.

The selected document MUST correspond to the skill version advertised by the
agent. If the agent cannot provide a conforming compatible document, it MUST
fail the request with a machine-readable error rather than accepting an
unvalidated opaque payload.

## Client-agent behavior

A client agent performs the following sequence:

1. retrieve the target Agent Card and obtain its A2A endpoint, agent version,
   and advertised skill identifiers;
2. verify that both `describe_skill` and the selected domain skill are
   advertised;
3. call `describe_skill` for the selected skill;
4. validate the returned Skill Interface Document against a trusted local
   copy of the selected Skill Interface Schema;
5. verify and, when necessary, resolve the referenced domain schemas;
6. validate the outgoing Skill Request;
7. delegate the task through the Agent-to-Agent protocol;
8. receive status, a Skill Outcome, and supporting records;
9. validate the Skill Outcome and supporting records; and
10. preserve, forward, display, or interpret them according to local policy.

Before delegating a domain skill under this framework, the client agent MUST
possess a successfully validated Skill Interface Document obtained from that
target's `describe_skill` skill. If `describe_skill` is absent, fails, returns
a document for a different skill or version, or returns a document that cannot
be validated, the client agent MUST NOT delegate the domain request under this
profile.

The client agent MAY reuse a cached Skill Interface Document without calling
`describe_skill` before every task when the cache entry is bound to the same
target identity, agent version, skill identifier, skill version, and, when
advertised, interface-document digest. A change to any of those values
invalidates the entry and requires a new `describe_skill` exchange before the
next delegation.

A generic client agent can validate and route an unfamiliar vendor schema without
understanding its domain semantics. A domain-aware orchestrator may install
optional handlers keyed by stable schema URI to evaluate operational thresholds,
incident records, configuration policy, or other domain behavior.

## Composition of consecutive skills

When the outcome of one skill becomes the input to another skill, the component
initiating the downstream delegation is the client agent for that interaction.
That component may be a centralized orchestrator or the upstream agent itself
communicating directly with the downstream agent. The same composition rules
apply in either topology.

The following figure shows the reference comparison and validation decisions
performed by that delegating component.

~~~ ascii-art
 Upstream Agent                 Delegating Component
       |                                  |
       |-- Outcome payload -------------->|
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
       |      Validate outcome against        Trusted transformation
       |      downstream input schema          available?
       |                |                       |         |
       |                |                      Yes        No
       |                |                       |         |
       |                +----------+------------+       Reject
       |                           |
       |                           v
       |                Delegate validated input
       |                           |
       |                           v
       |                   Downstream Agent
       |                validates and processes
~~~

The standardized Schema Reference allows an orchestrating system or delegating
agent to determine structural compatibility without interpreting a
domain-specific schema. Direct composition SHOULD require the Schema Reference
for the transferred upstream outcome payload and the Schema Reference accepted
for the corresponding downstream input to have the same `schema_uri`,
`version`, `dialect`, and `digest`. Their deployment-specific resolution
information need not match.

The orchestrating system or delegating agent MUST validate the transferred
instance mechanically against the downstream input schema before delegation,
and the receiving agent MUST validate the received instance before processing
it. Neither operation requires the orchestrating system or delegating agent to
understand the schema's domain semantics.

If those Schema Reference fields do not match, composition requires an
explicitly identified and trusted transformation. The transformed instance
MUST validate against the downstream input schema. In the absence of either an
exact match or such a transformation, the delegating component SHOULD reject
the composition rather than infer a mapping from opaque JSON or text.

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
5. produce a schema-bundle manifest; and
6. sign or otherwise integrity-protect the bundle as part of the agent
   package.

The pipeline does not need access to a customer registry.

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

## Customer onboarding

At onboarding time, a customer deployment MAY:

- register the bundle in a customer-operated registry;
- install the bundle in a platform-controlled local store;
- allow the agent to serve the bundled schemas; or
- permit inline schemas in `describe_skill`.

If a customer registry is present, onboarding registers the schemas and
creates a deployment-local mapping from stable schema URI and digest to
registry subject, version, and identifier. That mapping is supplied to the
agent or made available to the client agent.

# Schema Resolution

## Trusted cache

A client agent SHOULD cache verified schema content by stable schema URI and digest.
A cached schema may be used while a registry or agent schema endpoint is
temporarily unavailable.

## Optional schema registry

A registry may provide centralized storage, subject versioning, references,
compatibility checks, publisher metadata, and governance.  {{CONFLUENT}} is one
non-normative example of this class of service. The standard does
not require a particular registry implementation or REST API.

An agent identifies a registry by a logical deployment name. The client agent maps
that name to an administrator-configured trusted endpoint. A client agent MUST NOT
retrieve schemas from an arbitrary registry URL supplied in an untrusted task
payload.

## Agent-hosted schemas

An agent MAY expose bundled schemas beneath a well-known path associated with
the already identified and authenticated agent endpoint. A Schema Reference
using this mechanism contains a relative path and digest. It does not redirect
the client agent to an arbitrary host.

## Inline schemas

`describe_skill` MAY return schemas inline. Inline resolution is suitable for
small skill interfaces, local development, and deployments without a registry.
The client agent still verifies the declared digest and applies publisher and size
policy.

## Offline bundle

An air-gapped deployment MAY install an approved schema bundle alongside the
client agent. The client agent resolves stable schema URIs from that bundle without
network access.

## Resolution order

A deployment may use the following resolution order:

1. trusted cache;
2. configured customer registry;
3. platform-installed bundle;
4. authenticated agent-hosted schema endpoint; and
5. inline schema.

Local policy determines which mechanisms are permitted.

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
used by the skill. A caller MUST NOT substitute a registry's mutable `latest`
version after accepting a document.

# Skill Requests, Outcomes, and Supporting Records

## Skill Request Envelope

The Skill Request Envelope carries the application request associated with an
Agent-to-Agent task. It includes common correlation and constraint fields and
a typed input payload.

An illustrative Skill Request Envelope is:

```json
{
  "schema": {
    "schema_uri": "urn:example:agent:skill-request-envelope:1.0",
    "version": "1.0",
    "digest": "sha256:..."
  },
  "workflow_id": "workflow-123",
  "step_id": "investigate-incident",
  "attempt_id": "attempt-1",
  "skill_id": "investigate_incident",
  "goal": "Identify the root cause of the incident",
  "constraints": {
    "deadline": "2026-10-19T22:00:00Z",
    "authority": "read-only",
    "approval_required": false
  },
  "input": {
    "schema": {
      "schema_uri": "urn:example:incident-analysis:investigate-incident-input:1.0",
      "version": "1.0",
      "digest": "sha256:..."
    },
    "data": {
      "incident_id": "incident-000001"
    }
  }
}
```

The `workflow_id`, `step_id`, and `attempt_id` are application-level
correlation identifiers. They do not replace the protocol task and context
identifiers.

## Skill Outcome Envelope

The Skill Outcome Envelope carries the final application outcome, deliverable
references, and supporting-record references.

```json
{
  "schema": {
    "schema_uri": "urn:example:agent:skill-outcome-envelope:1.0",
    "version": "1.0",
    "digest": "sha256:..."
  },
  "skill_id": "investigate_incident",
  "outcome": {
    "schema": {
      "schema_uri": "urn:example:incident-analysis:root-cause-result:1.0",
      "version": "1.0",
      "digest": "sha256:..."
    },
    "data": {
      "incident_id": "incident-000001",
      "root_cause_event_id": "1",
      "summary": "A hardware fault initiated the downstream failures.",
      "provisional": false
    }
  },
  "deliverable_refs": [],
  "supporting_record_refs": [
    "event-record-1",
    "causal-path-1"
  ]
}
```

The protocol task status indicates whether protocol execution completed. The
Skill Outcome describes what the application concluded or produced.
Completion of a protocol task does not by itself establish that a requested
downstream network operation completed successfully.

## Supporting Record Envelope

A Supporting Record Envelope associates a typed observation or artifact with
its producer, source, time, integrity information, derivation, and
classification.

```json
{
  "schema": {
    "schema_uri": "urn:example:agent:supporting-record-envelope:1.0",
    "version": "1.0",
    "digest": "sha256:..."
  },
  "record_id": "causal-path-1",
  "workflow_id": "workflow-123",
  "step_id": "investigate-incident",
  "attempt_id": "attempt-1",
  "kind": "validated-causal-path",
  "classification": "authoritative",
  "producer": {
    "agent": "event-analyzer",
    "component": "incident-correlator",
    "version": "1.0"
  },
  "source": {
    "system": "incident-graph",
    "resource": "incident-000001"
  },
  "observed_at": "2026-08-11T12:00:01Z",
  "produced_at": "2026-10-19T18:00:00Z",
  "derived_from": [
    "event-record-1"
  ],
  "payload": {
    "schema": {
      "schema_uri": "urn:example:incident-analysis:causal-path-record:1.0",
      "version": "1.0",
      "digest": "sha256:..."
    },
    "data": {
      "from_event_id": "1",
      "to_event_id": "2",
      "entity_path": [
        "node-pe-15",
        "node-pe-15/et-1-1-4"
      ],
      "topology_version": "standalone-fixture-v1"
    }
  }
}
```

Supporting records SHOULD be append-only once published. Corrections SHOULD be
expressed as new records that identify the record they supersede rather than
by silently replacing earlier content.

## Outcome and supporting-record relationship

The Skill Outcome is the answer, decision, or deliverable normally consumed by
the caller. Supporting records contain the observations and artifacts that
support that outcome.

For incident analysis:

```text
Skill Outcome:
  Hardware fault event 1 is the root cause.

Supporting Records:
  Event 1 preceded event 2.
  Both events resolve to connected entities.
  The stored incident graph contains the validated causal edge.
```

For an analytical skill:

```text
Skill Outcome:
  The analysis completed and found no threshold violations.

Supporting Records:
  Input-data digest, topology revision, analysis parameters, engine version,
  raw engine report, and validation result.
```

Supporting records are not merely additional unstructured output. They carry
provenance, integrity, time, derivation, and an explicit relationship to the
outcome they support.

# Agent-to-Agent Mapping

The Agent-to-Agent protocol remains authoritative for:

- protocol task and context identifiers;
- submitted, working, completed, failed, and canceled states;
- synchronous task completion;
- streaming task updates;
- task retrieval and polling; and
- cancellation delivery.

The Skill Request Envelope adds an application-level goal, workflow
correlation, typed input, and constraints. The Skill Outcome Envelope carries
the application conclusion, deliverables, and supporting-record references.

Task progress is not automatically a supporting record. A progress update
becomes one only when published as a Supporting Record Envelope with the
required provenance and integrity properties.

Receiving a cancellation request does not prove that downstream network work
has stopped. The final Skill Outcome and supporting records must describe the
effective state of relevant downstream operations when that distinction
matters.

# Security Considerations {#security}

## Schema trust

A syntactically valid schema is not necessarily trustworthy. A client agent applies
policy for trusted publishers, schema identities, digests, versions, dialects,
and resolution mechanisms.

## Arbitrary retrieval

Following arbitrary schema URLs can expose a client agent to server-side request
forgery, credential leakage, malicious redirects, and availability attacks.
Registry aliases and agent-relative paths are resolved only through trusted,
administrator-configured endpoints.

## Resource limits

A client agent enforces limits on schema size, nesting, reference depth, reference
cycles, compilation time, payload size, and cache consumption.

## Schema validation and authorization

Schema validation establishes structural conformance, not caller authority,
operational safety, truth, or permission to modify a network. Authorization
and policy checks occur at execution time.

## Supporting-record integrity and provenance

Supporting records can be stale, replayed, forged, selectively omitted, or
derived from untrusted inputs. They include source, producer, observation and
production times, digest, derivation, and classification. Deployments define
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
against the selected Skill Interface Schema and verifies all resolved schema
digests. A structurally valid document for a different skill or version MUST
NOT be accepted as a substitute.

# Operational Considerations

Interface retrieval and schema resolution SHOULD NOT add a `describe_skill`
or registry lookup to every task. A client agent caches validated Skill
Interface Documents, verified domain schemas, and compiled validators. A
cache entry is bound to the agent identity, skill identifier, skill version,
interface version, and, when advertised, interface-document digest. A changed
advertised version or digest invalidates the corresponding entry.

An implementation SHOULD expose diagnostics identifying:

- the Skill Interface Schema version and skill version selected;
- schema URIs, versions, and digests used;
- the resolution mechanism used for each schema;
- validation failures;
- unavailable or untrusted schemas; and
- compatibility or policy failures.

Deployments SHOULD test operation during temporary registry unavailability
and SHOULD define cache refresh and schema-revocation behavior.

# Non-Normative Examples

## Analytical skill

An analytical skill may declare:

```text
Input schema:
  analysis objective, input-data reference, constraints, and requested scenario

Output schema:
  analysis conclusion, candidate action, and summarized metrics

Supporting-record schemas:
  input-data snapshot, topology revision, analysis parameters, raw engine
  report, policy-validation report, and engine identity
```

For an analysis task, the outcome may state that no operational thresholds
were violated. Supporting records include the exact input-data digest,
parameters, engine version, run identifier, and raw result from which the
outcome was produced.

## Diagnostic skill

An incident-investigation skill may declare:

```text
Input schema:
  incident identifier and optional investigation constraints

Output schema:
  root-cause event, summary, reason, and provisional status

Supporting-record schemas:
  incident events, entity resolutions, topology version, and validated causal
  edges or paths
```

The outcome may claim that a hardware-fault event initiated downstream
interface and link failures. Supporting records include the authoritative
stored events, their resolved entities, and the validated path through the
incident graph. An inferred model proposal is distinguished from records
validated against authoritative data.

## Artifact used as both deliverable and a supporting record

A simulation report may be the requested skill deliverable and also support a
higher-level claim that a proposed change is safe. The report is published
once with a stable identifier. The Skill Outcome includes that identifier in
both `deliverable_refs` and `supporting_record_refs` when both roles apply.

# IANA Considerations {#iana}

This early version does not request any IANA actions. A later version may
request identifiers for the schema-interface profile, media types, or URN
namespaces after the representation and protocol mapping stabilize.

# Open Issues

The following issues require further review:

1. the exact JSON Schema definitions for the common Skill Request, Skill
   Outcome, and Supporting Record Envelopes;
2. version-negotiation behavior when multiple interface versions are
   supported;
3. whether outcome claims require an explicit claim identifier and per-claim
   supporting-record references;
4. representation of confidential supporting records and access-controlled
   artifact references;
5. schema revocation and emergency withdrawal;
6. signature format for schema bundles and Skill Interface Documents; and
7. mapping to existing schema registries without making a registry API
   normative.

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
    "request_envelope",
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
    "request_envelope": {
      "$ref": "#/$defs/schemaReference"
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
        "schema_uri",
        "version",
        "dialect",
        "digest",
        "resolution"
      ],
      "properties": {
        "kind": {
          "type": "string",
          "minLength": 1
        },
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
