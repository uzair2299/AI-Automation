package com.company.starter.modules.identity.controller;

import com.company.starter.modules.identity.dto.CreateUserRequest;
import com.company.starter.modules.identity.dto.UpdateUserRequest;
import com.company.starter.modules.identity.dto.UserDto;
import com.company.starter.modules.identity.dto.UserStatusRequest;
import com.company.starter.modules.identity.service.UserService;
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
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Set;
import java.util.UUID;

/**
 * Admin management controller for system users.
 */
@RestController
@RequestMapping("/api/v1/admin/users")
@RequiredArgsConstructor
@SecurityRequirement(name = "bearerAuth")
@PreAuthorize("hasRole('ADMIN')")
@Tag(name = "Admin Users", description = "Administrative endpoints for managing system users and access")
public class AdminUserController {

    private final UserService userService;

    @PostMapping
    @Operation(summary = "Create user", description = "Create a new user account with profile and assigned roles (Admin only)")
    public ResponseEntity<ApiResponse<UserDto>> create(@Valid @RequestBody CreateUserRequest request) {
        UserDto created = userService.createUser(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.created("User created successfully", created));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Update user", description = "Update user profile details and role memberships (Admin only)")
    public ResponseEntity<ApiResponse<UserDto>> update(@PathVariable UUID id, @Valid @RequestBody UpdateUserRequest request) {
        UserDto updated = userService.updateUser(id, request);
        return ResponseEntity.ok(ApiResponse.ok("User updated successfully", updated));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get user by ID", description = "Retrieve user details, profile, and roles by ID (Admin only)")
    public ResponseEntity<ApiResponse<UserDto>> getById(@PathVariable UUID id) {
        UserDto user = userService.getUserById(id);
        return ResponseEntity.ok(ApiResponse.ok(user));
    }

    @GetMapping
    @Operation(summary = "Get paginated users", description = "Retrieve paginated list of users with search filter (Admin only)")
    public ResponseEntity<ApiResponse<Page<UserDto>>> getAll(@ModelAttribute RequestParamDto paramDto) {
        Page<UserDto> page = userService.getUsers(paramDto);
        return ResponseEntity.ok(ApiResponse.ok(page));
    }

    @PatchMapping("/{id}/status")
    @Operation(summary = "Change user status", description = "Enable or disable a user account (Admin only)")
    public ResponseEntity<ApiResponse<Void>> changeStatus(@PathVariable UUID id, @Valid @RequestBody UserStatusRequest request) {
        userService.changeStatus(id, request.getEnabled());
        return ResponseEntity.ok(ApiResponse.noContent("User status updated successfully"));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Delete user", description = "Soft delete a user account (Admin only)")
    public ResponseEntity<ApiResponse<Void>> delete(@PathVariable UUID id) {
        userService.deleteUser(id);
        return ResponseEntity.ok(ApiResponse.noContent("User soft-deleted successfully"));
    }

    @PostMapping("/{id}/roles")
    @Operation(summary = "Assign roles to user", description = "Replace user roles with the given set of role codes (Admin only)")
    public ResponseEntity<ApiResponse<Void>> assignRoles(@PathVariable UUID id, @RequestBody Set<String> roles) {
        userService.assignRoles(id, roles);
        return ResponseEntity.ok(ApiResponse.noContent("User roles updated successfully"));
    }
}

