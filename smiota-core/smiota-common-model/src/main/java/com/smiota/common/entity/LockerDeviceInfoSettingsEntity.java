package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "locker_device_info_settings")
public class LockerDeviceInfoSettingsEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "locker_device_info_id", nullable = false)
    private Long lockerDeviceInfoId;

    @Column(name = "locker_device_settings_id", nullable = false)
    private Long lockerDeviceSettingsId;

    @Column(name = "default_value", nullable = false, length = 64)
    private String defaultValue;

    @Column(name = "created_at")
    private Timestamp createdAt;

    @Column(name = "last_modified_at")
    private Timestamp lastModifiedAt;

    @Column(name = "created_by_user_id", nullable = false)
    private Long createdByUserId;

    @Column(name = "last_modified_by_user_id", nullable = false)
    private Long lastModifiedByUserId;

    public LockerDeviceInfoSettingsEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getLockerDeviceInfoId() {
        return this.lockerDeviceInfoId;
    }

    public void setLockerDeviceInfoId(Long lockerDeviceInfoId) {
        this.lockerDeviceInfoId = lockerDeviceInfoId;
    }

    public Long getLockerDeviceSettingsId() {
        return this.lockerDeviceSettingsId;
    }

    public void setLockerDeviceSettingsId(Long lockerDeviceSettingsId) {
        this.lockerDeviceSettingsId = lockerDeviceSettingsId;
    }

    public String getDefaultValue() {
        return this.defaultValue;
    }

    public void setDefaultValue(String defaultValue) {
        this.defaultValue = defaultValue;
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
