package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "package_advanced_props_config")
public class PackageAdvancedPropsConfigEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Integer id;

    @Column(name = "location_properties_id", nullable = false)
    private Long locationPropertiesId;

    @Column(name = "name", nullable = false, length = 45)
    private String name;

    @Column(name = "value", nullable = false)
    private Boolean value;

    public PackageAdvancedPropsConfigEntity() {}

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

    public Boolean getValue() {
        return this.value;
    }

    public void setValue(Boolean value) {
        this.value = value;
    }

}
