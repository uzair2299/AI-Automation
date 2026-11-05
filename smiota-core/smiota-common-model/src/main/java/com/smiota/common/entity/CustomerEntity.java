package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "CUSTOMER")
public class CustomerEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "NAME", nullable = false, length = 100)
    private String name;

    @Column(name = "PHONE", length = 20)
    private String phone;

    @Column(name = "EMAIL", length = 255)
    private String email;

    @Column(name = "INACTIVE")
    private Boolean inactive;

    @Column(name = "COMMENTS", length = 1000)
    private String comments;

    @Column(name = "LAST_MODIFIED_TIME")
    private Timestamp lastModifiedTime;

    @Column(name = "ENABLE_PACKAGE_REMINDERS")
    private Boolean enablePackageReminders;

    @Column(name = "ALLOW_RECIPIENTS_TO_SELF_RELEASE_PACKAGES")
    private Boolean allowRecipientsToSelfReleasePackages;

    @Column(name = "ENABLE_EXPIRED_PACKAGE_REMINDERS_FOR_ADMINS")
    private Boolean enableExpiredPackageRemindersForAdmins;

    @Column(name = "UUID", length = 36)
    private String uuid;

    @Column(name = "is_test_customer")
    private Boolean isTestCustomer;

    @Column(name = "ADMIN_NOTIFICATIONS_PHONE", length = 20)
    private String adminNotificationsPhone;

    @Column(name = "image_url", length = 255)
    private String imageUrl;

    @Column(name = "created_time", nullable = false)
    private Timestamp createdTime;

    @Column(name = "access_key", length = 256)
    private String accessKey;

    @Column(name = "access_id", length = 256)
    private String accessId;

    @Column(name = "TWILIO_LONG_CODE", length = 20)
    private String twilioLongCode;

    public CustomerEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return this.name;
    }

    public void setName(String name) {
        this.name = name;
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

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
    }

    public String getComments() {
        return this.comments;
    }

    public void setComments(String comments) {
        this.comments = comments;
    }

    public Timestamp getLastModifiedTime() {
        return this.lastModifiedTime;
    }

    public void setLastModifiedTime(Timestamp lastModifiedTime) {
        this.lastModifiedTime = lastModifiedTime;
    }

    public Boolean getEnablePackageReminders() {
        return this.enablePackageReminders;
    }

    public void setEnablePackageReminders(Boolean enablePackageReminders) {
        this.enablePackageReminders = enablePackageReminders;
    }

    public Boolean getAllowRecipientsToSelfReleasePackages() {
        return this.allowRecipientsToSelfReleasePackages;
    }

    public void setAllowRecipientsToSelfReleasePackages(Boolean allowRecipientsToSelfReleasePackages) {
        this.allowRecipientsToSelfReleasePackages = allowRecipientsToSelfReleasePackages;
    }

    public Boolean getEnableExpiredPackageRemindersForAdmins() {
        return this.enableExpiredPackageRemindersForAdmins;
    }

    public void setEnableExpiredPackageRemindersForAdmins(Boolean enableExpiredPackageRemindersForAdmins) {
        this.enableExpiredPackageRemindersForAdmins = enableExpiredPackageRemindersForAdmins;
    }

    public String getUuid() {
        return this.uuid;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }

    public Boolean isTestCustomer() {
        return this.isTestCustomer;
    }

    public void setIsTestCustomer(Boolean isTestCustomer) {
        this.isTestCustomer = isTestCustomer;
    }

    public String getAdminNotificationsPhone() {
        return this.adminNotificationsPhone;
    }

    public void setAdminNotificationsPhone(String adminNotificationsPhone) {
        this.adminNotificationsPhone = adminNotificationsPhone;
    }

    public String getImageUrl() {
        return this.imageUrl;
    }

    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }

    public Timestamp getCreatedTime() {
        return this.createdTime;
    }

    public void setCreatedTime(Timestamp createdTime) {
        this.createdTime = createdTime;
    }

    public String getAccessKey() {
        return this.accessKey;
    }

    public void setAccessKey(String accessKey) {
        this.accessKey = accessKey;
    }

    public String getAccessId() {
        return this.accessId;
    }

    public void setAccessId(String accessId) {
        this.accessId = accessId;
    }

    public String getTwilioLongCode() {
        return this.twilioLongCode;
    }

    public void setTwilioLongCode(String twilioLongCode) {
        this.twilioLongCode = twilioLongCode;
    }

}
