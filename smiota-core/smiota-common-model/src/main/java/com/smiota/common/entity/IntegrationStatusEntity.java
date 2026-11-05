package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "INTEGRATION_STATUS")
public class IntegrationStatusEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "TYPE")
    private Integer type;

    @Column(name = "LAST_SYNC_TIME")
    private Timestamp lastSyncTime;

    @Column(name = "LOCATION_ID")
    private Long locationId;

    @Column(name = "CUSTOMER_ID")
    private Long customerId;

    @Column(name = "number_updated")
    private Integer numberUpdated;

    @Column(name = "orders_updated")
    private Integer ordersUpdated;

    @Column(name = "number_failed")
    private Integer numberFailed;

    @Column(name = "details")
    private String details;

    public IntegrationStatusEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Integer getType() {
        return this.type;
    }

    public void setType(Integer type) {
        this.type = type;
    }

    public Timestamp getLastSyncTime() {
        return this.lastSyncTime;
    }

    public void setLastSyncTime(Timestamp lastSyncTime) {
        this.lastSyncTime = lastSyncTime;
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

    public Integer getNumberUpdated() {
        return this.numberUpdated;
    }

    public void setNumberUpdated(Integer numberUpdated) {
        this.numberUpdated = numberUpdated;
    }

    public Integer getOrdersUpdated() {
        return this.ordersUpdated;
    }

    public void setOrdersUpdated(Integer ordersUpdated) {
        this.ordersUpdated = ordersUpdated;
    }

    public Integer getNumberFailed() {
        return this.numberFailed;
    }

    public void setNumberFailed(Integer numberFailed) {
        this.numberFailed = numberFailed;
    }

    public String getDetails() {
        return this.details;
    }

    public void setDetails(String details) {
        this.details = details;
    }

}
