package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "config_values")
public class ConfigValuesEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "config_props_id")
    private Long configPropsId;

    @Column(name = "value", length = 2000)
    private String value;

    @Column(name = "customer_id")
    private Long customerId;

    @Column(name = "created_time", nullable = false)
    private Timestamp createdTime;

    @Column(name = "user_id")
    private Long userId;

    @Column(name = "location_id")
    private Long locationId;

    public ConfigValuesEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getConfigPropsId() {
        return this.configPropsId;
    }

    public void setConfigPropsId(Long configPropsId) {
        this.configPropsId = configPropsId;
    }

    public String getValue() {
        return this.value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    public Timestamp getCreatedTime() {
        return this.createdTime;
    }

    public void setCreatedTime(Timestamp createdTime) {
        this.createdTime = createdTime;
    }

    public Long getUserId() {
        return this.userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public Long getLocationId() {
        return this.locationId;
    }

    public void setLocationId(Long locationId) {
        this.locationId = locationId;
    }

}
