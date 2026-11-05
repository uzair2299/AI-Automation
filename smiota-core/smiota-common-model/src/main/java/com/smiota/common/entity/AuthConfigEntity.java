package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "auth_config")
public class AuthConfigEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "sub_domain", nullable = false, length = 255)
    private String subDomain;

    @Column(name = "customer_id", nullable = false)
    private Long customerId;

    @Column(name = "location_id")
    private Long locationId;

    @Column(name = "tenant_id")
    private Long tenantId;

    @Column(name = "idp_id", nullable = false, length = 255)
    private String idpId;

    @Column(name = "auth_url", nullable = false, length = 255)
    private String authUrl;

    @Column(name = "onboard_mode", nullable = false)
    private Integer onboardMode;

    @Column(name = "inactive", nullable = false)
    private Boolean inactive;

    @Column(name = "created_by", nullable = false)
    private Long createdBy;

    @Column(name = "updated_by", nullable = false)
    private Long updatedBy;

    @Column(name = "created_time", nullable = false)
    private Timestamp createdTime;

    @Column(name = "updated_time", nullable = false)
    private Timestamp updatedTime;

    @Column(name = "email_domains", length = 100)
    private String emailDomains;

    @Column(name = "disallow_password_login")
    private Boolean disallowPasswordLogin;

    @Column(name = "uuid", nullable = false, length = 36)
    private String uuid;

    public AuthConfigEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getSubDomain() {
        return this.subDomain;
    }

    public void setSubDomain(String subDomain) {
        this.subDomain = subDomain;
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

    public Long getTenantId() {
        return this.tenantId;
    }

    public void setTenantId(Long tenantId) {
        this.tenantId = tenantId;
    }

    public String getIdpId() {
        return this.idpId;
    }

    public void setIdpId(String idpId) {
        this.idpId = idpId;
    }

    public String getAuthUrl() {
        return this.authUrl;
    }

    public void setAuthUrl(String authUrl) {
        this.authUrl = authUrl;
    }

    public Integer getOnboardMode() {
        return this.onboardMode;
    }

    public void setOnboardMode(Integer onboardMode) {
        this.onboardMode = onboardMode;
    }

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
    }

    public Long getCreatedBy() {
        return this.createdBy;
    }

    public void setCreatedBy(Long createdBy) {
        this.createdBy = createdBy;
    }

    public Long getUpdatedBy() {
        return this.updatedBy;
    }

    public void setUpdatedBy(Long updatedBy) {
        this.updatedBy = updatedBy;
    }

    public Timestamp getCreatedTime() {
        return this.createdTime;
    }

    public void setCreatedTime(Timestamp createdTime) {
        this.createdTime = createdTime;
    }

    public Timestamp getUpdatedTime() {
        return this.updatedTime;
    }

    public void setUpdatedTime(Timestamp updatedTime) {
        this.updatedTime = updatedTime;
    }

    public String getEmailDomains() {
        return this.emailDomains;
    }

    public void setEmailDomains(String emailDomains) {
        this.emailDomains = emailDomains;
    }

    public Boolean getDisallowPasswordLogin() {
        return this.disallowPasswordLogin;
    }

    public void setDisallowPasswordLogin(Boolean disallowPasswordLogin) {
        this.disallowPasswordLogin = disallowPasswordLogin;
    }

    public String getUuid() {
        return this.uuid;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }

}
