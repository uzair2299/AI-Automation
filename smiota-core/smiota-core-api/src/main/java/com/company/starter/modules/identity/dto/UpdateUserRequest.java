package com.company.starter.modules.identity.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Set;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UpdateUserRequest {

    @NotBlank(message = "Email is required")
    @Email(message = "Email must be valid")
    @Schema(description = "Account email", example = "jane.doe@company.com")
    private String email;

    @NotBlank(message = "First name is required")
    @Schema(description = "User first name", example = "Jane")
    private String firstName;

    @NotBlank(message = "Last name is required")
    @Schema(description = "User last name", example = "Doe")
    private String lastName;

    @Schema(description = "Phone number", example = "+1-555-0188")
    private String phoneNumber;

    @Schema(description = "Avatar URL", example = "https://example.com/avatar.png")
    private String avatarUrl;

    @Schema(description = "Bio", example = "Software Engineer")
    private String bio;

    @Schema(description = "Set of role codes to assign", example = "[\"ROLE_USER\", \"ROLE_ADMIN\"]")
    private Set<String> roles;
}

