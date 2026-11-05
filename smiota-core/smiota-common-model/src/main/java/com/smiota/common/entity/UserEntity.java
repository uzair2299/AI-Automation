package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "USER")
public class UserEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "FIRST_NAME", length = 255)
    private String firstName;

    @Column(name = "LAST_NAME", length = 255)
    private String lastName;

    @Column(name = "DESCRIPTION", length = 1000)
    private String description;

    @Column(name = "INACTIVE")
    private Boolean inactive;

    @Column(name = "PHOTO")
    private byte[] photo;

    @Column(name = "PHONE", length = 20)
    private String phone;

    @Column(name = "EMAIL", length = 255)
    private String email;

    @Column(name = "IS_AUTHORIZED_USER_FOR_TENANT")
    private Boolean isAuthorizedUserForTenant;

    @Column(name = "ACCOUNT_ID")
    private Long accountId;

    @Column(name = "CUSTOMER_ID")
    private Long customerId;

    @Column(name = "LOCATION_ID")
    private Long locationId;

    @Column(name = "TENANT_ID")
    private Long tenantId;

    @Column(name = "LAST_MODIFIED_TIME")
    private Timestamp lastModifiedTime;

    @Column(name = "PASSCODE", length = 10)
    private String passcode;

    @Column(name = "BUILDING_ID")
    private Long buildingId;

    @Column(name = "external_id", length = 255)
    private String externalId;

    @Column(name = "unit_no", length = 255)
    private String unitNo;

    @Column(name = "updated_by_user_id")
    private Long updatedByUserId;

    @Column(name = "delegate_notifications_to_user_id")
    private Long delegateNotificationsToUserId;

    @Column(name = "keep_local_changes")
    private Boolean keepLocalChanges;

    @Column(name = "needs_wheel_chair_access")
    private Boolean needsWheelChairAccess;

    @Column(name = "preferred_communication_method1", length = 20)
    private String preferredCommunicationMethod1;

    @Column(name = "preferred_communication_method2", length = 20)
    private String preferredCommunicationMethod2;

    @Column(name = "preferred_communication_method3", length = 20)
    private String preferredCommunicationMethod3;

    @Column(name = "OPT_OUT_OPTION")
    private Boolean optOutOption;

    @Column(name = "EMAIL_UNSUBSCRIBE")
    private Boolean emailUnsubscribe;

    @Column(name = "PHONE_UNSUBSCRIBE")
    private Boolean phoneUnsubscribe;

    @Column(name = "NUM_LOGIN_RETRIES")
    private Integer numLoginRetries;

    @Column(name = "LAST_FAILED_ATTEMPT")
    private Timestamp lastFailedAttempt;

    @Column(name = "HAS_SPECIAL_STATUS")
    private Boolean hasSpecialStatus;

    @Column(name = "ADDRESS_LINE1", length = 128)
    private String addressLine1;

    @Column(name = "ADDRESS_LINE2", length = 128)
    private String addressLine2;

    @Column(name = "CITY", length = 128)
    private String city;

    @Column(name = "STATE", length = 128)
    private String state;

    @Column(name = "ZIP_CODE", length = 64)
    private String zipCode;

    @Column(name = "last_passcode_created_time")
    private Timestamp lastPasscodeCreatedTime;

    @Column(name = "auth_id", length = 255)
    private String authId;

    @Column(name = "do_not_associate_to_a_package")
    private Boolean doNotAssociateToAPackage;

    @Column(name = "UUID", length = 36)
    private String uuid;

    @Column(name = "voice_call_phone", length = 256)
    private String voiceCallPhone;

    @Column(name = "badge_id", length = 255)
    private String badgeId;

    public UserEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getFirstName() {
        return this.firstName;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public String getLastName() {
        return this.lastName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public String getDescription() {
        return this.description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
    }

    public byte[] getPhoto() {
        return this.photo;
    }

    public void setPhoto(byte[] photo) {
        this.photo = photo;
    }

    public String getPhone() {
        return this.phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getEmail() {
        return this.email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public Boolean isAuthorizedUserForTenant() {
        return this.isAuthorizedUserForTenant;
    }

    public void setIsAuthorizedUserForTenant(Boolean isAuthorizedUserForTenant) {
        this.isAuthorizedUserForTenant = isAuthorizedUserForTenant;
    }

    public Long getAccountId() {
        return this.accountId;
    }

    public void setAccountId(Long accountId) {
        this.accountId = accountId;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    public Long getLocationId() {
        return this.locationId;
    }

    public void setLocationId(Long locationId) {
        this.locationId = locationId;
    }

    public Long getTenantId() {
        return this.tenantId;
    }

    public void setTenantId(Long tenantId) {
        this.tenantId = tenantId;
    }

    public Timestamp getLastModifiedTime() {
        return this.lastModifiedTime;
    }

    public void setLastModifiedTime(Timestamp lastModifiedTime) {
        this.lastModifiedTime = lastModifiedTime;
    }

    public String getPasscode() {
        return this.passcode;
    }

    public void setPasscode(String passcode) {
        this.passcode = passcode;
    }

    public Long getBuildingId() {
        return this.buildingId;
    }

    public void setBuildingId(Long buildingId) {
        this.buildingId = buildingId;
    }

    public String getExternalId() {
        return this.externalId;
    }

    public void setExternalId(String externalId) {
        this.externalId = externalId;
    }

    public String getUnitNo() {
        return this.unitNo;
    }

    public void setUnitNo(String unitNo) {
        this.unitNo = unitNo;
    }

    public Long getUpdatedByUserId() {
        return this.updatedByUserId;
    }

    public void setUpdatedByUserId(Long updatedByUserId) {
        this.updatedByUserId = updatedByUserId;
    }

    public Long getDelegateNotificationsToUserId() {
        return this.delegateNotificationsToUserId;
    }

    public void setDelegateNotificationsToUserId(Long delegateNotificationsToUserId) {
        this.delegateNotificationsToUserId = delegateNotificationsToUserId;
    }

    public Boolean getKeepLocalChanges() {
        return this.keepLocalChanges;
    }

    public void setKeepLocalChanges(Boolean keepLocalChanges) {
        this.keepLocalChanges = keepLocalChanges;
    }

    public Boolean getNeedsWheelChairAccess() {
        return this.needsWheelChairAccess;
    }

    public void setNeedsWheelChairAccess(Boolean needsWheelChairAccess) {
        this.needsWheelChairAccess = needsWheelChairAccess;
    }

    public String getPreferredCommunicationMethod1() {
        return this.preferredCommunicationMethod1;
    }

    public void setPreferredCommunicationMethod1(String preferredCommunicationMethod1) {
        this.preferredCommunicationMethod1 = preferredCommunicationMethod1;
    }

    public String getPreferredCommunicationMethod2() {
        return this.preferredCommunicationMethod2;
    }

    public void setPreferredCommunicationMethod2(String preferredCommunicationMethod2) {
        this.preferredCommunicationMethod2 = preferredCommunicationMethod2;
    }

    public String getPreferredCommunicationMethod3() {
        return this.preferredCommunicationMethod3;
    }

    public void setPreferredCommunicationMethod3(String preferredCommunicationMethod3) {
        this.preferredCommunicationMethod3 = preferredCommunicationMethod3;
    }

    public Boolean getOptOutOption() {
        return this.optOutOption;
    }

    public void setOptOutOption(Boolean optOutOption) {
        this.optOutOption = optOutOption;
    }

    public Boolean getEmailUnsubscribe() {
        return this.emailUnsubscribe;
    }

    public void setEmailUnsubscribe(Boolean emailUnsubscribe) {
        this.emailUnsubscribe = emailUnsubscribe;
    }

    public Boolean getPhoneUnsubscribe() {
        return this.phoneUnsubscribe;
    }

    public void setPhoneUnsubscribe(Boolean phoneUnsubscribe) {
        this.phoneUnsubscribe = phoneUnsubscribe;
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

    public Boolean getHasSpecialStatus() {
        return this.hasSpecialStatus;
    }

    public void setHasSpecialStatus(Boolean hasSpecialStatus) {
        this.hasSpecialStatus = hasSpecialStatus;
    }

    public String getAddressLine1() {
        return this.addressLine1;
    }

    public void setAddressLine1(String addressLine1) {
        this.addressLine1 = addressLine1;
    }

    public String getAddressLine2() {
        return this.addressLine2;
    }

    public void setAddressLine2(String addressLine2) {
        this.addressLine2 = addressLine2;
    }

    public String getCity() {
        return this.city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    public String getState() {
        return this.state;
    }

    public void setState(String state) {
        this.state = state;
    }

    public String getZipCode() {
        return this.zipCode;
    }

    public void setZipCode(String zipCode) {
        this.zipCode = zipCode;
    }

    public Timestamp getLastPasscodeCreatedTime() {
        return this.lastPasscodeCreatedTime;
    }

    public void setLastPasscodeCreatedTime(Timestamp lastPasscodeCreatedTime) {
        this.lastPasscodeCreatedTime = lastPasscodeCreatedTime;
    }

    public String getAuthId() {
        return this.authId;
    }

    public void setAuthId(String authId) {
        this.authId = authId;
    }

    public Boolean getDoNotAssociateToAPackage() {
        return this.doNotAssociateToAPackage;
    }

    public void setDoNotAssociateToAPackage(Boolean doNotAssociateToAPackage) {
        this.doNotAssociateToAPackage = doNotAssociateToAPackage;
    }

    public String getUuid() {
        return this.uuid;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }

    public String getVoiceCallPhone() {
        return this.voiceCallPhone;
    }

    public void setVoiceCallPhone(String voiceCallPhone) {
        this.voiceCallPhone = voiceCallPhone;
    }

    public String getBadgeId() {
        return this.badgeId;
    }

    public void setBadgeId(String badgeId) {
        this.badgeId = badgeId;
    }

}
