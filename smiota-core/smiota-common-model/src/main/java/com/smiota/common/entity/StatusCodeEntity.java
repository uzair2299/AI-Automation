package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "STATUS_CODE")
public class StatusCodeEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Column(name = "CODE", nullable = false)
    private Integer code;

    @Column(name = "TYPE", length = 100)
    private String type;

    @Column(name = "DESCRIPTION", length = 255)
    private String description;

    @Column(name = "BIT_INDEX")
    private Integer bitIndex;

    @Column(name = "APPLIES_TO_LOCKER")
    private Boolean appliesToLocker;

    @Id
    @Column(name = "ID")
    private Integer id;

    @Column(name = "APPLIES_TO_LOCKER_DEVICE_ADDRESS")
    private Boolean appliesToLockerDeviceAddress;

    @Column(name = "USED_BY_CLIENTS")
    private Boolean usedByClients;

    public StatusCodeEntity() {}

    public Integer getCode() {
        return this.code;
    }

    public void setCode(Integer code) {
        this.code = code;
    }

    public String getType() {
        return this.type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getDescription() {
        return this.description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Integer getBitIndex() {
        return this.bitIndex;
    }

    public void setBitIndex(Integer bitIndex) {
        this.bitIndex = bitIndex;
    }

    public Boolean getAppliesToLocker() {
        return this.appliesToLocker;
    }

    public void setAppliesToLocker(Boolean appliesToLocker) {
        this.appliesToLocker = appliesToLocker;
    }

    public Integer getId() {
        return this.id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Boolean getAppliesToLockerDeviceAddress() {
        return this.appliesToLockerDeviceAddress;
    }

    public void setAppliesToLockerDeviceAddress(Boolean appliesToLockerDeviceAddress) {
        this.appliesToLockerDeviceAddress = appliesToLockerDeviceAddress;
    }

    public Boolean getUsedByClients() {
        return this.usedByClients;
    }

    public void setUsedByClients(Boolean usedByClients) {
        this.usedByClients = usedByClients;
    }

}
