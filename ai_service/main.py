from datetime import date
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
import csv
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from tavily import TavilyClient


# --------------------------------------------------
# 1. FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Scholo AI Service",
    version="0.4.1",
    description="Scholarship search and eligibility matching service.",
)


# --------------------------------------------------
# 2. Dataset location
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
DATA_FILE = PROJECT_ROOT / "data" / "scholarships.csv"


# --------------------------------------------------
# 3. Request models
# --------------------------------------------------

class StudentProfile(BaseModel):
    state: Optional[str] = None
    education_level: Optional[str] = None
    course: Optional[str] = None
    year_of_study: Optional[str] = None

    annual_income_inr: Optional[int] = Field(default=None, ge=0)
    marks_percent: Optional[float] = Field(default=None, ge=0, le=100)

    gender: Optional[str] = None
    disability_status: Optional[str] = None
    category: Optional[str] = None
    application_type: Optional[str] = None
    academic_year: Optional[str] = None


class MatchRequest(BaseModel):
    profile: StudentProfile
    query: Optional[str] = None


# --------------------------------------------------
# 4. Load scholarship records
# --------------------------------------------------

def load_scholarships():
    """Read scholarship records from the project CSV file."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open(
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            return list(csv.DictReader(file))
    except (OSError, csv.Error):
        return []


# --------------------------------------------------
# 5. Matching helpers
# --------------------------------------------------

def normalize(value):
    """Return normalized text for case-insensitive comparisons."""
    return " ".join(str(value or "").strip().casefold().split())


def matches_allowed_values(allowed_values, student_value):
    """
    Match a student value against semicolon-separated allowed values.
    Blank restrictions are not treated as proof of eligibility.
    """
    if not normalize(allowed_values) or not normalize(student_value):
        return False

    allowed = [
        normalize(item)
        for item in str(allowed_values).split(";")
        if normalize(item)
    ]
    student = normalize(student_value)

    if not allowed:
        return False

    if any(item in {"all", "all india", "any"} for item in allowed):
        return True

    return student in allowed


def check_requirement(record, column, student_value):
    """
    Return True/False when a categorical requirement can be checked.
    Return None when the record or profile does not supply the value.
    """
    requirement = str(record.get(column, "") or "").strip()

    if not requirement or not student_value:
        return None

    return matches_allowed_values(requirement, student_value)


# --------------------------------------------------
# 6. Check general eligibility
# --------------------------------------------------

def get_eligibility(record, profile):
    """
    Check the general criteria represented in the CSV.

    True means the recorded general criteria passed. It does not
    independently verify special scheme-specific conditions.
    """
    checks = []

    # State
    eligible_states = str(record.get("eligible_states", "") or "").strip()
    if eligible_states:
        if not profile.state:
            return False
        checks.append(matches_allowed_values(eligible_states, profile.state))

    # Education level
    education = str(record.get("education_level", "") or "").strip()
    if education:
        if not profile.education_level:
            return False
        checks.append(matches_allowed_values(education, profile.education_level))

    # Course
    courses = str(record.get("eligible_courses", "") or "").strip()
    if courses:
        if not profile.course:
            return False
        checks.append(matches_allowed_values(courses, profile.course))

    # Annual family income
    income_limit = str(record.get("max_annual_income_inr", "") or "").strip()
    if income_limit:
        if profile.annual_income_inr is None:
            return False
        try:
            checks.append(profile.annual_income_inr <= float(income_limit))
        except (ValueError, TypeError):
            return False

    # Minimum marks
    minimum_marks = str(record.get("min_marks_percent", "") or "").strip()
    if minimum_marks:
        if profile.marks_percent is None:
            return False
        try:
            checks.append(profile.marks_percent >= float(minimum_marks))
        except (ValueError, TypeError):
            return False

    # Categorical requirements
    requirement_fields = [
        ("gender_requirement", profile.gender),
        ("disability_requirement", profile.disability_status),
        ("category_requirement", profile.category),
        ("application_type", profile.application_type),
        ("academic_year", profile.academic_year),
    ]

    for field, student_value in requirement_fields:
        requirement = str(record.get(field, "") or "").strip()
        if requirement:
            if not student_value:
                return False
            result = check_requirement(record, field, student_value)
            if result is not True:
                return False

    # Do not treat a record with no usable general criteria as a match.
    return bool(checks) and all(checks)


# --------------------------------------------------
# 7. Check whether a record is listed as applicable
# --------------------------------------------------

def is_currently_applicable(record):
    """
    Apply basic CSV status, URL-format, and deadline checks.
    These checks do not independently verify a scholarship website.
    """
    status = normalize(record.get("status", ""))

    # Only records explicitly marked open/upcoming are considered.
    if status not in {"open", "upcoming"}:
        return False

    official_url = str(record.get("official_source_url", "") or "").strip()
    if not official_url.startswith(("https://", "http://")):
        return False

    deadline = str(record.get("application_deadline", "") or "").strip()
    if deadline:
        try:
            deadline_date = date.fromisoformat(deadline)
        except ValueError:
            return False

        if deadline_date < date.today():
            return False

    return True


# --------------------------------------------------
# 8. Health endpoint
# --------------------------------------------------

@app.get("/health")
def health():
    records = load_scholarships()

    return {
        "service": "scholo-ai",
        "status": "ok",
        "dataset_file_found": DATA_FILE.exists(),
        "total_records_loaded": len(records),
        "live_scholarship_data": False,
    }


# --------------------------------------------------
# 9. Scholarship matching endpoint
# --------------------------------------------------



class ScholarshipSearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)
    state: Optional[str] = None
    education_level: Optional[str] = None
    course: Optional[str] = None
    annual_income_inr: Optional[int] = Field(default=None, ge=0)
    marks_percent: Optional[float] = Field(default=None, ge=0, le=100)

@app.post("/search-scholarships")
def search_scholarships(request: ScholarshipSearchRequest):
    """
    Search the web for scholarship opportunities.
    Search results are leads, not confirmed eligibility decisions.
    """

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Tavily API key is missing. Check the project-root .env file."
        )

    # Build a more specific search from the student's profile.
    search_terms = [
    request.query,
    "scholarships in India",
    "official scholarship eligibility application deadline",
    ]
    if request.state:
        search_terms.append(f"State: {request.state}")

    if request.education_level:
        search_terms.append(f"Education level: {request.education_level}")

    if request.course:
        search_terms.append(f"Course: {request.course}")

    if request.annual_income_inr is not None:
        search_terms.append(
            f"Annual family income: INR {request.annual_income_inr}"
        )

    if request.marks_percent is not None:
        search_terms.append(
            f"Academic marks: {request.marks_percent}%"
        )

    search_query = " ".join(search_terms)

    search_query = (
    '"scholarships for undergraduate engineering students" '
    'India 2026-27 '
    'official scholarship application '
    'eligibility criteria award amount deadline'
    )

    if request.state:
        search_query += f' "{request.state}"'
    try:
        client = TavilyClient(api_key=api_key)

        response = client.search(
            query=search_query,
            search_depth="basic",
            max_results=10,
            include_answer=False,
            include_raw_content="markdown",
            country="india",
            
        )

        results = []
        seen_urls = set()

        for item in response.get("results", []):
            title = (item.get("title") or "Untitled result").strip()
            url = (item.get("url") or "").strip()
            snippet = (item.get("content") or "").strip()
            raw_content = item.get("raw_content") or ""

            parsed_url = urlparse(url)

            # Accept only valid HTTPS URLs.
            if parsed_url.scheme.lower() != "https" or not parsed_url.hostname:
                continue

            normalized_url = url.rstrip("/").lower()

            if normalized_url in seen_urls:
                continue

            combined_text = f"{title} {snippet} {raw_content}".casefold()

            # Keep scholarship-related webpages.
            scholarship_keywords = [
                "scholarship",
                "scholarships",
                "financial aid",
                "fellowship",
                "education grant",
                "tuition fee",
                "fee waiver",
                "student funding",
                "stipend",
                "bursary",
            ]

            if not any(keyword in combined_text for keyword in scholarship_keywords):
                continue

            # Reject irrelevant results.
            negative_terms = [
                "national overseas scholarship",
                "study abroad",
                "ph.d",
                "2019-20",
                "2018-19",
            ]

            if any(term in combined_text for term in negative_terms):
                continue

            if "something went wrong" in combined_text:
                continue

            if "are you sure you want to sign out" in combined_text:
                continue

            if not snippet and title == "Untitled result":
                continue

            seen_urls.add(normalized_url)

            results.append({
                "title": title,
                "url": url,
                "snippet": snippet,
                "raw_content": raw_content,
                "relevance_score": item.get("score"),
                "verification_status": "not_verified",
                "eligibility_status": "requires_manual_verification",
            })

        # Sort after collecting all results.
        results.sort(
            key=lambda result: (
                result["relevance_score"]
                if isinstance(result["relevance_score"], (int, float))
                else 0
            ),
            reverse=True,
        )

        return {
            "query": request.query,
            "total_results": len(results),
            "results": results,
            "data_status": (
                "search_results_found" if results else "no_results_found"
            ),
            "notice": (
                "These search results are leads, not verified scholarship "
                "offers. Check the official scheme guidelines, eligibility "
                "criteria, award amount, and current application deadline "
                "before applying."
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:
        print(f"Tavily search failed: {type(exc).__name__}")

        raise HTTPException(
            status_code=502,
            detail=(
                "Scholarship search is temporarily unavailable. "
                "Please try again."
            ),
        ) from exc