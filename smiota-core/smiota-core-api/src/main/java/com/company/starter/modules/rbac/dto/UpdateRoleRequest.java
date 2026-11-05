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
public class UpdateRoleRequest {

    @NotBlank(message = "Role name is required")
    @Size(max = 100, message = "Role name must not exceed 100 characters")
    @Schema(description = "Display name", example = "Operations Manager")
    private String name;

    @Size(max = 500, message = "Description must not exceed 500 characters")
    @Schema(description = "Role description", example = "Manages daily operations and approvals")
    private String description;

    @Schema(description = "Active status flag", example = "true")
    private Boolean active;

    @Schema(description = "Set of permission codes to associate with this role", example = "[\"USER_READ\", \"ROLE_READ\"]")
    private Set<String> permissions;
}

