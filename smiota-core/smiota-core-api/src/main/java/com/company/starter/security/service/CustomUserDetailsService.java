package com.company.starter.security.service;

import com.company.starter.modules.identity.entity.User;
import com.company.starter.modules.identity.repository.SmiotaAccountRepository;
import com.company.starter.modules.identity.repository.UserRepository;
import com.company.starter.modules.rbac.entity.Role;
import com.company.starter.modules.rbac.repository.PermissionRepository;
import com.company.starter.modules.rbac.repository.UserRoleRepository;
import com.company.starter.security.context.CustomUserDetails;
import com.smiota.common.dto.user.SmiotaUserAuthProjection;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * Custom UserDetailsService implementation loading users with their dynamic roles and permissions.
 * Supports both native Smiota USER/ACCOUNT authentication and system users.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CustomUserDetailsService implements UserDetailsService {

    private final SmiotaAccountRepository smiotaAccountRepository;
    private final UserRepository userRepository;
    private final UserRoleRepository userRoleRepository;
    private final PermissionRepository permissionRepository;

    @Override
    @Transactional(readOnly = true)
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        log.debug("Authenticating user by identifier: '{}'", username);

        // 1. Try Smiota native USER + ACCOUNT authentication query first
        Optional<SmiotaUserAuthProjection> smiotaAuthOpt = smiotaAccountRepository.findAuthUserByLogin(username);
        if (smiotaAuthOpt.isPresent()) {
            SmiotaUserAuthProjection authUser = smiotaAuthOpt.get();
            log.debug("Found Smiota account for login '{}': userId={}, locationId={}, customerId={}",
                    username, authUser.getId(), authUser.getLocationId(), authUser.getCustomerId());

            List<String> roleNames = smiotaAccountRepository.findRoleNamesByUserId(authUser.getId());
            Set<GrantedAuthority> authorities = roleNames.stream()
                    .map(role -> role.startsWith("ROLE_") ? role : "ROLE_" + role)
                    .map(SimpleGrantedAuthority::new)
                    .collect(Collectors.toSet());

            boolean accountNonLocked = authUser.getIsLocked() == null || !authUser.getIsLocked();

            return CustomUserDetails.builder()
                    .id(new UUID(0L, authUser.getId()))
                    .smiotaUserId(authUser.getId())
                    .locationId(authUser.getLocationId())
                    .customerId(authUser.getCustomerId())
                    .username(username)
                    .email(authUser.getEmail() != null ? authUser.getEmail() : username)
                    .firstName(authUser.getFirstName())
                    .lastName(authUser.getLastName())
                    .password(authUser.getEffectivePasswordHash())
                    .authorities(authorities)
                    .roles(new HashSet<>(roleNames))
                    .permissions(Collections.emptySet())
                    .accountNonLocked(accountNonLocked)
                    .enabled(true)
                    .accountNonExpired(true)
                    .credentialsNonExpired(true)
                    .build();
        }

        // 2. Fallback to system starter users (e.g. tbl_users if present)
        User user = userRepository.findByUsernameOrEmail(username)
                .orElseThrow(() -> new UsernameNotFoundException("User not found with username or email: " + username));

        List<Role> userRoles = userRoleRepository.findRolesByUserId(user.getId());
        Set<String> roleCodes = userRoles.stream()
                .map(Role::getCode)
                .collect(Collectors.toSet());

        Set<String> permissionCodes = roleCodes.isEmpty()
                ? Set.of()
                : permissionRepository.findPermissionCodesByRoleCodes(roleCodes);

        Set<GrantedAuthority> authorities = new HashSet<>();

        // Add Roles with Spring Security ROLE_ prefix standard
        for (String roleCode : roleCodes) {
            String authorityName = roleCode.startsWith("ROLE_") ? roleCode : "ROLE_" + roleCode;
            authorities.add(new SimpleGrantedAuthority(authorityName));
        }

        // Add granular permissions as authorities
        for (String permission : permissionCodes) {
            authorities.add(new SimpleGrantedAuthority(permission));
        }

        String firstName = (user.getProfile() != null) ? user.getProfile().getFirstName() : null;
        String lastName = (user.getProfile() != null) ? user.getProfile().getLastName() : null;

        return CustomUserDetails.builder()
                .id(user.getId())
                .username(user.getUsername())
                .email(user.getEmail())
                .password(user.getPassword())
                .firstName(firstName)
                .lastName(lastName)
                .enabled(Boolean.TRUE.equals(user.getEnabled()))
                .accountNonExpired(Boolean.TRUE.equals(user.getAccountNonExpired()))
                .accountNonLocked(Boolean.TRUE.equals(user.getAccountNonLocked()))
                .credentialsNonExpired(Boolean.TRUE.equals(user.getCredentialsNonExpired()))
                .authorities(authorities)
                .roles(roleCodes)
                .permissions(permissionCodes)
                .build();
    }
}
