from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.agents.state import InvestigationState

from app.graph.nodes import (
    database_node,
    documentation_node,
    finalize_node,
    logs_node,
    metrics_node,
    planner_node,
    route_next_action,
    service_health_node,
    hypothesis_node
)


def build_investigation_graph():
    """
    Build the adaptive AgentOps investigation graph.

    The LLM planner decides which investigation tool should
    execute next. After each tool call, control returns to
    the planner with the updated investigation state.
    """

    graph = StateGraph(InvestigationState)

    # ---------------------------------------------------------------
    # Nodes
    # ---------------------------------------------------------------

    graph.add_node(
        "planner",
        planner_node,
    )

    graph.add_node(
        "service_health",
        service_health_node,
    )

    graph.add_node(
        "logs",
        logs_node,
    )

    graph.add_node(
        "metrics",
        metrics_node,
    )

    graph.add_node(
        "database",
        database_node,
    )

    graph.add_node(
        "documentation",
        documentation_node,
    )

    graph.add_node(
        "finalize",
        finalize_node,
    )
    graph.add_node(
    "hypothesis",
    hypothesis_node
)
    # ---------------------------------------------------------------
    # Entry
    # ---------------------------------------------------------------

    graph.add_edge(
        START,
        "planner",
    )

    # ---------------------------------------------------------------
    # Planner → selected investigation action
    # ---------------------------------------------------------------

    graph.add_conditional_edges(
        "planner",
        route_next_action,
        {
            "check_service_health": "service_health",
            "search_logs": "logs",
            "query_metrics": "metrics",
            "query_database": "database",
            "search_documentation": "documentation",
            "finish": "finalize",
        },
    )

    # ---------------------------------------------------------------
    # Every investigation action returns to planner
    # ---------------------------------------------------------------

    graph.add_edge(
        "logs",
        "hypothesis"
    )

    graph.add_edge(
        "metrics",
        "hypothesis"
    )

    graph.add_edge(
        "database",
        "hypothesis"
    )

    graph.add_edge(
        "documentation",
        "hypothesis"
    )

    graph.add_edge(
        "service_health",
        "hypothesis"
    )

    graph.add_edge(
        "hypothesis",
        "planner"
    )

    # ---------------------------------------------------------------
    # Finalization
    # ---------------------------------------------------------------

    graph.add_edge(
        "finalize",
        END,
    )

    return graph.compile()