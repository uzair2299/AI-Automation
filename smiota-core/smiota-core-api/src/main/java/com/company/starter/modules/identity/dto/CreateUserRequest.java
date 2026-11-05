package com.company.starter.modules.identity.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Set;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CreateUserRequest {

    @NotBlank(message = "Username is required")
    @Size(min = 3, max = 50, message = "Username must be between 3 and 50 characters")
    @Schema(description = "Account username", example = "jane_doe")
    private String username;

    @NotBlank(message = "Email is required")
    @Email(message = "Email must be valid")
    @Schema(description = "Account email", example = "jane.doe@company.com")
    private String email;

    @NotBlank(message = "Password is required")
    @Size(min = 6, message = "Password must be at least 6 characters")
    @Schema(description = "Account password", example = "SecurePassword123")
    private String password;

    @NotBlank(message = "First name is required")
    @Schema(description = "User first name", example = "Jane")
    private String firstName;

    @NotBlank(message = "Last name is required")
    @Schema(description = "User last name", example = "Doe")
    private String lastName;

    @Schema(description = "Phone number", example = "+1-555-0188")
    private String phoneNumber;

    @Schema(description = "Set of role codes to assign", example = "[\"ROLE_USER\"]")
    private Set<String> roles;
}

