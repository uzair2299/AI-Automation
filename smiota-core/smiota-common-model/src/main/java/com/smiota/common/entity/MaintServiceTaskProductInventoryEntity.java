package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "maint_service_task_product_inventory")
public class MaintServiceTaskProductInventoryEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "maint_service_task_id", nullable = false)
    private Long maintServiceTaskId;

    @Column(name = "product_inventory_id", nullable = false)
    private Long productInventoryId;

    @Column(name = "created_time", nullable = false)
    private Timestamp createdTime;

    @Column(name = "created_by_user_id", nullable = false)
    private Long createdByUserId;

    @Column(name = "last_modified_by_user_id", nullable = false)
    private Long lastModifiedByUserId;

    @Column(name = "last_modified_time", nullable = false)
    private Timestamp lastModifiedTime;

    public MaintServiceTaskProductInventoryEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getMaintServiceTaskId() {
        return this.maintServiceTaskId;
    }

    public void setMaintServiceTaskId(Long maintServiceTaskId) {
        this.maintServiceTaskId = maintServiceTaskId;
    }

    public Long getProductInventoryId() {
        return this.productInventoryId;
    }

    public void setProductInventoryId(Long productInventoryId) {
        this.productInventoryId = productInventoryId;
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

    public Long getLastModifiedByUserId() {
        return this.lastModifiedByUserId;
    }

    public void setLastModifiedByUserId(Long lastModifiedByUserId) {
        this.lastModifiedByUserId = lastModifiedByUserId;
    }

    public Timestamp getLastModifiedTime() {
        return this.lastModifiedTime;
    }

    public void setLastModifiedTime(Timestamp lastModifiedTime) {
        this.lastModifiedTime = lastModifiedTime;
    }

}
