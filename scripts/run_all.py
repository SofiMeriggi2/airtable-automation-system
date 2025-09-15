import json
from typing import Optional
from .config import (
    TABLE_APPLICANTS, FIELD_APPLICANT_ID, FIELD_COMPRESSED_JSON,
    FIELD_LLM_SUMMARY, FIELD_LLM_SCORE, FIELD_LLM_FOLLOWUPS
)
from .airtable_client import list_records, update_record
from .compression import compress_for_applicant, write_compressed_json_to_applicant
from .decompression import decompress_from_json_file
from .shortlist import evaluate_shortlist, create_shortlisted_lead
from .llm_client import call_llm


def process_applicant_record(rec: dict):
    rid = rec["id"]
    fields = rec.get("fields", {})
    applicant_id_value = fields.get(FIELD_APPLICANT_ID)

    print(f"\n[PROCESS] Applicant {applicant_id_value} (rec_id={rid})")

    # 1) Compress
    compressed_obj = compress_for_applicant(applicant_id_value)
    compressed_text = json.dumps(compressed_obj, ensure_ascii=False)
    write_compressed_json_to_applicant(rid, compressed_obj)
    print(f"[COMPRESS] Compressed JSON written for {applicant_id_value}")

    # 2) Shortlist
    verdict = evaluate_shortlist(compressed_obj)
    print(f"[SHORTLIST] Verdict for {applicant_id_value}: {verdict}")
    if verdict["meets"]:
        print(f"[SHORTLIST] Creating Shortlisted Lead for {applicant_id_value}")
        create_shortlisted_lead(rid, compressed_text, verdict["reason"])
    else:
        print(f"[SHORTLIST] Applicant {applicant_id_value} did NOT meet criteria")

    # 3) LLM evaluation
    try:
        llm_output = call_llm(compressed_text)
        summary, score, followups, issues = _parse_llm_output(llm_output)
    except Exception as e:
        print(f"[LLM] Skipping LLM eval for {applicant_id_value}: {e}")
        summary = "LLM evaluation skipped (no API key)."
        score = 0
        followups = "None"

    update_record(TABLE_APPLICANTS, rid, {
        FIELD_LLM_SUMMARY: summary,
        FIELD_LLM_SCORE: score,
        FIELD_LLM_FOLLOWUPS: followups
    })
    print(f"[DONE] Applicant {applicant_id_value} processed.\n")


def _parse_llm_output(txt: str):
    summary = ""
    score = None
    issues = ""
    followups = ""

    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    current = None
    bullets = []
    for line in lines:
        lowered = line.lower()
        if lowered.startswith("summary:"):
            current = "summary"
            summary = line.split(":", 1)[1].strip()
        elif lowered.startswith("score:"):
            current = "score"
            val = line.split(":", 1)[1].strip()
            try:
                score = int("".join(ch for ch in val if ch.isdigit()))
            except Exception:
                score = None
        elif lowered.startswith("issues:"):
            current = "issues"
            issues = line.split(":", 1)[1].strip()
        elif lowered.startswith("follow-ups:") or lowered.startswith("follow ups:"):
            current = "followups"
        elif line.startswith("-") or line.startswith("•"):
            if current == "followups":
                bullets.append(line.lstrip("-• ").strip())
        else:
            if current == "summary":
                summary += " " + line
    if bullets:
        followups = "\n".join(f"• {b}" for b in bullets)
    if score is None:
        score = 0
    return summary[:600], score, followups[:1000], issues[:600]


def run(applicant_id: Optional[str] = None):
    if applicant_id:
        recs = list_records(TABLE_APPLICANTS, filter_formula=f"{{{FIELD_APPLICANT_ID}}} = '{applicant_id}'")
    else:
        recs = list_records(TABLE_APPLICANTS)

    print(f"\n[RUN] Found {len(recs)} applicants to process")

    for rec in recs:
        process_applicant_record(rec)


if __name__ == "__main__":
    run()
