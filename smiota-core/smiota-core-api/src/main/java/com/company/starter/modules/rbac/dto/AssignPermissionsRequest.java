package com.company.starter.modules.rbac.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Set;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AssignPermissionsRequest {

    @NotNull(message = "Permission codes set must not be null")
    @Schema(description = "Set of permission codes to assign to the role", example = "[\"USER_READ\", \"USER_CREATE\"]")
    private Set<String> permissions;
}

