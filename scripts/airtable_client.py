import requests
from typing import Dict, List, Optional
from .config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, require # type: ignore

# Ensure environment variables are strings for type safety
AIRTABLE_API_KEY: str = str(AIRTABLE_API_KEY)
AIRTABLE_BASE_ID: str = str(AIRTABLE_BASE_ID)

API_BASE = "https://api.airtable.com/v0"

def _headers():
    token = require(AIRTABLE_API_KEY, "AIRTABLE_API_KEY")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def _url(table_name: str):
    base_id = require(AIRTABLE_BASE_ID, "AIRTABLE_BASE_ID")
    return f"{API_BASE}/{base_id}/{requests.utils.quote(table_name, safe='')}" # type: ignore

def list_records(table_name: str, filter_formula: Optional[str] = None, fields: Optional[List[str]] = None, page_size: int = 100) -> List[Dict]:
    url = _url(table_name)
    params = {"pageSize": page_size}
    if filter_formula:
        params["filterByFormula"] = filter_formula # type: ignore
    if fields:
        for i, fld in enumerate(fields):
            params[f"fields[{i}]"] = fld # type: ignore

    out = []
    offset = None
    while True:
        if offset:
            params["offset"] = offset
        resp = requests.get(url, headers=_headers(), params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        out.extend(data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
    return out

def create_record(table_name: str, fields: Dict) -> Dict:
    url = _url(table_name)
    payload = {"records": [{"fields": fields}]}
    resp = requests.post(url, headers=_headers(), json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["records"][0]

def update_record(table_name: str, record_id: str, fields: Dict) -> Dict:
    url = _url(table_name)
    payload = {"records": [{"id": record_id, "fields": fields}]}
    resp = requests.patch(url, headers=_headers(), json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["records"][0]

def delete_records(table_name: str, record_ids: List[str]):
    url = _url(table_name)
    # Airtable supports batch deletes via query string ?records[]=rec1&records[]=rec2
    params = []
    for rid in record_ids:
        params.append(("records[]", rid))
    resp = requests.delete(url, headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()
