import os
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")

TABLE_APPLICANTS = os.getenv("AIRTABLE_TABLE_APPLICANTS", "Applicants")
TABLE_PERSONAL = os.getenv("AIRTABLE_TABLE_PERSONAL", "Personal Details")
TABLE_EXPERIENCE = os.getenv("AIRTABLE_TABLE_EXPERIENCE", "Work Experience")
TABLE_SALARY = os.getenv("AIRTABLE_TABLE_SALARY", "Salary Preferences")
TABLE_SHORTLIST = os.getenv("AIRTABLE_TABLE_SHORTLIST", "Shortlisted Leads")

FIELD_APPLICANT_ID = os.getenv("FIELD_APPLICANT_ID", "Applicant ID")
FIELD_COMPRESSED_JSON = os.getenv("FIELD_COMPRESSED_JSON", "Compressed JSON")
FIELD_SHORTLIST_STATUS = os.getenv("FIELD_SHORTLIST_STATUS", "Shortlist Status")
FIELD_LLM_SUMMARY = os.getenv("FIELD_LLM_SUMMARY", "LLM Summary")
FIELD_LLM_SCORE = os.getenv("FIELD_LLM_SCORE", "LLM Score")
FIELD_LLM_FOLLOWUPS = os.getenv("FIELD_LLM_FOLLOWUPS", "LLM Follow-Ups")

# --- Shortlisted Leads fields ---
FIELD_SL_APPLICANT = os.getenv("FIELD_SL_APPLICANT", "Applicant")
FIELD_SL_JSON = os.getenv("FIELD_SL_JSON", "Compressed JSON")
FIELD_SL_REASON = os.getenv("FIELD_SL_REASON", "Score Reason")
FIELD_SL_CREATED_AT = os.getenv("FIELD_SL_CREATED_AT", "Created At")

TIER1_COMPANIES = [s.strip() for s in os.getenv("TIER1_COMPANIES", "").split(",") if s.strip()]
SHORTLIST_COUNTRIES = [s.strip() for s in os.getenv("SHORTLIST_COUNTRIES", "").split(",") if s.strip()]
MAX_RATE_USD = float(os.getenv("MAX_RATE_USD", "100"))
MIN_AVAIL_HOURS = float(os.getenv("MIN_AVAIL_HOURS", "20"))

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

LLM_MAX_OUTPUT_TOKENS = int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "350"))
LLM_RETRY_MAX = int(os.getenv("LLM_RETRY_MAX", "3"))
LLM_RETRY_BASE_SECONDS = float(os.getenv("LLM_RETRY_BASE_SECONDS", "1.2"))


def require(var_value: str, var_name: str):
    if not var_value:
        raise RuntimeError(f"Missing required environment variable: {var_name}")
    return var_value
