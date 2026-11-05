package com.company.starter.bootstrap.seeder;

import com.company.starter.modules.identity.entity.User;
import com.company.starter.modules.identity.entity.UserProfile;
import com.company.starter.modules.identity.repository.UserRepository;
import com.company.starter.modules.rbac.entity.Permission;
import com.company.starter.modules.rbac.entity.Role;
import com.company.starter.modules.rbac.entity.RolePermission;
import com.company.starter.modules.rbac.entity.UserRole;
import com.company.starter.modules.rbac.repository.PermissionRepository;
import com.company.starter.modules.rbac.repository.RolePermissionRepository;
import com.company.starter.modules.rbac.repository.RoleRepository;
import com.company.starter.modules.rbac.repository.UserRoleRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * Startup database seeder ensuring essential security roles, admin accounts, and permission grants exist.
 * Controlled by property 'application.security.seeder.enabled' (defaults to false to protect existing databases).
 */
@Slf4j
@Component
@ConditionalOnProperty(name = "application.security.seeder.enabled", havingValue = "true", matchIfMissing = false)
@RequiredArgsConstructor
public class SecurityDataSeeder implements CommandLineRunner {

    private final RoleRepository roleRepository;
    private final PermissionRepository permissionRepository;
    private final RolePermissionRepository rolePermissionRepository;
    private final UserRepository userRepository;
    private final UserRoleRepository userRoleRepository;
    private final PasswordEncoder passwordEncoder;

    @Override
    @Transactional
    public void run(String... args) {
        log.info("Starting security bootstrap data seeding...");

        Role adminRole = seedRoleIfMissing("ROLE_ADMIN", "Administrator", "Full system administration access", true);
        Role userRole = seedRoleIfMissing("ROLE_USER", "Standard User", "Standard system user access", true);

        seedAdminPermissions(adminRole);
        seedAdminUser(adminRole);
        seedSampleUser(userRole);

        log.info("Security bootstrap data seeding completed successfully.");
    }

    private Role seedRoleIfMissing(String code, String name, String description, boolean isSystem) {
        return roleRepository.findByCodeAndDeletedFalse(code).orElseGet(() -> {
            log.info("Seeding missing security role: {}", code);
            Role role = Role.builder()
                    .code(code)
                    .name(name)
                    .description(description)
                    .isSystem(isSystem)
                    .active(Boolean.TRUE)
                    .deleted(Boolean.FALSE)
                    .build();
            return roleRepository.save(role);
        });
    }

    private void seedAdminPermissions(Role adminRole) {
        List<Permission> allPermissions = permissionRepository.findAll();
        for (Permission permission : allPermissions) {
            if (!rolePermissionRepository.existsByRoleIdAndPermissionId(adminRole.getId(), permission.getId())) {
                rolePermissionRepository.save(RolePermission.builder()
                        .role(adminRole)
                        .permission(permission)
                        .build());
            }
        }
    }

    private void seedAdminUser(Role adminRole) {
        if (!userRepository.existsByUsername("admin")) {
            log.info("Seeding default admin user: 'admin' / 'adminpassword'");

            User adminUser = User.builder()
                    .username("admin")
                    .email("admin@company.com")
                    .password(passwordEncoder.encode("adminpassword"))
                    .enabled(Boolean.TRUE)
                    .accountNonExpired(Boolean.TRUE)
                    .accountNonLocked(Boolean.TRUE)
                    .credentialsNonExpired(Boolean.TRUE)
                    .deleted(Boolean.FALSE)
                    .build();

            UserProfile profile = UserProfile.builder()
                    .user(adminUser)
                    .firstName("System")
                    .lastName("Administrator")
                    .phoneNumber("+1-800-555-0100")
                    .bio("Default root enterprise administrator")
                    .build();

            adminUser.setProfile(profile);
            User savedAdmin = userRepository.save(adminUser);

            userRoleRepository.save(UserRole.builder()
                    .user(savedAdmin)
                    .role(adminRole)
                    .build());

            log.info("Default admin user created successfully.");
        }
    }

    private void seedSampleUser(Role userRole) {
        if (!userRepository.existsByUsername("user")) {
            log.info("Seeding default sample user: 'user' / 'userpassword'");

            User standardUser = User.builder()
                    .username("user")
                    .email("user@company.com")
                    .password(passwordEncoder.encode("userpassword"))
                    .enabled(Boolean.TRUE)
                    .accountNonExpired(Boolean.TRUE)
                    .accountNonLocked(Boolean.TRUE)
                    .credentialsNonExpired(Boolean.TRUE)
                    .deleted(Boolean.FALSE)
                    .build();

            UserProfile profile = UserProfile.builder()
                    .user(standardUser)
                    .firstName("Standard")
                    .lastName("User")
                    .phoneNumber("+1-800-555-0101")
                    .bio("Default standard application user")
                    .build();

            standardUser.setProfile(profile);
            User savedUser = userRepository.save(standardUser);

            userRoleRepository.save(UserRole.builder()
                    .user(savedUser)
                    .role(userRole)
                    .build());

            log.info("Default standard user created successfully.");
        }
    }
}

