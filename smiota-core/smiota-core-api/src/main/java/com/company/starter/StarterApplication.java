package com.company.starter;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

/**
 * Enterprise Spring Boot Starter Application entry point.
 * Configured with multi-module component scanning for com.company.starter and com.smiota.common.
 */
@SpringBootApplication(scanBasePackages = {"com.company.starter", "com.smiota.common"})
@EntityScan(basePackages = {"com.company.starter", "com.smiota.common"})
@EnableJpaRepositories(basePackages = {"com.company.starter", "com.smiota.common"})
public class StarterApplication {

    public static void main(String[] args) {
        SpringApplication.run(StarterApplication.class, args);
    }
}
