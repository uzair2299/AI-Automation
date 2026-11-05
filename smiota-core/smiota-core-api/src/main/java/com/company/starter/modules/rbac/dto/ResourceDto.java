package com.company.starter.modules.rbac.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ResourceDto {

    private UUID id;
    private String name;
    private String code;
    private String description;
    private Boolean active;
    private List<PermissionDto> permissions;
}

