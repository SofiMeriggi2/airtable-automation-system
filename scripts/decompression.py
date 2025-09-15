import json
from typing import Dict, List, Optional
from .config import (
    TABLE_PERSONAL, TABLE_EXPERIENCE, TABLE_SALARY,
    FIELD_APPLICANT_ID, TABLE_APPLICANTS
)
from .airtable_client import list_records, create_record, update_record, delete_records


def _get_applicant_rec_id_by_id(applicant_id_value: str) -> Optional[str]:
    """Busca el record ID interno en Applicants dado un Applicant ID lógico (ej: '0001')."""
    print(f"[DEBUG] Buscando rec_id para Applicant ID='{applicant_id_value}'")
    recs = list_records(
        TABLE_APPLICANTS,
        filter_formula=f"{{Applicant ID}} = '{applicant_id_value}'"
    )
    if not recs:
        print(f"[WARN] No Applicant found with Applicant ID {applicant_id_value}")
        return None
    rec_id = recs[0]["id"]
    print(f"[DEBUG] Applicant ID '{applicant_id_value}' → rec_id {rec_id}")
    return rec_id


def _get_child_records(table_name: str, rec_id: str) -> List[Dict]:
    filt = f"SEARCH('{rec_id}', ARRAYJOIN({{Applicant ID}}))"
    return list_records(table_name, filter_formula=filt)


def _normalize_technologies(value):
    """Convierte Technologies a string (para Airtable Long Text)."""
    if isinstance(value, list):
        return ", ".join([str(v).strip() for v in value if v])
    if isinstance(value, str):
        return value.strip()
    return ""


def _normalize_dates(fields: Dict) -> Dict:
    """Normaliza las fechas para Airtable: elimina vacíos y corta a YYYY-MM-DD."""
    for key in ["Start", "End"]:
        val = fields.get(key)
        if val and isinstance(val, str):
            fields[key] = val[:10]  
        else:
            fields.pop(key, None)  
    return fields


def _ensure_single_record(table_name: str, rec_id: str, fields: Dict):
    if "Technologies" in fields:
        fields["Technologies"] = _normalize_technologies(fields["Technologies"])

    existing = _get_child_records(table_name, rec_id)
    if existing:
        rid = existing[0]["id"]
        print(f"Updating {table_name} for Applicant {rec_id} with {fields}")
        new_fields = _normalize_dates(fields.copy())
        new_fields[FIELD_APPLICANT_ID] = [rec_id]
        try:
            update_record(table_name, rid, new_fields)
        except Exception as e:
            print(f"[ERROR] Failed to update {table_name} for {rec_id}: {e}")
        for r in existing[1:]:
            delete_records(table_name, [r["id"]])
    else:
        fields2 = _normalize_dates(fields.copy())
        fields2[FIELD_APPLICANT_ID] = [rec_id]
        print(f"Creating {table_name} for Applicant {rec_id} with {fields2}")
        try:
            create_record(table_name, fields2)
        except Exception as e:
            print(f"[ERROR] Failed to create {table_name} for {rec_id}: {e}")


def _replace_all_records(table_name: str, rec_id: str, rows: List[Dict]):
    existing = _get_child_records(table_name, rec_id)
    if existing:
        print(f"Deleting {len(existing)} existing {table_name} records for Applicant {rec_id}")
        delete_records(table_name, [r["id"] for r in existing])
    for row in rows:
        f = _normalize_dates(row.copy())
        if "Technologies" in f:
            f["Technologies"] = _normalize_technologies(f["Technologies"])

        f[FIELD_APPLICANT_ID] = [rec_id]
        print(f"Creating {table_name} record for Applicant {rec_id} with {f}")
        try:
            create_record(table_name, f)
        except Exception as e:
            print(f"[ERROR] Failed to create record in {table_name} for {rec_id}: {e}")


def decompress_from_json_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        applicants = json.load(f)

    print(f"\n=== Starting decompression for {len(applicants)} Applicants from {file_path} ===")

    for app in applicants:
        applicant_id_value = app.get("Applicant ID")
        if not applicant_id_value:
            print(f"[WARN] Applicant missing Applicant ID, skipping: {app}")
            continue

        rec_id = _get_applicant_rec_id_by_id(applicant_id_value)
        if not rec_id:
            continue

        personal = app.get("personal", {}) or {}
        salary = app.get("salary", {}) or {}
        experiences = app.get("experience", []) or []

        print(f"\n--- Decompressing Applicant {applicant_id_value} ({personal.get('Full Name')}) ---")
        _ensure_single_record(TABLE_PERSONAL, rec_id, personal)
        _ensure_single_record(TABLE_SALARY, rec_id, salary)
        _replace_all_records(TABLE_EXPERIENCE, rec_id, experiences)

        print(f"[DONE] Finished Applicant {applicant_id_value}")

    print("\n=== Decompression run finished ===")


if __name__ == "__main__":
    decompress_from_json_file("sample_compressed.json")
