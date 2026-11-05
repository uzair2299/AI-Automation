package com.company.starter.modules.rbac.dto;

import io.swagger.v3.oas.annotations.media.Schema;
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
public class CreateRoleRequest {

    @NotBlank(message = "Role name is required")
    @Size(max = 100, message = "Role name must not exceed 100 characters")
    @Schema(description = "Display name", example = "Operations Manager")
    private String name;

    @NotBlank(message = "Role code is required")
    @Size(max = 50, message = "Role code must not exceed 50 characters")
    @Schema(description = "Unique code (will be prefixed with ROLE_ if not present)", example = "ROLE_OPS_MANAGER")
    private String code;

    @Size(max = 500, message = "Description must not exceed 500 characters")
    @Schema(description = "Role description", example = "Manages daily operations and approvals")
    private String description;

    @Schema(description = "Set of permission codes to associate with this role", example = "[\"USER_READ\", \"ROLE_READ\"]")
    private Set<String> permissions;
}

