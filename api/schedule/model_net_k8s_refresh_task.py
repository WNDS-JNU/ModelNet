import logging

import app
from services.model_net_k8s_registry_service import refresh_model_net_registry_from_k8s

logger = logging.getLogger(__name__)


@app.celery.task(queue="schedule_poller")
def refresh_model_net_k8s_registry() -> None:
    status = refresh_model_net_registry_from_k8s(triggered_by="schedule")
    logger.info(
        "ModelNet k8s refresh finished: status=%s applied=%s models=%s skipped=%s",
        status.get("status"),
        status.get("applied"),
        status.get("model_count"),
        status.get("skipped_count"),
    )
