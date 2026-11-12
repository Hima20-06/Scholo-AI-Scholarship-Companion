package com.scholo.controller;

import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HealthController {
    @GetMapping("/api/health")
    public Map<String, Object> health() {
        return Map.of(
            "service", "scholo-java-backend",
            "status", "ok",
            "version", "0.1.0",
            "note", "Starter backend; persistence and authentication are not configured yet."
        );
    }
}
