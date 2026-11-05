package com.company.starter.modules.navigation.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Hierarchical DTO representing navigation tree nodes.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MenuItemDto {

    private UUID id;
    private UUID parentId;
    private String title;
    private String icon;
    private String path;
    private String permissionCode;
    private NavigationSection layoutSection;
    private Integer sortOrder;

    @Builder.Default
    @Schema(description = "Child navigation menu nodes")
    private List<MenuItemDto> children = new ArrayList<>();
}

