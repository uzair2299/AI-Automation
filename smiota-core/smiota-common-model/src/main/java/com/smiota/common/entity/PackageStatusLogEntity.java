package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "PACKAGE_STATUS_LOG")
public class PackageStatusLogEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "PACKAGE_ID", nullable = false)
    private Long packageId;

    @Column(name = "PACKAGE_STATUS_ID")
    private Integer packageStatusId;

    @Column(name = "TRANSACTION_RECORDED_TIME")
    private Timestamp transactionRecordedTime;

    @Column(name = "UPDATED_BY_USER_ID", nullable = false)
    private Long updatedByUserId;

    @Column(name = "CURRENT_BUILDING")
    private Long currentBuilding;

    @Column(name = "DESTINATION_BUILDING")
    private Long destinationBuilding;

    @Column(name = "STATUS_CHANGE_TIME")
    private Timestamp statusChangeTime;

    public PackageStatusLogEntity() {}

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

    public Integer getPackageStatusId() {
        return this.packageStatusId;
    }

    public void setPackageStatusId(Integer packageStatusId) {
        this.packageStatusId = packageStatusId;
    }

    public Timestamp getTransactionRecordedTime() {
        return this.transactionRecordedTime;
    }

    public void setTransactionRecordedTime(Timestamp transactionRecordedTime) {
        this.transactionRecordedTime = transactionRecordedTime;
    }

    public Long getUpdatedByUserId() {
        return this.updatedByUserId;
    }

    public void setUpdatedByUserId(Long updatedByUserId) {
        this.updatedByUserId = updatedByUserId;
    }

    public Long getCurrentBuilding() {
        return this.currentBuilding;
    }

    public void setCurrentBuilding(Long currentBuilding) {
        this.currentBuilding = currentBuilding;
    }

    public Long getDestinationBuilding() {
        return this.destinationBuilding;
    }

    public void setDestinationBuilding(Long destinationBuilding) {
        this.destinationBuilding = destinationBuilding;
    }

    public Timestamp getStatusChangeTime() {
        return this.statusChangeTime;
    }

    public void setStatusChangeTime(Timestamp statusChangeTime) {
        this.statusChangeTime = statusChangeTime;
    }

}
