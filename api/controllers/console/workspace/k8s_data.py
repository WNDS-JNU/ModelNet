"""Console APIs for the ModelNet Kubernetes data plane."""

from flask import request
from flask_restx import Resource

from controllers.console import console_ns
from controllers.console.wraps import account_initialization_required, setup_required
from libs.login import login_required
from services.model_net_k8s_data_service import (
    get_k8s_cluster_snapshot,
    get_k8s_data_sources,
    get_k8s_events,
    get_k8s_models,
    get_k8s_nodes,
    get_k8s_overview,
    get_k8s_pods,
)


def _refresh_enabled() -> bool:
    return str(request.args.get("refresh", "true")).lower() not in {"0", "false", "no"}


@console_ns.route("/workspaces/current/k8s/overview")
class K8sOverviewApi(Resource):
    @console_ns.doc("get_k8s_overview")
    @console_ns.doc(description="Return a read-only overview of the Kubernetes inference data plane.")
    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        if _refresh_enabled():
            return get_k8s_overview(), 200
        snapshot = get_k8s_cluster_snapshot(refresh=False)
        return {
            "generated_at": snapshot["generated_at"],
            "namespaces": snapshot.get("namespaces", []),
            "overview": snapshot.get("overview", {}),
            "data_sources": snapshot.get("data_sources", []),
            "errors": snapshot.get("errors", []),
        }, 200


@console_ns.route("/workspaces/current/k8s/nodes")
class K8sNodesApi(Resource):
    @console_ns.doc("get_k8s_nodes")
    @console_ns.doc(description="Return normalized Kubernetes node snapshots with GPU and Jetson metrics.")
    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        return get_k8s_nodes(), 200


@console_ns.route("/workspaces/current/k8s/models")
class K8sModelsApi(Resource):
    @console_ns.doc("get_k8s_models")
    @console_ns.doc(description="Return normalized inference model runtime snapshots.")
    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        return get_k8s_models(), 200


@console_ns.route("/workspaces/current/k8s/pods")
class K8sPodsApi(Resource):
    @console_ns.doc("get_k8s_pods")
    @console_ns.doc(description="Return normalized inference Pod snapshots.")
    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        return get_k8s_pods(), 200


@console_ns.route("/workspaces/current/k8s/events")
class K8sEventsApi(Resource):
    @console_ns.doc("get_k8s_events")
    @console_ns.doc(description="Return recent Kubernetes events associated with the inference namespaces.")
    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        return get_k8s_events(), 200


@console_ns.route("/workspaces/current/k8s/data-sources")
class K8sDataSourcesApi(Resource):
    @console_ns.doc("get_k8s_data_sources")
    @console_ns.doc(
        description="Return health status for Kubernetes, metrics-server, Prometheus, and app metrics sources."
    )
    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        return get_k8s_data_sources(), 200
