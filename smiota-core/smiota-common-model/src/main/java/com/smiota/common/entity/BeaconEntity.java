package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "BEACON")
public class BeaconEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "GLOBAL_ID")
    private Long globalId;

    @Column(name = "MINOR_ID")
    private Integer minorId;

    @Column(name = "LOCKER_UNIT_ID")
    private Long lockerUnitId;

    @Column(name = "BUILDING_ID")
    private Long buildingId;

    @Column(name = "LOCATION_ID")
    private Long locationId;

    @Column(name = "CUSTOMER_ID")
    private Long customerId;

    @Column(name = "UUID", length = 36)
    private String uuid;

    public BeaconEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getGlobalId() {
        return this.globalId;
    }

    public void setGlobalId(Long globalId) {
        this.globalId = globalId;
    }

    public Integer getMinorId() {
        return this.minorId;
    }

    public void setMinorId(Integer minorId) {
        this.minorId = minorId;
    }

    public Long getLockerUnitId() {
        return this.lockerUnitId;
    }

    public void setLockerUnitId(Long lockerUnitId) {
        this.lockerUnitId = lockerUnitId;
    }

    public Long getBuildingId() {
        return this.buildingId;
    }

    public void setBuildingId(Long buildingId) {
        this.buildingId = buildingId;
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

    public String getUuid() {
        return this.uuid;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }

}
