package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "LOCATION")
public class LocationEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "NAME", nullable = false, length = 255)
    private String name;

    @Column(name = "INACTIVE")
    private Boolean inactive;

    @Column(name = "PHONE", length = 20)
    private String phone;

    @Column(name = "EMAIL", length = 255)
    private String email;

    @Column(name = "ADDRESS_LINE1", length = 100)
    private String addressLine1;

    @Column(name = "ADDRESS_LINE2", length = 100)
    private String addressLine2;

    @Column(name = "CITY", length = 100)
    private String city;

    @Column(name = "STATE_ID")
    private Integer stateId;

    @Column(name = "COUNTRY_CODE", nullable = false, length = 2)
    private String countryCode;

    @Column(name = "POST_CODE", length = 10)
    private String postCode;

    @Column(name = "language_id")
    private Integer languageId;

    @Column(name = "PHONE_MESSAGE_TEMPLATE", length = 1000)
    private String phoneMessageTemplate;

    @Column(name = "email_message_template")
    private String emailMessageTemplate;

    @Column(name = "CUSTOMER_ID", nullable = false)
    private Long customerId;

    @Column(name = "LAST_MODIFIED_TIME")
    private Timestamp lastModifiedTime;

    @Column(name = "ALLOWS_OUTBOUND_PACKAGES")
    private Boolean allowsOutboundPackages;

    @Column(name = "TENANT_LABEL", length = 100)
    private String tenantLabel;

    @Column(name = "TENANT_LABEL_PLURAL", length = 100)
    private String tenantLabelPlural;

    @Column(name = "external_id", length = 100)
    private String externalId;

    @Column(name = "DO_NOT_DISPLAY_UNIT_INFO")
    private Boolean doNotDisplayUnitInfo;

    @Column(name = "allow_in_app_editing")
    private Boolean allowInAppEditing;

    @Column(name = "reply_to_email", nullable = false, length = 255)
    private String replyToEmail;

    @Column(name = "from_email", length = 255)
    private String fromEmail;

    @Column(name = "timezone", length = 100)
    private String timezone;

    @Column(name = "from_email_name", length = 300)
    private String fromEmailName;

    @Column(name = "enable_package_doesnt_fit_feature")
    private Boolean enablePackageDoesntFitFeature;

    @Column(name = "package_doesnt_fit_courier_message", length = 1000)
    private String packageDoesntFitCourierMessage;

    @Column(name = "package_doesnt_fit_recipient_message", length = 1000)
    private String packageDoesntFitRecipientMessage;

    @Column(name = "time_zone_id")
    private Long timeZoneId;

    @Column(name = "COURIER_LABEL", length = 50)
    private String courierLabel;

    @Column(name = "SEND_APP_NOTIFICATION")
    private Boolean sendAppNotification;

    @Column(name = "OPT_OUT_MESSAGE", nullable = false, length = 255)
    private String optOutMessage;

    @Column(name = "ENABLE_REPLY_EMAIL")
    private Boolean enableReplyEmail;

    @Column(name = "EXPECT_A_DELAY_MESSAGE", nullable = false, length = 255)
    private String expectADelayMessage;

    @Column(name = "ADDITIONAL_MESSAGE_IN_EMAIL", length = 255)
    private String additionalMessageInEmail;

    @Column(name = "NOTIFY_FOR_EVERY_SCAN")
    private Boolean notifyForEveryScan;

    @Column(name = "ENABLE_OUTGOING_PACKAGE_DOESNT_FIT")
    private Boolean enableOutgoingPackageDoesntFit;

    @Column(name = "SUPPORT_EMAIL", nullable = false, length = 50)
    private String supportEmail;

    @Column(name = "SUPPORT_PHONE", nullable = false, length = 20)
    private String supportPhone;

    @Column(name = "contact_message", length = 1024)
    private String contactMessage;

    @Column(name = "DELAY_IN_PICKUP_BODY_MESSAGE", nullable = false, length = 512)
    private String delayInPickupBodyMessage;

    @Column(name = "PACKAGE_DOESNT_FIT_MESSAGE_IN_EMAIL", length = 255)
    private String packageDoesntFitMessageInEmail;

    @Column(name = "MAILROOM_MESSAGE_IN_EMAIL", length = 255)
    private String mailroomMessageInEmail;

    @Column(name = "POD_DUPLICATE_NAME_MESSAGE", length = 1000)
    private String podDuplicateNameMessage;

    @Column(name = "NOTIFY_PACKAGE_RELEASE")
    private Boolean notifyPackageRelease;

    @Column(name = "PACKAGE_RELEASE_PHONE_MESSAGE_TEMPLATE", length = 500)
    private String packageReleasePhoneMessageTemplate;

    @Column(name = "IS_BOPIS")
    private Boolean isBopis;

    @Column(name = "SPECIAL_STATUS_MESSAGE", length = 500)
    private String specialStatusMessage;

    @Column(name = "created_time", nullable = false)
    private Timestamp createdTime;

    @Column(name = "cc_email", length = 255)
    private String ccEmail;

    @Column(name = "courier_can_retrieve_expired_packages")
    private Boolean courierCanRetrieveExpiredPackages;

    @Column(name = "UUID", length = 36)
    private String uuid;

    @Column(name = "image_url", length = 255)
    private String imageUrl;

    public LocationEntity() {}

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

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
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

    public Integer getStateId() {
        return this.stateId;
    }

    public void setStateId(Integer stateId) {
        this.stateId = stateId;
    }

    public String getCountryCode() {
        return this.countryCode;
    }

    public void setCountryCode(String countryCode) {
        this.countryCode = countryCode;
    }

    public String getPostCode() {
        return this.postCode;
    }

    public void setPostCode(String postCode) {
        this.postCode = postCode;
    }

    public Integer getLanguageId() {
        return this.languageId;
    }

    public void setLanguageId(Integer languageId) {
        this.languageId = languageId;
    }

    public String getPhoneMessageTemplate() {
        return this.phoneMessageTemplate;
    }

    public void setPhoneMessageTemplate(String phoneMessageTemplate) {
        this.phoneMessageTemplate = phoneMessageTemplate;
    }

    public String getEmailMessageTemplate() {
        return this.emailMessageTemplate;
    }

    public void setEmailMessageTemplate(String emailMessageTemplate) {
        this.emailMessageTemplate = emailMessageTemplate;
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

    public Boolean getAllowsOutboundPackages() {
        return this.allowsOutboundPackages;
    }

    public void setAllowsOutboundPackages(Boolean allowsOutboundPackages) {
        this.allowsOutboundPackages = allowsOutboundPackages;
    }

    public String getTenantLabel() {
        return this.tenantLabel;
    }

    public void setTenantLabel(String tenantLabel) {
        this.tenantLabel = tenantLabel;
    }

    public String getTenantLabelPlural() {
        return this.tenantLabelPlural;
    }

    public void setTenantLabelPlural(String tenantLabelPlural) {
        this.tenantLabelPlural = tenantLabelPlural;
    }

    public String getExternalId() {
        return this.externalId;
    }

    public void setExternalId(String externalId) {
        this.externalId = externalId;
    }

    public Boolean getDoNotDisplayUnitInfo() {
        return this.doNotDisplayUnitInfo;
    }

    public void setDoNotDisplayUnitInfo(Boolean doNotDisplayUnitInfo) {
        this.doNotDisplayUnitInfo = doNotDisplayUnitInfo;
    }

    public Boolean getAllowInAppEditing() {
        return this.allowInAppEditing;
    }

    public void setAllowInAppEditing(Boolean allowInAppEditing) {
        this.allowInAppEditing = allowInAppEditing;
    }

    public String getReplyToEmail() {
        return this.replyToEmail;
    }

    public void setReplyToEmail(String replyToEmail) {
        this.replyToEmail = replyToEmail;
    }

    public String getFromEmail() {
        return this.fromEmail;
    }

    public void setFromEmail(String fromEmail) {
        this.fromEmail = fromEmail;
    }

    public String getTimezone() {
        return this.timezone;
    }

    public void setTimezone(String timezone) {
        this.timezone = timezone;
    }

    public String getFromEmailName() {
        return this.fromEmailName;
    }

    public void setFromEmailName(String fromEmailName) {
        this.fromEmailName = fromEmailName;
    }

    public Boolean getEnablePackageDoesntFitFeature() {
        return this.enablePackageDoesntFitFeature;
    }

    public void setEnablePackageDoesntFitFeature(Boolean enablePackageDoesntFitFeature) {
        this.enablePackageDoesntFitFeature = enablePackageDoesntFitFeature;
    }

    public String getPackageDoesntFitCourierMessage() {
        return this.packageDoesntFitCourierMessage;
    }

    public void setPackageDoesntFitCourierMessage(String packageDoesntFitCourierMessage) {
        this.packageDoesntFitCourierMessage = packageDoesntFitCourierMessage;
    }

    public String getPackageDoesntFitRecipientMessage() {
        return this.packageDoesntFitRecipientMessage;
    }

    public void setPackageDoesntFitRecipientMessage(String packageDoesntFitRecipientMessage) {
        this.packageDoesntFitRecipientMessage = packageDoesntFitRecipientMessage;
    }

    public Long getTimeZoneId() {
        return this.timeZoneId;
    }

    public void setTimeZoneId(Long timeZoneId) {
        this.timeZoneId = timeZoneId;
    }

    public String getCourierLabel() {
        return this.courierLabel;
    }

    public void setCourierLabel(String courierLabel) {
        this.courierLabel = courierLabel;
    }

    public Boolean getSendAppNotification() {
        return this.sendAppNotification;
    }

    public void setSendAppNotification(Boolean sendAppNotification) {
        this.sendAppNotification = sendAppNotification;
    }

    public String getOptOutMessage() {
        return this.optOutMessage;
    }

    public void setOptOutMessage(String optOutMessage) {
        this.optOutMessage = optOutMessage;
    }

    public Boolean getEnableReplyEmail() {
        return this.enableReplyEmail;
    }

    public void setEnableReplyEmail(Boolean enableReplyEmail) {
        this.enableReplyEmail = enableReplyEmail;
    }

    public String getExpectADelayMessage() {
        return this.expectADelayMessage;
    }

    public void setExpectADelayMessage(String expectADelayMessage) {
        this.expectADelayMessage = expectADelayMessage;
    }

    public String getAdditionalMessageInEmail() {
        return this.additionalMessageInEmail;
    }

    public void setAdditionalMessageInEmail(String additionalMessageInEmail) {
        this.additionalMessageInEmail = additionalMessageInEmail;
    }

    public Boolean getNotifyForEveryScan() {
        return this.notifyForEveryScan;
    }

    public void setNotifyForEveryScan(Boolean notifyForEveryScan) {
        this.notifyForEveryScan = notifyForEveryScan;
    }

    public Boolean getEnableOutgoingPackageDoesntFit() {
        return this.enableOutgoingPackageDoesntFit;
    }

    public void setEnableOutgoingPackageDoesntFit(Boolean enableOutgoingPackageDoesntFit) {
        this.enableOutgoingPackageDoesntFit = enableOutgoingPackageDoesntFit;
    }

    public String getSupportEmail() {
        return this.supportEmail;
    }

    public void setSupportEmail(String supportEmail) {
        this.supportEmail = supportEmail;
    }

    public String getSupportPhone() {
        return this.supportPhone;
    }

    public void setSupportPhone(String supportPhone) {
        this.supportPhone = supportPhone;
    }

    public String getContactMessage() {
        return this.contactMessage;
    }

    public void setContactMessage(String contactMessage) {
        this.contactMessage = contactMessage;
    }

    public String getDelayInPickupBodyMessage() {
        return this.delayInPickupBodyMessage;
    }

    public void setDelayInPickupBodyMessage(String delayInPickupBodyMessage) {
        this.delayInPickupBodyMessage = delayInPickupBodyMessage;
    }

    public String getPackageDoesntFitMessageInEmail() {
        return this.packageDoesntFitMessageInEmail;
    }

    public void setPackageDoesntFitMessageInEmail(String packageDoesntFitMessageInEmail) {
        this.packageDoesntFitMessageInEmail = packageDoesntFitMessageInEmail;
    }

    public String getMailroomMessageInEmail() {
        return this.mailroomMessageInEmail;
    }

    public void setMailroomMessageInEmail(String mailroomMessageInEmail) {
        this.mailroomMessageInEmail = mailroomMessageInEmail;
    }

    public String getPodDuplicateNameMessage() {
        return this.podDuplicateNameMessage;
    }

    public void setPodDuplicateNameMessage(String podDuplicateNameMessage) {
        this.podDuplicateNameMessage = podDuplicateNameMessage;
    }

    public Boolean getNotifyPackageRelease() {
        return this.notifyPackageRelease;
    }

    public void setNotifyPackageRelease(Boolean notifyPackageRelease) {
        this.notifyPackageRelease = notifyPackageRelease;
    }

    public String getPackageReleasePhoneMessageTemplate() {
        return this.packageReleasePhoneMessageTemplate;
    }

    public void setPackageReleasePhoneMessageTemplate(String packageReleasePhoneMessageTemplate) {
        this.packageReleasePhoneMessageTemplate = packageReleasePhoneMessageTemplate;
    }

    public Boolean isBopis() {
        return this.isBopis;
    }

    public void setIsBopis(Boolean isBopis) {
        this.isBopis = isBopis;
    }

    public String getSpecialStatusMessage() {
        return this.specialStatusMessage;
    }

    public void setSpecialStatusMessage(String specialStatusMessage) {
        this.specialStatusMessage = specialStatusMessage;
    }

    public Timestamp getCreatedTime() {
        return this.createdTime;
    }

    public void setCreatedTime(Timestamp createdTime) {
        this.createdTime = createdTime;
    }

    public String getCcEmail() {
        return this.ccEmail;
    }

    public void setCcEmail(String ccEmail) {
        this.ccEmail = ccEmail;
    }

    public Boolean getCourierCanRetrieveExpiredPackages() {
        return this.courierCanRetrieveExpiredPackages;
    }

    public void setCourierCanRetrieveExpiredPackages(Boolean courierCanRetrieveExpiredPackages) {
        this.courierCanRetrieveExpiredPackages = courierCanRetrieveExpiredPackages;
    }

    public String getUuid() {
        return this.uuid;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }

    public String getImageUrl() {
        return this.imageUrl;
    }

    public void setImageUrl(String imageUrl) {
        this.imageUrl = imageUrl;
    }

}
