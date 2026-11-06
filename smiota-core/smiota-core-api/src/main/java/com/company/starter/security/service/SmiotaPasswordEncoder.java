package com.company.starter.security.service;

import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.spec.InvalidKeySpecException;
import java.util.Base64;

/**
 * Custom Smiota PasswordEncoder implementing Spring Security's PasswordEncoder interface.
 * Uses PBKDF2 with HmacSHA-512 (modern standard) and falls back to PBKDF2 with HmacSHA-1 (legacy).
 */
@Service
public class SmiotaPasswordEncoder implements PasswordEncoder {

    private static final int ITERATIONS = 20_000;

    // Modern SHA-512 (Current Smiota standard)
    private static final String ALGORITHM_SHA512 = "PBKDF2WithHmacSHA512";
    private static final int SALT_LEN_SHA512 = 64;   // 64 bytes (512 bits)
    private static final int KEY_LEN_SHA512 = 512;    // 512 bits

    // Legacy SHA-1 (fallback for older accounts)
    private static final String ALGORITHM_SHA1 = "PBKDF2WithHmacSHA1";
    private static final int KEY_LEN_SHA1 = 256;      // 256 bits

    private final SecureRandom secureRandom;

    public SmiotaPasswordEncoder() {
        try {
            // Smiota specifically uses SHA1PRNG for SecureRandom
            this.secureRandom = SecureRandom.getInstance("SHA1PRNG");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("Failed to initialize SecureRandom", e);
        }
    }

    /**
     * Spring Security PasswordEncoder implementation for hashing.
     */
    @Override
    public String encode(CharSequence rawPassword) {
        if (rawPassword == null) {
            throw new IllegalArgumentException("Password cannot be null.");
        }
        return hashPassword(rawPassword.toString());
    }

    /**
     * Spring Security PasswordEncoder implementation for verifying.
     */
    @Override
    public boolean matches(CharSequence rawPassword, String encodedPassword) {
        if (rawPassword == null || encodedPassword == null) {
            return false;
        }
        return verifyPassword(rawPassword.toString(), encodedPassword);
    }

    /**
     * Creates a new salted PBKDF2-SHA512 password hash for storing in ACCOUNT.password_hash
     */
    public String hashPassword(String rawPassword) {
        if (rawPassword == null || rawPassword.isEmpty()) {
            throw new IllegalArgumentException("Password cannot be empty.");
        }
        byte[] salt = new byte[SALT_LEN_SHA512];
        secureRandom.nextBytes(salt);

        String hash = computeHash(rawPassword, salt, ALGORITHM_SHA512, KEY_LEN_SHA512);
        return Base64.getEncoder().encodeToString(salt) + "$" + hash;
    }

    /**
     * Matches raw password against stored hash (checks SHA-512, falls back to legacy SHA-1)
     */
    public boolean verifyPassword(String rawPassword, String storedHash) {
        if (rawPassword == null || storedHash == null || !storedHash.contains("$")) {
            return false;
        }

        String[] parts = storedHash.split("\\$");
        if (parts.length != 2) {
            return false;
        }

        try {
            byte[] salt = Base64.getDecoder().decode(parts[0]);
            String expectedHash = parts[1];

            // 1. Try SHA-512 (Standard)
            String computedHash = computeHash(rawPassword, salt, ALGORITHM_SHA512, KEY_LEN_SHA512);
            if (MessageDigest.isEqual(computedHash.getBytes(), expectedHash.getBytes())) {
                return true;
            }

            // 2. Fallback to Legacy SHA-1 if salt was 32 bytes / 256-bit key
            String legacyComputed = computeHash(rawPassword, salt, ALGORITHM_SHA1, KEY_LEN_SHA1);
            return MessageDigest.isEqual(legacyComputed.getBytes(), expectedHash.getBytes());

        } catch (Exception e) {
            return false;
        }
    }

    private String computeHash(String password, byte[] salt, String algorithm, int keyLength) {
        try {
            PBEKeySpec spec = new PBEKeySpec(password.toCharArray(), salt, ITERATIONS, keyLength);
            SecretKeyFactory skf = SecretKeyFactory.getInstance(algorithm);
            byte[] keyBytes = skf.generateSecret(spec).getEncoded();
            return Base64.getEncoder().encodeToString(keyBytes);
        } catch (NoSuchAlgorithmException | InvalidKeySpecException e) {
            throw new RuntimeException("Error computing password hash", e);
        }
    }
}

