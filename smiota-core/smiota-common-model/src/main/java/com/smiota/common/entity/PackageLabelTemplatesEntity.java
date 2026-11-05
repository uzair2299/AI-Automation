package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "package_label_templates")
public class PackageLabelTemplatesEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Integer id;

    @Column(name = "customer_id", nullable = false)
    private Long customerId;

    @Column(name = "location_id")
    private Long locationId;

    @Column(name = "template", nullable = false, length = 2000)
    private String template;

    @Column(name = "inactive", nullable = false)
    private Boolean inactive;

    @Column(name = "is_outbound")
    private Boolean isOutbound;

    public PackageLabelTemplatesEntity() {}

    public Integer getId() {
        return this.id;
    }

    public void setId(Integer id) {
        this.id = id;
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

    public String getTemplate() {
        return this.template;
    }

    public void setTemplate(String template) {
        this.template = template;
    }

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
    }

    public Boolean isOutbound() {
        return this.isOutbound;
    }

    public void setIsOutbound(Boolean isOutbound) {
        this.isOutbound = isOutbound;
    }

}
