from app.graph.workflow import build_investigation_graph


graph = build_investigation_graph()

initial_state = {
    "incident": (
        "Customers are being charged twice for some payments."
    ),
    "service": "svc-payment",

    "severity": "HIGH",

    "evidence": [],

    "hypotheses": [],

    "tool_calls": [],

    "investigation_steps": [],

    "status": "investigating",

    "evidence_sufficient": False,

    "root_cause": None,

    "root_cause_confidence": None,

    "recommendations": [],

    "next_action": None,
    
    "next_action_args": {},

    "planner_reason": None,

    "investigation_complete": False,

    "max_steps": 8,
}


result = graph.invoke(initial_state)

print("=" * 70)
print("INVESTIGATION COMPLETE")
print("=" * 70)

print(f"Status: {result['status']}")
print(
    f"Evidence items: "
    f"{len(result['evidence'])}"
)
print(
    f"Tool calls: "
    f"{len(result['tool_calls'])}"
)
print(
    f"Investigation steps: "
    f"{len(result['investigation_steps'])}"
)

print("\n" + "=" * 70)
print("TOOL EXECUTION")
print("=" * 70)

for call in result["tool_calls"]:

    status = (
        "SUCCESS"
        if call["success"]
        else "FAILED"
    )

    print(
        f"\n{call['tool_name']} -> {status}"
    )

    print(
        f"Input: {call['input']}"
    )

    print(
        f"Output:\n{call['output_summary']}"
    )

print("\n" + "=" * 70)
print("EVIDENCE TYPES")
print("=" * 70)

for item in result["evidence"]:
    print(
        f"- {item['evidence_type']}: "
        f"{item['source']}"
    )

print("\n" + "=" * 70)
print("PLANNER DECISIONS")
print("=" * 70)

for step in result["investigation_steps"]:

    if step["action"] == "planner":

        print(
            f"Step {step['step']}: "
            f"{step['result']}"
        )

        print(
            f"Reason: {step['reason']}"
        )

        print()

print("\n" + "=" * 70)
print("PLANNER DECISIONS")
print("=" * 70)

for step in result["investigation_steps"]:

    if step["action"] == "planner":

        print(
            f"Step {step['step']}: "
            f"{step['result']}"
        )

        print(
            f"Reason: {step['reason']}"
        )

        print()