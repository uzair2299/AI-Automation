package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "PACKAGE_FLOW")
public class PackageFlowEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "package_id")
    private Long packageId;

    @Column(name = "building_id")
    private Long buildingId;

    @Column(name = "locker_unit_id")
    private Long lockerUnitId;

    @Column(name = "received_at_building_time")
    private Timestamp receivedAtBuildingTime;

    @Column(name = "received_at_building_by_id")
    private Long receivedAtBuildingById;

    @Column(name = "delivered_to_building_by_id")
    private Long deliveredToBuildingById;

    public PackageFlowEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getPackageId() {
        return this.packageId;
    }

    public void setPackageId(Long packageId) {
        this.packageId = packageId;
    }

    public Long getBuildingId() {
        return this.buildingId;
    }

    public void setBuildingId(Long buildingId) {
        this.buildingId = buildingId;
    }

    public Long getLockerUnitId() {
        return this.lockerUnitId;
    }

    public void setLockerUnitId(Long lockerUnitId) {
        this.lockerUnitId = lockerUnitId;
    }

    public Timestamp getReceivedAtBuildingTime() {
        return this.receivedAtBuildingTime;
    }

    public void setReceivedAtBuildingTime(Timestamp receivedAtBuildingTime) {
        this.receivedAtBuildingTime = receivedAtBuildingTime;
    }

    public Long getReceivedAtBuildingById() {
        return this.receivedAtBuildingById;
    }

    public void setReceivedAtBuildingById(Long receivedAtBuildingById) {
        this.receivedAtBuildingById = receivedAtBuildingById;
    }

    public Long getDeliveredToBuildingById() {
        return this.deliveredToBuildingById;
    }

    public void setDeliveredToBuildingById(Long deliveredToBuildingById) {
        this.deliveredToBuildingById = deliveredToBuildingById;
    }

}
