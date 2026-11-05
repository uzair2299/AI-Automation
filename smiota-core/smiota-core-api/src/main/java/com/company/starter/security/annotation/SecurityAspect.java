package com.company.starter.security.annotation;

import com.company.starter.security.context.CustomUserDetails;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.JoinPoint;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Before;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * AOP Aspect intercepting methods annotated with {@link HasRole} and {@link HasPermission}.
 */
@Slf4j
@Aspect
@Component
public class SecurityAspect {

    @Before("@annotation(hasRole) || @within(hasRole)")
    public void checkRole(JoinPoint joinPoint, HasRole hasRole) {
        Authentication auth = getAuthentication();
        String[] requiredRoles = hasRole.value();

        Set<String> userRoles = auth.getAuthorities().stream()
                .map(GrantedAuthority::getAuthority)
                .collect(Collectors.toSet());

        boolean matched = Arrays.stream(requiredRoles).anyMatch(role -> {
            String roleName = role.startsWith("ROLE_") ? role : "ROLE_" + role;
            return userRoles.contains(roleName) || userRoles.contains(role);
        });

        if (!matched) {
            log.warn("Access denied for user '{}' on method '{}'. Required roles: {}",
                    auth.getName(), joinPoint.getSignature().toShortString(), Arrays.toString(requiredRoles));
            throw new AccessDeniedException("Access denied: Required role not granted");
        }
    }

    @Before("@annotation(hasPermission) || @within(hasPermission)")
    public void checkPermission(JoinPoint joinPoint, HasPermission hasPermission) {
        Authentication auth = getAuthentication();
        String[] requiredPermissions = hasPermission.value();

        // Admin role bypasses granular permission check
        boolean isAdmin = auth.getAuthorities().stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN") || a.getAuthority().equals("ADMIN"));
        if (isAdmin) {
            return;
        }

        Set<String> userAuthorities = auth.getAuthorities().stream()
                .map(GrantedAuthority::getAuthority)
                .collect(Collectors.toSet());

        boolean matched = Arrays.stream(requiredPermissions).anyMatch(perm ->
                userAuthorities.contains(perm) || userAuthorities.contains("PERMISSION_" + perm)
        );

        if (!matched) {
            log.warn("Access denied for user '{}' on method '{}'. Required permissions: {}",
                    auth.getName(), joinPoint.getSignature().toShortString(), Arrays.toString(requiredPermissions));
            throw new AccessDeniedException("Access denied: Required permission not granted");
        }
    }

    private Authentication getAuthentication() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated() || "anonymousUser".equals(auth.getPrincipal())) {
            throw new AccessDeniedException("Authentication required to access this resource");
        }
        return auth;
    }
}

