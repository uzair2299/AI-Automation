package com.company.starter.security.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Set;
import java.util.UUID;

/**
 * Authentication response payload containing JWT token, user details, and authorizations.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LoginResponse {

    @Schema(description = "JWT Access Token")
    private String token;

    @Builder.Default
    @Schema(description = "Token type indicator", example = "Bearer")
    private String tokenType = "Bearer";

    @Schema(description = "Token lifetime in seconds", example = "86400")
    private Long expiresIn;

    @Schema(description = "User primary identifier")
    private UUID userId;

    @Schema(description = "Smiota numeric User ID", example = "1042")
    private Long smiotaUserId;

    @Schema(description = "Smiota Location ID", example = "12")
    private Long locationId;

    @Schema(description = "Smiota Customer ID", example = "5")
    private Long customerId;

    @Schema(description = "User account username", example = "admin")
    private String username;

    @Schema(description = "User account email", example = "admin@company.com")
    private String email;

    @Schema(description = "User first name", example = "System")
    private String firstName;

    @Schema(description = "User last name", example = "Administrator")
    private String lastName;

    @Schema(description = "Assigned user roles", example = "[\"ROLE_ADMIN\"]")
    private Set<String> roles;

    @Schema(description = "Assigned granular permissions", example = "[\"USER_READ\", \"USER_CREATE\"]")
    private Set<String> permissions;
}

