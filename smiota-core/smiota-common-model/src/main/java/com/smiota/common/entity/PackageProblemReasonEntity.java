package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "package_problem_reason")
public class PackageProblemReasonEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Integer id;

    @Column(name = "location_properties_id", nullable = false)
    private Long locationPropertiesId;

    @Column(name = "name", length = 45)
    private String name;

    @Column(name = "description", length = 250)
    private String description;

    @Column(name = "order_display", nullable = false)
    private Integer orderDisplay;

    public PackageProblemReasonEntity() {}

    public Integer getId() {
        return this.id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Long getLocationPropertiesId() {
        return this.locationPropertiesId;
    }

    public void setLocationPropertiesId(Long locationPropertiesId) {
        this.locationPropertiesId = locationPropertiesId;
    }

    public String getName() {
        return this.name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return this.description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Integer getOrderDisplay() {
        return this.orderDisplay;
    }

    public void setOrderDisplay(Integer orderDisplay) {
        this.orderDisplay = orderDisplay;
    }

}
