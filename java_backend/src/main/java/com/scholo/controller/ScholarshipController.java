package com.scholo.controller;

import com.scholo.model.Scholarship;
import com.scholo.service.ScholarshipService;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/scholarships")
public class ScholarshipController {

    private final ScholarshipService scholarshipService;

    public ScholarshipController(ScholarshipService scholarshipService) {
        this.scholarshipService = scholarshipService;
    }

    @GetMapping("/health")
    public Map<String, Object> scholarshipHealth() {
        return Map.of(
                "service", "scholo-scholarship-api",
                "status", "ok",
                "message", "Scholarship API is ready"
        );
    }

    @GetMapping
    public Map<String, Object> getScholarships() {
        List<Scholarship> scholarships =
                scholarshipService.getAllScholarships();

        return Map.of(
                "total", scholarships.size(),
                "data_status", "postgresql_connected",
                "message", "Scholarship records loaded from PostgreSQL",
                "scholarships", scholarships
        );
    }

    @GetMapping("/{id}")
    public Scholarship getScholarshipById(@PathVariable String id) {
        return scholarshipService.getScholarshipById(id)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND,
                        "Scholarship not found: " + id
                ));
    }
}

