package com.company.starter.modules.navigation.service;

import com.company.starter.modules.navigation.dto.MenuItemDto;
import com.company.starter.modules.navigation.dto.NavigationSection;
import com.company.starter.modules.navigation.entity.MenuItem;
import com.company.starter.modules.navigation.repository.MenuItemRepository;
import com.company.starter.security.context.CustomUserDetails;
import com.company.starter.security.context.SecurityUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * Service dynamically constructing permission-filtered navigation hierarchies for the UI.
 */
@Slf4j
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class NavigationService {

    private final MenuItemRepository menuItemRepository;

    /**
     * Builds navigation tree filtered by layout section and current user permissions.
     */
    public List<MenuItemDto> getNavigationTree(NavigationSection section) {
        CustomUserDetails currentUser = SecurityUtils.getCurrentUserDetails().orElse(null);
        return getNavigationTree(section, currentUser);
    }

    /**
     * Builds navigation tree for specified section and user context.
     */
    public List<MenuItemDto> getNavigationTree(NavigationSection section, CustomUserDetails user) {
        List<MenuItem> allItems = (section != null)
                ? menuItemRepository.findByDeletedFalseAndActiveTrueAndLayoutSectionOrderBySortOrderAsc(section)
                : menuItemRepository.findByDeletedFalseAndActiveTrueOrderBySortOrderAsc();

        boolean isAdmin = user != null && user.hasRole("ADMIN");
        Set<String> userPermissions = (user != null && user.getPermissions() != null)
                ? user.getPermissions()
                : Collections.emptySet();

        // Filter items user is permitted to see
        List<MenuItem> permittedItems = allItems.stream()
                .filter(item -> isItemPermitted(item, isAdmin, userPermissions))
                .toList();

        // Group by parent ID
        Map<UUID, List<MenuItem>> childrenByParentId = permittedItems.stream()
                .filter(item -> item.getParentId() != null)
                .collect(Collectors.groupingBy(MenuItem::getParentId));

        // Get top-level items (parentId == null)
        List<MenuItem> rootItems = permittedItems.stream()
                .filter(item -> item.getParentId() == null)
                .sorted(Comparator.comparing(MenuItem::getSortOrder, Comparator.nullsLast(Comparator.naturalOrder())))
                .toList();

        // Recursively build tree
        List<MenuItemDto> result = new ArrayList<>();
        for (MenuItem root : rootItems) {
            MenuItemDto dto = buildTreeNode(root, childrenByParentId);
            // Include root if it has a route path OR has accessible children
            if (hasPathOrChildren(dto)) {
                result.add(dto);
            }
        }

        return result;
    }

    private MenuItemDto buildTreeNode(MenuItem item, Map<UUID, List<MenuItem>> childrenMap) {
        MenuItemDto dto = MenuItemDto.builder()
                .id(item.getId())
                .parentId(item.getParentId())
                .title(item.getTitle())
                .icon(item.getIcon())
                .path(item.getPath())
                .permissionCode(item.getPermissionCode())
                .layoutSection(item.getLayoutSection())
                .sortOrder(item.getSortOrder())
                .children(new ArrayList<>())
                .build();

        List<MenuItem> children = childrenMap.get(item.getId());
        if (children != null && !children.isEmpty()) {
            children.stream()
                    .sorted(Comparator.comparing(MenuItem::getSortOrder, Comparator.nullsLast(Comparator.naturalOrder())))
                    .forEach(child -> {
                        MenuItemDto childDto = buildTreeNode(child, childrenMap);
                        if (hasPathOrChildren(childDto)) {
                            dto.getChildren().add(childDto);
                        }
                    });
        }

        return dto;
    }

    private boolean isItemPermitted(MenuItem item, boolean isAdmin, Set<String> userPermissions) {
        if (isAdmin) {
            return true;
        }
        if (item.getPermissionCode() == null || item.getPermissionCode().trim().isEmpty()) {
            return true;
        }
        return userPermissions.contains(item.getPermissionCode().trim());
    }

    private boolean hasPathOrChildren(MenuItemDto dto) {
        boolean hasPath = dto.getPath() != null && !dto.getPath().trim().isEmpty();
        boolean hasChildren = dto.getChildren() != null && !dto.getChildren().isEmpty();
        return hasPath || hasChildren;
    }
}

