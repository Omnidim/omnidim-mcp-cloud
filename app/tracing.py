"""OpenTelemetry traces, on only when OTEL_EXPORTER_OTLP_ENDPOINT is set.

The request id is the trace id: the server span adopts the caller's traceparent, else a
32-hex X-Request-ID, else mints its own id. RequestIdMiddleware then reads it back.
"""

import os
import re

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.context import Context
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.propagators.textmap import (
    CarrierT,
    DefaultGetter,
    Getter,
    Setter,
    TextMapPropagator,
    default_setter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter
from opentelemetry.sdk.trace.id_generator import RandomIdGenerator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

SERVICE_NAME = "omnidim-mcp-cloud"
UNTRACED_PATHS = "healthz,readyz"
_TRACE_ID = re.compile(r"[0-9a-f]{32}")


class _RequestIdPropagator(TextMapPropagator):
    """Use a bare 32-hex X-Request-ID as the trace id when no traceparent came in."""

    def extract(
        self,
        carrier: CarrierT,
        context: Context | None = None,
        getter: Getter[CarrierT] = DefaultGetter(),  # type: ignore[assignment]  # noqa: B008
    ) -> Context:
        context = context if context is not None else Context()
        if trace.get_current_span(context).get_span_context().is_valid:
            return context
        raw = getter.get(carrier, "x-request-id")
        value = raw[0].lower() if raw else ""
        if not _TRACE_ID.fullmatch(value) or int(value, 16) == 0:
            return context
        parent = trace.SpanContext(
            trace_id=int(value, 16),
            span_id=RandomIdGenerator().generate_span_id(),
            is_remote=True,
            trace_flags=trace.TraceFlags(trace.TraceFlags.SAMPLED),
        )
        return trace.set_span_in_context(trace.NonRecordingSpan(parent), context)

    def inject(
        self,
        carrier: CarrierT,
        context: Context | None = None,
        setter: Setter[CarrierT] = default_setter,
    ) -> None:
        return None

    @property
    def fields(self) -> set[str]:
        return set()


def tracing_endpoint() -> str:
    return os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()


def setup_tracing(app: FastAPI, exporter: SpanExporter | None = None) -> TracerProvider:
    """Instrument the app and httpx. Export never blocks a request: bounded queue, 2 s timeout."""
    provider = TracerProvider(resource=Resource.create({"service.name": SERVICE_NAME}))
    provider.add_span_processor(
        BatchSpanProcessor(
            exporter or OTLPSpanExporter(timeout=2),
            max_queue_size=2048,
            export_timeout_millis=2000,
        )
    )
    set_global_textmap(
        CompositePropagator([TraceContextTextMapPropagator(), _RequestIdPropagator()])
    )
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider, excluded_urls=UNTRACED_PATHS)
    HTTPXClientInstrumentor().instrument(tracer_provider=provider)
    return provider


def current_trace_id() -> str | None:
    ctx = trace.get_current_span().get_span_context()
    return format(ctx.trace_id, "032x") if ctx.is_valid else None
