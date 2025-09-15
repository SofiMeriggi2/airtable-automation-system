import json
from typing import Dict, List
from .config import (
    TABLE_APPLICANTS, TABLE_PERSONAL, TABLE_EXPERIENCE, TABLE_SALARY,
    FIELD_APPLICANT_ID, FIELD_COMPRESSED_JSON
)
from .airtable_client import list_records, update_record


def compress_for_applicant(applicant_id: str) -> Dict:
    """Recolecta toda la info normalizada (personal, salary, experiences) para un applicant específico."""
    filt = f"{{{FIELD_APPLICANT_ID}}} = '{applicant_id}'"

    # 1) Personal Details (one-to-one)
    personal_rows = list_records(TABLE_PERSONAL, filter_formula=filt)
    personal = {}
    if personal_rows:
        personal = personal_rows[0]["fields"].copy()
        personal.pop(FIELD_APPLICANT_ID, None)

    # 2) Salary Preferences (one-to-one)
    salary_rows = list_records(TABLE_SALARY, filter_formula=filt)
    salary = {}
    if salary_rows:
        salary = salary_rows[0]["fields"].copy()
        salary.pop(FIELD_APPLICANT_ID, None)

    # 3) Work Experience (one-to-many)
    exp_rows = list_records(TABLE_EXPERIENCE, filter_formula=filt)
    experiences = []
    for r in exp_rows:
        fields = r["fields"].copy()
        fields.pop(FIELD_APPLICANT_ID, None)

        for key in ["Start", "End"]:
            if fields.get(key) and isinstance(fields[key], str):
                fields[key] = fields[key][:10]  

        experiences.append(fields)

    return {
        "personal": personal,
        "experience": experiences,
        "salary": salary
    }


def write_compressed_json_to_applicant(applicant_record_id: str, compressed_obj: Dict):
    """Escribe el JSON comprimido en la fila Applicants correspondiente."""
    update_record(TABLE_APPLICANTS, applicant_record_id, {
        FIELD_COMPRESSED_JSON: json.dumps(compressed_obj, ensure_ascii=False)
    })
