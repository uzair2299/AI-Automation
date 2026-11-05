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
public class ModuleDto {

    private UUID id;
    private String name;
    private String code;
    private String description;
    private Boolean active;
    private Integer sortOrder;
    private List<ResourceDto> resources;
}

