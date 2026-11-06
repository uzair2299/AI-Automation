package com.company.starter.security.service;

import com.company.starter.modules.identity.entity.User;
import com.company.starter.modules.identity.entity.UserProfile;
import com.company.starter.modules.identity.repository.UserRepository;
import com.company.starter.modules.rbac.entity.Role;
import com.company.starter.modules.rbac.entity.UserRole;
import com.company.starter.modules.rbac.repository.RoleRepository;
import com.company.starter.modules.rbac.repository.UserRoleRepository;
import com.company.starter.security.context.CustomUserDetails;
import com.company.starter.security.dto.LoginRequest;
import com.company.starter.security.dto.LoginResponse;
import com.company.starter.security.dto.RegisterRequest;
import com.company.starter.security.jwt.JwtProvider;
import com.company.starter.shared.exception.ConflictException;
import com.company.starter.shared.exception.ResourceNotFoundException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Set;

/**
 * Service orchestrating user login and registration workflows.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AuthService {

    private final AuthenticationManager authenticationManager;
    private final JwtProvider jwtProvider;
    private final UserRepository userRepository;
    private final RoleRepository roleRepository;
    private final UserRoleRepository userRoleRepository;
    private final PasswordEncoder passwordEncoder;

    @Transactional(readOnly = true)
    public LoginResponse login(LoginRequest request) {
        log.info("Processing login request for user: {}", request.getUsername());

        Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword())
        );

        CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();
        String token = jwtProvider.generateToken(userDetails);

        return LoginResponse.builder()
                .token(token)
                .tokenType("Bearer")
                .expiresIn(jwtProvider.getExpirationInSeconds())
                .userId(userDetails.getId())
                .smiotaUserId(userDetails.getSmiotaUserId())
                .locationId(userDetails.getLocationId())
                .customerId(userDetails.getCustomerId())
                .username(userDetails.getUsername())
                .email(userDetails.getEmail())
                .firstName(userDetails.getFirstName())
                .lastName(userDetails.getLastName())
                .roles(userDetails.getRoles())
                .permissions(userDetails.getPermissions())
                .build();
    }

    @Transactional
    public LoginResponse register(RegisterRequest request) {
        log.info("Processing registration for username: {}, email: {}", request.getUsername(), request.getEmail());

        if (userRepository.existsByUsername(request.getUsername())) {
            throw new ConflictException("Username '" + request.getUsername() + "' is already in use");
        }

        if (userRepository.existsByEmail(request.getEmail())) {
            throw new ConflictException("Email '" + request.getEmail() + "' is already in use");
        }

        Role userRole = roleRepository.findByCodeAndDeletedFalse("ROLE_USER")
                .or(() -> roleRepository.findByCodeAndDeletedFalse("USER"))
                .orElseThrow(() -> new ResourceNotFoundException("Role", "code", "ROLE_USER"));

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

        UserRole mapping = UserRole.builder()
                .user(savedUser)
                .role(userRole)
                .build();
        userRoleRepository.save(mapping);

        log.info("User successfully registered with ID: {}", savedUser.getId());

        // Authenticate new user and return response
        LoginRequest loginRequest = LoginRequest.builder()
                .username(savedUser.getUsername())
                .password(request.getPassword())
                .build();

        return login(loginRequest);
    }
}

