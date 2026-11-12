package com.scholo.service;

import com.scholo.model.Scholarship;
import com.scholo.repository.ScholarshipRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public class ScholarshipService {

    private final ScholarshipRepository scholarshipRepository;

    public ScholarshipService(ScholarshipRepository scholarshipRepository) {
        this.scholarshipRepository = scholarshipRepository;
    }

    public List<Scholarship> getAllScholarships() {
        return scholarshipRepository.findAll();
    }

    public Optional<Scholarship> getScholarshipById(String id) {
        return getAllScholarships()
                .stream()
                .filter(scholarship -> scholarship.getId() != null)
                .filter(scholarship -> scholarship.getId().equalsIgnoreCase(id))
                .findFirst();
    }

    public int getTotalScholarships() {
        return getAllScholarships().size();
    }
}

