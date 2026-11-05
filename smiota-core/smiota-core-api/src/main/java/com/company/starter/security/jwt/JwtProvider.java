package com.company.starter.security.jwt;

import com.company.starter.security.context.CustomUserDetails;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Service;

import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Service for generating, parsing, and validating JWT access and refresh tokens.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class JwtProvider {

    private final JwtTokenUtil jwtTokenUtil;

    @Value("${application.security.jwt.expiration:86400000}")
    private long jwtExpirationInMs; // Default: 24h

    @Value("${application.security.jwt.refresh-token.expiration:604800000}")
    private long refreshExpirationInMs; // Default: 7d

    public String generateToken(CustomUserDetails userDetails) {
        Map<String, Object> extraClaims = new HashMap<>();
        extraClaims.put("userId", userDetails.getId() != null ? userDetails.getId().toString() : null);
        extraClaims.put("email", userDetails.getEmail());
        extraClaims.put("roles", userDetails.getRoles());
        extraClaims.put("permissions", userDetails.getPermissions());

        return buildToken(extraClaims, userDetails.getUsername(), jwtExpirationInMs);
    }

    public String generateRefreshToken(UserDetails userDetails) {
        return buildToken(new HashMap<>(), userDetails.getUsername(), refreshExpirationInMs);
    }

    private String buildToken(Map<String, Object> extraClaims, String subject, long expiration) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + expiration);

        return Jwts.builder()
                .setClaims(extraClaims)
                .setSubject(subject)
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .signWith(jwtTokenUtil.getSigningKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    public boolean isTokenValid(String token, UserDetails userDetails) {
        final String username = extractUsername(token);
        return (username.equals(userDetails.getUsername()) && !jwtTokenUtil.isTokenExpired(token));
    }

    public boolean validateToken(String token) {
        return jwtTokenUtil.validateToken(token);
    }

    public String extractUsername(String token) {
        return jwtTokenUtil.extractUsername(token);
    }

    public UUID extractUserId(String token) {
        Claims claims = jwtTokenUtil.extractAllClaims(token);
        String userIdStr = claims.get("userId", String.class);
        return userIdStr != null ? UUID.fromString(userIdStr) : null;
    }

    @SuppressWarnings("unchecked")
    public Set<String> extractRoles(String token) {
        Claims claims = jwtTokenUtil.extractAllClaims(token);
        Object rolesObj = claims.get("roles");
        if (rolesObj instanceof Iterable) {
            return (Set<String>) ((Iterable<?>) rolesObj);
        }
        return Set.of();
    }

    public long getExpirationInSeconds() {
        return jwtExpirationInMs / 1000;
    }
}

