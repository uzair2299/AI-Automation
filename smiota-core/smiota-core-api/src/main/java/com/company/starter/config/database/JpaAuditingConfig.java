package com.company.starter.config.database;

import com.company.starter.security.context.SecurityUtils;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.domain.AuditorAware;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

import java.util.Optional;

/**
 * JPA Auditing configuration providing current authenticated username for createdBy and updatedBy fields.
 */
@Configuration
@EnableJpaAuditing(auditorAwareRef = "auditorAware")
public class JpaAuditingConfig {

    @Bean
    public AuditorAware<String> auditorAware() {
        return () -> {
            Optional<String> username = SecurityUtils.getCurrentUsernameOptional();
            return Optional.of(username.orElse("system"));
        };
    }
}

