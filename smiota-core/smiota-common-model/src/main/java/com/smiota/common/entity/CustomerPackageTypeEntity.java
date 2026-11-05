package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "CUSTOMER_PACKAGE_TYPE")
public class CustomerPackageTypeEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "PACKAGE_TYPE")
    private Integer packageType;

    @Column(name = "REGEX", length = 255)
    private String regex;

    @Column(name = "CUSTOMER_ID")
    private Long customerId;

    @Column(name = "LAST_MODIFIED_TIME")
    private Timestamp lastModifiedTime;

    @Column(name = "REMINDER_FREQUENCY_HOURS")
    private Integer reminderFrequencyHours;

    @Column(name = "EXPIRES_AFTER_HOURS")
    private Integer expiresAfterHours;

    @Column(name = "EXPIRED_EMAIL_MESSAGE_TEMPLATE", length = 2000)
    private String expiredEmailMessageTemplate;

    @Column(name = "EXPIRED_PHONE_MESSAGE_TEMPLATE", length = 2000)
    private String expiredPhoneMessageTemplate;

    @Column(name = "LOCATION_ID")
    private Long locationId;

    @Column(name = "ORDINAL", nullable = false)
    private Integer ordinal;

    @Column(name = "INTERVAL_REMINDER_HOURS")
    private Integer intervalReminderHours;

    public CustomerPackageTypeEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Integer getPackageType() {
        return this.packageType;
    }

    public void setPackageType(Integer packageType) {
        this.packageType = packageType;
    }

    public String getRegex() {
        return this.regex;
    }

    public void setRegex(String regex) {
        this.regex = regex;
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

    public Integer getReminderFrequencyHours() {
        return this.reminderFrequencyHours;
    }

    public void setReminderFrequencyHours(Integer reminderFrequencyHours) {
        this.reminderFrequencyHours = reminderFrequencyHours;
    }

    public Integer getExpiresAfterHours() {
        return this.expiresAfterHours;
    }

    public void setExpiresAfterHours(Integer expiresAfterHours) {
        this.expiresAfterHours = expiresAfterHours;
    }

    public String getExpiredEmailMessageTemplate() {
        return this.expiredEmailMessageTemplate;
    }

    public void setExpiredEmailMessageTemplate(String expiredEmailMessageTemplate) {
        this.expiredEmailMessageTemplate = expiredEmailMessageTemplate;
    }

    public String getExpiredPhoneMessageTemplate() {
        return this.expiredPhoneMessageTemplate;
    }

    public void setExpiredPhoneMessageTemplate(String expiredPhoneMessageTemplate) {
        this.expiredPhoneMessageTemplate = expiredPhoneMessageTemplate;
    }

    public Long getLocationId() {
        return this.locationId;
    }

    public void setLocationId(Long locationId) {
        this.locationId = locationId;
    }

    public Integer getOrdinal() {
        return this.ordinal;
    }

    public void setOrdinal(Integer ordinal) {
        this.ordinal = ordinal;
    }

    public Integer getIntervalReminderHours() {
        return this.intervalReminderHours;
    }

    public void setIntervalReminderHours(Integer intervalReminderHours) {
        this.intervalReminderHours = intervalReminderHours;
    }

}
