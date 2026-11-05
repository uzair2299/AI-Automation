package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "LOCKER_UNIT")
public class LockerUnitEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "NAME", length = 255)
    private String name;

    @Column(name = "INACTIVE")
    private Boolean inactive;

    @Column(name = "BUILDING_ID")
    private Long buildingId;

    @Column(name = "CUSTOMER_ID", nullable = false)
    private Long customerId;

    @Column(name = "LAST_MODIFIED_TIME")
    private Timestamp lastModifiedTime;

    @Column(name = "ACCOUNT_ID")
    private Long accountId;

    @Column(name = "BLUETOOTH_MAC_ADDRESS", length = 25)
    private String bluetoothMacAddress;

    @Column(name = "ip_address", length = 130)
    private String ipAddress;

    @Column(name = "port_number")
    private Integer portNumber;

    @Column(name = "MAGIC_BOX_AVAILABLE", nullable = false)
    private Boolean magicBoxAvailable;

    @Column(name = "STATUS_CODE", length = 64)
    private String statusCode;

    @Column(name = "BTN_TENANT_LABEL", length = 128)
    private String btnTenantLabel;

    @Column(name = "BTN_COURIER_LABEL", length = 128)
    private String btnCourierLabel;

    @Column(name = "UPDATED_BY")
    private Long updatedBy;

    @Column(name = "UUID", length = 36)
    private String uuid;

    public LockerUnitEntity() {}

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

    public Long getBuildingId() {
        return this.buildingId;
    }

    public void setBuildingId(Long buildingId) {
        this.buildingId = buildingId;
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

    public Long getAccountId() {
        return this.accountId;
    }

    public void setAccountId(Long accountId) {
        this.accountId = accountId;
    }

    public String getBluetoothMacAddress() {
        return this.bluetoothMacAddress;
    }

    public void setBluetoothMacAddress(String bluetoothMacAddress) {
        this.bluetoothMacAddress = bluetoothMacAddress;
    }

    public String getIpAddress() {
        return this.ipAddress;
    }

    public void setIpAddress(String ipAddress) {
        this.ipAddress = ipAddress;
    }

    public Integer getPortNumber() {
        return this.portNumber;
    }

    public void setPortNumber(Integer portNumber) {
        this.portNumber = portNumber;
    }

    public Boolean getMagicBoxAvailable() {
        return this.magicBoxAvailable;
    }

    public void setMagicBoxAvailable(Boolean magicBoxAvailable) {
        this.magicBoxAvailable = magicBoxAvailable;
    }

    public String getStatusCode() {
        return this.statusCode;
    }

    public void setStatusCode(String statusCode) {
        this.statusCode = statusCode;
    }

    public String getBtnTenantLabel() {
        return this.btnTenantLabel;
    }

    public void setBtnTenantLabel(String btnTenantLabel) {
        this.btnTenantLabel = btnTenantLabel;
    }

    public String getBtnCourierLabel() {
        return this.btnCourierLabel;
    }

    public void setBtnCourierLabel(String btnCourierLabel) {
        this.btnCourierLabel = btnCourierLabel;
    }

    public Long getUpdatedBy() {
        return this.updatedBy;
    }

    public void setUpdatedBy(Long updatedBy) {
        this.updatedBy = updatedBy;
    }

    public String getUuid() {
        return this.uuid;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }

}
