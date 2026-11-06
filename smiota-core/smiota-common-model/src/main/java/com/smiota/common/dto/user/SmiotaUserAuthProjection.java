package com.smiota.common.dto.user;

/**
 * Interface projection for Smiota database authentication query.
 * Maps columns:
 * - USER.ID -> id
 * - USER.LOCATION_ID -> locationId
 * - USER.CUSTOMER_ID -> customerId
 * - USER.FIRST_NAME -> firstName
 * - USER.LAST_NAME -> lastName
 * - USER.EMAIL -> email
 * - ACCOUNT.password_hash -> passwordHash
 * - ACCOUNT.hashed_password -> hashedPassword
 * - ACCOUNT.IS_LOCKED -> isLocked
 * - ACCOUNT.NUM_LOGIN_RETRIES -> numLoginRetries
 */
public interface SmiotaUserAuthProjection {

    Long getId();

    Long getLocationId();

    Long getCustomerId();

    String getFirstName();

    String getLastName();

    String getEmail();

    String getPasswordHash();

    String getHashedPassword();

    Boolean getIsLocked();

    Integer getNumLoginRetries();

    /**
     * Helper to return modern SHA-512 hash if present, otherwise legacy hash.
     */
    default String getEffectivePasswordHash() {
        return (getPasswordHash() != null && !getPasswordHash().isBlank())
                ? getPasswordHash()
                : getHashedPassword();
    }
}
