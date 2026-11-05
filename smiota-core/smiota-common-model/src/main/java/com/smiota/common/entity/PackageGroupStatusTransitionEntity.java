package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "package_group_status_transition")
public class PackageGroupStatusTransitionEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

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

    @Column(name = "last_modified_at", nullable = false)
    private Timestamp lastModifiedAt;

    @Column(name = "created_by_user_id")
    private Long createdByUserId;

    @Column(name = "last_modified_by_user_id")
    private Long lastModifiedByUserId;

    public PackageGroupStatusTransitionEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
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

}
