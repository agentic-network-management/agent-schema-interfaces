# Examples

The files in this directory are non-normative examples. They demonstrate how
an agent can populate the common Skill Interface with domain-specific schemas.
They do not define a required network-management skill or domain vocabulary.

`skill-interface-example.json` uses inline schema resolution so that the full
example can be inspected and validated without a schema registry.

## Discovery sequence

The Skill Interface is the result of the second of two distinct discovery
exchanges:

1. The client agent retrieves the remote agent's Agent Card from
   `/.well-known/agent-card.json`. The card identifies the A2A endpoint,
   protocol version, capabilities, agent version, and advertised skills. It
   advertises `describe_skill` when the agent conforms to this framework.
2. The client agent sends a structured `describe_skill` request to the
   discovered A2A endpoint, naming the skill it intends to invoke. The
   completed A2A task contains a skill description whose `interface` member is
   a Skill Interface document conforming to
   `schemas/skill-interface-v1.json`.

Before delegating the selected domain skill, the client agent validates the
returned Skill Interface, verifies that its `skill_id` and version identify
the selected skill, and may cache the verified document using the target
identity, agent version, and skill identifier. It then validates the domain
input against `input_schema` before invoking the selected skill. The client
agent MUST NOT delegate the skill under this framework if discovery or
validation fails. It does not need to call `describe_skill` before every task
while the matching cached interface remains valid.

`skill-interface-example.json` represents only the standardized `interface`
member. It is not a complete Agent Card, A2A request, A2A task, or
`describe_skill` response envelope.

## Cisco CP integration example

The following sanitized fixtures show the two discovery exchanges implemented
by the Cisco Crosswork Planning (CP) Agent. They are provided to help an
integrator implement a client agent that discovers CP and invokes its
`plan_network` skill:

- `cisco-cp-agent-card.json` is the response to
  `GET /.well-known/agent-card.json`.
- `cisco-cp-describe-skill-request.json` is the JSON-RPC request sent to the
  CP A2A endpoint to describe `plan_network`.
- `cisco-cp-describe-skill-response.json` is the completed A2A task returned
  by CP. The standardized Skill Interface is located at
  `result.task.artifacts[0].parts[0].data.result.interface`.

The fixtures were produced from the CP implementation and then normalized to
use stable example identifiers, timestamps, and the reserved hostname
`cp-agent.example.com`. These values are illustrative; an integration MUST
use the endpoint advertised by the deployed agent and MUST treat task,
context, message, and artifact identifiers as runtime values.

The CP fixtures illustrate one vendor implementation and are not normative.
The common requirements are defined by the Internet-Draft and
`schemas/skill-interface-v1.json`.
