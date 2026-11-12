package com.scholo.repository;

import com.scholo.model.Scholarship;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;

@Repository
public class ScholarshipRepository {

    private final JdbcTemplate jdbcTemplate;

    public ScholarshipRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public List<Scholarship> findAll() {
        String sql = """
                SELECT id, name, provider, description,
                       education_level, eligible_courses, eligible_states,
                       max_annual_income_inr, min_marks_percent,
                       award_min_inr, award_max_inr,
                       application_start, application_deadline,
                       status, official_source_url, application_url
                FROM scholarships
                ORDER BY id
                """;

        return jdbcTemplate.query(sql, (rs, rowNum) -> mapScholarship(rs));
    }

    private Scholarship mapScholarship(ResultSet rs) throws SQLException {
        Scholarship scholarship = new Scholarship();

        scholarship.setId(rs.getString("id"));
        scholarship.setName(rs.getString("name"));
        scholarship.setProvider(rs.getString("provider"));
        scholarship.setDescription(rs.getString("description"));
        scholarship.setEducationLevel(rs.getString("education_level"));
        scholarship.setEligibleCourses(rs.getString("eligible_courses"));
        scholarship.setEligibleStates(rs.getString("eligible_states"));

        scholarship.setMaxAnnualIncomeInr(
                rs.getBigDecimal("max_annual_income_inr"));
        scholarship.setMinMarksPercent(
                rs.getBigDecimal("min_marks_percent"));
        scholarship.setAwardMinInr(
                rs.getBigDecimal("award_min_inr"));
        scholarship.setAwardMaxInr(
                rs.getBigDecimal("award_max_inr"));

        java.sql.Date start = rs.getDate("application_start");
        scholarship.setApplicationStart(
                start == null ? null : start.toLocalDate());

        java.sql.Date deadline = rs.getDate("application_deadline");
        scholarship.setApplicationDeadline(
                deadline == null ? null : deadline.toLocalDate());

        scholarship.setStatus(rs.getString("status"));
        scholarship.setOfficialSourceUrl(rs.getString("official_source_url"));
        scholarship.setApplicationUrl(rs.getString("application_url"));

        return scholarship;
    }
}