package com.company.starter.modules.rbac.service;

import com.company.starter.modules.rbac.dto.ModuleDto;
import com.company.starter.modules.rbac.dto.PermissionDto;
import com.company.starter.modules.rbac.dto.ResourceDto;
import com.company.starter.modules.rbac.entity.Module;
import com.company.starter.modules.rbac.entity.Permission;
import com.company.starter.modules.rbac.repository.ModuleRepository;
import com.company.starter.modules.rbac.repository.PermissionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Comparator;
import java.util.List;

/**
 * Service managing access to security modules, resources, and permissions catalog.
 */
@Slf4j
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PermissionService {

    private final ModuleRepository moduleRepository;
    private final PermissionRepository permissionRepository;

    public List<ModuleDto> getAllModulesAndPermissions() {
        List<Module> modules = moduleRepository.findAllWithResourcesAndPermissions();

        return modules.stream()
                .sorted(Comparator.comparing(Module::getSortOrder))
                .map(module -> ModuleDto.builder()
                        .id(module.getId())
                        .name(module.getName())
                        .code(module.getCode())
                        .description(module.getDescription())
                        .active(module.getActive())
                        .sortOrder(module.getSortOrder())
                        .resources(module.getResources().stream()
                                .map(resource -> ResourceDto.builder()
                                        .id(resource.getId())
                                        .name(resource.getName())
                                        .code(resource.getCode())
                                        .description(resource.getDescription())
                                        .active(resource.getActive())
                                        .permissions(resource.getPermissions().stream()
                                                .map(this::mapPermissionToDto)
                                                .toList())
                                        .build())
                                .toList())
                        .build())
                .toList();
    }

    public List<PermissionDto> getAllPermissions() {
        return permissionRepository.findAll().stream()
                .map(this::mapPermissionToDto)
                .toList();
    }

    private PermissionDto mapPermissionToDto(Permission p) {
        return PermissionDto.builder()
                .id(p.getId())
                .name(p.getName())
                .code(p.getCode())
                .action(p.getAction())
                .description(p.getDescription())
                .build();
    }
}

