package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "LOCKER")
public class LockerEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "INACTIVE")
    private Boolean inactive;

    @Column(name = "SIZE")
    private Integer size;

    @Column(name = "RELAY_ID")
    private Integer relayId;

    @Column(name = "note", length = 1000)
    private String note;

    @Column(name = "IS_GATE_OPEN")
    private Boolean isGateOpen;

    @Column(name = "IS_IN_ERROR_STATE")
    private Boolean isInErrorState;

    @Column(name = "ERROR_MESSAGE", length = 1000)
    private String errorMessage;

    @Column(name = "CUSTOMER_ID", nullable = false)
    private Long customerId;

    @Column(name = "NAME", length = 255)
    private String name;

    @Column(name = "TYPE")
    private Integer type;

    @Column(name = "UNIT_CONTROLLER_ID")
    private Long unitControllerId;

    @Column(name = "STATUS_CODE", length = 64)
    private String statusCode;

    @Column(name = "do_not_detect_presence")
    private Boolean doNotDetectPresence;

    @Column(name = "ADA_COMPLIANT")
    private Boolean adaCompliant;

    @Column(name = "external_id", length = 255)
    private String externalId;

    @Column(name = "LAST_MODIFIED_TIME")
    private Timestamp lastModifiedTime;

    @Column(name = "USER_ID")
    private Long userId;

    @Column(name = "locker_device_address_id")
    private Long lockerDeviceAddressId;

    @Column(name = "UUID", length = 36)
    private String uuid;

    public LockerEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
    }

    public Integer getSize() {
        return this.size;
    }

    public void setSize(Integer size) {
        this.size = size;
    }

    public Integer getRelayId() {
        return this.relayId;
    }

    public void setRelayId(Integer relayId) {
        this.relayId = relayId;
    }

    public String getNote() {
        return this.note;
    }

    public void setNote(String note) {
        this.note = note;
    }

    public Boolean isGateOpen() {
        return this.isGateOpen;
    }

    public void setIsGateOpen(Boolean isGateOpen) {
        this.isGateOpen = isGateOpen;
    }

    public Boolean isInErrorState() {
        return this.isInErrorState;
    }

    public void setIsInErrorState(Boolean isInErrorState) {
        this.isInErrorState = isInErrorState;
    }

    public String getErrorMessage() {
        return this.errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    public String getName() {
        return this.name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getType() {
        return this.type;
    }

    public void setType(Integer type) {
        this.type = type;
    }

    public Long getUnitControllerId() {
        return this.unitControllerId;
    }

    public void setUnitControllerId(Long unitControllerId) {
        this.unitControllerId = unitControllerId;
    }

    public String getStatusCode() {
        return this.statusCode;
    }

    public void setStatusCode(String statusCode) {
        this.statusCode = statusCode;
    }

    public Boolean getDoNotDetectPresence() {
        return this.doNotDetectPresence;
    }

    public void setDoNotDetectPresence(Boolean doNotDetectPresence) {
        this.doNotDetectPresence = doNotDetectPresence;
    }

    public Boolean getAdaCompliant() {
        return this.adaCompliant;
    }

    public void setAdaCompliant(Boolean adaCompliant) {
        this.adaCompliant = adaCompliant;
    }

    public String getExternalId() {
        return this.externalId;
    }

    public void setExternalId(String externalId) {
        this.externalId = externalId;
    }

    public Timestamp getLastModifiedTime() {
        return this.lastModifiedTime;
    }

    public void setLastModifiedTime(Timestamp lastModifiedTime) {
        this.lastModifiedTime = lastModifiedTime;
    }

    public Long getUserId() {
        return this.userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public Long getLockerDeviceAddressId() {
        return this.lockerDeviceAddressId;
    }

    public void setLockerDeviceAddressId(Long lockerDeviceAddressId) {
        this.lockerDeviceAddressId = lockerDeviceAddressId;
    }

    public String getUuid() {
        return this.uuid;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }

}
