from app.tools.documentation import search_documentation
from app.tools.logs import search_logs
from app.tools.metrics import query_metrics
from app.tools.database import query_database
from app.tools.service_health import check_service_health


INVESTIGATION_TOOLS = [
    search_documentation,
    search_logs,
    query_metrics,
    query_database,
    check_service_health,
]


TOOL_REGISTRY = {
    tool.name: tool
    for tool in INVESTIGATION_TOOLS
}