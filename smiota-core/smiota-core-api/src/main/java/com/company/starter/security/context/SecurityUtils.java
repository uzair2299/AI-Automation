package com.company.starter.security.context;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;

import java.util.Optional;
import java.util.UUID;

/**
 * Utility functions to extract authenticated user details from Spring SecurityContext.
 */
public final class SecurityUtils {

    private SecurityUtils() {
    }

    /**
     * Get the current authenticated username, or "system" if not available.
     */
    public static String getCurrentUsername() {
        return getCurrentUsernameOptional().orElse("system");
    }

    /**
     * Get the current authenticated username as Optional.
     */
    public static Optional<String> getCurrentUsernameOptional() {
        return Optional.ofNullable(SecurityContextHolder.getContext())
                .map(SecurityContext::getAuthentication)
                .filter(Authentication::isAuthenticated)
                .map(auth -> {
                    Object principal = auth.getPrincipal();
                    if (principal instanceof UserDetails userDetails) {
                        return userDetails.getUsername();
                    }
                    if (principal instanceof String principalString && !principalString.equals("anonymousUser")) {
                        return principalString;
                    }
                    return null;
                });
    }

    /**
     * Get the current authenticated CustomUserDetails if available.
     */
    public static Optional<CustomUserDetails> getCurrentUserDetails() {
        return Optional.ofNullable(SecurityContextHolder.getContext())
                .map(SecurityContext::getAuthentication)
                .filter(Authentication::isAuthenticated)
                .map(Authentication::getPrincipal)
                .filter(CustomUserDetails.class::isInstance)
                .map(CustomUserDetails.class::cast);
    }

    /**
     * Get the current authenticated user's UUID if available.
     */
    public static Optional<UUID> getCurrentUserId() {
        return getCurrentUserDetails().map(CustomUserDetails::getId);
    }
}

