package com.company.starter.modules.rbac.controller;

import com.company.starter.modules.rbac.dto.ModuleDto;
import com.company.starter.modules.rbac.dto.PermissionDto;
import com.company.starter.modules.rbac.service.PermissionService;
import com.company.starter.shared.dto.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/**
 * Admin management controller for system permission catalog.
 */
@RestController
@RequestMapping("/api/v1/admin/permissions")
@RequiredArgsConstructor
@SecurityRequirement(name = "bearerAuth")
@PreAuthorize("hasRole('ADMIN')")
@Tag(name = "Admin Permissions", description = "Endpoints for inspecting system modules, resources, and granular permissions")
public class AdminPermissionController {

    private final PermissionService permissionService;

    @GetMapping
    @Operation(summary = "Get all modules with permissions", description = "Retrieve hierarchical structure of modules, resources, and permissions (Admin only)")
    public ResponseEntity<ApiResponse<List<ModuleDto>>> getAllModulesAndPermissions() {
        List<ModuleDto> modules = permissionService.getAllModulesAndPermissions();
        return ResponseEntity.ok(ApiResponse.ok(modules));
    }

    @GetMapping("/flat")
    @Operation(summary = "Get flat permissions list", description = "Retrieve flat list of all defined permissions (Admin only)")
    public ResponseEntity<ApiResponse<List<PermissionDto>>> getAllPermissions() {
        List<PermissionDto> permissions = permissionService.getAllPermissions();
        return ResponseEntity.ok(ApiResponse.ok(permissions));
    }
}

