package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "product_inventory")
public class ProductInventoryEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "product_id", nullable = false)
    private Long productId;

    @Column(name = "package_id")
    private Long packageId;

    @Column(name = "status", nullable = false)
    private Integer status;

    @Column(name = "created_time", nullable = false)
    private Timestamp createdTime;

    @Column(name = "created_by_user_id", nullable = false)
    private Long createdByUserId;

    @Column(name = "currently_with_user_id")
    private Long currentlyWithUserId;

    @Column(name = "last_modified_time", nullable = false)
    private Timestamp lastModifiedTime;

    @Column(name = "currently_at_maint_location_id")
    private Long currentlyAtMaintLocationId;

    public ProductInventoryEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getProductId() {
        return this.productId;
    }

    public void setProductId(Long productId) {
        this.productId = productId;
    }

    public Long getPackageId() {
        return this.packageId;
    }

    public void setPackageId(Long packageId) {
        this.packageId = packageId;
    }

    public Integer getStatus() {
        return this.status;
    }

    public void setStatus(Integer status) {
        this.status = status;
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

    public Long getCurrentlyWithUserId() {
        return this.currentlyWithUserId;
    }

    public void setCurrentlyWithUserId(Long currentlyWithUserId) {
        this.currentlyWithUserId = currentlyWithUserId;
    }

    public Timestamp getLastModifiedTime() {
        return this.lastModifiedTime;
    }

    public void setLastModifiedTime(Timestamp lastModifiedTime) {
        this.lastModifiedTime = lastModifiedTime;
    }

    public Long getCurrentlyAtMaintLocationId() {
        return this.currentlyAtMaintLocationId;
    }

    public void setCurrentlyAtMaintLocationId(Long currentlyAtMaintLocationId) {
        this.currentlyAtMaintLocationId = currentlyAtMaintLocationId;
    }

}
