# Examples

The files in this directory are non-normative examples. They demonstrate how
an agent can populate the common Skill Interface with domain-specific schemas.
They do not define a required network-management skill or domain vocabulary.

`skill-interface-example.json` uses inline schema resolution so that the full
example can be inspected and validated without a schema registry.

## Agent identification and interface retrieval sequence

The Skill Interface is the result of the second of two distinct protocol
exchanges:

1. The client agent retrieves the remote agent's Agent Card from
   `/.well-known/agent-card.json`. The card identifies the A2A endpoint,
   protocol version, capabilities, agent version, and advertised skills. It
   advertises `describe_skill` when the agent conforms to this framework.
2. The client agent sends a structured `describe_skill` request to the
   advertised A2A endpoint, naming the skill it intends to invoke. The
   completed A2A task contains a skill description whose `interface` member is
   a Skill Interface document conforming to
   `schemas/skill-interface-v1.json`.

Before delegating the selected domain skill, the client agent validates the
returned Skill Interface, verifies that its `skill_id` and version identify
the selected skill, and may cache the verified document using the target
identity, agent version, and skill identifier. It then validates the domain
input against `input_schema` before invoking the selected skill. The client
agent MUST NOT delegate the skill under this framework if interface retrieval
or validation fails. It does not need to call `describe_skill` before every
task while the matching cached interface remains valid.

`skill-interface-example.json` represents only the standardized `interface`
member. It is not a complete Agent Card, A2A request, A2A task, or
`describe_skill` response envelope.
