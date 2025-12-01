"""Main FastMCP server for monitoring operations."""

import random
from datetime import datetime, timedelta
from typing import Optional

from fastmcp import FastMCP

from ..config import get_settings
from ..utils import logger

# Initialize settings
settings = get_settings()
logger_instance = logger

# Initialize MCP server
mcp_server = FastMCP("monitoring-mcp-server")

# Mock data samples
INTERFACE_LOG_SAMPLES = [
    "Status: SUCCESS | System: {system_name} | Records: {records} | Time: {timestamp} | Duration: {duration}ms",
    "Status: ERROR | System: {system_name} | Records: {records} | Time: {timestamp} | Error: Connection timeout",
    "Status: PENDING | System: {system_name} | Records: {records} | Time: {timestamp} | Waiting for processing",
    "Status: SUCCESS | System: {system_name} | Records: {records} | Time: {timestamp} | Duration: {duration}ms | Data synced successfully",
    "Status: ERROR | System: {system_name} | Records: {records} | Time: {timestamp} | Error: Invalid data format",
]

BATCH_LOG_SAMPLES = [
    "Job: {job_name} | Status: SUCCESS | Start: {start_time} | End: {end_time} | Duration: {duration}s | Records processed: {records}",
    "Job: {job_name} | Status: FAILED | Start: {start_time} | End: {end_time} | Error: Database connection failed",
    "Job: {job_name} | Status: RUNNING | Start: {start_time} | Progress: {progress}% | ETA: {eta} minutes",
    "Job: {job_name} | Status: SUCCESS | Start: {start_time} | End: {end_time} | Duration: {duration}s | All tasks completed",
    "Job: {job_name} | Status: FAILED | Start: {start_time} | End: {end_time} | Error: Memory limit exceeded",
]

APP_LOG_SAMPLES = [
    "[{level}] {timestamp} - {service} - {message} | Thread: {thread} | User: {user}",
    "[{level}] {timestamp} - {service} - Database query failed: {error} | Query: {query}",
    "[{level}] {timestamp} - {service} - API request processed | Endpoint: {endpoint} | Status: {status} | Duration: {duration}ms",
    "[{level}] {timestamp} - {service} - {message} | Memory usage: {memory}MB | CPU: {cpu}%",
    "[{level}] {timestamp} - {service} - Exception occurred: {exception} | Stack trace available",
]

SERVER_PERF_SAMPLES = [
    "Node: {node} | CPU: {cpu}% | Memory: {memory}% | Disk I/O: {disk_io} MB/s | Network: {network} MB/s | Time: {timestamp}",
    "Node: {node} | CPU: {cpu}% | Memory: {memory}% | Load Average: {load_avg} | Uptime: {uptime} hours",
    "Node: {node} | CPU: {cpu}% | Memory: {memory}% | Disk Usage: {disk_usage}% | IOPS: {iops}",
    "Node: {node} | Metric: {metric_type} | Value: {value} | Status: {status} | Timestamp: {timestamp}",
]

APP_PERF_SAMPLES = [
    "Service: {service} | Endpoint: {endpoint} | Latency: {latency}ms | Throughput: {throughput} req/s | Error Rate: {error_rate}%",
    "Service: {service} | Endpoint: {endpoint} | P50: {p50}ms | P95: {p95}ms | P99: {p99}ms | Requests: {requests}",
    "Service: {service} | Endpoint: {endpoint} | Avg Response Time: {avg_time}ms | Success Rate: {success_rate}%",
    "Service: {service} | Performance Summary | Total Requests: {total_req} | Failed: {failed} | Avg Latency: {latency}ms",
]

APM_SAMPLES = [
    "Service: {service} | Trace ID: {trace_id} | Span: {span} | Duration: {duration}ms | Status: {status} | Timestamp: {timestamp}",
    "Service: {service} | Error Rate: {error_rate}% | Total Errors: {errors} | Time Range: {minutes} minutes",
    "Service: {service} | Latency P50: {p50}ms | P95: {p95}ms | P99: {p99}ms | Time: {timestamp}",
    "Service: {service} | Metric: {metric_type} | Value: {value} | Threshold: {threshold} | Status: {status}",
]

API_HEALTH_SAMPLES = [
    "Service: {service_name} | Endpoint: /health | Status: {status} | Response Time: {response_time}ms | HTTP Code: {http_code}",
    "Service: {service_name} | Health Check: {status} | Uptime: {uptime}% | Last Check: {timestamp}",
    "Service: {service_name} | Status: {status} | Dependencies: {dependencies} | Latency: {latency}ms",
]


# Register tools with MCP server
@mcp_server.tool()
async def check_interface_logs(
    system_name: str = "all",
    hours: int = 1,
    status: str = None,
) -> str:
    """
    Check interface logs for deployment abnormalities.

    Args:
        system_name: System to check (HR, Policy, Payment, or 'all')
        hours: Look back N hours from now
        status: Filter by status (SUCCESS, PENDING, ERROR, or None for all)

    Returns:
        Formatted string with I/F log results

    Examples:
        - "Check today's interface data for the HR system"
        - "Show me I/F records that failed in the last 1 hour"
        - "Verify if new policy data arrived in the interface table"
        - "Is there any I/F data stuck in PENDING status?"
    """
    results = []
    num_results = random.randint(3, 8)
    
    for _ in range(num_results):
        template = random.choice(INTERFACE_LOG_SAMPLES)
        timestamp = datetime.now() - timedelta(hours=random.randint(0, hours))
        system = system_name if system_name != "all" else random.choice(["HR", "Policy", "Payment", "Finance"])
        
        result = template.format(
            system_name=system,
            records=random.randint(10, 1000),
            timestamp=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            duration=random.randint(50, 2000),
        )
        results.append(result)
    
    return f"Interface Logs for {system_name} (last {hours} hours):\n" + "\n".join(results)


@mcp_server.tool()
async def check_batch_logs(
    job_name: str = "all",
    hours: int = 24,
    status: str = None,
) -> str:
    """
    Check batch processing results for abnormalities.

    Args:
        job_name: Batch job name or 'all'
        hours: Look back N hours
        status: Filter by status (SUCCESS, FAILED, RUNNING, or None)

    Returns:
        Formatted batch job results

    Examples:
        - "Check the results of last night's batch jobs"
        - "Show me failed batch records for the premium calculation batch"
        - "Did the membership sync batch complete successfully today?"
        - "List all batch jobs that are still running or delayed"
    """
    results = []
    num_results = random.randint(3, 8)
    
    for _ in range(num_results):
        template = random.choice(BATCH_LOG_SAMPLES)
        start_time = datetime.now() - timedelta(hours=random.randint(0, hours))
        end_time = start_time + timedelta(minutes=random.randint(5, 120))
        job = job_name if job_name != "all" else random.choice(["premium_calc", "membership_sync", "data_export", "report_generation"])
        
        result = template.format(
            job_name=job,
            start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
            end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
            duration=random.randint(30, 3600),
            records=random.randint(100, 10000),
            progress=random.randint(10, 95),
            eta=random.randint(5, 60),
        )
        results.append(result)
    
    return f"Batch Logs for {job_name} (last {hours} hours):\n" + "\n".join(results)


@mcp_server.tool()
async def check_application_logs(
    service: str = "all",
    minutes: int = 30,
    level: str = "ERROR",
    search_pattern: str = None,
) -> str:
    """
    Retrieve and analyze application logs for errors and exceptions.

    Args:
        service: Service name or 'all'
        minutes: Look back N minutes
        level: Log level (ERROR, WARN, INFO)
        search_pattern: Search for specific pattern in message

    Returns:
        Formatted application log results

    Examples:
        - "Search the application logs for errors in the last 30 minutes"
        - "Show me all WARN or ERROR logs for the payment service"
        - "Are there any database connection errors?"
    """
    results = []
    num_results = random.randint(3, 10)
    
    for _ in range(num_results):
        template = random.choice(APP_LOG_SAMPLES)
        timestamp = datetime.now() - timedelta(minutes=random.randint(0, minutes))
        svc = service if service != "all" else random.choice(["payment-service", "api-gateway", "user-service", "order-service"])
        
        result = template.format(
            level=level,
            timestamp=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            service=svc,
            message=f"Pattern: {search_pattern}" if search_pattern else random.choice([
                "Request processed successfully",
                "Database connection established",
                "Cache miss occurred",
                "Authentication failed"
            ]),
            thread=f"thread-{random.randint(1, 100)}",
            user=f"user{random.randint(1000, 9999)}",
            error="Connection timeout" if level == "ERROR" else "N/A",
            query="SELECT * FROM users WHERE id = ?" if level == "ERROR" else "N/A",
            endpoint=f"/api/v1/{random.choice(['users', 'orders', 'payments'])}",
            status=random.choice([200, 201, 400, 500]),
            duration=random.randint(10, 500),
            memory=random.randint(100, 2000),
            cpu=random.uniform(0.5, 95.0),
            exception="NullPointerException" if level == "ERROR" else "N/A",
        )
        results.append(result)
    
    return f"Application Logs for {service} [{level}] (last {minutes} minutes):\n" + "\n".join(results)


@mcp_server.tool()
async def view_server_performance(
    node: str = "all",
    metric_type: str = "all",
    minutes: int = 5,
) -> str:
    """
    Check real-time server and infrastructure performance metrics.

    Args:
        node: Node name or 'all'
        metric_type: Type of metric (cpu, memory, disk_io, network, or 'all')
        minutes: Time range in minutes

    Returns:
        Server performance metrics summary

    Examples:
        - "Show me CPU usage for all nodes"
        - "What's the memory usage on k8s-node-01?"
        - "Check network I/O across all nodes"
        - "Are any nodes running hot?"
    """
    results = []
    num_results = random.randint(3, 6)
    
    for _ in range(num_results):
        template = random.choice(SERVER_PERF_SAMPLES)
        timestamp = datetime.now() - timedelta(minutes=random.randint(0, minutes))
        node_name = node if node != "all" else f"k8s-node-{random.randint(1, 5):02d}"
        
        result = template.format(
            node=node_name,
            cpu=round(random.uniform(5.0, 95.0), 2),
            memory=round(random.uniform(20.0, 90.0), 2),
            disk_io=round(random.uniform(10.0, 500.0), 2),
            network=round(random.uniform(5.0, 1000.0), 2),
            timestamp=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            load_avg=round(random.uniform(0.5, 8.0), 2),
            uptime=random.randint(1, 720),
            disk_usage=random.randint(30, 85),
            iops=random.randint(100, 5000),
            metric_type=metric_type,
            value=round(random.uniform(10.0, 100.0), 2),
            status=random.choice(["OK", "WARNING", "CRITICAL"]),
        )
        results.append(result)
    
    return f"Server Performance for {node} [{metric_type}] (last {minutes} minutes):\n" + "\n".join(results)


@mcp_server.tool()
async def view_application_performance(
    service: str = "all",
    endpoint: str = None,
    minutes: int = 5,
) -> str:
    """
    View application-level performance metrics (latency, throughput, error rates).

    Args:
        service: Service name or 'all'
        endpoint: Specific endpoint or None
        minutes: Time range in minutes

    Returns:
        Application performance metrics

    Examples:
        - "Show me API latency for payment service"
        - "What's the error rate across all services?"
        - "Check throughput for the api-gateway"
        - "Is /api/v1/users experiencing high latency?"
    """
    results = []
    num_results = random.randint(3, 8)
    
    for _ in range(num_results):
        template = random.choice(APP_PERF_SAMPLES)
        svc = service if service != "all" else random.choice(["payment-service", "api-gateway", "user-service", "order-service"])
        ep = endpoint if endpoint else f"/api/v1/{random.choice(['users', 'orders', 'payments', 'products'])}"
        
        result = template.format(
            service=svc,
            endpoint=ep,
            latency=random.randint(10, 500),
            throughput=random.randint(10, 1000),
            error_rate=round(random.uniform(0.1, 5.0), 2),
            p50=random.randint(50, 150),
            p95=random.randint(150, 400),
            p99=random.randint(400, 1000),
            requests=random.randint(100, 10000),
            avg_time=random.randint(50, 300),
            success_rate=round(random.uniform(95.0, 99.9), 2),
            total_req=random.randint(1000, 50000),
            failed=random.randint(10, 500),
        )
        results.append(result)
    
    return f"Application Performance for {service} (last {minutes} minutes):\n" + "\n".join(results)


@mcp_server.tool()
async def application_performance_inquiry(
    area: str = "all",
    time_range_minutes: int = 5,
) -> str:
    """
    Monitor the performance of the APPL (Application) area.

    Args:
        area: Application area to monitor (e.g., "payment", "order", "user", "all")
        time_range_minutes: Time range in minutes to query (default: 5)

    Returns:
        Prometheus-style metrics response for application performance

    Examples:
        - "Check payment application performance"
        - "Monitor order processing area performance"
        - "Show me user service performance metrics"
    """
    results = []
    num_results = random.randint(3, 6)
    
    for _ in range(num_results):
        template = random.choice(APP_PERF_SAMPLES)
        app_area = area if area != "all" else random.choice(["payment", "order", "user", "product"])
        
        result = template.format(
            service=f"{app_area}-service",
            endpoint=f"/api/v1/{app_area}",
            latency=random.randint(10, 300),
            throughput=random.randint(50, 2000),
            error_rate=round(random.uniform(0.1, 3.0), 2),
            p50=random.randint(30, 100),
            p95=random.randint(100, 300),
            p99=random.randint(300, 800),
            requests=random.randint(500, 20000),
            avg_time=random.randint(40, 200),
            success_rate=round(random.uniform(96.0, 99.9), 2),
            total_req=random.randint(5000, 100000),
            failed=random.randint(5, 200),
        )
        results.append(result)
    
    return f"Application Performance Inquiry for {area} (last {time_range_minutes} minutes):\n" + "\n".join(results)


@mcp_server.tool()
async def check_apm(
    service: str = "all",
    metric_type: str = "traces",
    minutes: int = 15,
    error_threshold: Optional[float] = None,
) -> str:
    """
    Query APM data such as application traces, error rates, and latency metrics.

    Args:
        service: Service name to query (e.g., "payment-service", "api-gateway", "all")
        metric_type: Type of APM data ("traces", "errors", "latency", "all")
        minutes: Time range in minutes (default: 15)
        error_threshold: Optional error rate threshold to filter (e.g., 5.0 for 5%)

    Returns:
        APM data in distributed tracing format (OpenTelemetry/Jaeger style) or Prometheus metrics

    Examples:
        - "Check APM traces for payment service"
        - "Show me error rates across all services"
        - "Get latency metrics for the last 15 minutes"
        - "Find services with error rate above 5%"
    """
    results = []
    num_results = random.randint(4, 10)
    
    for _ in range(num_results):
        template = random.choice(APM_SAMPLES)
        timestamp = datetime.now() - timedelta(minutes=random.randint(0, minutes))
        svc = service if service != "all" else random.choice(["payment-service", "api-gateway", "user-service", "order-service"])
        error_rate = round(random.uniform(0.1, 10.0), 2)
        
        # Skip if error_threshold is set and error_rate is below threshold
        if error_threshold and error_rate < error_threshold:
            continue
        
        result = template.format(
            service=svc,
            trace_id=f"trace-{random.randint(100000, 999999)}",
            span=f"span-{random.randint(1, 100)}",
            duration=random.randint(10, 1000),
            status=random.choice(["OK", "ERROR", "TIMEOUT"]),
            timestamp=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            error_rate=error_rate,
            errors=random.randint(1, 100),
            minutes=minutes,
            p50=random.randint(30, 100),
            p95=random.randint(100, 400),
            p99=random.randint(400, 1000),
            metric_type=metric_type,
            value=round(random.uniform(10.0, 500.0), 2),
            threshold=error_threshold if error_threshold else "N/A",
        )
        results.append(result)
    
    threshold_msg = f" (threshold: {error_threshold}%)" if error_threshold else ""
    return f"APM Data for {service} [{metric_type}] (last {minutes} minutes){threshold_msg}:\n" + "\n".join(results)


@mcp_server.tool()
async def check_api_health(
    service_name: str = "all",
) -> str:
    """
    Check HTTP API health by calling health check endpoints and monitoring response codes and times.

    Args:
        service_name: Service name (e.g., "payment-service", "all")

    Returns:
        Prometheus-style metrics response for API health checks

    Examples:
        - "Check health of payment service"
        - "Show me all API health status"
        - "Get health status for order service"
    """
    results = []
    num_results = random.randint(3, 8)
    
    for _ in range(num_results):
        template = random.choice(API_HEALTH_SAMPLES)
        timestamp = datetime.now() - timedelta(seconds=random.randint(0, 300))
        svc = service_name if service_name != "all" else random.choice(["payment-service", "api-gateway", "user-service", "order-service", "product-service"])
        
        result = template.format(
            service_name=svc,
            status=random.choice(["healthy", "unhealthy", "degraded"]),
            response_time=random.randint(5, 500),
            http_code=random.choice([200, 201, 500, 503]),
            uptime=round(random.uniform(95.0, 99.99), 2),
            timestamp=timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            dependencies=random.randint(1, 5),
            latency=random.randint(10, 300),
        )
        results.append(result)
    
    return f"API Health Check for {service_name}:\n" + "\n".join(results)


def main():
    """Run the MCP server."""
    logger_instance.info(
        f"Starting {settings.server_name} v{settings.server_version}"
    )
    logger_instance.info(f"Log level: {settings.log_level}")
    logger_instance.info("Using mock data generation (no data loader required)")
    logger_instance.info(f"Transport: {settings.server_transport}")
    
    transport = settings.server_transport.lower()
    
    if transport == "stdio":
        logger_instance.info("Monitoring MCP server running with STDIO transport")
        mcp_server.run()
    elif transport == "sse":
        logger_instance.info(
            f"Monitoring MCP server running with SSE transport on "
            f"{settings.server_host}:{settings.server_port}"
        )
        mcp_server.run(
            transport="sse",
            host=settings.server_host,
            port=settings.server_port,
        )
    elif transport in ("streamable-http", "http"):
        logger_instance.info(
            f"Monitoring MCP server running with Streamable HTTP transport on "
            f"{settings.server_host}:{settings.server_port}"
        )
        mcp_server.run(
            transport="streamable-http",
            host=settings.server_host,
            port=settings.server_port,
        )
    else:
        logger_instance.warning(
            f"Unknown transport '{transport}', falling back to STDIO"
        )
        mcp_server.run()


if __name__ == "__main__":
    main()
