package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "ACCOUNT")
public class AccountEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "LOGIN", length = 100)
    private String login;

    @Column(name = "INACTIVE")
    private Boolean inactive;

    @Column(name = "SESSION_TIMEOUT")
    private Integer sessionTimeout;

    @Column(name = "IS_LOCKED")
    private Boolean isLocked;

    @Column(name = "IS_TEMPORARY_PASSWORD")
    private Boolean isTemporaryPassword;

    @Column(name = "temporary_password_expiration")
    private Timestamp temporaryPasswordExpiration;

    @Column(name = "CUSTOMER_ID")
    private Long customerId;

    @Column(name = "LAST_MODIFIED_TIME")
    private Timestamp lastModifiedTime;

    @Column(name = "LOCATION_ID")
    private Long locationId;

    @Column(name = "language_id")
    private Integer languageId;

    @Column(name = "SECURITY_CARD_ID")
    private Long securityCardId;

    @Column(name = "ENABLE_PING")
    private Boolean enablePing;

    @Column(name = "sync_required")
    private Boolean syncRequired;

    @Column(name = "HASHED_PASSWORD", length = 1024)
    private String hashedPassword;

    @Column(name = "NUM_LOGIN_RETRIES")
    private Integer numLoginRetries;

    @Column(name = "LAST_FAILED_ATTEMPT")
    private Timestamp lastFailedAttempt;

    @Column(name = "FORGOT_PASSWORD_CODE", length = 255)
    private String forgotPasswordCode;

    @Column(name = "FORGOT_PASSWORD_CODE_NUM_ATTEMPTS")
    private Integer forgotPasswordCodeNumAttempts;

    @Column(name = "FORGOT_PASSWORD_CODE_LAST_FAILED_TIMESTAMP")
    private Timestamp forgotPasswordCodeLastFailedTimestamp;

    @Column(name = "FORGOT_PASSWORD_CODE_EXPIRES")
    private Timestamp forgotPasswordCodeExpires;

    @Column(name = "password_hash", length = 1024)
    private String passwordHash;

    @Column(name = "client_id", length = 36)
    private String clientId;

    @Column(name = "secret_hash", length = 1024)
    private String secretHash;

    @Column(name = "is_deleted")
    private Boolean isDeleted;

    @Column(name = "uuid", length = 36)
    private String uuid;

    public AccountEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getLogin() {
        return this.login;
    }

    public void setLogin(String login) {
        this.login = login;
    }

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
    }

    public Integer getSessionTimeout() {
        return this.sessionTimeout;
    }

    public void setSessionTimeout(Integer sessionTimeout) {
        this.sessionTimeout = sessionTimeout;
    }

    public Boolean isLocked() {
        return this.isLocked;
    }

    public void setIsLocked(Boolean isLocked) {
        this.isLocked = isLocked;
    }

    public Boolean isTemporaryPassword() {
        return this.isTemporaryPassword;
    }

    public void setIsTemporaryPassword(Boolean isTemporaryPassword) {
        this.isTemporaryPassword = isTemporaryPassword;
    }

    public Timestamp getTemporaryPasswordExpiration() {
        return this.temporaryPasswordExpiration;
    }

    public void setTemporaryPasswordExpiration(Timestamp temporaryPasswordExpiration) {
        this.temporaryPasswordExpiration = temporaryPasswordExpiration;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    public Timestamp getLastModifiedTime() {
        return this.lastModifiedTime;
    }

    public void setLastModifiedTime(Timestamp lastModifiedTime) {
        this.lastModifiedTime = lastModifiedTime;
    }

    public Long getLocationId() {
        return this.locationId;
    }

    public void setLocationId(Long locationId) {
        this.locationId = locationId;
    }

    public Integer getLanguageId() {
        return this.languageId;
    }

    public void setLanguageId(Integer languageId) {
        this.languageId = languageId;
    }

    public Long getSecurityCardId() {
        return this.securityCardId;
    }

    public void setSecurityCardId(Long securityCardId) {
        this.securityCardId = securityCardId;
    }

    public Boolean getEnablePing() {
        return this.enablePing;
    }

    public void setEnablePing(Boolean enablePing) {
        this.enablePing = enablePing;
    }

    public Boolean getSyncRequired() {
        return this.syncRequired;
    }

    public void setSyncRequired(Boolean syncRequired) {
        this.syncRequired = syncRequired;
    }

    public String getHashedPassword() {
        return this.hashedPassword;
    }

    public void setHashedPassword(String hashedPassword) {
        this.hashedPassword = hashedPassword;
    }

    public Integer getNumLoginRetries() {
        return this.numLoginRetries;
    }

    public void setNumLoginRetries(Integer numLoginRetries) {
        this.numLoginRetries = numLoginRetries;
    }

    public Timestamp getLastFailedAttempt() {
        return this.lastFailedAttempt;
    }

    public void setLastFailedAttempt(Timestamp lastFailedAttempt) {
        this.lastFailedAttempt = lastFailedAttempt;
    }

    public String getForgotPasswordCode() {
        return this.forgotPasswordCode;
    }

    public void setForgotPasswordCode(String forgotPasswordCode) {
        this.forgotPasswordCode = forgotPasswordCode;
    }

    public Integer getForgotPasswordCodeNumAttempts() {
        return this.forgotPasswordCodeNumAttempts;
    }

    public void setForgotPasswordCodeNumAttempts(Integer forgotPasswordCodeNumAttempts) {
        this.forgotPasswordCodeNumAttempts = forgotPasswordCodeNumAttempts;
    }

    public Timestamp getForgotPasswordCodeLastFailedTimestamp() {
        return this.forgotPasswordCodeLastFailedTimestamp;
    }

    public void setForgotPasswordCodeLastFailedTimestamp(Timestamp forgotPasswordCodeLastFailedTimestamp) {
        this.forgotPasswordCodeLastFailedTimestamp = forgotPasswordCodeLastFailedTimestamp;
    }

    public Timestamp getForgotPasswordCodeExpires() {
        return this.forgotPasswordCodeExpires;
    }

    public void setForgotPasswordCodeExpires(Timestamp forgotPasswordCodeExpires) {
        this.forgotPasswordCodeExpires = forgotPasswordCodeExpires;
    }

    public String getPasswordHash() {
        return this.passwordHash;
    }

    public void setPasswordHash(String passwordHash) {
        this.passwordHash = passwordHash;
    }

    public String getClientId() {
        return this.clientId;
    }

    public void setClientId(String clientId) {
        this.clientId = clientId;
    }

    public String getSecretHash() {
        return this.secretHash;
    }

    public void setSecretHash(String secretHash) {
        this.secretHash = secretHash;
    }

    public Boolean isDeleted() {
        return this.isDeleted;
    }

    public void setIsDeleted(Boolean isDeleted) {
        this.isDeleted = isDeleted;
    }

    public String getUuid() {
        return this.uuid;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }

}
