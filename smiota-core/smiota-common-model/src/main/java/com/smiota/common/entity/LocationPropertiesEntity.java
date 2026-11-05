package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "location_properties")
public class LocationPropertiesEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "customer_id")
    private Long customerId;

    @Column(name = "location_id")
    private Long locationId;

    @Column(name = "frequency_id")
    private Integer frequencyId;

    @Column(name = "frequency_value", length = 128)
    private String frequencyValue;

    @Column(name = "enable_package_reminder_recipient")
    private Boolean enablePackageReminderRecipient;

    @Column(name = "enable_package_reminder_admin")
    private Boolean enablePackageReminderAdmin;

    @Column(name = "enable_package_sent_back")
    private Boolean enablePackageSentBack;

    @Column(name = "notify_sub_par_level_products")
    private Boolean notifySubParLevelProducts;

    @Column(name = "pri_sla_start_time", length = 5)
    private String priSlaStartTime;

    @Column(name = "pri_sla_end_time", length = 5)
    private String priSlaEndTime;

    @Column(name = "std_sla_start_time", length = 5)
    private String stdSlaStartTime;

    @Column(name = "std_sla_end_time", length = 5)
    private String stdSlaEndTime;

    @Column(name = "enable_pack_notify_recipient")
    private Boolean enablePackNotifyRecipient;

    @Column(name = "is_package_group")
    private Boolean isPackageGroup;

    @Column(name = "is_package_group_passcode")
    private Boolean isPackageGroupPasscode;

    @Column(name = "package_group_regex", length = 100)
    private String packageGroupRegex;

    @Column(name = "package_group_alphanumeric")
    private Boolean packageGroupAlphanumeric;

    @Column(name = "package_group_min_length")
    private Integer packageGroupMinLength;

    @Column(name = "package_group_max_length")
    private Integer packageGroupMaxLength;

    @Column(name = "package_group_retrieval_code_length")
    private Integer packageGroupRetrievalCodeLength;

    @Column(name = "package_group_trim", nullable = false)
    private Boolean packageGroupTrim;

    @Column(name = "package_group_trim_front")
    private Integer packageGroupTrimFront;

    @Column(name = "package_group_trim_end")
    private Integer packageGroupTrimEnd;

    @Column(name = "can_receive_packages_for_other_locations", nullable = false)
    private Boolean canReceivePackagesForOtherLocations;

    @Column(name = "show_review_packages_option", nullable = false)
    private Boolean showReviewPackagesOption;

    @Column(name = "show_package_delete_option", nullable = false)
    private Boolean showPackageDeleteOption;

    @Column(name = "restricted_entry", nullable = false)
    private Boolean restrictedEntry;

    @Column(name = "package_arrival_mandatory", nullable = false)
    private Boolean packageArrivalMandatory;

    @Column(name = "enable_attempted_to_deliver", nullable = false)
    private Boolean enableAttemptedToDeliver;

    @Column(name = "has_mailroom", nullable = false)
    private Boolean hasMailroom;

    @Column(name = "is_external_scanner", nullable = false)
    private Boolean isExternalScanner;

    @Column(name = "package_passcode_generation")
    private Integer packagePasscodeGeneration;

    @Column(name = "enable_outbound_recipient_notification")
    private Boolean enableOutboundRecipientNotification;

    @Column(name = "enable_outgoing_courier_user_notification")
    private Boolean enableOutgoingCourierUserNotification;

    @Column(name = "enable_passcode_download")
    private Boolean enablePasscodeDownload;

    @Column(name = "is_enable_outbound_label_print", nullable = false)
    private Boolean isEnableOutboundLabelPrint;

    @Column(name = "is_require_outbound_signature", nullable = false)
    private Boolean isRequireOutboundSignature;

    @Column(name = "is_network_printer", nullable = false)
    private Boolean isNetworkPrinter;

    @Column(name = "printer_ip_address", length = 100)
    private String printerIpAddress;

    @Column(name = "onlyShowManageSection")
    private Boolean onlyshowmanagesection;

    @Column(name = "can_talk_to_locker_unit")
    private Boolean canTalkToLockerUnit;

    @Column(name = "package_num_subitems_min", nullable = false)
    private Integer packageNumSubitemsMin;

    @Column(name = "package_num_subitems_max")
    private Integer packageNumSubitemsMax;

    @Column(name = "use_dmy")
    private Boolean useDmy;

    @Column(name = "ecommerce_flow")
    private Boolean ecommerceFlow;

    @Column(name = "ui_skin_id", nullable = false)
    private Long uiSkinId;

    @Column(name = "is_user_registration_enabled")
    private Boolean isUserRegistrationEnabled;

    @Column(name = "unit_no_label", length = 128)
    private String unitNoLabel;

    @Column(name = "track_package_transactions")
    private Boolean trackPackageTransactions;

    @Column(name = "package_transaction_timeout")
    private Integer packageTransactionTimeout;

    @Column(name = "cla_deposit_timeout")
    private Integer claDepositTimeout;

    @Column(name = "cla_retrieve_timeout")
    private Integer claRetrieveTimeout;

    @Column(name = "force_notifications")
    private Boolean forceNotifications;

    @Column(name = "show_orders_with_recipient")
    private Boolean showOrdersWithRecipient;

    @Column(name = "it_flow")
    private Boolean itFlow;

    @Column(name = "integration_config", length = 1024)
    private String integrationConfig;

    @Column(name = "enable_notification_unsubscribe")
    private Boolean enableNotificationUnsubscribe;

    @Column(name = "enable_temp_alert_voice_call")
    private Boolean enableTempAlertVoiceCall;

    @Column(name = "voice_call_default_phone", length = 256)
    private String voiceCallDefaultPhone;

    @Column(name = "enable_shift_management")
    private Boolean enableShiftManagement;

    @Column(name = "require_sso_on_urban_admin_login")
    private Boolean requireSsoOnUrbanAdminLogin;

    @Column(name = "mobile_sso_base_url", length = 100)
    private String mobileSsoBaseUrl;

    @Column(name = "EMAIL_MAX_REMINDERS")
    private Integer emailMaxReminders;

    @Column(name = "PHONE_MAX_REMINDERS")
    private Integer phoneMaxReminders;

    @Column(name = "ENFORCE_MAX_IF_ONLY_CONTACT_INFO")
    private Boolean enforceMaxIfOnlyContactInfo;

    @Column(name = "show_user_passcode")
    private Integer showUserPasscode;

    @Column(name = "show_waiver_before_release")
    private Integer showWaiverBeforeRelease;

    @Column(name = "waiver_urls")
    private String waiverUrls;

    @Column(name = "waiver_text")
    private String waiverText;

    @Column(name = "ignore_duplicate_order_id")
    private Integer ignoreDuplicateOrderId;

    @Column(name = "mailroom_app_ui", length = 255)
    private String mailroomAppUi;

    @Column(name = "mailroom_screen_saver_file", length = 255)
    private String mailroomScreenSaverFile;

    @Column(name = "mailroom_screen_saver_mode", length = 128)
    private String mailroomScreenSaverMode;

    @Column(name = "mailroom_screen_saver_animation_duration")
    private Integer mailroomScreenSaverAnimationDuration;

    @Column(name = "mailroom_screen_saver_item_count")
    private Integer mailroomScreenSaverItemCount;

    @Column(name = "show_notifications_in_package_details")
    private Integer showNotificationsInPackageDetails;

    @Column(name = "allow_complex_courier_codes")
    private Integer allowComplexCourierCodes;

    @Column(name = "enable_expired_reminder_recipient")
    private Integer enableExpiredReminderRecipient;

    @Column(name = "package_group_validate_locker_unit")
    private Integer packageGroupValidateLockerUnit;

    public LocationPropertiesEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
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

    public Integer getFrequencyId() {
        return this.frequencyId;
    }

    public void setFrequencyId(Integer frequencyId) {
        this.frequencyId = frequencyId;
    }

    public String getFrequencyValue() {
        return this.frequencyValue;
    }

    public void setFrequencyValue(String frequencyValue) {
        this.frequencyValue = frequencyValue;
    }

    public Boolean getEnablePackageReminderRecipient() {
        return this.enablePackageReminderRecipient;
    }

    public void setEnablePackageReminderRecipient(Boolean enablePackageReminderRecipient) {
        this.enablePackageReminderRecipient = enablePackageReminderRecipient;
    }

    public Boolean getEnablePackageReminderAdmin() {
        return this.enablePackageReminderAdmin;
    }

    public void setEnablePackageReminderAdmin(Boolean enablePackageReminderAdmin) {
        this.enablePackageReminderAdmin = enablePackageReminderAdmin;
    }

    public Boolean getEnablePackageSentBack() {
        return this.enablePackageSentBack;
    }

    public void setEnablePackageSentBack(Boolean enablePackageSentBack) {
        this.enablePackageSentBack = enablePackageSentBack;
    }

    public Boolean getNotifySubParLevelProducts() {
        return this.notifySubParLevelProducts;
    }

    public void setNotifySubParLevelProducts(Boolean notifySubParLevelProducts) {
        this.notifySubParLevelProducts = notifySubParLevelProducts;
    }

    public String getPriSlaStartTime() {
        return this.priSlaStartTime;
    }

    public void setPriSlaStartTime(String priSlaStartTime) {
        this.priSlaStartTime = priSlaStartTime;
    }

    public String getPriSlaEndTime() {
        return this.priSlaEndTime;
    }

    public void setPriSlaEndTime(String priSlaEndTime) {
        this.priSlaEndTime = priSlaEndTime;
    }

    public String getStdSlaStartTime() {
        return this.stdSlaStartTime;
    }

    public void setStdSlaStartTime(String stdSlaStartTime) {
        this.stdSlaStartTime = stdSlaStartTime;
    }

    public String getStdSlaEndTime() {
        return this.stdSlaEndTime;
    }

    public void setStdSlaEndTime(String stdSlaEndTime) {
        this.stdSlaEndTime = stdSlaEndTime;
    }

    public Boolean getEnablePackNotifyRecipient() {
        return this.enablePackNotifyRecipient;
    }

    public void setEnablePackNotifyRecipient(Boolean enablePackNotifyRecipient) {
        this.enablePackNotifyRecipient = enablePackNotifyRecipient;
    }

    public Boolean isPackageGroup() {
        return this.isPackageGroup;
    }

    public void setIsPackageGroup(Boolean isPackageGroup) {
        this.isPackageGroup = isPackageGroup;
    }

    public Boolean isPackageGroupPasscode() {
        return this.isPackageGroupPasscode;
    }

    public void setIsPackageGroupPasscode(Boolean isPackageGroupPasscode) {
        this.isPackageGroupPasscode = isPackageGroupPasscode;
    }

    public String getPackageGroupRegex() {
        return this.packageGroupRegex;
    }

    public void setPackageGroupRegex(String packageGroupRegex) {
        this.packageGroupRegex = packageGroupRegex;
    }

    public Boolean getPackageGroupAlphanumeric() {
        return this.packageGroupAlphanumeric;
    }

    public void setPackageGroupAlphanumeric(Boolean packageGroupAlphanumeric) {
        this.packageGroupAlphanumeric = packageGroupAlphanumeric;
    }

    public Integer getPackageGroupMinLength() {
        return this.packageGroupMinLength;
    }

    public void setPackageGroupMinLength(Integer packageGroupMinLength) {
        this.packageGroupMinLength = packageGroupMinLength;
    }

    public Integer getPackageGroupMaxLength() {
        return this.packageGroupMaxLength;
    }

    public void setPackageGroupMaxLength(Integer packageGroupMaxLength) {
        this.packageGroupMaxLength = packageGroupMaxLength;
    }

    public Integer getPackageGroupRetrievalCodeLength() {
        return this.packageGroupRetrievalCodeLength;
    }

    public void setPackageGroupRetrievalCodeLength(Integer packageGroupRetrievalCodeLength) {
        this.packageGroupRetrievalCodeLength = packageGroupRetrievalCodeLength;
    }

    public Boolean getPackageGroupTrim() {
        return this.packageGroupTrim;
    }

    public void setPackageGroupTrim(Boolean packageGroupTrim) {
        this.packageGroupTrim = packageGroupTrim;
    }

    public Integer getPackageGroupTrimFront() {
        return this.packageGroupTrimFront;
    }

    public void setPackageGroupTrimFront(Integer packageGroupTrimFront) {
        this.packageGroupTrimFront = packageGroupTrimFront;
    }

    public Integer getPackageGroupTrimEnd() {
        return this.packageGroupTrimEnd;
    }

    public void setPackageGroupTrimEnd(Integer packageGroupTrimEnd) {
        this.packageGroupTrimEnd = packageGroupTrimEnd;
    }

    public Boolean getCanReceivePackagesForOtherLocations() {
        return this.canReceivePackagesForOtherLocations;
    }

    public void setCanReceivePackagesForOtherLocations(Boolean canReceivePackagesForOtherLocations) {
        this.canReceivePackagesForOtherLocations = canReceivePackagesForOtherLocations;
    }

    public Boolean getShowReviewPackagesOption() {
        return this.showReviewPackagesOption;
    }

    public void setShowReviewPackagesOption(Boolean showReviewPackagesOption) {
        this.showReviewPackagesOption = showReviewPackagesOption;
    }

    public Boolean getShowPackageDeleteOption() {
        return this.showPackageDeleteOption;
    }

    public void setShowPackageDeleteOption(Boolean showPackageDeleteOption) {
        this.showPackageDeleteOption = showPackageDeleteOption;
    }

    public Boolean getRestrictedEntry() {
        return this.restrictedEntry;
    }

    public void setRestrictedEntry(Boolean restrictedEntry) {
        this.restrictedEntry = restrictedEntry;
    }

    public Boolean getPackageArrivalMandatory() {
        return this.packageArrivalMandatory;
    }

    public void setPackageArrivalMandatory(Boolean packageArrivalMandatory) {
        this.packageArrivalMandatory = packageArrivalMandatory;
    }

    public Boolean getEnableAttemptedToDeliver() {
        return this.enableAttemptedToDeliver;
    }

    public void setEnableAttemptedToDeliver(Boolean enableAttemptedToDeliver) {
        this.enableAttemptedToDeliver = enableAttemptedToDeliver;
    }

    public Boolean getHasMailroom() {
        return this.hasMailroom;
    }

    public void setHasMailroom(Boolean hasMailroom) {
        this.hasMailroom = hasMailroom;
    }

    public Boolean isExternalScanner() {
        return this.isExternalScanner;
    }

    public void setIsExternalScanner(Boolean isExternalScanner) {
        this.isExternalScanner = isExternalScanner;
    }

    public Integer getPackagePasscodeGeneration() {
        return this.packagePasscodeGeneration;
    }

    public void setPackagePasscodeGeneration(Integer packagePasscodeGeneration) {
        this.packagePasscodeGeneration = packagePasscodeGeneration;
    }

    public Boolean getEnableOutboundRecipientNotification() {
        return this.enableOutboundRecipientNotification;
    }

    public void setEnableOutboundRecipientNotification(Boolean enableOutboundRecipientNotification) {
        this.enableOutboundRecipientNotification = enableOutboundRecipientNotification;
    }

    public Boolean getEnableOutgoingCourierUserNotification() {
        return this.enableOutgoingCourierUserNotification;
    }

    public void setEnableOutgoingCourierUserNotification(Boolean enableOutgoingCourierUserNotification) {
        this.enableOutgoingCourierUserNotification = enableOutgoingCourierUserNotification;
    }

    public Boolean getEnablePasscodeDownload() {
        return this.enablePasscodeDownload;
    }

    public void setEnablePasscodeDownload(Boolean enablePasscodeDownload) {
        this.enablePasscodeDownload = enablePasscodeDownload;
    }

    public Boolean isEnableOutboundLabelPrint() {
        return this.isEnableOutboundLabelPrint;
    }

    public void setIsEnableOutboundLabelPrint(Boolean isEnableOutboundLabelPrint) {
        this.isEnableOutboundLabelPrint = isEnableOutboundLabelPrint;
    }

    public Boolean isRequireOutboundSignature() {
        return this.isRequireOutboundSignature;
    }

    public void setIsRequireOutboundSignature(Boolean isRequireOutboundSignature) {
        this.isRequireOutboundSignature = isRequireOutboundSignature;
    }

    public Boolean isNetworkPrinter() {
        return this.isNetworkPrinter;
    }

    public void setIsNetworkPrinter(Boolean isNetworkPrinter) {
        this.isNetworkPrinter = isNetworkPrinter;
    }

    public String getPrinterIpAddress() {
        return this.printerIpAddress;
    }

    public void setPrinterIpAddress(String printerIpAddress) {
        this.printerIpAddress = printerIpAddress;
    }

    public Boolean getOnlyshowmanagesection() {
        return this.onlyshowmanagesection;
    }

    public void setOnlyshowmanagesection(Boolean onlyshowmanagesection) {
        this.onlyshowmanagesection = onlyshowmanagesection;
    }

    public Boolean getCanTalkToLockerUnit() {
        return this.canTalkToLockerUnit;
    }

    public void setCanTalkToLockerUnit(Boolean canTalkToLockerUnit) {
        this.canTalkToLockerUnit = canTalkToLockerUnit;
    }

    public Integer getPackageNumSubitemsMin() {
        return this.packageNumSubitemsMin;
    }

    public void setPackageNumSubitemsMin(Integer packageNumSubitemsMin) {
        this.packageNumSubitemsMin = packageNumSubitemsMin;
    }

    public Integer getPackageNumSubitemsMax() {
        return this.packageNumSubitemsMax;
    }

    public void setPackageNumSubitemsMax(Integer packageNumSubitemsMax) {
        this.packageNumSubitemsMax = packageNumSubitemsMax;
    }

    public Boolean getUseDmy() {
        return this.useDmy;
    }

    public void setUseDmy(Boolean useDmy) {
        this.useDmy = useDmy;
    }

    public Boolean getEcommerceFlow() {
        return this.ecommerceFlow;
    }

    public void setEcommerceFlow(Boolean ecommerceFlow) {
        this.ecommerceFlow = ecommerceFlow;
    }

    public Long getUiSkinId() {
        return this.uiSkinId;
    }

    public void setUiSkinId(Long uiSkinId) {
        this.uiSkinId = uiSkinId;
    }

    public Boolean isUserRegistrationEnabled() {
        return this.isUserRegistrationEnabled;
    }

    public void setIsUserRegistrationEnabled(Boolean isUserRegistrationEnabled) {
        this.isUserRegistrationEnabled = isUserRegistrationEnabled;
    }

    public String getUnitNoLabel() {
        return this.unitNoLabel;
    }

    public void setUnitNoLabel(String unitNoLabel) {
        this.unitNoLabel = unitNoLabel;
    }

    public Boolean getTrackPackageTransactions() {
        return this.trackPackageTransactions;
    }

    public void setTrackPackageTransactions(Boolean trackPackageTransactions) {
        this.trackPackageTransactions = trackPackageTransactions;
    }

    public Integer getPackageTransactionTimeout() {
        return this.packageTransactionTimeout;
    }

    public void setPackageTransactionTimeout(Integer packageTransactionTimeout) {
        this.packageTransactionTimeout = packageTransactionTimeout;
    }

    public Integer getClaDepositTimeout() {
        return this.claDepositTimeout;
    }

    public void setClaDepositTimeout(Integer claDepositTimeout) {
        this.claDepositTimeout = claDepositTimeout;
    }

    public Integer getClaRetrieveTimeout() {
        return this.claRetrieveTimeout;
    }

    public void setClaRetrieveTimeout(Integer claRetrieveTimeout) {
        this.claRetrieveTimeout = claRetrieveTimeout;
    }

    public Boolean getForceNotifications() {
        return this.forceNotifications;
    }

    public void setForceNotifications(Boolean forceNotifications) {
        this.forceNotifications = forceNotifications;
    }

    public Boolean getShowOrdersWithRecipient() {
        return this.showOrdersWithRecipient;
    }

    public void setShowOrdersWithRecipient(Boolean showOrdersWithRecipient) {
        this.showOrdersWithRecipient = showOrdersWithRecipient;
    }

    public Boolean getItFlow() {
        return this.itFlow;
    }

    public void setItFlow(Boolean itFlow) {
        this.itFlow = itFlow;
    }

    public String getIntegrationConfig() {
        return this.integrationConfig;
    }

    public void setIntegrationConfig(String integrationConfig) {
        this.integrationConfig = integrationConfig;
    }

    public Boolean getEnableNotificationUnsubscribe() {
        return this.enableNotificationUnsubscribe;
    }

    public void setEnableNotificationUnsubscribe(Boolean enableNotificationUnsubscribe) {
        this.enableNotificationUnsubscribe = enableNotificationUnsubscribe;
    }

    public Boolean getEnableTempAlertVoiceCall() {
        return this.enableTempAlertVoiceCall;
    }

    public void setEnableTempAlertVoiceCall(Boolean enableTempAlertVoiceCall) {
        this.enableTempAlertVoiceCall = enableTempAlertVoiceCall;
    }

    public String getVoiceCallDefaultPhone() {
        return this.voiceCallDefaultPhone;
    }

    public void setVoiceCallDefaultPhone(String voiceCallDefaultPhone) {
        this.voiceCallDefaultPhone = voiceCallDefaultPhone;
    }

    public Boolean getEnableShiftManagement() {
        return this.enableShiftManagement;
    }

    public void setEnableShiftManagement(Boolean enableShiftManagement) {
        this.enableShiftManagement = enableShiftManagement;
    }

    public Boolean getRequireSsoOnUrbanAdminLogin() {
        return this.requireSsoOnUrbanAdminLogin;
    }

    public void setRequireSsoOnUrbanAdminLogin(Boolean requireSsoOnUrbanAdminLogin) {
        this.requireSsoOnUrbanAdminLogin = requireSsoOnUrbanAdminLogin;
    }

    public String getMobileSsoBaseUrl() {
        return this.mobileSsoBaseUrl;
    }

    public void setMobileSsoBaseUrl(String mobileSsoBaseUrl) {
        this.mobileSsoBaseUrl = mobileSsoBaseUrl;
    }

    public Integer getEmailMaxReminders() {
        return this.emailMaxReminders;
    }

    public void setEmailMaxReminders(Integer emailMaxReminders) {
        this.emailMaxReminders = emailMaxReminders;
    }

    public Integer getPhoneMaxReminders() {
        return this.phoneMaxReminders;
    }

    public void setPhoneMaxReminders(Integer phoneMaxReminders) {
        this.phoneMaxReminders = phoneMaxReminders;
    }

    public Boolean getEnforceMaxIfOnlyContactInfo() {
        return this.enforceMaxIfOnlyContactInfo;
    }

    public void setEnforceMaxIfOnlyContactInfo(Boolean enforceMaxIfOnlyContactInfo) {
        this.enforceMaxIfOnlyContactInfo = enforceMaxIfOnlyContactInfo;
    }

    public Integer getShowUserPasscode() {
        return this.showUserPasscode;
    }

    public void setShowUserPasscode(Integer showUserPasscode) {
        this.showUserPasscode = showUserPasscode;
    }

    public Integer getShowWaiverBeforeRelease() {
        return this.showWaiverBeforeRelease;
    }

    public void setShowWaiverBeforeRelease(Integer showWaiverBeforeRelease) {
        this.showWaiverBeforeRelease = showWaiverBeforeRelease;
    }

    public String getWaiverUrls() {
        return this.waiverUrls;
    }

    public void setWaiverUrls(String waiverUrls) {
        this.waiverUrls = waiverUrls;
    }

    public String getWaiverText() {
        return this.waiverText;
    }

    public void setWaiverText(String waiverText) {
        this.waiverText = waiverText;
    }

    public Integer getIgnoreDuplicateOrderId() {
        return this.ignoreDuplicateOrderId;
    }

    public void setIgnoreDuplicateOrderId(Integer ignoreDuplicateOrderId) {
        this.ignoreDuplicateOrderId = ignoreDuplicateOrderId;
    }

    public String getMailroomAppUi() {
        return this.mailroomAppUi;
    }

    public void setMailroomAppUi(String mailroomAppUi) {
        this.mailroomAppUi = mailroomAppUi;
    }

    public String getMailroomScreenSaverFile() {
        return this.mailroomScreenSaverFile;
    }

    public void setMailroomScreenSaverFile(String mailroomScreenSaverFile) {
        this.mailroomScreenSaverFile = mailroomScreenSaverFile;
    }

    public String getMailroomScreenSaverMode() {
        return this.mailroomScreenSaverMode;
    }

    public void setMailroomScreenSaverMode(String mailroomScreenSaverMode) {
        this.mailroomScreenSaverMode = mailroomScreenSaverMode;
    }

    public Integer getMailroomScreenSaverAnimationDuration() {
        return this.mailroomScreenSaverAnimationDuration;
    }

    public void setMailroomScreenSaverAnimationDuration(Integer mailroomScreenSaverAnimationDuration) {
        this.mailroomScreenSaverAnimationDuration = mailroomScreenSaverAnimationDuration;
    }

    public Integer getMailroomScreenSaverItemCount() {
        return this.mailroomScreenSaverItemCount;
    }

    public void setMailroomScreenSaverItemCount(Integer mailroomScreenSaverItemCount) {
        this.mailroomScreenSaverItemCount = mailroomScreenSaverItemCount;
    }

    public Integer getShowNotificationsInPackageDetails() {
        return this.showNotificationsInPackageDetails;
    }

    public void setShowNotificationsInPackageDetails(Integer showNotificationsInPackageDetails) {
        this.showNotificationsInPackageDetails = showNotificationsInPackageDetails;
    }

    public Integer getAllowComplexCourierCodes() {
        return this.allowComplexCourierCodes;
    }

    public void setAllowComplexCourierCodes(Integer allowComplexCourierCodes) {
        this.allowComplexCourierCodes = allowComplexCourierCodes;
    }

    public Integer getEnableExpiredReminderRecipient() {
        return this.enableExpiredReminderRecipient;
    }

    public void setEnableExpiredReminderRecipient(Integer enableExpiredReminderRecipient) {
        this.enableExpiredReminderRecipient = enableExpiredReminderRecipient;
    }

    public Integer getPackageGroupValidateLockerUnit() {
        return this.packageGroupValidateLockerUnit;
    }

    public void setPackageGroupValidateLockerUnit(Integer packageGroupValidateLockerUnit) {
        this.packageGroupValidateLockerUnit = packageGroupValidateLockerUnit;
    }

}
