package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "satellite_locker_unit")
public class SatelliteLockerUnitEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "locker_unit_id")
    private Long lockerUnitId;

    @Column(name = "satellite_locker_unit_id")
    private Long satelliteLockerUnitId;

    public SatelliteLockerUnitEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getLockerUnitId() {
        return this.lockerUnitId;
    }

    public void setLockerUnitId(Long lockerUnitId) {
        this.lockerUnitId = lockerUnitId;
    }

    public Long getSatelliteLockerUnitId() {
        return this.satelliteLockerUnitId;
    }

    public void setSatelliteLockerUnitId(Long satelliteLockerUnitId) {
        this.satelliteLockerUnitId = satelliteLockerUnitId;
    }

}
