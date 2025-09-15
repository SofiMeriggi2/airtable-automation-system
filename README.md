Features

  Multi-table Airtable schema with Applicants, Personal Details, Work Experience, Salary Preferences, and Shortlisted Leads.

  JSON Compression/Decompression: store normalized applicant data in a single field and rebuild it on demand.

  Shortlisting Automation: automatically select promising candidates based on configurable rules.

  LLM Integration: summarize candidates, assign quality score, and suggest follow-ups.

  Configurable via .env file (no hardcoded values).



Airtable Schema

  Applicants (Parent)

  Applicant ID (primary)

  Compressed JSON

  Shortlist Status

  LLM Summary

  LLM Score

  LLM Follow-Ups

  Personal Details (1:1)

  Full Name

  Email

  Location

  LinkedIn

  Applicant ID (link to Applicants)

  Work Experience (1:N)

  Company

  Title

  Start

  End

  Technologies

  Applicant ID (link to Applicants)

  Salary Preferences (1:1)

  Preferred Rate

  Minimum Rate

  Currency

  Availability (hrs/wk)

  Applicant ID (link to Applicants)

  Shortlisted Leads (auto-populated)

  Applicant (link to Applicants)

  Compressed JSON

  Score Reason

  Created At



Setup

  Clone repo & install dependencies:

  pip install -r requirements.txt


  Create .env file with:

  AIRTABLE_API_KEY=...
  AIRTABLE_BASE_ID=...
  OPENAI_API_KEY=...   # or Anthropic / Gemini
  LLM_PROVIDER=openai


  Configure shortlist rules in .env:

  TIER1_COMPANIES=Google,Meta,OpenAI,...
  SHORTLIST_COUNTRIES=United States,Canada,UK,Germany,India
  MAX_RATE_USD=100
  MIN_AVAIL_HOURS=20



Usage
  1. Decompress JSON → Airtable

  Populate child tables from a JSON file:

  python -m scripts.decompression

  2. Full Pipeline (Compress + Shortlist + LLM)

  Run processing for all Applicants:

  python -m scripts.run_all



LLM Integration

  Provider configurable: openai, anthropic, gemini.

  Prompt generates:

  Summary (≤75 words)

  Score (1–10)

  Issues (missing or inconsistent fields)

  Follow-Ups (up to 3 questions)

  Guardrails:

  Max output tokens = 350

  Retries with exponential backoff

  Skips if no API key is present



Shortlist Criteria

  Defined in shortlist.py → evaluate_shortlist():

  Experience ≥ 4 years OR Tier-1 company

  Preferred Rate ≤ MAX_RATE_USD

  Availability ≥ MIN_AVAIL_HOURS

  Location in SHORTLIST_COUNTRIES

  Configurable entirely via .env.



Extending

  Add new shortlist rules → edit evaluate_shortlist.

  Add new fields → update Airtable schema + compression/decompression logic.

  Swap LLM provider → change LLM_PROVIDER in .env.