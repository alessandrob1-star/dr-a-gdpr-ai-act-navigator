# Runtime Agents

This package contains the explicit agent boundaries used by the running
application. Each agent has one narrow responsibility and delegates detailed
domain calculations to the existing auditable service functions.

| Agent | File | Runtime responsibility |
|---|---|---|
| Company Profile Agent | `company_profile_agent.py` | Validates questionnaire answers and builds deterministic company memory |
| Regulatory Monitoring Agent | `regulatory_monitoring_agent.py` | Refreshes sources and selects live, cached, or disclosed demo feed data |
| Regulatory Matching Agent | `regulatory_matching_agent.py` | Matches company memory to regulatory events, warnings, and evidence |
| Dr. A | `dr_a_agent.py` | Coordinates policy checks, grounded prompts, citations, and `gpt-5.6-sol` answers |
| Policy Agent | `../policy_agent/` | Applies deterministic input and output safety boundaries |

`dashboard_server.py` is now the HTTP adapter: it validates requests and hands
work to these runtime agents. It does not impersonate agent intelligence with
hardcoded answers.

## Assessment handoff

```text
questionnaire
  -> Company Profile Agent
  -> Regulatory Monitoring Agent
  -> Regulatory Matching Agent
  -> structured dashboard
```

For chat, the server rebuilds that trusted assessment before invoking:

```text
question + trusted assessment
  -> Policy Agent input check
  -> Dr. A question-specific grounding
  -> OpenAI GPT-5.6 Sol
  -> cumulative grounding and Policy Agent output checks
  -> streamed browser response
```

If model output fails an objective check, Dr. A may request one corrected model
answer using sanitized error categories. Rejected claims are not copied into the
retry, and no deterministic text is presented as model reasoning.

## Deterministic Trace Demo

`demo_trace.py` is a separate presentation tool. It renders the
source-monitoring pipeline as an auditable handoff trace without claiming that
each deterministic processing step is an autonomous model.

## Run the trace locally

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m module_agents.demo_trace
```

Outputs:

- `storage/agent_trace.md`
- `storage/agent_trace.json`

## What the Trace Demonstrates

The trace shows how the platform:

- starts from curated regulatory sources;
- creates monitored items;
- separates official evidence from warnings;
- classifies regulatory events by validation level;
- calculates priority and recommended attention;
- generates review-ready demo artifacts.

This is a technical demo, not legal advice.
