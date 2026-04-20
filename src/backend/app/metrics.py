from collections import defaultdict
from collections.abc import Iterable
from threading import Lock

from fastapi import Request


class HttpMetricsCollector:
    """Собирает базовые HTTP метрики."""

    def __init__(self, buckets: Iterable[float] | None = None) -> None:
        self._buckets = tuple(
            buckets
            or (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
        )
        self._lock = Lock()
        self._request_total: dict[tuple[str, str, str], int] = defaultdict(
            int
        )
        self._duration_sum: dict[tuple[str, str, str], float] = defaultdict(
            float
        )
        self._duration_count: dict[tuple[str, str, str], int] = defaultdict(
            int
        )
        self._duration_buckets: dict[
            tuple[str, str, str],
            list[int],
        ] = defaultdict(lambda: [0] * len(self._buckets))

    def observe(
        self,
        method: str,
        path: str,
        status: str,
        duration_seconds: float,
    ) -> None:
        labels = (method, path, status)
        with self._lock:
            self._request_total[labels] += 1
            self._duration_sum[labels] += duration_seconds
            self._duration_count[labels] += 1
            for index, bucket in enumerate(self._buckets):
                if duration_seconds <= bucket:
                    self._duration_buckets[labels][index] += 1
                    break

    @staticmethod
    def _escape(value: str) -> str:
        escaped_value = value.replace("\\", "\\\\")
        escaped_value = escaped_value.replace('"', '\\"')
        return escaped_value.replace("\n", "\\n")

    def _labels(
        self,
        method: str,
        path: str,
        status: str,
        extra: str = "",
    ) -> str:
        base = (
            f'method="{self._escape(method)}",'
            f'path="{self._escape(path)}",'
            f'status="{self._escape(status)}"'
        )
        if extra:
            return f"{base},{extra}"
        return base

    def render(self) -> str:
        lines = [
            "# HELP http_requests_total Total HTTP requests.",
            "# TYPE http_requests_total counter",
        ]

        with self._lock:
            request_items = sorted(self._request_total.items())
            for (method, path, status), value in request_items:
                labels = self._labels(method, path, status)
                lines.append(f"http_requests_total{{{labels}}} {value}")

            lines.extend(
                [
                    "# HELP http_request_duration_seconds "
                    "HTTP request duration in seconds.",
                    "# TYPE http_request_duration_seconds histogram",
                ]
            )

            duration_items = sorted(self._duration_count.items())
            for labels_key, total_count in duration_items:
                method, path, status = labels_key
                labels = self._labels(method, path, status)
                cumulative_count = 0

                for index, bucket in enumerate(self._buckets):
                    bucket_count = self._duration_buckets[labels_key][index]
                    cumulative_count += bucket_count
                    bucket_labels = self._labels(
                        method,
                        path,
                        status,
                        f'le="{bucket:g}"',
                    )
                    lines.append(
                        "http_request_duration_seconds_bucket"
                        f"{{{bucket_labels}}} {cumulative_count}"
                    )

                inf_labels = self._labels(method, path, status, 'le="+Inf"')
                lines.append(
                    "http_request_duration_seconds_bucket"
                    f"{{{inf_labels}}} {total_count}"
                )
                lines.append(
                    "http_request_duration_seconds_sum"
                    f"{{{labels}}} {self._duration_sum[labels_key]}"
                )
                lines.append(
                    "http_request_duration_seconds_count"
                    f"{{{labels}}} {total_count}"
                )

        return "\n".join(lines) + "\n"


def resolve_metrics_path(request: Request) -> str:
    route = request.scope.get("route")
    route_path = getattr(route, "path", None)
    if route_path:
        return str(route_path)
    return request.url.path
