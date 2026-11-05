package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "locker_device_address_info_settings")
public class LockerDeviceAddressInfoSettingsEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "locker_device_address_id", nullable = false)
    private Long lockerDeviceAddressId;

    @Column(name = "locker_device_info_settings_id", nullable = false)
    private Long lockerDeviceInfoSettingsId;

    @Column(name = "value", nullable = false, length = 64)
    private String value;

    @Column(name = "created_at")
    private Timestamp createdAt;

    @Column(name = "last_modified_at")
    private Timestamp lastModifiedAt;

    @Column(name = "created_by_user_id", nullable = false)
    private Long createdByUserId;

    @Column(name = "last_modified_by_user_id", nullable = false)
    private Long lastModifiedByUserId;

    public LockerDeviceAddressInfoSettingsEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getLockerDeviceAddressId() {
        return this.lockerDeviceAddressId;
    }

    public void setLockerDeviceAddressId(Long lockerDeviceAddressId) {
        this.lockerDeviceAddressId = lockerDeviceAddressId;
    }

    public Long getLockerDeviceInfoSettingsId() {
        return this.lockerDeviceInfoSettingsId;
    }

    public void setLockerDeviceInfoSettingsId(Long lockerDeviceInfoSettingsId) {
        this.lockerDeviceInfoSettingsId = lockerDeviceInfoSettingsId;
    }

    public String getValue() {
        return this.value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public Timestamp getCreatedAt() {
        return this.createdAt;
    }

    public void setCreatedAt(Timestamp createdAt) {
        this.createdAt = createdAt;
    }

    public Timestamp getLastModifiedAt() {
        return this.lastModifiedAt;
    }

    public void setLastModifiedAt(Timestamp lastModifiedAt) {
        this.lastModifiedAt = lastModifiedAt;
    }

    public Long getCreatedByUserId() {
        return this.createdByUserId;
    }

    public void setCreatedByUserId(Long createdByUserId) {
        this.createdByUserId = createdByUserId;
    }

    public Long getLastModifiedByUserId() {
        return this.lastModifiedByUserId;
    }

    public void setLastModifiedByUserId(Long lastModifiedByUserId) {
        this.lastModifiedByUserId = lastModifiedByUserId;
    }

}
