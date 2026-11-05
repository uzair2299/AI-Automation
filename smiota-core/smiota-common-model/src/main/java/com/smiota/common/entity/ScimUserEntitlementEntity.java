package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "SCIM_USER_ENTITLEMENT")
public class ScimUserEntitlementEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "scim_entitlement_id", nullable = false)
    private Integer scimEntitlementId;

    @Column(name = "scim_user_id", nullable = false, length = 36)
    private String scimUserId;

    public ScimUserEntitlementEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Integer getScimEntitlementId() {
        return this.scimEntitlementId;
    }

    public void setScimEntitlementId(Integer scimEntitlementId) {
        this.scimEntitlementId = scimEntitlementId;
    }

    public String getScimUserId() {
        return this.scimUserId;
    }

    public void setScimUserId(String scimUserId) {
        this.scimUserId = scimUserId;
    }

}
