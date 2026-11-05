package com.company.starter.modules.identity.service;

import com.company.starter.modules.identity.dto.CreateUserRequest;
import com.company.starter.modules.identity.dto.UpdateUserRequest;
import com.company.starter.modules.identity.dto.UserDto;
import com.company.starter.modules.identity.entity.User;
import com.company.starter.modules.identity.entity.UserProfile;
import com.company.starter.modules.identity.repository.UserProfileRepository;
import com.company.starter.modules.identity.repository.UserRepository;
import com.company.starter.modules.rbac.entity.Role;
import com.company.starter.modules.rbac.entity.UserRole;
import com.company.starter.modules.rbac.repository.RoleRepository;
import com.company.starter.modules.rbac.repository.UserRoleRepository;
import com.company.starter.security.context.SecurityUtils;
import com.company.starter.shared.dto.RequestParamDto;
import com.company.starter.shared.exception.ConflictException;
import com.company.starter.shared.exception.ResourceNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * Service managing user identity, profile details, and role assignments.
 */
@Slf4j
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class UserService {

    private final UserRepository userRepository;
    private final UserProfileRepository userProfileRepository;
    private final RoleRepository roleRepository;
    private final UserRoleRepository userRoleRepository;
    private final PasswordEncoder passwordEncoder;

    @Transactional
    public UserDto createUser(CreateUserRequest request) {
        log.info("Admin creating user with username: {}", request.getUsername());

        if (userRepository.existsByUsername(request.getUsername())) {
            throw new ConflictException("Username '" + request.getUsername() + "' is already in use");
        }

        if (userRepository.existsByEmail(request.getEmail())) {
            throw new ConflictException("Email '" + request.getEmail() + "' is already in use");
        }

        User user = User.builder()
                .username(request.getUsername().trim().toLowerCase())
                .email(request.getEmail().trim().toLowerCase())
                .password(passwordEncoder.encode(request.getPassword()))
                .enabled(Boolean.TRUE)
                .accountNonExpired(Boolean.TRUE)
                .accountNonLocked(Boolean.TRUE)
                .credentialsNonExpired(Boolean.TRUE)
                .deleted(Boolean.FALSE)
                .build();

        UserProfile profile = UserProfile.builder()
                .user(user)
                .firstName(request.getFirstName())
                .lastName(request.getLastName())
                .phoneNumber(request.getPhoneNumber())
                .build();

        user.setProfile(profile);
        User savedUser = userRepository.save(user);

        if (request.getRoles() != null && !request.getRoles().isEmpty()) {
            assignRolesToUser(savedUser, request.getRoles());
        } else {
            // Default to ROLE_USER
            roleRepository.findByCodeAndDeletedFalse("ROLE_USER")
                    .ifPresent(r -> userRoleRepository.save(UserRole.builder().user(savedUser).role(r).build()));
        }

        return mapToDto(savedUser);
    }

    @Transactional
    public UserDto updateUser(UUID id, UpdateUserRequest request) {
        log.info("Admin updating user with ID: {}", id);
        User user = findUserById(id);

        if (!user.getEmail().equalsIgnoreCase(request.getEmail()) && userRepository.existsByEmail(request.getEmail())) {
            throw new ConflictException("Email '" + request.getEmail() + "' is already in use");
        }

        user.setEmail(request.getEmail().trim().toLowerCase());

        UserProfile profile = user.getProfile();
        if (profile == null) {
            profile = UserProfile.builder().user(user).build();
            user.setProfile(profile);
        }

        profile.setFirstName(request.getFirstName());
        profile.setLastName(request.getLastName());
        profile.setPhoneNumber(request.getPhoneNumber());
        profile.setAvatarUrl(request.getAvatarUrl());
        profile.setBio(request.getBio());

        if (request.getRoles() != null) {
            userRoleRepository.deleteByUserId(user.getId());
            assignRolesToUser(user, request.getRoles());
        }

        User updatedUser = userRepository.save(user);
        return mapToDto(updatedUser);
    }

    public UserDto getUserById(UUID id) {
        User user = findUserById(id);
        return mapToDto(user);
    }

    public Page<UserDto> getUsers(RequestParamDto paramDto) {
        Page<User> usersPage = userRepository.searchUsers(paramDto.getSearch(), paramDto.toPageable());
        return usersPage.map(this::mapToDto);
    }

    @Transactional
    public void changeStatus(UUID id, boolean enabled) {
        log.info("Updating user {} enabled status to: {}", id, enabled);
        User user = findUserById(id);
        user.setEnabled(enabled);
        userRepository.save(user);
    }

    @Transactional
    public void deleteUser(UUID id) {
        log.info("Soft-deleting user with ID: {}", id);
        User user = findUserById(id);
        user.setDeleted(Boolean.TRUE);
        user.setDeletedAt(Instant.now());
        user.setDeletedBy(SecurityUtils.getCurrentUsername());
        user.setEnabled(Boolean.FALSE);
        userRepository.save(user);
    }

    @Transactional
    public void assignRoles(UUID id, Set<String> roleCodes) {
        log.info("Assigning roles {} to user ID: {}", roleCodes, id);
        User user = findUserById(id);
        userRoleRepository.deleteByUserId(user.getId());
        assignRolesToUser(user, roleCodes);
    }

    private void assignRolesToUser(User user, Set<String> roleCodes) {
        for (String roleCode : roleCodes) {
            String normalized = roleCode.startsWith("ROLE_") ? roleCode : "ROLE_" + roleCode;
            Role role = roleRepository.findByCodeAndDeletedFalse(normalized)
                    .or(() -> roleRepository.findByCodeAndDeletedFalse(roleCode))
                    .orElseThrow(() -> new ResourceNotFoundException("Role", "code", roleCode));

            userRoleRepository.save(UserRole.builder()
                    .user(user)
                    .role(role)
                    .build());
        }
    }

    private User findUserById(UUID id) {
        return userRepository.findActiveById(id)
                .orElseThrow(() -> new ResourceNotFoundException("User", "id", id));
    }

    private UserDto mapToDto(User user) {
        List<Role> roles = userRoleRepository.findRolesByUserId(user.getId());
        Set<String> roleCodes = roles.stream().map(Role::getCode).collect(Collectors.toSet());

        UserProfile profile = user.getProfile();
        return UserDto.builder()
                .id(user.getId())
                .username(user.getUsername())
                .email(user.getEmail())
                .enabled(user.getEnabled())
                .firstName(profile != null ? profile.getFirstName() : null)
                .lastName(profile != null ? profile.getLastName() : null)
                .phoneNumber(profile != null ? profile.getPhoneNumber() : null)
                .avatarUrl(profile != null ? profile.getAvatarUrl() : null)
                .bio(profile != null ? profile.getBio() : null)
                .roles(roleCodes)
                .createdAt(user.getCreatedAt())
                .updatedAt(user.getUpdatedAt())
                .build();
    }
}

