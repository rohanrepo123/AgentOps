# from app.tools.database import query_database


# result = query_database.invoke(
#     {
#         "entity": "payments",
#         "limit": 5,
#     }
# )

# print(result)

# #testind Database tools


# from app.tools.database import query_database


# print("=" * 60)
# print("SERVICES")
# print("=" * 60)

# result = query_database.invoke(
#     {
#         "entity": "services",
#         "limit": 3,
#     }
# )

# print(result)


# print("\n" + "=" * 60)
# print("PAYMENTS")
# print("=" * 60)

# result = query_database.invoke(
#     {
#         "entity": "payments",
#         "limit": 3,
#     }
# )

# print(result)


# print("\n" + "=" * 60)
# print("FAILED PAYMENTS")
# print("=" * 60)

# result = query_database.invoke(
#     {
#         "entity": "payments",
#         "filters": {
#             "status": "FAILED",
#         },
#         "limit": 5,
#     }
# )

# print(result)


# print("\n" + "=" * 60)
# print("INCIDENTS")
# print("=" * 60)

# result = query_database.invoke(
#     {
#         "entity": "incidents",
#         "limit": 3,
#     }
# )

# print(result)

# from app.tools.database import query_database

# result = query_database.invoke(
#     {
#         "entity": "payments",
#         "limit": 20,
#     }
# )

# print(result)

# import sqlite3

# conn = sqlite3.connect("data/acmecloud.db")

# rows = conn.execute(
#     """
#     SELECT status, COUNT(*)
#     FROM payments
#     GROUP BY status
#     """
# ).fetchall()

# for row in rows:
#     print(row)

# conn.close()

# from app.tools.logs import search_logs


# print("=" * 60)
# print("RECENT LOGS")
# print("=" * 60)

# result = search_logs.invoke(
#     {
#         "limit": 5,
#     }
# )

# print(result)


# print("\n" + "=" * 60)
# print("ERROR LOGS")
# print("=" * 60)

# result = search_logs.invoke(
#     {
#         "level": "ERROR",
#         "limit": 10,
#     }
# )

# print(result)


# print("\n" + "=" * 60)
# print("TIMEOUT SEARCH")
# print("=" * 60)

# result = search_logs.invoke(
#     {
#         "query": "timeout",
#         "limit": 10,
#     }
# )

# print(result)
# Metrice.py
# from app.tools.metrics import query_metrics


# print("=" * 60)
# print("AVERAGE METRIC")
# print("=" * 60)

# result = query_metrics.invoke(
#     {
#         "metric_name": "api_latency",
#     }
# )

# print(result)

# cpu_usage: 504
# error_rate: 507
# memory_usage: 504
# p95_latency_ms: 506
# queue_depth: 505
# request_rate: 504
# retry_rate: 505

# import sqlite3

# conn = sqlite3.connect("data/acmecloud.db")

# rows = conn.execute(
#     """
#     SELECT
#         service_id,
#         metric_name,
#         metric_value,
#         unit,
#         environment,
#         recorded_at
#     FROM metric_samples
#     LIMIT 10
#     """
# ).fetchall()

# for row in rows:
#     print(row)

# conn.close()
# from app.tools.metrics import query_metrics


# print("=" * 60)
# print("AVERAGE P95 LATENCY")
# print("=" * 60)

# result = query_metrics.invoke(
#     {
#         "metric_name": "p95_latency_ms",
#     }
# )

# print(result)

# print("=" * 60)
# print("SERVICE METRIC")
# print("=" * 60)

# result = query_metrics.invoke(
#     {
#         "metric_name": "p95_latency_ms",
#         "service_id": "svc-api",
#     }
# )

# print(result)
# result = query_metrics.invoke(
#     {
#         "metric_name": "error_rate",
#         "service_id": "svc-api",
#         "aggregation": "avg",
#     }
# )

# print(result)

# import sqlite3

# conn = sqlite3.connect("data/acmecloud.db")

# rows = conn.execute(
#     """
#     SELECT
#         service_id,
#         service_name,
#         status
#     FROM services
#     ORDER BY service_id
#     """
# ).fetchall()

# for row in rows:
#     print(row)

# conn.close()

from app.tools.service_health import check_service_health


result = check_service_health.invoke(
    {
        "service_id": "svc-payment",
    }
)

print(result)
result = check_service_health.invoke(
    {
        "service_id": "svc-api",
    }
)

print(result)