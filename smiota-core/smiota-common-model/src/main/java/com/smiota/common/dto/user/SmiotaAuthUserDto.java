package com.smiota.common.dto.user;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;

/**
 * Concrete DTO holding Smiota authentication and account security details.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SmiotaAuthUserDto implements Serializable {
    private static final long serialVersionUID = 1L;

    private Long id;
    private Long locationId;
    private Long customerId;
    private String firstName;
    private String lastName;
    private String email;
    private String passwordHash;
    private String hashedPassword;
    private Boolean isLocked;
    private Integer numLoginRetries;

    /**
     * Factory method creating a DTO from the projection.
     */
    public static SmiotaAuthUserDto fromProjection(SmiotaUserAuthProjection projection) {
        if (projection == null) {
            return null;
        }
        return SmiotaAuthUserDto.builder()
                .id(projection.getId())
                .locationId(projection.getLocationId())
                .customerId(projection.getCustomerId())
                .firstName(projection.getFirstName())
                .lastName(projection.getLastName())
                .email(projection.getEmail())
                .passwordHash(projection.getPasswordHash())
                .hashedPassword(projection.getHashedPassword())
                .isLocked(projection.getIsLocked())
                .numLoginRetries(projection.getNumLoginRetries())
                .build();
    }

    public String getEffectivePasswordHash() {
        return (passwordHash != null && !passwordHash.isBlank())
                ? passwordHash
                : hashedPassword;
    }
}
