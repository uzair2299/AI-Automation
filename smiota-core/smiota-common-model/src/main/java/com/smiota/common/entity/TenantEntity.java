package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.math.BigDecimal;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "TENANT")
public class TenantEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "NAME", nullable = false, length = 255)
    private String name;

    @Column(name = "INACTIVE")
    private Boolean inactive;

    @Column(name = "UNIT", length = 24)
    private String unit;

    @Column(name = "PHONE", length = 24)
    private String phone;

    @Column(name = "EMAIL", length = 225)
    private String email;

    @Column(name = "LOCATION_ID", nullable = false)
    private Long locationId;

    @Column(name = "CUSTOMER_ID", nullable = false)
    private Long customerId;

    @Column(name = "LAST_MODIFIED_TIME")
    private Timestamp lastModifiedTime;

    @Column(name = "PASSCODE", length = 10)
    private String passcode;

    @Column(name = "external_id", length = 100)
    private String externalId;

    @Column(name = "represents_customer")
    private Boolean representsCustomer;

    @Column(name = "building_id")
    private Long buildingId;

    @Column(name = "last_passcode_created_time")
    private Timestamp lastPasscodeCreatedTime;

    @Column(name = "modified_by_user_id")
    private Long modifiedByUserId;

    @Column(name = "created_time", nullable = false)
    private Timestamp createdTime;

    @Column(name = "created_by_user_id")
    private Long createdByUserId;

    @Column(name = "latitude", precision = 8, scale = 6)
    private BigDecimal latitude;

    @Column(name = "longitude", precision = 9, scale = 6)
    private BigDecimal longitude;

    public TenantEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return this.name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
    }

    public String getUnit() {
        return this.unit;
    }

    public void setUnit(String unit) {
        this.unit = unit;
    }

    public String getPhone() {
        return this.phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getEmail() {
        return this.email;
    }

    public void setEmail(String email) {
        this.email = email;
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

    public Timestamp getLastModifiedTime() {
        return this.lastModifiedTime;
    }

    public void setLastModifiedTime(Timestamp lastModifiedTime) {
        this.lastModifiedTime = lastModifiedTime;
    }

    public String getPasscode() {
        return this.passcode;
    }

    public void setPasscode(String passcode) {
        this.passcode = passcode;
    }

    public String getExternalId() {
        return this.externalId;
    }

    public void setExternalId(String externalId) {
        this.externalId = externalId;
    }

    public Boolean getRepresentsCustomer() {
        return this.representsCustomer;
    }

    public void setRepresentsCustomer(Boolean representsCustomer) {
        this.representsCustomer = representsCustomer;
    }

    public Long getBuildingId() {
        return this.buildingId;
    }

    public void setBuildingId(Long buildingId) {
        this.buildingId = buildingId;
    }

    public Timestamp getLastPasscodeCreatedTime() {
        return this.lastPasscodeCreatedTime;
    }

    public void setLastPasscodeCreatedTime(Timestamp lastPasscodeCreatedTime) {
        this.lastPasscodeCreatedTime = lastPasscodeCreatedTime;
    }

    public Long getModifiedByUserId() {
        return this.modifiedByUserId;
    }

    public void setModifiedByUserId(Long modifiedByUserId) {
        this.modifiedByUserId = modifiedByUserId;
    }

    public Timestamp getCreatedTime() {
        return this.createdTime;
    }

    public void setCreatedTime(Timestamp createdTime) {
        this.createdTime = createdTime;
    }

    public Long getCreatedByUserId() {
        return this.createdByUserId;
    }

    public void setCreatedByUserId(Long createdByUserId) {
        this.createdByUserId = createdByUserId;
    }

    public BigDecimal getLatitude() {
        return this.latitude;
    }

    public void setLatitude(BigDecimal latitude) {
        this.latitude = latitude;
    }

    public BigDecimal getLongitude() {
        return this.longitude;
    }

    public void setLongitude(BigDecimal longitude) {
        this.longitude = longitude;
    }

}
