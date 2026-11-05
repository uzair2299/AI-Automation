package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "locker_device_address")
public class LockerDeviceAddressEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "name", nullable = false, length = 255)
    private String name;

    @Column(name = "locker_unit_id", nullable = false)
    private Long lockerUnitId;

    @Column(name = "locker_device_info_id", nullable = false)
    private Long lockerDeviceInfoId;

    @Column(name = "address", nullable = false)
    private Long address;

    @Column(name = "updated_by")
    private Long updatedBy;

    @Column(name = "inactive")
    private Boolean inactive;

    @Column(name = "modified_time", nullable = false)
    private Timestamp modifiedTime;

    @Column(name = "baud_rate")
    private Integer baudRate;

    @Column(name = "status_code", length = 64)
    private String statusCode;

    @Column(name = "temperature_unit_id")
    private Integer temperatureUnitId;

    public LockerDeviceAddressEntity() {}

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

    public Long getLockerUnitId() {
        return this.lockerUnitId;
    }

    public void setLockerUnitId(Long lockerUnitId) {
        this.lockerUnitId = lockerUnitId;
    }

    public Long getLockerDeviceInfoId() {
        return this.lockerDeviceInfoId;
    }

    public void setLockerDeviceInfoId(Long lockerDeviceInfoId) {
        this.lockerDeviceInfoId = lockerDeviceInfoId;
    }

    public Long getAddress() {
        return this.address;
    }

    public void setAddress(Long address) {
        this.address = address;
    }

    public Long getUpdatedBy() {
        return this.updatedBy;
    }

    public void setUpdatedBy(Long updatedBy) {
        this.updatedBy = updatedBy;
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

    public Integer getBaudRate() {
        return this.baudRate;
    }

    public void setBaudRate(Integer baudRate) {
        this.baudRate = baudRate;
    }

    public String getStatusCode() {
        return this.statusCode;
    }

    public void setStatusCode(String statusCode) {
        this.statusCode = statusCode;
    }

    public Integer getTemperatureUnitId() {
        return this.temperatureUnitId;
    }

    public void setTemperatureUnitId(Integer temperatureUnitId) {
        this.temperatureUnitId = temperatureUnitId;
    }

}
