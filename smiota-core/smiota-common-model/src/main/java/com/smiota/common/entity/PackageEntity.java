package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.math.BigDecimal;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "PACKAGE")
public class PackageEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "UUID", length = 36)
    private String uuid;

    @Column(name = "RECIPIENT_ID")
    private Long recipientId;

    @Column(name = "IS_RECIPIENT_TENANT")
    private Boolean isRecipientTenant;

    @Column(name = "RECEIVED_BY_ID")
    private Long receivedById;

    @Column(name = "LABEL_OCR", length = 1000)
    private String labelOcr;

    @Column(name = "LABEL_PHOTO")
    private byte[] labelPhoto;

    @Column(name = "PASSCODE", length = 100)
    private String passcode;

    @Column(name = "NOTES", length = 1000)
    private String notes;

    @Column(name = "COURIER", length = 1000)
    private String courier;

    @Column(name = "tracking_number", length = 750)
    private String trackingNumber;

    @Column(name = "SENDER_INFO", length = 1000)
    private String senderInfo;

    @Column(name = "TYPE")
    private Integer type;

    @Column(name = "CUSTOMER_ID")
    private Long customerId;

    @Column(name = "LOCATION_ID")
    private Long locationId;

    @Column(name = "STATUS")
    private Integer status;

    @Column(name = "RECEIVED_TIME")
    private Timestamp receivedTime;

    @Column(name = "LAST_MODIFIED_TIME")
    private Timestamp lastModifiedTime;

    @Column(name = "received_at_building_id")
    private Long receivedAtBuildingId;

    @Column(name = "LOCKER_ID")
    private Long lockerId;

    @Column(name = "IS_OUTBOUND")
    private Boolean isOutbound;

    @Column(name = "COURIER_ID")
    private Long courierId;

    @Column(name = "intended_for_building_id")
    private Long intendedForBuildingId;

    @Column(name = "currently_at_building_id")
    private Long currentlyAtBuildingId;

    @Column(name = "didnt_fit")
    private Boolean didntFit;

    @Column(name = "label_pic")
    private byte[] labelPic;

    @Column(name = "dimension_1", precision = 5, scale = 2)
    private BigDecimal dimension1;

    @Column(name = "dimension_2", precision = 5, scale = 2)
    private BigDecimal dimension2;

    @Column(name = "dimension_3", precision = 5, scale = 2)
    private BigDecimal dimension3;

    @Column(name = "deposited_by_user_id")
    private Long depositedByUserId;

    @Column(name = "IS_PRIORITY_MAIL")
    private Boolean isPriorityMail;

    @Column(name = "SENDER_ID")
    private Long senderId;

    @Column(name = "OCR_TEXT")
    private String ocrText;

    @Column(name = "EXTERNAL_ID", length = 255)
    private String externalId;

    @Column(name = "EXPIRATION_TIME")
    private Timestamp expirationTime;

    @Column(name = "is_at_destination", nullable = false)
    private Boolean isAtDestination;

    @Column(name = "is_deleted", nullable = false)
    private Boolean isDeleted;

    @Column(name = "has_label_pic")
    private Boolean hasLabelPic;

    @Column(name = "tenant_id")
    private Long tenantId;

    @Column(name = "status_change_time")
    private Timestamp statusChangeTime;

    public PackageEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getUuid() {
        return this.uuid;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }

    public Long getRecipientId() {
        return this.recipientId;
    }

    public void setRecipientId(Long recipientId) {
        this.recipientId = recipientId;
    }

    public Boolean isRecipientTenant() {
        return this.isRecipientTenant;
    }

    public void setIsRecipientTenant(Boolean isRecipientTenant) {
        this.isRecipientTenant = isRecipientTenant;
    }

    public Long getReceivedById() {
        return this.receivedById;
    }

    public void setReceivedById(Long receivedById) {
        this.receivedById = receivedById;
    }

    public String getLabelOcr() {
        return this.labelOcr;
    }

    public void setLabelOcr(String labelOcr) {
        this.labelOcr = labelOcr;
    }

    public byte[] getLabelPhoto() {
        return this.labelPhoto;
    }

    public void setLabelPhoto(byte[] labelPhoto) {
        this.labelPhoto = labelPhoto;
    }

    public String getPasscode() {
        return this.passcode;
    }

    public void setPasscode(String passcode) {
        this.passcode = passcode;
    }

    public String getNotes() {
        return this.notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }

    public String getCourier() {
        return this.courier;
    }

    public void setCourier(String courier) {
        this.courier = courier;
    }

    public String getTrackingNumber() {
        return this.trackingNumber;
    }

    public void setTrackingNumber(String trackingNumber) {
        this.trackingNumber = trackingNumber;
    }

    public String getSenderInfo() {
        return this.senderInfo;
    }

    public void setSenderInfo(String senderInfo) {
        this.senderInfo = senderInfo;
    }

    public Integer getType() {
        return this.type;
    }

    public void setType(Integer type) {
        this.type = type;
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

    public Integer getStatus() {
        return this.status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public Timestamp getReceivedTime() {
        return this.receivedTime;
    }

    public void setReceivedTime(Timestamp receivedTime) {
        this.receivedTime = receivedTime;
    }

    public Timestamp getLastModifiedTime() {
        return this.lastModifiedTime;
    }

    public void setLastModifiedTime(Timestamp lastModifiedTime) {
        this.lastModifiedTime = lastModifiedTime;
    }

    public Long getReceivedAtBuildingId() {
        return this.receivedAtBuildingId;
    }

    public void setReceivedAtBuildingId(Long receivedAtBuildingId) {
        this.receivedAtBuildingId = receivedAtBuildingId;
    }

    public Long getLockerId() {
        return this.lockerId;
    }

    public void setLockerId(Long lockerId) {
        this.lockerId = lockerId;
    }

    public Boolean isOutbound() {
        return this.isOutbound;
    }

    public void setIsOutbound(Boolean isOutbound) {
        this.isOutbound = isOutbound;
    }

    public Long getCourierId() {
        return this.courierId;
    }

    public void setCourierId(Long courierId) {
        this.courierId = courierId;
    }

    public Long getIntendedForBuildingId() {
        return this.intendedForBuildingId;
    }

    public void setIntendedForBuildingId(Long intendedForBuildingId) {
        this.intendedForBuildingId = intendedForBuildingId;
    }

    public Long getCurrentlyAtBuildingId() {
        return this.currentlyAtBuildingId;
    }

    public void setCurrentlyAtBuildingId(Long currentlyAtBuildingId) {
        this.currentlyAtBuildingId = currentlyAtBuildingId;
    }

    public Boolean getDidntFit() {
        return this.didntFit;
    }

    public void setDidntFit(Boolean didntFit) {
        this.didntFit = didntFit;
    }

    public byte[] getLabelPic() {
        return this.labelPic;
    }

    public void setLabelPic(byte[] labelPic) {
        this.labelPic = labelPic;
    }

    public BigDecimal getDimension1() {
        return this.dimension1;
    }

    public void setDimension1(BigDecimal dimension1) {
        this.dimension1 = dimension1;
    }

    public BigDecimal getDimension2() {
        return this.dimension2;
    }

    public void setDimension2(BigDecimal dimension2) {
        this.dimension2 = dimension2;
    }

    public BigDecimal getDimension3() {
        return this.dimension3;
    }

    public void setDimension3(BigDecimal dimension3) {
        this.dimension3 = dimension3;
    }

    public Long getDepositedByUserId() {
        return this.depositedByUserId;
    }

    public void setDepositedByUserId(Long depositedByUserId) {
        this.depositedByUserId = depositedByUserId;
    }

    public Boolean isPriorityMail() {
        return this.isPriorityMail;
    }

    public void setIsPriorityMail(Boolean isPriorityMail) {
        this.isPriorityMail = isPriorityMail;
    }

    public Long getSenderId() {
        return this.senderId;
    }

    public void setSenderId(Long senderId) {
        this.senderId = senderId;
    }

    public String getOcrText() {
        return this.ocrText;
    }

    public void setOcrText(String ocrText) {
        this.ocrText = ocrText;
    }

    public String getExternalId() {
        return this.externalId;
    }

    public void setExternalId(String externalId) {
        this.externalId = externalId;
    }

    public Timestamp getExpirationTime() {
        return this.expirationTime;
    }

    public void setExpirationTime(Timestamp expirationTime) {
        this.expirationTime = expirationTime;
    }

    public Boolean isAtDestination() {
        return this.isAtDestination;
    }

    public void setIsAtDestination(Boolean isAtDestination) {
        this.isAtDestination = isAtDestination;
    }

    public Boolean isDeleted() {
        return this.isDeleted;
    }

    public void setIsDeleted(Boolean isDeleted) {
        this.isDeleted = isDeleted;
    }

    public Boolean getHasLabelPic() {
        return this.hasLabelPic;
    }

    public void setHasLabelPic(Boolean hasLabelPic) {
        this.hasLabelPic = hasLabelPic;
    }

    public Long getTenantId() {
        return this.tenantId;
    }

    public void setTenantId(Long tenantId) {
        this.tenantId = tenantId;
    }

    public Timestamp getStatusChangeTime() {
        return this.statusChangeTime;
    }

    public void setStatusChangeTime(Timestamp statusChangeTime) {
        this.statusChangeTime = statusChangeTime;
    }

}
