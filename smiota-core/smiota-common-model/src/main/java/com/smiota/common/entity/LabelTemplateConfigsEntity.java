package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "label_template_configs")
public class LabelTemplateConfigsEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Integer id;

    @Column(name = "name", nullable = false, length = 45)
    private String name;

    @Column(name = "value", nullable = false)
    private Integer value;

    @Column(name = "description", nullable = false, length = 250)
    private String description;

    @Column(name = "customer_id", nullable = false)
    private Long customerId;

    @Column(name = "location_id")
    private Long locationId;

    @Column(name = "is_outbound")
    private Boolean isOutbound;

    public LabelTemplateConfigsEntity() {}

    public Integer getId() {
        return this.id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getName() {
        return this.name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getValue() {
        return this.value;
    }

    public void setValue(Integer value) {
        this.value = value;
    }

    public String getDescription() {
        return this.description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    public Long getLocationId() {
        return this.locationId;
    }

    public void setLocationId(Long locationId) {
        this.locationId = locationId;
    }

    public Boolean isOutbound() {
        return this.isOutbound;
    }

    public void setIsOutbound(Boolean isOutbound) {
        this.isOutbound = isOutbound;
    }

}
