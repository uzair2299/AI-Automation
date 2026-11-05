package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.math.BigDecimal;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "event_definition")
public class EventDefinitionEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "event_id", nullable = false)
    private Integer eventId;

    @Column(name = "max_value", precision = 5, scale = 2)
    private BigDecimal maxValue;

    @Column(name = "min_value", precision = 5, scale = 2)
    private BigDecimal minValue;

    @Column(name = "eligible_time_for_event_to_generate")
    private Integer eligibleTimeForEventToGenerate;

    @Column(name = "locker_id")
    private Long lockerId;

    @Column(name = "locker_unit_controller_id")
    private Long lockerUnitControllerId;

    @Column(name = "locker_unit_id")
    private Long lockerUnitId;

    @Column(name = "location_id", nullable = false)
    private Long locationId;

    @Column(name = "customer_id", nullable = false)
    private Long customerId;

    @Column(name = "created_at")
    private Timestamp createdAt;

    @Column(name = "last_modified_at")
    private Timestamp lastModifiedAt;

    @Column(name = "created_by_user_id", nullable = false)
    private Long createdByUserId;

    @Column(name = "last_modified_by_user_id", nullable = false)
    private Long lastModifiedByUserId;

    @Column(name = "locker_device_address_id")
    private Long lockerDeviceAddressId;

    @Column(name = "locker_device_type_id")
    private Long lockerDeviceTypeId;

    @Column(name = "inactive")
    private Boolean inactive;

    public EventDefinitionEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Integer getEventId() {
        return this.eventId;
    }

    public void setEventId(Integer eventId) {
        this.eventId = eventId;
    }

    public BigDecimal getMaxValue() {
        return this.maxValue;
    }

    public void setMaxValue(BigDecimal maxValue) {
        this.maxValue = maxValue;
    }

    public BigDecimal getMinValue() {
        return this.minValue;
    }

    public void setMinValue(BigDecimal minValue) {
        this.minValue = minValue;
    }

    public Integer getEligibleTimeForEventToGenerate() {
        return this.eligibleTimeForEventToGenerate;
    }

    public void setEligibleTimeForEventToGenerate(Integer eligibleTimeForEventToGenerate) {
        this.eligibleTimeForEventToGenerate = eligibleTimeForEventToGenerate;
    }

    public Long getLockerId() {
        return this.lockerId;
    }

    public void setLockerId(Long lockerId) {
        this.lockerId = lockerId;
    }

    public Long getLockerUnitControllerId() {
        return this.lockerUnitControllerId;
    }

    public void setLockerUnitControllerId(Long lockerUnitControllerId) {
        this.lockerUnitControllerId = lockerUnitControllerId;
    }

    public Long getLockerUnitId() {
        return this.lockerUnitId;
    }

    public void setLockerUnitId(Long lockerUnitId) {
        this.lockerUnitId = lockerUnitId;
    }

    public Long getLocationId() {
        return this.locationId;
    }

    public void setLocationId(Long locationId) {
        this.locationId = locationId;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
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

    public Long getLockerDeviceAddressId() {
        return this.lockerDeviceAddressId;
    }

    public void setLockerDeviceAddressId(Long lockerDeviceAddressId) {
        this.lockerDeviceAddressId = lockerDeviceAddressId;
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

}
