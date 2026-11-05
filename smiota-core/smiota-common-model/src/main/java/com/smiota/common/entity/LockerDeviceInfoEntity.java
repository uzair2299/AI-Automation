package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "locker_device_info")
public class LockerDeviceInfoEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "model", nullable = false, length = 255)
    private String model;

    @Column(name = "description", length = 255)
    private String description;

    @Column(name = "locker_device_type_id", nullable = false)
    private Long lockerDeviceTypeId;

    @Column(name = "inactive")
    private Boolean inactive;

    @Column(name = "modified_time", nullable = false)
    private Timestamp modifiedTime;

    @Column(name = "manufacturer_id")
    private Integer manufacturerId;

    public LockerDeviceInfoEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getModel() {
        return this.model;
    }

    public void setModel(String model) {
        this.model = model;
    }

    public String getDescription() {
        return this.description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Long getLockerDeviceTypeId() {
        return this.lockerDeviceTypeId;
    }

    public void setLockerDeviceTypeId(Long lockerDeviceTypeId) {
        this.lockerDeviceTypeId = lockerDeviceTypeId;
    }

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
    }

    public Timestamp getModifiedTime() {
        return this.modifiedTime;
    }

    public void setModifiedTime(Timestamp modifiedTime) {
        this.modifiedTime = modifiedTime;
    }

    public Integer getManufacturerId() {
        return this.manufacturerId;
    }

    public void setManufacturerId(Integer manufacturerId) {
        this.manufacturerId = manufacturerId;
    }

}
