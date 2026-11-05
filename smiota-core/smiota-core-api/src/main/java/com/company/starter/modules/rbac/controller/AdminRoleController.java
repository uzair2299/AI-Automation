package com.company.starter.modules.rbac.controller;

import com.company.starter.modules.rbac.dto.AssignPermissionsRequest;
import com.company.starter.modules.rbac.dto.CreateRoleRequest;
import com.company.starter.modules.rbac.dto.PermissionDto;
import com.company.starter.modules.rbac.dto.RoleDto;
import com.company.starter.modules.rbac.dto.UpdateRoleRequest;
import com.company.starter.modules.rbac.service.RoleService;
import com.company.starter.shared.dto.ApiResponse;
import com.company.starter.shared.dto.RequestParamDto;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.UUID;

/**
 * Admin management controller for system roles and permissions mapping.
 */
@RestController
@RequestMapping("/api/v1/admin/roles")
@RequiredArgsConstructor
@SecurityRequirement(name = "bearerAuth")
@PreAuthorize("hasRole('ADMIN')")
@Tag(name = "Admin Roles", description = "Administrative endpoints for managing roles and access privileges")
public class AdminRoleController {

    private final RoleService roleService;

    @PostMapping
    @Operation(summary = "Create role", description = "Create a new security role (Admin only)")
    public ResponseEntity<ApiResponse<RoleDto>> create(@Valid @RequestBody CreateRoleRequest request) {
        RoleDto role = roleService.createRole(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.created("Role created successfully", role));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Update role", description = "Update role metadata and permissions (Admin only)")
    public ResponseEntity<ApiResponse<RoleDto>> update(@PathVariable UUID id, @Valid @RequestBody UpdateRoleRequest request) {
        RoleDto role = roleService.updateRole(id, request);
        return ResponseEntity.ok(ApiResponse.ok("Role updated successfully", role));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get role by ID", description = "Retrieve role details and mapped permissions (Admin only)")
    public ResponseEntity<ApiResponse<RoleDto>> getById(@PathVariable UUID id) {
        RoleDto role = roleService.getRoleById(id);
        return ResponseEntity.ok(ApiResponse.ok(role));
    }

    @GetMapping
    @Operation(summary = "Get paginated roles", description = "Retrieve paginated list of roles (Admin only)")
    public ResponseEntity<ApiResponse<Page<RoleDto>>> getAll(@ModelAttribute RequestParamDto paramDto) {
        Page<RoleDto> page = roleService.getRoles(paramDto);
        return ResponseEntity.ok(ApiResponse.ok(page));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Delete role", description = "Soft delete a custom role (Admin only)")
    public ResponseEntity<ApiResponse<Void>> delete(@PathVariable UUID id) {
        roleService.deleteRole(id);
        return ResponseEntity.ok(ApiResponse.noContent("Role soft-deleted successfully"));
    }

    @PostMapping("/{id}/permissions")
    @Operation(summary = "Assign permissions to role", description = "Assign or replace permission grants for a role (Admin only)")
    public ResponseEntity<ApiResponse<Void>> assignPermissions(@PathVariable UUID id, @Valid @RequestBody AssignPermissionsRequest request) {
        roleService.assignPermissions(id, request.getPermissions());
        return ResponseEntity.ok(ApiResponse.noContent("Permissions assigned successfully"));
    }

    @GetMapping("/{id}/permissions")
    @Operation(summary = "Get permissions for role", description = "List all permissions assigned to a role (Admin only)")
    public ResponseEntity<ApiResponse<List<PermissionDto>>> getPermissionsForRole(@PathVariable UUID id) {
        List<PermissionDto> permissions = roleService.getPermissionsForRole(id);
        return ResponseEntity.ok(ApiResponse.ok(permissions));
    }
}

