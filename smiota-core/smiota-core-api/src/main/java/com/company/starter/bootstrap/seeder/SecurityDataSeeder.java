package com.company.starter.bootstrap.seeder;

import com.company.starter.modules.rbac.entity.Role;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

/**
 * Startup database seeder skeleton.
 * All data seeding operations have been removed; methods are retained with empty implementations.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class SecurityDataSeeder implements CommandLineRunner {

    @Override
    @Transactional
    public void run(String... args) {
        // Empty implementation - no data seeding
    }

    private Role seedRoleIfMissing(String code, String name, String description, boolean isSystem) {
        return null;
    }

    private void seedAdminPermissions(Role adminRole) {
        // Empty implementation - no data seeding
    }

    private void seedAdminUser(Role adminRole) {
        // Empty implementation - no data seeding
    }

    private void seedSampleUser(Role userRole) {
        // Empty implementation - no data seeding
    }
}
