from app.celery import celery
from app.api.v1.gapi.dal import get_gsheets_dal
from app.core.gapi.schemas import CTScanRequestSchema
from app.core.util.deidentification import run_deidentifier


@celery.task
def deidentify_ct_scan(ct_scan_request_dict):
    ct_scan_request = CTScanRequestSchema.parse_obj(ct_scan_request_dict)
    ct_scan = get_gsheets_dal().get_ctscan(ct_scan_request)
    run_deidentifier(ct_scan)
    return {"message": "success!!"}
