package com.scholo.model;

import java.math.BigDecimal;
import java.time.LocalDate;

public class Scholarship {

    private String id;
    private String name;
    private String provider;
    private String description;
    private String educationLevel;
    private String eligibleCourses;
    private String eligibleStates;
    private BigDecimal maxAnnualIncomeInr;
    private BigDecimal minMarksPercent;
    private BigDecimal awardMinInr;
    private BigDecimal awardMaxInr;
    private LocalDate applicationStart;
    private LocalDate applicationDeadline;
    private String status;
    private String officialSourceUrl;
    private String applicationUrl;

    public Scholarship() {
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getProvider() {
        return provider;
    }

    public void setProvider(String provider) {
        this.provider = provider;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getEducationLevel() {
        return educationLevel;
    }

    public void setEducationLevel(String educationLevel) {
        this.educationLevel = educationLevel;
    }

    public String getEligibleCourses() {
        return eligibleCourses;
    }

    public void setEligibleCourses(String eligibleCourses) {
        this.eligibleCourses = eligibleCourses;
    }

    public String getEligibleStates() {
        return eligibleStates;
    }

    public void setEligibleStates(String eligibleStates) {
        this.eligibleStates = eligibleStates;
    }

    public BigDecimal getMaxAnnualIncomeInr() {
        return maxAnnualIncomeInr;
    }

    public void setMaxAnnualIncomeInr(BigDecimal maxAnnualIncomeInr) {
        this.maxAnnualIncomeInr = maxAnnualIncomeInr;
    }

    public BigDecimal getMinMarksPercent() {
        return minMarksPercent;
    }

    public void setMinMarksPercent(BigDecimal minMarksPercent) {
        this.minMarksPercent = minMarksPercent;
    }

    public BigDecimal getAwardMinInr() {
        return awardMinInr;
    }

    public void setAwardMinInr(BigDecimal awardMinInr) {
        this.awardMinInr = awardMinInr;
    }

    public BigDecimal getAwardMaxInr() {
        return awardMaxInr;
    }

    public void setAwardMaxInr(BigDecimal awardMaxInr) {
        this.awardMaxInr = awardMaxInr;
    }

    public LocalDate getApplicationStart() {
        return applicationStart;
    }

    public void setApplicationStart(LocalDate applicationStart) {
        this.applicationStart = applicationStart;
    }

    public LocalDate getApplicationDeadline() {
        return applicationDeadline;
    }

    public void setApplicationDeadline(LocalDate applicationDeadline) {
        this.applicationDeadline = applicationDeadline;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getOfficialSourceUrl() {
        return officialSourceUrl;
    }

    public void setOfficialSourceUrl(String officialSourceUrl) {
        this.officialSourceUrl = officialSourceUrl;
    }

    public String getApplicationUrl() {
        return applicationUrl;
    }

    public void setApplicationUrl(String applicationUrl) {
        this.applicationUrl = applicationUrl;
    }
}


