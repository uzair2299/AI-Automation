package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "tag")
public class TagEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Integer id;

    @Column(name = "tag_type_id", nullable = false)
    private Integer tagTypeId;

    @Column(name = "tag_option_id", nullable = false)
    private Integer tagOptionId;

    @Column(name = "start_time", nullable = false)
    private Timestamp startTime;

    @Column(name = "end_time")
    private Timestamp endTime;

    @Column(name = "notes", length = 250)
    private String notes;

    @Column(name = "customer_id", nullable = false)
    private Long customerId;

    @Column(name = "location_id", nullable = false)
    private Long locationId;

    @Column(name = "tracking_number", length = 750)
    private String trackingNumber;

    @Column(name = "user_last_modified")
    private Long userLastModified;

    @Column(name = "sender_id")
    private Integer senderId;

    @Column(name = "inactive")
    private Boolean inactive;

    @Column(name = "recipient_id")
    private Long recipientId;

    @Column(name = "signature_waived")
    private Integer signatureWaived;

    @Column(name = "package_group_external_id", length = 255)
    private String packageGroupExternalId;

    public TagEntity() {}

    public Integer getId() {
        return this.id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getTagTypeId() {
        return this.tagTypeId;
    }

    public void setTagTypeId(Integer tagTypeId) {
        this.tagTypeId = tagTypeId;
    }

    public Integer getTagOptionId() {
        return this.tagOptionId;
    }

    public void setTagOptionId(Integer tagOptionId) {
        this.tagOptionId = tagOptionId;
    }

    public Timestamp getStartTime() {
        return this.startTime;
    }

    public void setStartTime(Timestamp startTime) {
        this.startTime = startTime;
    }

    public Timestamp getEndTime() {
        return this.endTime;
    }

    public void setEndTime(Timestamp endTime) {
        this.endTime = endTime;
    }

    public String getNotes() {
        return this.notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
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

    public String getTrackingNumber() {
        return this.trackingNumber;
    }

    public void setTrackingNumber(String trackingNumber) {
        this.trackingNumber = trackingNumber;
    }

    public Long getUserLastModified() {
        return this.userLastModified;
    }

    public void setUserLastModified(Long userLastModified) {
        this.userLastModified = userLastModified;
    }

    public Integer getSenderId() {
        return this.senderId;
    }

    public void setSenderId(Integer senderId) {
        this.senderId = senderId;
    }

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
    }

    public Long getRecipientId() {
        return this.recipientId;
    }

    public void setRecipientId(Long recipientId) {
        this.recipientId = recipientId;
    }

    public Integer getSignatureWaived() {
        return this.signatureWaived;
    }

    public void setSignatureWaived(Integer signatureWaived) {
        this.signatureWaived = signatureWaived;
    }

    public String getPackageGroupExternalId() {
        return this.packageGroupExternalId;
    }

    public void setPackageGroupExternalId(String packageGroupExternalId) {
        this.packageGroupExternalId = packageGroupExternalId;
    }

}
