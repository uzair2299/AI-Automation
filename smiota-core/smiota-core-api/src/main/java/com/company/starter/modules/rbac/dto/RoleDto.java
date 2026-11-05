package com.company.starter.modules.rbac.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.Set;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RoleDto {

    private UUID id;
    private String name;
    private String code;
    private String description;
    private Boolean isSystem;
    private Boolean active;
    private Set<String> permissions;
    private Instant createdAt;
    private Instant updatedAt;
}

