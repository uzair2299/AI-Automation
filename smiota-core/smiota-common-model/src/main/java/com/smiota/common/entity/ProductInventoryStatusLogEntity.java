package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "product_inventory_status_log")
public class ProductInventoryStatusLogEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "product_inventory_id", nullable = false)
    private Long productInventoryId;

    @Column(name = "status", nullable = false)
    private Integer status;

    @Column(name = "created_time", nullable = false)
    private Timestamp createdTime;

    @Column(name = "action_from_user_id")
    private Long actionFromUserId;

    @Column(name = "currently_with_user_id")
    private Long currentlyWithUserId;

    @Column(name = "action_from_maint_location_id")
    private Long actionFromMaintLocationId;

    @Column(name = "currently_at_maint_location_id")
    private Long currentlyAtMaintLocationId;

    @Column(name = "transaction_uuid", length = 36)
    private String transactionUuid;

    public ProductInventoryStatusLogEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getProductInventoryId() {
        return this.productInventoryId;
    }

    public void setProductInventoryId(Long productInventoryId) {
        this.productInventoryId = productInventoryId;
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

    public Long getActionFromUserId() {
        return this.actionFromUserId;
    }

    public void setActionFromUserId(Long actionFromUserId) {
        this.actionFromUserId = actionFromUserId;
    }

    public Long getCurrentlyWithUserId() {
        return this.currentlyWithUserId;
    }

    public void setCurrentlyWithUserId(Long currentlyWithUserId) {
        this.currentlyWithUserId = currentlyWithUserId;
    }

    public Long getActionFromMaintLocationId() {
        return this.actionFromMaintLocationId;
    }

    public void setActionFromMaintLocationId(Long actionFromMaintLocationId) {
        this.actionFromMaintLocationId = actionFromMaintLocationId;
    }

    public Long getCurrentlyAtMaintLocationId() {
        return this.currentlyAtMaintLocationId;
    }

    public void setCurrentlyAtMaintLocationId(Long currentlyAtMaintLocationId) {
        this.currentlyAtMaintLocationId = currentlyAtMaintLocationId;
    }

    public String getTransactionUuid() {
        return this.transactionUuid;
    }

    public void setTransactionUuid(String transactionUuid) {
        this.transactionUuid = transactionUuid;
    }

}
