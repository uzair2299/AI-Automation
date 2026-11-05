package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "PACKAGE_STATUS")
public class PackageStatusEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Integer id;

    @Column(name = "NAME", length = 24)
    private String name;

    @Column(name = "COMMENT", length = 1000)
    private String comment;

    @Column(name = "color", length = 45)
    private String color;

    @Column(name = "ordinal")
    private Integer ordinal;

    @Column(name = "customer_id")
    private Long customerId;

    @Column(name = "location_id")
    private Long locationId;

    @Column(name = "is_required", nullable = false)
    private Boolean isRequired;

    @Column(name = "package_status_group_id")
    private Integer packageStatusGroupId;

    @Column(name = "inactive", nullable = false)
    private Boolean inactive;

    public PackageStatusEntity() {}

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

    public String getComment() {
        return this.comment;
    }

    public void setComment(String comment) {
        this.comment = comment;
    }

    public String getColor() {
        return this.color;
    }

    public void setColor(String color) {
        this.color = color;
    }

    public Integer getOrdinal() {
        return this.ordinal;
    }

    public void setOrdinal(Integer ordinal) {
        this.ordinal = ordinal;
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

    public Boolean isRequired() {
        return this.isRequired;
    }

    public void setIsRequired(Boolean isRequired) {
        this.isRequired = isRequired;
    }

    public Integer getPackageStatusGroupId() {
        return this.packageStatusGroupId;
    }

    public void setPackageStatusGroupId(Integer packageStatusGroupId) {
        this.packageStatusGroupId = packageStatusGroupId;
    }

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
    }

}
