package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "package_group_status_transition_log")
public class PackageGroupStatusTransitionLogEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @Column(name = "id", length = 36)
    private String id;

    @Column(name = "package_group_status_transition_id", nullable = false)
    private Long packageGroupStatusTransitionId;

    @Column(name = "package_group_status_id", nullable = false)
    private Long packageGroupStatusId;

    @Column(name = "package_group_allowed_status_id", nullable = false)
    private Long packageGroupAllowedStatusId;

    @Column(name = "inactive")
    private Boolean inactive;

    @Column(name = "location_id")
    private Long locationId;

    @Column(name = "customer_id")
    private Long customerId;

    @Column(name = "created_at", nullable = false)
    private Timestamp createdAt;

    @Column(name = "created_by_user_id", nullable = false)
    private Long createdByUserId;

    public PackageGroupStatusTransitionLogEntity() {}

    public String getId() {
        return this.id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public Long getPackageGroupStatusTransitionId() {
        return this.packageGroupStatusTransitionId;
    }

    public void setPackageGroupStatusTransitionId(Long packageGroupStatusTransitionId) {
        this.packageGroupStatusTransitionId = packageGroupStatusTransitionId;
    }

    public Long getPackageGroupStatusId() {
        return this.packageGroupStatusId;
    }

    public void setPackageGroupStatusId(Long packageGroupStatusId) {
        this.packageGroupStatusId = packageGroupStatusId;
    }

    public Long getPackageGroupAllowedStatusId() {
        return this.packageGroupAllowedStatusId;
    }

    public void setPackageGroupAllowedStatusId(Long packageGroupAllowedStatusId) {
        this.packageGroupAllowedStatusId = packageGroupAllowedStatusId;
    }

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
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

    public Long getCreatedByUserId() {
        return this.createdByUserId;
    }

    public void setCreatedByUserId(Long createdByUserId) {
        this.createdByUserId = createdByUserId;
    }

}
