package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "package_group_status_log")
public class PackageGroupStatusLogEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "package_group_id", nullable = false)
    private Long packageGroupId;

    @Column(name = "package_group_status_id", nullable = false)
    private Long packageGroupStatusId;

    @Column(name = "created_time", nullable = false)
    private Timestamp createdTime;

    @Column(name = "created_by_user_id", nullable = false)
    private Long createdByUserId;

    @Column(name = "package_status_log_id")
    private Long packageStatusLogId;

    @Column(name = "uuid", nullable = false, length = 36)
    private String uuid;

    @Column(name = "current_building_id")
    private Long currentBuildingId;

    @Column(name = "status_change_time")
    private Timestamp statusChangeTime;

    public PackageGroupStatusLogEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getPackageGroupId() {
        return this.packageGroupId;
    }

    public void setPackageGroupId(Long packageGroupId) {
        this.packageGroupId = packageGroupId;
    }

    public Long getPackageGroupStatusId() {
        return this.packageGroupStatusId;
    }

    public void setPackageGroupStatusId(Long packageGroupStatusId) {
        this.packageGroupStatusId = packageGroupStatusId;
    }

    public Timestamp getCreatedTime() {
        return this.createdTime;
    }

    public void setCreatedTime(Timestamp createdTime) {
        this.createdTime = createdTime;
    }

    public Long getCreatedByUserId() {
        return this.createdByUserId;
    }

    public void setCreatedByUserId(Long createdByUserId) {
        this.createdByUserId = createdByUserId;
    }

    public Long getPackageStatusLogId() {
        return this.packageStatusLogId;
    }

    public void setPackageStatusLogId(Long packageStatusLogId) {
        this.packageStatusLogId = packageStatusLogId;
    }

    public String getUuid() {
        return this.uuid;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }

    public Long getCurrentBuildingId() {
        return this.currentBuildingId;
    }

    public void setCurrentBuildingId(Long currentBuildingId) {
        this.currentBuildingId = currentBuildingId;
    }

    public Timestamp getStatusChangeTime() {
        return this.statusChangeTime;
    }

    public void setStatusChangeTime(Timestamp statusChangeTime) {
        this.statusChangeTime = statusChangeTime;
    }

}
