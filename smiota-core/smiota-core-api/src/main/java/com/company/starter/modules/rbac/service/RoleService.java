package com.company.starter.modules.rbac.service;

import com.company.starter.modules.rbac.dto.CreateRoleRequest;
import com.company.starter.modules.rbac.dto.PermissionDto;
import com.company.starter.modules.rbac.dto.RoleDto;
import com.company.starter.modules.rbac.dto.UpdateRoleRequest;
import com.company.starter.modules.rbac.entity.Permission;
import com.company.starter.modules.rbac.entity.Role;
import com.company.starter.modules.rbac.entity.RolePermission;
import com.company.starter.modules.rbac.repository.PermissionRepository;
import com.company.starter.modules.rbac.repository.RolePermissionRepository;
import com.company.starter.modules.rbac.repository.RoleRepository;
import com.company.starter.security.context.SecurityUtils;
import com.company.starter.shared.dto.RequestParamDto;
import com.company.starter.shared.exception.BadRequestException;
import com.company.starter.shared.exception.ConflictException;
import com.company.starter.shared.exception.ResourceNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * Service managing security roles and permission mappings.
 */
@Slf4j
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class RoleService {

    private final RoleRepository roleRepository;
    private final PermissionRepository permissionRepository;
    private final RolePermissionRepository rolePermissionRepository;

    @Transactional
    public RoleDto createRole(CreateRoleRequest request) {
        String code = request.getCode().trim().toUpperCase();
        if (!code.startsWith("ROLE_")) {
            code = "ROLE_" + code;
        }

        if (roleRepository.existsByCodeAndDeletedFalse(code)) {
            throw new ConflictException("Role with code '" + code + "' already exists");
        }

        Role role = Role.builder()
                .name(request.getName().trim())
                .code(code)
                .description(request.getDescription())
                .isSystem(Boolean.FALSE)
                .active(Boolean.TRUE)
                .deleted(Boolean.FALSE)
                .build();

        Role savedRole = roleRepository.save(role);

        if (request.getPermissions() != null && !request.getPermissions().isEmpty()) {
            assignPermissionsToRole(savedRole, request.getPermissions());
        }

        return mapToDto(savedRole);
    }

    @Transactional
    public RoleDto updateRole(UUID id, UpdateRoleRequest request) {
        Role role = findRoleById(id);

        if (Boolean.TRUE.equals(role.getIsSystem()) && Boolean.FALSE.equals(request.getActive())) {
            throw new BadRequestException("System roles cannot be deactivated");
        }

        role.setName(request.getName().trim());
        role.setDescription(request.getDescription());
        if (request.getActive() != null) {
            role.setActive(request.getActive());
        }

        if (request.getPermissions() != null) {
            rolePermissionRepository.deleteByRoleId(role.getId());
            assignPermissionsToRole(role, request.getPermissions());
        }

        Role updated = roleRepository.save(role);
        return mapToDto(updated);
    }

    public RoleDto getRoleById(UUID id) {
        Role role = findRoleById(id);
        return mapToDto(role);
    }

    public Page<RoleDto> getRoles(RequestParamDto paramDto) {
        Page<Role> rolesPage = roleRepository.searchRoles(paramDto.getSearch(), paramDto.toPageable());
        return rolesPage.map(this::mapToDto);
    }

    @Transactional
    public void deleteRole(UUID id) {
        Role role = findRoleById(id);
        if (Boolean.TRUE.equals(role.getIsSystem())) {
            throw new BadRequestException("System role '" + role.getCode() + "' cannot be deleted");
        }

        role.setDeleted(Boolean.TRUE);
        role.setDeletedAt(Instant.now());
        role.setDeletedBy(SecurityUtils.getCurrentUsername());
        role.setActive(Boolean.FALSE);
        roleRepository.save(role);
    }

    @Transactional
    public void assignPermissions(UUID roleId, Set<String> permissionCodes) {
        Role role = findRoleById(roleId);
        rolePermissionRepository.deleteByRoleId(role.getId());
        assignPermissionsToRole(role, permissionCodes);
    }

    public List<PermissionDto> getPermissionsForRole(UUID roleId) {
        findRoleById(roleId);
        List<Permission> permissions = rolePermissionRepository.findPermissionsByRoleId(roleId);
        return permissions.stream()
                .map(p -> PermissionDto.builder()
                        .id(p.getId())
                        .name(p.getName())
                        .code(p.getCode())
                        .action(p.getAction())
                        .description(p.getDescription())
                        .build())
                .toList();
    }

    private void assignPermissionsToRole(Role role, Set<String> permissionCodes) {
        if (permissionCodes == null || permissionCodes.isEmpty()) {
            return;
        }

        List<Permission> permissions = permissionRepository.findByCodeIn(permissionCodes);
        for (Permission permission : permissions) {
            rolePermissionRepository.save(RolePermission.builder()
                    .role(role)
                    .permission(permission)
                    .build());
        }
    }

    private Role findRoleById(UUID id) {
        return roleRepository.findById(id)
                .filter(r -> !Boolean.TRUE.equals(r.getDeleted()))
                .orElseThrow(() -> new ResourceNotFoundException("Role", "id", id));
    }

    private RoleDto mapToDto(Role role) {
        List<Permission> permissions = rolePermissionRepository.findPermissionsByRoleId(role.getId());
        Set<String> permissionCodes = permissions.stream()
                .map(Permission::getCode)
                .collect(Collectors.toSet());

        return RoleDto.builder()
                .id(role.getId())
                .name(role.getName())
                .code(role.getCode())
                .description(role.getDescription())
                .isSystem(role.getIsSystem())
                .active(role.getActive())
                .permissions(permissionCodes)
                .createdAt(role.getCreatedAt())
                .updatedAt(role.getUpdatedAt())
                .build();
    }
}

