-- Starter schema sketch for PostgreSQL. Run only after reviewing and configuring your database.
CREATE TABLE IF NOT EXISTS scholarships (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    award_min_inr BIGINT,
    award_max_inr BIGINT,
    application_start DATE,
    application_deadline DATE,
    status TEXT NOT NULL CHECK (status IN ('open','upcoming','closed','unverified')),
    official_source_url TEXT NOT NULL,
    application_url TEXT,
    eligibility_rules JSONB NOT NULL DEFAULT '{}'::jsonb,
    last_verified_at TIMESTAMPTZ,
    verification_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS student_profiles (
    id BIGSERIAL PRIMARY KEY,
    preferred_name TEXT,
    state TEXT,
    education_level TEXT,
    course TEXT,
    year_of_study TEXT,
    annual_income_inr BIGINT,
    marks_percent NUMERIC(5,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS saved_scholarships (
    student_id BIGINT NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    scholarship_id BIGINT NOT NULL REFERENCES scholarships(id) ON DELETE CASCADE,
    saved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (student_id, scholarship_id)
);

CREATE TABLE IF NOT EXISTS applications (
    id BIGSERIAL PRIMARY KEY,
    student_id BIGINT NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    scholarship_id BIGINT NOT NULL REFERENCES scholarships(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('interested','checking_eligibility','preparing_documents','ready_to_apply','applied','awarded','not_selected')),
    notes TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (student_id, scholarship_id)
);
