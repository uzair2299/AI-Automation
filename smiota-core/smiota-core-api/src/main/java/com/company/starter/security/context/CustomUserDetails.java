package com.company.starter.security.context;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Collection;
import java.util.Collections;
import java.util.Set;
import java.util.UUID;

/**
 * Custom UserDetails implementation holding enriched identity context (id, email, roles, permissions).
 */
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CustomUserDetails implements UserDetails {

    private UUID id;
    private String username;
    private String email;
    private String password;
    private String firstName;
    private String lastName;

    @Builder.Default
    private boolean enabled = true;

    @Builder.Default
    private boolean accountNonExpired = true;

    @Builder.Default
    private boolean accountNonLocked = true;

    @Builder.Default
    private boolean credentialsNonExpired = true;

    @Builder.Default
    private Collection<? extends GrantedAuthority> authorities = Collections.emptyList();

    @Builder.Default
    private Set<String> roles = Collections.emptySet();

    @Builder.Default
    private Set<String> permissions = Collections.emptySet();

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return authorities;
    }

    @Override
    public String getPassword() {
        return password;
    }

    @Override
    public String getUsername() {
        return username;
    }

    @Override
    public boolean isAccountNonExpired() {
        return accountNonExpired;
    }

    @Override
    public boolean isAccountNonLocked() {
        return accountNonLocked;
    }

    @Override
    public boolean isCredentialsNonExpired() {
        return credentialsNonExpired;
    }

    @Override
    public boolean isEnabled() {
        return enabled;
    }

    public boolean hasRole(String role) {
        if (roles == null) return false;
        String normalized = role.startsWith("ROLE_") ? role.substring(5) : role;
        return roles.contains(role) || roles.contains(normalized) || roles.contains("ROLE_" + normalized);
    }

    public boolean hasPermission(String permission) {
        return permissions != null && permissions.contains(permission);
    }
}

