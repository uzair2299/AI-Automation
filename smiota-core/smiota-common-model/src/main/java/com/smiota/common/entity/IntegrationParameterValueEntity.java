package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "INTEGRATION_PARAMETER_VALUE")
public class IntegrationParameterValueEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "PARM")
    private Integer parm;

    @Column(name = "VALUE")
    private String value;

    @Column(name = "CUSTOMER_ID")
    private Long customerId;

    @Column(name = "LOCATION_ID")
    private Long locationId;

    public IntegrationParameterValueEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Integer getParm() {
        return this.parm;
    }

    public void setParm(Integer parm) {
        this.parm = parm;
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

    public Long getLocationId() {
        return this.locationId;
    }

    public void setLocationId(Long locationId) {
        this.locationId = locationId;
    }

}
