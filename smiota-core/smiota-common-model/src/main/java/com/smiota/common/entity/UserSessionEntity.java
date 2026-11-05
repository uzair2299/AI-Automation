package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "USER_SESSION")
public class UserSessionEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "USER_ID")
    private Long userId;

    @Column(name = "auth_token", length = 100)
    private String authToken;

    @Column(name = "TEMP_PASSCODE", length = 10)
    private String tempPasscode;

    @Column(name = "TEMP_PASSCODE_EXPIRES")
    private Timestamp tempPasscodeExpires;

    @Column(name = "USER_AGENT", length = 255)
    private String userAgent;

    @Column(name = "DEVICE_TYPE")
    private Integer deviceType;

    @Column(name = "device_token", length = 300)
    private String deviceToken;

    @Column(name = "INACTIVE")
    private Boolean inactive;

    @Column(name = "CUSTOMER_ID")
    private Long customerId;

    @Column(name = "SIGNIN_TIME")
    private Timestamp signinTime;

    @Column(name = "expiration_time")
    private Timestamp expirationTime;

    @Column(name = "SIGNOUT_TIME")
    private Timestamp signoutTime;

    @Column(name = "LAST_MODIFIED_TIME")
    private Timestamp lastModifiedTime;

    @Column(name = "LAST_PING_TIME")
    private Timestamp lastPingTime;

    @Column(name = "LAST_NOTIFICATION_TIME")
    private Timestamp lastNotificationTime;

    @Column(name = "building_id")
    private Long buildingId;

    @Column(name = "NUM_LOGIN_RETRIES")
    private Integer numLoginRetries;

    @Column(name = "LAST_FAILED_ATTEMPT")
    private Timestamp lastFailedAttempt;

    @Column(name = "REFRESH_TOKEN", length = 2048)
    private String refreshToken;

    @Column(name = "REFRESH_TOKEN_EXPIRES_AFTER")
    private Timestamp refreshTokenExpiresAfter;

    @Column(name = "app_token", length = 255)
    private String appToken;

    @Column(name = "do_not_refresh")
    private Integer doNotRefresh;

    public UserSessionEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getUserId() {
        return this.userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public String getAuthToken() {
        return this.authToken;
    }

    public void setAuthToken(String authToken) {
        this.authToken = authToken;
    }

    public String getTempPasscode() {
        return this.tempPasscode;
    }

    public void setTempPasscode(String tempPasscode) {
        this.tempPasscode = tempPasscode;
    }

    public Timestamp getTempPasscodeExpires() {
        return this.tempPasscodeExpires;
    }

    public void setTempPasscodeExpires(Timestamp tempPasscodeExpires) {
        this.tempPasscodeExpires = tempPasscodeExpires;
    }

    public String getUserAgent() {
        return this.userAgent;
    }

    public void setUserAgent(String userAgent) {
        this.userAgent = userAgent;
    }

    public Integer getDeviceType() {
        return this.deviceType;
    }

    public void setDeviceType(Integer deviceType) {
        this.deviceType = deviceType;
    }

    public String getDeviceToken() {
        return this.deviceToken;
    }

    public void setDeviceToken(String deviceToken) {
        this.deviceToken = deviceToken;
    }

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    public Timestamp getSigninTime() {
        return this.signinTime;
    }

    public void setSigninTime(Timestamp signinTime) {
        this.signinTime = signinTime;
    }

    public Timestamp getExpirationTime() {
        return this.expirationTime;
    }

    public void setExpirationTime(Timestamp expirationTime) {
        this.expirationTime = expirationTime;
    }

    public Timestamp getSignoutTime() {
        return this.signoutTime;
    }

    public void setSignoutTime(Timestamp signoutTime) {
        this.signoutTime = signoutTime;
    }

    public Timestamp getLastModifiedTime() {
        return this.lastModifiedTime;
    }

    public void setLastModifiedTime(Timestamp lastModifiedTime) {
        this.lastModifiedTime = lastModifiedTime;
    }

    public Timestamp getLastPingTime() {
        return this.lastPingTime;
    }

    public void setLastPingTime(Timestamp lastPingTime) {
        this.lastPingTime = lastPingTime;
    }

    public Timestamp getLastNotificationTime() {
        return this.lastNotificationTime;
    }

    public void setLastNotificationTime(Timestamp lastNotificationTime) {
        this.lastNotificationTime = lastNotificationTime;
    }

    public Long getBuildingId() {
        return this.buildingId;
    }

    public void setBuildingId(Long buildingId) {
        this.buildingId = buildingId;
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

    public String getRefreshToken() {
        return this.refreshToken;
    }

    public void setRefreshToken(String refreshToken) {
        this.refreshToken = refreshToken;
    }

    public Timestamp getRefreshTokenExpiresAfter() {
        return this.refreshTokenExpiresAfter;
    }

    public void setRefreshTokenExpiresAfter(Timestamp refreshTokenExpiresAfter) {
        this.refreshTokenExpiresAfter = refreshTokenExpiresAfter;
    }

    public String getAppToken() {
        return this.appToken;
    }

    public void setAppToken(String appToken) {
        this.appToken = appToken;
    }

    public Integer getDoNotRefresh() {
        return this.doNotRefresh;
    }

    public void setDoNotRefresh(Integer doNotRefresh) {
        this.doNotRefresh = doNotRefresh;
    }

}
