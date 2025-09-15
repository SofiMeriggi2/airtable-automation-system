import json
import re
from datetime import datetime
from .config import (
    TABLE_SHORTLIST,
    FIELD_SL_APPLICANT,
    FIELD_SL_JSON,
    FIELD_SL_REASON,
)
from .airtable_client import create_record
from typing import Dict, List

from .config import (
    TABLE_SHORTLIST, TABLE_APPLICANTS,
    FIELD_COMPRESSED_JSON, FIELD_APPLICANT_ID,
    FIELD_SL_APPLICANT, FIELD_SL_JSON, FIELD_SL_REASON, FIELD_SL_CREATED_AT,
    TIER1_COMPANIES, SHORTLIST_COUNTRIES, MAX_RATE_USD, MIN_AVAIL_HOURS
)
from .airtable_client import create_record, list_records

DATE_FORMATS = (
    "%Y-%m-%d",   # 2020-01-31
    "%Y/%m/%d",   # 2020/01/31
    "%d-%m-%Y",   # 31-01-2020
    "%d/%m/%Y",   # 31/01/2020
)

def _parse_date(s: str):
    if not s:
        return None
    s = s.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    print(f"[WARN] Could not parse date '{s}'")
    return None

def _total_years(experiences: List[Dict]) -> float:
    days = 0
    for e in experiences:
        start = _parse_date(str(e.get("Start", "")))
        end = _parse_date(str(e.get("End", ""))) or datetime.utcnow()
        if start and end and end > start:
            days += (end - start).days
    return round(days / 365.25, 2)

def _worked_tier1(experiences: List[Dict]) -> bool:
    joined = " | ".join([str(e.get("Company", "")) for e in experiences])
    for brand in TIER1_COMPANIES:
        if re.search(rf"\b{re.escape(brand)}\b", joined, re.IGNORECASE):
            return True
    return False

def _location_ok(personal: Dict) -> bool:
    loc = str(personal.get("Location", ""))
    for c in SHORTLIST_COUNTRIES:
        if re.search(rf"\b{re.escape(c)}\b", loc, re.IGNORECASE):
            return True
    return False

def evaluate_shortlist(compressed: Dict) -> Dict:
    personal = compressed.get("personal") or {}
    salary = compressed.get("salary") or {}
    experiences = compressed.get("experience") or []

    yrs = _total_years(experiences)
    cond_exp = (yrs >= 4) or _worked_tier1(experiences)
    cond_comp = float(salary.get("Preferred Rate", 1e9)) <= MAX_RATE_USD and float(salary.get("Availability (hrs/wk)", 0)) >= MIN_AVAIL_HOURS
    cond_loc = _location_ok(personal)

    meets = all([cond_exp, cond_comp, cond_loc])

    reasons = []
    reasons.append(f"Experience: {yrs} years total; Tier-1: {'yes' if _worked_tier1(experiences) else 'no'}")
    reasons.append(f"Compensation: Preferred Rate={salary.get('Preferred Rate','N/A')} <= ${MAX_RATE_USD}/h; Availability={salary.get('Availability (hrs/wk)','N/A')} >= {MIN_AVAIL_HOURS} h/wk")
    reasons.append(f"Location: {personal.get('Location','N/A')} in allowed set: {'yes' if cond_loc else 'no'}")

    return {
        "meets": meets,
        "reason": " | ".join(reasons)
    }

def create_shortlisted_lead(applicant_record_id: str, compressed_json_text: str, score_reason: str):
    fields = {
        FIELD_SL_APPLICANT: [applicant_record_id],  # link field expects array of rec IDs
        FIELD_SL_JSON: compressed_json_text,
        FIELD_SL_REASON: score_reason,
    }
    print(f"[INFO] Creating Shortlisted Lead for {applicant_record_id}")
    print(f"[DEBUG] Payload enviado a Airtable ({TABLE_SHORTLIST}): {fields}")

    try:
        create_record(TABLE_SHORTLIST, fields)
    except Exception as e:
        print(f"[ERROR] Airtable rejected record for {applicant_record_id}: {e}")
        raise

def run_shortlist():
    print("\n=== Running Shortlist Evaluation ===")
    applicants = list_records(TABLE_APPLICANTS)
    for rec in applicants:
        rec_id = rec["id"]
        fields = rec.get("fields", {})
        json_text = fields.get(FIELD_COMPRESSED_JSON)
        if not json_text:
            continue
        try:
            compressed = json.loads(json_text)
        except Exception as e:
            print(f"[WARN] Invalid JSON for Applicant {rec_id}: {e}")
            continue

        result = evaluate_shortlist(compressed)
        if result["meets"]:
            create_shortlisted_lead(rec_id, json_text, result["reason"])
        else:
            print(f"[INFO] Applicant {rec_id} not shortlisted. Reason: {result['reason']}")

    print("=== Done ===")

if __name__ == "__main__":
    run_shortlist()
