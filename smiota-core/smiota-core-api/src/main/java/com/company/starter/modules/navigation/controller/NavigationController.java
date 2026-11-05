package com.company.starter.modules.navigation.controller;

import com.company.starter.modules.navigation.dto.MenuItemDto;
import com.company.starter.modules.navigation.dto.NavigationSection;
import com.company.starter.modules.navigation.service.NavigationService;
import com.company.starter.security.annotation.CurrentUser;
import com.company.starter.security.context.CustomUserDetails;
import com.company.starter.shared.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * Controller providing dynamic UI navigation trees customized to the user's role and permissions.
 */
@RestController
@RequestMapping("/api/v1/navigation")
@RequiredArgsConstructor
@SecurityRequirement(name = "bearerAuth")
@Tag(name = "Navigation", description = "Dynamic navigation tree generation based on RBAC and UI layout sections")
public class NavigationController {

    private final NavigationService navigationService;

    @GetMapping
    @Operation(summary = "Get user navigation tree", description = "Retrieve dynamic navigation tree filtered by authenticated user permissions and layout section")
    public ResponseEntity<ApiResponse<List<MenuItemDto>>> getNavigation(
            @RequestParam(required = false, defaultValue = "SIDEBAR") NavigationSection section,
            @CurrentUser CustomUserDetails currentUser) {
        List<MenuItemDto> tree = navigationService.getNavigationTree(section, currentUser);
        return ResponseEntity.ok(ApiResponse.ok(tree));
    }
}

