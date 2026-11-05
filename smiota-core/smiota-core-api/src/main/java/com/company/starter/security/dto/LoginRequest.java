package com.company.starter.security.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Authentication request payload.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LoginRequest {

    @NotBlank(message = "Username or email is required")
    @Schema(description = "Account username or email", example = "admin")
    private String username;

    @NotBlank(message = "Password is required")
    @Schema(description = "Account password", example = "adminpassword")
    private String password;
}

