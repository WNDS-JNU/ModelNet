"""Console API: ``GET /workspaces/current/local-models``.

Surface for the parallel-ensemble node's *model* dropdown (P2.11). Each
entry is a :class:`BackendInfo` projection of one yaml registry row —
``{id, backend, model_name, capabilities, metadata}`` — with **no
url / api_key / api_key_env**. The omission is the workspace-side half
of the T2 SSRF / credential boundary: even if the frontend leaks the
response into a workflow DSL, no secret travels.

Reads :class:`ModelRegistry.instance()` directly. The registry is the
authoritative source the node will consume at runtime; routing through
a service layer would just reflect the same call.
"""

from flask import request
from flask_restx import Resource, fields

from controllers.console import console_ns
from controllers.console.wraps import (
    account_initialization_required,
    is_admin_or_owner_required,
    setup_required,
)
from core.workflow.nodes.parallel_ensemble.registry import ModelRegistry
from libs.login import login_required
from services.model_net_k8s_registry_service import (
    get_model_net_k8s_refresh_status,
    refresh_model_net_registry_from_k8s,
)
from services.model_net_load_service import (
    get_model_net_load_status,
    route_model_from_payload,
)


@console_ns.route("/workspaces/current/local-models")
class LocalModelsApi(Resource):
    @console_ns.doc("list_local_models")
    @console_ns.doc(description="List parallel-ensemble model aliases (BackendInfo, no url/api_key).")
    @console_ns.response(
        200,
        "Success",
        fields.List(fields.Raw(description="BackendInfo: id, backend, model_name, capabilities, metadata")),
    )
    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        return {"models": list(ModelRegistry.instance().list_aliases())}


@console_ns.route("/workspaces/current/local-models/refresh")
class LocalModelsRefreshApi(Resource):
    @console_ns.doc("refresh_local_models_from_k8s")
    @console_ns.doc(description="Refresh the ModelNet model registry from Kubernetes Ingress discovery.")
    @setup_required
    @login_required
    @account_initialization_required
    @is_admin_or_owner_required
    def post(self):
        return refresh_model_net_registry_from_k8s(triggered_by="manual"), 200


@console_ns.route("/workspaces/current/local-models/refresh-status")
class LocalModelsRefreshStatusApi(Resource):
    @console_ns.doc("get_local_models_refresh_status")
    @console_ns.doc(description="Return the latest ModelNet k8s discovery refresh status.")
    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        return get_model_net_k8s_refresh_status(), 200


@console_ns.route("/workspaces/current/local-models/load-status")
class LocalModelsLoadStatusApi(Resource):
    @console_ns.doc("get_local_model_load_status")
    @console_ns.doc(description="Return ModelNet aliases enriched with Prometheus-backed load status.")
    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        return get_model_net_load_status(), 200


@console_ns.route("/workspaces/current/local-models/route")
class LocalModelsRouteApi(Resource):
    @console_ns.doc("route_local_model")
    @console_ns.doc(description="Rank ModelNet aliases and select the best model for a load-aware call.")
    @setup_required
    @login_required
    @account_initialization_required
    def post(self):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            payload = {}
        return route_model_from_payload(payload), 200
