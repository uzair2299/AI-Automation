package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.math.BigDecimal;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "locker_unit_config")
public class LockerUnitConfigEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "locker_unit_id", nullable = false)
    private Long lockerUnitId;

    @Column(name = "is_allows_out_bound_packages")
    private Boolean isAllowsOutBoundPackages;

    @Column(name = "is_enable_package_doesnt_fit_feature")
    private Boolean isEnablePackageDoesntFitFeature;

    @Column(name = "is_enable_outgoing_package_doesnt_fit")
    private Boolean isEnableOutgoingPackageDoesntFit;

    @Column(name = "is_displays_unit_numbers")
    private Boolean isDisplaysUnitNumbers;

    @Column(name = "is_courier_auth")
    private Boolean isCourierAuth;

    @Column(name = "is_recipient_confirmation")
    private Boolean isRecipientConfirmation;

    @Column(name = "is_existing_packages")
    private Boolean isExistingPackages;

    @Column(name = "is_new_packages")
    private Boolean isNewPackages;

    @Column(name = "is_pkg_info_page")
    private Boolean isPkgInfoPage;

    @Column(name = "is_voice_alerts")
    private Boolean isVoiceAlerts;

    @Column(name = "is_retrieve_all")
    private Boolean isRetrieveAll;

    @Column(name = "is_external_package_flow")
    private Boolean isExternalPackageFlow;

    @Column(name = "deposit_timeout_seconds")
    private Long depositTimeoutSeconds;

    @Column(name = "retrieve_timeout_seconds")
    private Long retrieveTimeoutSeconds;

    @Column(name = "item_name", length = 255)
    private String itemName;

    @Column(name = "item_name_plural", length = 255)
    private String itemNamePlural;

    @Column(name = "returns_name", length = 255)
    private String returnsName;

    @Column(name = "app_mode", length = 255)
    private String appMode;

    @Column(name = "app_ui", length = 255)
    private String appUi;

    @Column(name = "door_open_audio_mode", length = 255)
    private String doorOpenAudioMode;

    @Column(name = "screen_saver_file", length = 255)
    private String screenSaverFile;

    @Column(name = "screen_saver_mode", length = 128)
    private String screenSaverMode;

    @Column(name = "created_by", nullable = false)
    private Long createdBy;

    @Column(name = "updated_by", nullable = false)
    private Long updatedBy;

    @Column(name = "created_time", nullable = false)
    private Timestamp createdTime;

    @Column(name = "updated_time", nullable = false)
    private Timestamp updatedTime;

    @Column(name = "lockers_per_user")
    private Integer lockersPerUser;

    @Column(name = "packages_per_locker")
    private Integer packagesPerLocker;

    @Column(name = "user_external_id_select_from_list_users")
    private Boolean userExternalIdSelectFromListUsers;

    @Column(name = "authenticate_recipient_flow")
    private Boolean authenticateRecipientFlow;

    @Column(name = "courier_can_retrieve_expired_packages")
    private Boolean courierCanRetrieveExpiredPackages;

    @Column(name = "temperature_interval")
    private Integer temperatureInterval;

    @Column(name = "latitude", precision = 8, scale = 6)
    private BigDecimal latitude;

    @Column(name = "longitude", precision = 9, scale = 6)
    private BigDecimal longitude;

    @Column(name = "track_package_transactions")
    private Boolean trackPackageTransactions;

    @Column(name = "existing_package_group")
    private Boolean existingPackageGroup;

    @Column(name = "private_recipient_list")
    private Boolean privateRecipientList;

    @Column(name = "hide_duplicate_users")
    private Boolean hideDuplicateUsers;

    @Column(name = "enable_light_settings")
    private Boolean enableLightSettings;

    @Column(name = "light_on_time", length = 8)
    private String lightOnTime;

    @Column(name = "light_off_time", length = 8)
    private String lightOffTime;

    @Column(name = "xxl_multi_package_max")
    private Integer xxlMultiPackageMax;

    @Column(name = "retrieval_confirmation")
    private Boolean retrievalConfirmation;

    @Column(name = "backloading")
    private Boolean backloading;

    @Column(name = "satellite")
    private Boolean satellite;

    @Column(name = "recipient_email_cell_search")
    private Boolean recipientEmailCellSearch;

    @Column(name = "enable_setting_scanner")
    private Boolean enableSettingScanner;

    @Column(name = "did_you_deposit")
    private Integer didYouDeposit;

    @Column(name = "screen_saver_animation_duration")
    private Integer screenSaverAnimationDuration;

    @Column(name = "screen_saver_item_count")
    private Integer screenSaverItemCount;

    @Column(name = "enable_remote_logging")
    private Boolean enableRemoteLogging;

    @Column(name = "skip_outbound_scan")
    private Boolean skipOutboundScan;

    @Column(name = "allow_tablet_developer_settings")
    private Boolean allowTabletDeveloperSettings;

    @Column(name = "show_complete_unit_no")
    private Integer showCompleteUnitNo;

    @Column(name = "enter_name_before_release")
    private Integer enterNameBeforeRelease;

    @Column(name = "recipient_search_only_name_and_unit")
    private Integer recipientSearchOnlyNameAndUnit;

    @Column(name = "disable_skip_scan")
    private Integer disableSkipScan;

    @Column(name = "enable_package_consolidation")
    private Integer enablePackageConsolidation;

    @Column(name = "enable_scan_confirmation")
    private Integer enableScanConfirmation;

    @Column(name = "enable_rfid_support")
    private Integer enableRfidSupport;

    @Column(name = "show_language_toggle")
    private Integer showLanguageToggle;

    @Column(name = "disable_locker_location_display")
    private Integer disableLockerLocationDisplay;

    @Column(name = "disable_onscreen_keyboard")
    private Integer disableOnscreenKeyboard;

    @Column(name = "hide_text_fields_on_scan_page")
    private Integer hideTextFieldsOnScanPage;

    @Column(name = "limit_to_single_deposit")
    private Integer limitToSingleDeposit;

    @Column(name = "scan_badge_text", length = 255)
    private String scanBadgeText;

    @Column(name = "scan_package_text", length = 255)
    private String scanPackageText;

    @Column(name = "scan_code_text", length = 255)
    private String scanCodeText;

    @Column(name = "show_expired_option_in_deposit")
    private Integer showExpiredOptionInDeposit;

    @Column(name = "show_custom_scan_messages")
    private Integer showCustomScanMessages;

    public LockerUnitConfigEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getLockerUnitId() {
        return this.lockerUnitId;
    }

    public void setLockerUnitId(Long lockerUnitId) {
        this.lockerUnitId = lockerUnitId;
    }

    public Boolean isAllowsOutBoundPackages() {
        return this.isAllowsOutBoundPackages;
    }

    public void setIsAllowsOutBoundPackages(Boolean isAllowsOutBoundPackages) {
        this.isAllowsOutBoundPackages = isAllowsOutBoundPackages;
    }

    public Boolean isEnablePackageDoesntFitFeature() {
        return this.isEnablePackageDoesntFitFeature;
    }

    public void setIsEnablePackageDoesntFitFeature(Boolean isEnablePackageDoesntFitFeature) {
        this.isEnablePackageDoesntFitFeature = isEnablePackageDoesntFitFeature;
    }

    public Boolean isEnableOutgoingPackageDoesntFit() {
        return this.isEnableOutgoingPackageDoesntFit;
    }

    public void setIsEnableOutgoingPackageDoesntFit(Boolean isEnableOutgoingPackageDoesntFit) {
        this.isEnableOutgoingPackageDoesntFit = isEnableOutgoingPackageDoesntFit;
    }

    public Boolean isDisplaysUnitNumbers() {
        return this.isDisplaysUnitNumbers;
    }

    public void setIsDisplaysUnitNumbers(Boolean isDisplaysUnitNumbers) {
        this.isDisplaysUnitNumbers = isDisplaysUnitNumbers;
    }

    public Boolean isCourierAuth() {
        return this.isCourierAuth;
    }

    public void setIsCourierAuth(Boolean isCourierAuth) {
        this.isCourierAuth = isCourierAuth;
    }

    public Boolean isRecipientConfirmation() {
        return this.isRecipientConfirmation;
    }

    public void setIsRecipientConfirmation(Boolean isRecipientConfirmation) {
        this.isRecipientConfirmation = isRecipientConfirmation;
    }

    public Boolean isExistingPackages() {
        return this.isExistingPackages;
    }

    public void setIsExistingPackages(Boolean isExistingPackages) {
        this.isExistingPackages = isExistingPackages;
    }

    public Boolean isNewPackages() {
        return this.isNewPackages;
    }

    public void setIsNewPackages(Boolean isNewPackages) {
        this.isNewPackages = isNewPackages;
    }

    public Boolean isPkgInfoPage() {
        return this.isPkgInfoPage;
    }

    public void setIsPkgInfoPage(Boolean isPkgInfoPage) {
        this.isPkgInfoPage = isPkgInfoPage;
    }

    public Boolean isVoiceAlerts() {
        return this.isVoiceAlerts;
    }

    public void setIsVoiceAlerts(Boolean isVoiceAlerts) {
        this.isVoiceAlerts = isVoiceAlerts;
    }

    public Boolean isRetrieveAll() {
        return this.isRetrieveAll;
    }

    public void setIsRetrieveAll(Boolean isRetrieveAll) {
        this.isRetrieveAll = isRetrieveAll;
    }

    public Boolean isExternalPackageFlow() {
        return this.isExternalPackageFlow;
    }

    public void setIsExternalPackageFlow(Boolean isExternalPackageFlow) {
        this.isExternalPackageFlow = isExternalPackageFlow;
    }

    public Long getDepositTimeoutSeconds() {
        return this.depositTimeoutSeconds;
    }

    public void setDepositTimeoutSeconds(Long depositTimeoutSeconds) {
        this.depositTimeoutSeconds = depositTimeoutSeconds;
    }

    public Long getRetrieveTimeoutSeconds() {
        return this.retrieveTimeoutSeconds;
    }

    public void setRetrieveTimeoutSeconds(Long retrieveTimeoutSeconds) {
        this.retrieveTimeoutSeconds = retrieveTimeoutSeconds;
    }

    public String getItemName() {
        return this.itemName;
    }

    public void setItemName(String itemName) {
        this.itemName = itemName;
    }

    public String getItemNamePlural() {
        return this.itemNamePlural;
    }

    public void setItemNamePlural(String itemNamePlural) {
        this.itemNamePlural = itemNamePlural;
    }

    public String getReturnsName() {
        return this.returnsName;
    }

    public void setReturnsName(String returnsName) {
        this.returnsName = returnsName;
    }

    public String getAppMode() {
        return this.appMode;
    }

    public void setAppMode(String appMode) {
        this.appMode = appMode;
    }

    public String getAppUi() {
        return this.appUi;
    }

    public void setAppUi(String appUi) {
        this.appUi = appUi;
    }

    public String getDoorOpenAudioMode() {
        return this.doorOpenAudioMode;
    }

    public void setDoorOpenAudioMode(String doorOpenAudioMode) {
        this.doorOpenAudioMode = doorOpenAudioMode;
    }

    public String getScreenSaverFile() {
        return this.screenSaverFile;
    }

    public void setScreenSaverFile(String screenSaverFile) {
        this.screenSaverFile = screenSaverFile;
    }

    public String getScreenSaverMode() {
        return this.screenSaverMode;
    }

    public void setScreenSaverMode(String screenSaverMode) {
        this.screenSaverMode = screenSaverMode;
    }

    public Long getCreatedBy() {
        return this.createdBy;
    }

    public void setCreatedBy(Long createdBy) {
        this.createdBy = createdBy;
    }

    public Long getUpdatedBy() {
        return this.updatedBy;
    }

    public void setUpdatedBy(Long updatedBy) {
        this.updatedBy = updatedBy;
    }

    public Timestamp getCreatedTime() {
        return this.createdTime;
    }

    public void setCreatedTime(Timestamp createdTime) {
        this.createdTime = createdTime;
    }

    public Timestamp getUpdatedTime() {
        return this.updatedTime;
    }

    public void setUpdatedTime(Timestamp updatedTime) {
        this.updatedTime = updatedTime;
    }

    public Integer getLockersPerUser() {
        return this.lockersPerUser;
    }

    public void setLockersPerUser(Integer lockersPerUser) {
        this.lockersPerUser = lockersPerUser;
    }

    public Integer getPackagesPerLocker() {
        return this.packagesPerLocker;
    }

    public void setPackagesPerLocker(Integer packagesPerLocker) {
        this.packagesPerLocker = packagesPerLocker;
    }

    public Boolean getUserExternalIdSelectFromListUsers() {
        return this.userExternalIdSelectFromListUsers;
    }

    public void setUserExternalIdSelectFromListUsers(Boolean userExternalIdSelectFromListUsers) {
        this.userExternalIdSelectFromListUsers = userExternalIdSelectFromListUsers;
    }

    public Boolean getAuthenticateRecipientFlow() {
        return this.authenticateRecipientFlow;
    }

    public void setAuthenticateRecipientFlow(Boolean authenticateRecipientFlow) {
        this.authenticateRecipientFlow = authenticateRecipientFlow;
    }

    public Boolean getCourierCanRetrieveExpiredPackages() {
        return this.courierCanRetrieveExpiredPackages;
    }

    public void setCourierCanRetrieveExpiredPackages(Boolean courierCanRetrieveExpiredPackages) {
        this.courierCanRetrieveExpiredPackages = courierCanRetrieveExpiredPackages;
    }

    public Integer getTemperatureInterval() {
        return this.temperatureInterval;
    }

    public void setTemperatureInterval(Integer temperatureInterval) {
        this.temperatureInterval = temperatureInterval;
    }

    public BigDecimal getLatitude() {
        return this.latitude;
    }

    public void setLatitude(BigDecimal latitude) {
        this.latitude = latitude;
    }

    public BigDecimal getLongitude() {
        return this.longitude;
    }

    public void setLongitude(BigDecimal longitude) {
        this.longitude = longitude;
    }

    public Boolean getTrackPackageTransactions() {
        return this.trackPackageTransactions;
    }

    public void setTrackPackageTransactions(Boolean trackPackageTransactions) {
        this.trackPackageTransactions = trackPackageTransactions;
    }

    public Boolean getExistingPackageGroup() {
        return this.existingPackageGroup;
    }

    public void setExistingPackageGroup(Boolean existingPackageGroup) {
        this.existingPackageGroup = existingPackageGroup;
    }

    public Boolean getPrivateRecipientList() {
        return this.privateRecipientList;
    }

    public void setPrivateRecipientList(Boolean privateRecipientList) {
        this.privateRecipientList = privateRecipientList;
    }

    public Boolean getHideDuplicateUsers() {
        return this.hideDuplicateUsers;
    }

    public void setHideDuplicateUsers(Boolean hideDuplicateUsers) {
        this.hideDuplicateUsers = hideDuplicateUsers;
    }

    public Boolean getEnableLightSettings() {
        return this.enableLightSettings;
    }

    public void setEnableLightSettings(Boolean enableLightSettings) {
        this.enableLightSettings = enableLightSettings;
    }

    public String getLightOnTime() {
        return this.lightOnTime;
    }

    public void setLightOnTime(String lightOnTime) {
        this.lightOnTime = lightOnTime;
    }

    public String getLightOffTime() {
        return this.lightOffTime;
    }

    public void setLightOffTime(String lightOffTime) {
        this.lightOffTime = lightOffTime;
    }

    public Integer getXxlMultiPackageMax() {
        return this.xxlMultiPackageMax;
    }

    public void setXxlMultiPackageMax(Integer xxlMultiPackageMax) {
        this.xxlMultiPackageMax = xxlMultiPackageMax;
    }

    public Boolean getRetrievalConfirmation() {
        return this.retrievalConfirmation;
    }

    public void setRetrievalConfirmation(Boolean retrievalConfirmation) {
        this.retrievalConfirmation = retrievalConfirmation;
    }

    public Boolean getBackloading() {
        return this.backloading;
    }

    public void setBackloading(Boolean backloading) {
        this.backloading = backloading;
    }

    public Boolean getSatellite() {
        return this.satellite;
    }

    public void setSatellite(Boolean satellite) {
        this.satellite = satellite;
    }

    public Boolean getRecipientEmailCellSearch() {
        return this.recipientEmailCellSearch;
    }

    public void setRecipientEmailCellSearch(Boolean recipientEmailCellSearch) {
        this.recipientEmailCellSearch = recipientEmailCellSearch;
    }

    public Boolean getEnableSettingScanner() {
        return this.enableSettingScanner;
    }

    public void setEnableSettingScanner(Boolean enableSettingScanner) {
        this.enableSettingScanner = enableSettingScanner;
    }

    public Integer getDidYouDeposit() {
        return this.didYouDeposit;
    }

    public void setDidYouDeposit(Integer didYouDeposit) {
        this.didYouDeposit = didYouDeposit;
    }

    public Integer getScreenSaverAnimationDuration() {
        return this.screenSaverAnimationDuration;
    }

    public void setScreenSaverAnimationDuration(Integer screenSaverAnimationDuration) {
        this.screenSaverAnimationDuration = screenSaverAnimationDuration;
    }

    public Integer getScreenSaverItemCount() {
        return this.screenSaverItemCount;
    }

    public void setScreenSaverItemCount(Integer screenSaverItemCount) {
        this.screenSaverItemCount = screenSaverItemCount;
    }

    public Boolean getEnableRemoteLogging() {
        return this.enableRemoteLogging;
    }

    public void setEnableRemoteLogging(Boolean enableRemoteLogging) {
        this.enableRemoteLogging = enableRemoteLogging;
    }

    public Boolean getSkipOutboundScan() {
        return this.skipOutboundScan;
    }

    public void setSkipOutboundScan(Boolean skipOutboundScan) {
        this.skipOutboundScan = skipOutboundScan;
    }

    public Boolean getAllowTabletDeveloperSettings() {
        return this.allowTabletDeveloperSettings;
    }

    public void setAllowTabletDeveloperSettings(Boolean allowTabletDeveloperSettings) {
        this.allowTabletDeveloperSettings = allowTabletDeveloperSettings;
    }

    public Integer getShowCompleteUnitNo() {
        return this.showCompleteUnitNo;
    }

    public void setShowCompleteUnitNo(Integer showCompleteUnitNo) {
        this.showCompleteUnitNo = showCompleteUnitNo;
    }

    public Integer getEnterNameBeforeRelease() {
        return this.enterNameBeforeRelease;
    }

    public void setEnterNameBeforeRelease(Integer enterNameBeforeRelease) {
        this.enterNameBeforeRelease = enterNameBeforeRelease;
    }

    public Integer getRecipientSearchOnlyNameAndUnit() {
        return this.recipientSearchOnlyNameAndUnit;
    }

    public void setRecipientSearchOnlyNameAndUnit(Integer recipientSearchOnlyNameAndUnit) {
        this.recipientSearchOnlyNameAndUnit = recipientSearchOnlyNameAndUnit;
    }

    public Integer getDisableSkipScan() {
        return this.disableSkipScan;
    }

    public void setDisableSkipScan(Integer disableSkipScan) {
        this.disableSkipScan = disableSkipScan;
    }

    public Integer getEnablePackageConsolidation() {
        return this.enablePackageConsolidation;
    }

    public void setEnablePackageConsolidation(Integer enablePackageConsolidation) {
        this.enablePackageConsolidation = enablePackageConsolidation;
    }

    public Integer getEnableScanConfirmation() {
        return this.enableScanConfirmation;
    }

    public void setEnableScanConfirmation(Integer enableScanConfirmation) {
        this.enableScanConfirmation = enableScanConfirmation;
    }

    public Integer getEnableRfidSupport() {
        return this.enableRfidSupport;
    }

    public void setEnableRfidSupport(Integer enableRfidSupport) {
        this.enableRfidSupport = enableRfidSupport;
    }

    public Integer getShowLanguageToggle() {
        return this.showLanguageToggle;
    }

    public void setShowLanguageToggle(Integer showLanguageToggle) {
        this.showLanguageToggle = showLanguageToggle;
    }

    public Integer getDisableLockerLocationDisplay() {
        return this.disableLockerLocationDisplay;
    }

    public void setDisableLockerLocationDisplay(Integer disableLockerLocationDisplay) {
        this.disableLockerLocationDisplay = disableLockerLocationDisplay;
    }

    public Integer getDisableOnscreenKeyboard() {
        return this.disableOnscreenKeyboard;
    }

    public void setDisableOnscreenKeyboard(Integer disableOnscreenKeyboard) {
        this.disableOnscreenKeyboard = disableOnscreenKeyboard;
    }

    public Integer getHideTextFieldsOnScanPage() {
        return this.hideTextFieldsOnScanPage;
    }

    public void setHideTextFieldsOnScanPage(Integer hideTextFieldsOnScanPage) {
        this.hideTextFieldsOnScanPage = hideTextFieldsOnScanPage;
    }

    public Integer getLimitToSingleDeposit() {
        return this.limitToSingleDeposit;
    }

    public void setLimitToSingleDeposit(Integer limitToSingleDeposit) {
        this.limitToSingleDeposit = limitToSingleDeposit;
    }

    public String getScanBadgeText() {
        return this.scanBadgeText;
    }

    public void setScanBadgeText(String scanBadgeText) {
        this.scanBadgeText = scanBadgeText;
    }

    public String getScanPackageText() {
        return this.scanPackageText;
    }

    public void setScanPackageText(String scanPackageText) {
        this.scanPackageText = scanPackageText;
    }

    public String getScanCodeText() {
        return this.scanCodeText;
    }

    public void setScanCodeText(String scanCodeText) {
        this.scanCodeText = scanCodeText;
    }

    public Integer getShowExpiredOptionInDeposit() {
        return this.showExpiredOptionInDeposit;
    }

    public void setShowExpiredOptionInDeposit(Integer showExpiredOptionInDeposit) {
        this.showExpiredOptionInDeposit = showExpiredOptionInDeposit;
    }

    public Integer getShowCustomScanMessages() {
        return this.showCustomScanMessages;
    }

    public void setShowCustomScanMessages(Integer showCustomScanMessages) {
        this.showCustomScanMessages = showCustomScanMessages;
    }

}
