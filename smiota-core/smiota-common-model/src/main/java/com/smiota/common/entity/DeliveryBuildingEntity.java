package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "DELIVERY_BUILDING")
public class DeliveryBuildingEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "building_id")
    private Long buildingId;

    @Column(name = "delivery_building_id")
    private Long deliveryBuildingId;

    @Column(name = "location_id")
    private Long locationId;

    @Column(name = "customer_id")
    private Long customerId;

    public DeliveryBuildingEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getBuildingId() {
        return this.buildingId;
    }

    public void setBuildingId(Long buildingId) {
        this.buildingId = buildingId;
    }

    public Long getDeliveryBuildingId() {
        return this.deliveryBuildingId;
    }

    public void setDeliveryBuildingId(Long deliveryBuildingId) {
        this.deliveryBuildingId = deliveryBuildingId;
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

}
