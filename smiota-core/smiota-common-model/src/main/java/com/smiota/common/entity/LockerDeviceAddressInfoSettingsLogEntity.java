package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "locker_device_address_info_settings_log")
public class LockerDeviceAddressInfoSettingsLogEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "locker_device_address_info_settings_id", nullable = false)
    private Long lockerDeviceAddressInfoSettingsId;

    @Column(name = "value", nullable = false, length = 64)
    private String value;

    @Column(name = "created_at")
    private Timestamp createdAt;

    @Column(name = "created_by_user_id", nullable = false)
    private Long createdByUserId;

    public LockerDeviceAddressInfoSettingsLogEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getLockerDeviceAddressInfoSettingsId() {
        return this.lockerDeviceAddressInfoSettingsId;
    }

    public void setLockerDeviceAddressInfoSettingsId(Long lockerDeviceAddressInfoSettingsId) {
        this.lockerDeviceAddressInfoSettingsId = lockerDeviceAddressInfoSettingsId;
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

    public Long getCreatedByUserId() {
        return this.createdByUserId;
    }

    public void setCreatedByUserId(Long createdByUserId) {
        this.createdByUserId = createdByUserId;
    }

}
