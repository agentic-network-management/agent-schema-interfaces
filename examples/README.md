# Examples

The files in this directory are non-normative examples. They demonstrate how
an agent can populate the common Skill Interface with domain-specific schemas.
They do not define a required network-management skill or domain vocabulary.

`skill-interface-example.json` uses inline schema resolution so that the full
example can be inspected and validated without a schema registry.

`schema-digest-test-vectors.json` demonstrates the version 1.0 Schema
Reference digest calculation.  Its `resolution_schema` value deliberately
contains non-integer numbers, escaped Unicode, and nested objects whose source
member order is not canonical.  `jcs_utf8` is the RFC 8785 serialization whose
UTF-8 bytes are hashed, and `digest` is the expected SHA-256 result.

`interface-digest-test-vectors.json` gives the expected Skill Interface
Document Digest (`interface_digest`) of each example document: the SHA-256
digest of the RFC 8785 serialization of the complete document, inline domain
schemas included.

## Validation

`tools/validate_examples.py` checks the schema, the test vectors, the
examples, and the end-to-end example of the draft, with schema retrieval
disabled and `format` evaluated as an assertion.  It runs on every pull
request and can be run locally from the repository root:

```
pip install -r tools/requirements.txt
python3 tools/validate_examples.py
```

## Agent identification and interface retrieval sequence

The Skill Interface is the result of the second of two distinct protocol
exchanges:

1. The client agent retrieves the remote agent's Agent Card from
   `/.well-known/agent-card.json`. The card identifies the A2A endpoint,
   protocol version, capabilities, agent version, and advertised skills. It
   advertises `describe_skill` and the schema-interface A2A extension when the
   agent conforms to this framework.  The extension binds each advertised
   skill identifier to one skill version and Skill Interface Document digest.
2. The client agent sends a structured `describe_skill` request to the
   advertised A2A endpoint, naming the skill it intends to invoke. The
   request activates the advertised extension using the A2A
   `A2A-Extensions` service parameter (the HTTP header when using the HTTP
   binding), and the Message lists the extension URI in `extensions`. The
   completed A2A task contains a skill description whose `interface` member is
   a Skill Interface document conforming to
   `schemas/skill-interface-v1.json`.

Before delegating the selected domain skill, the client agent validates the
returned Skill Interface, verifies that its `skill_id` and version identify
the selected skill, and verifies that its calculated document digest matches
the Agent Card and `describe_skill` values.  It may cache the verified
document using the target identity, skill identifier, skill version, and
interface digest. It then validates the domain input against `input_schema`
before invoking the selected skill and echoes the selected skill version and
interface digest in that invocation. The client agent MUST NOT delegate the
skill under this framework if interface retrieval or validation fails. It
does not need to call `describe_skill` before every task while the matching
cached interface remains valid.

`skill-interface-example.json` represents only the standardized `interface`
member. It is not a complete Agent Card, A2A request, A2A task, or
`describe_skill` response envelope.
