# Scholo — AI Scholarship Companion (starter)

A starter project for an India-first scholarship discovery app using **Streamlit + Python/FastAPI + Java/Spring Boot**.

## Important prototype limits
- The Streamlit UI contains **illustrative demo records only**.
- Example links use `example.org` and are not application links.
- No live LLM, verified scholarship feed, login, or persistent database connection is wired up yet.
- Do not present demo records or their sample dates/match scores as real scholarship information.

## Requirements
- Python 3.10+
- Java 17+
- Maven 3.8+ (for the Java service)

## 1. Run the Streamlit interface
```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
The Streamlit interface is available at `http://localhost:8501`.

## 2. Run the Python AI-service scaffold
In another terminal from the project root:
```bash
pip install -r requirements.txt
uvicorn ai_service.main:app --reload --port 8000
```
- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`
- Matching endpoint: `POST http://localhost:8000/match`

The matching endpoint intentionally returns no results until verified scholarship data and matching rules are implemented.

## 3. Run the Java backend scaffold
```bash
cd java_backend
mvn spring-boot:run
```
- Health check: `http://localhost:8080/api/health`

## 4. Database
`database/schema.sql` is a proposed PostgreSQL schema. The services do not connect to it yet. Configure credentials through environment variables and never commit real secrets.

## Suggested implementation order
1. Build and test the UI with demo records.
2. Import a small, manually verified scholarship dataset from official sources.
3. Implement structured eligibility rules and status verification.
4. Connect Streamlit to the FastAPI service.
5. Add Java APIs and PostgreSQL persistence.
6. Add scheduled checks, audit history, and notifications.

## Trust and data quality rules
Every real scholarship should have an official source URL, a last-verified timestamp, and an evidence-based status. Use `unverified` when the current status cannot be confirmed. Never infer that an application is open just because a page loads.
