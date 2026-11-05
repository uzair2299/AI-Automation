package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "package_group")
public class PackageGroupEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "uuid", nullable = false, length = 36)
    private String uuid;

    @Column(name = "package_group_external_id", length = 256)
    private String packageGroupExternalId;

    @Column(name = "created_by_user_id", nullable = false)
    private Long createdByUserId;

    @Column(name = "created_time", nullable = false)
    private Timestamp createdTime;

    @Column(name = "last_modified_by_user_id", nullable = false)
    private Long lastModifiedByUserId;

    @Column(name = "last_modified_time", nullable = false)
    private Timestamp lastModifiedTime;

    @Column(name = "status_change_time")
    private Timestamp statusChangeTime;

    @Column(name = "package_group_status_id", nullable = false)
    private Long packageGroupStatusId;

    @Column(name = "location_id", nullable = false)
    private Long locationId;

    @Column(name = "customer_id", nullable = false)
    private Long customerId;

    @Column(name = "tenant_id")
    private Long tenantId;

    @Column(name = "order_id", length = 256)
    private String orderId;

    @Column(name = "is_deleted")
    private Boolean isDeleted;

    @Column(name = "package_group_recipient_id")
    private Long packageGroupRecipientId;

    @Column(name = "customer_data", length = 1024)
    private String customerData;

    @Column(name = "passcode", length = 10)
    private String passcode;

    public PackageGroupEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getUuid() {
        return this.uuid;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }

    public String getPackageGroupExternalId() {
        return this.packageGroupExternalId;
    }

    public void setPackageGroupExternalId(String packageGroupExternalId) {
        this.packageGroupExternalId = packageGroupExternalId;
    }

    public Long getCreatedByUserId() {
        return this.createdByUserId;
    }

    public void setCreatedByUserId(Long createdByUserId) {
        this.createdByUserId = createdByUserId;
    }

    public Timestamp getCreatedTime() {
        return this.createdTime;
    }

    public void setCreatedTime(Timestamp createdTime) {
        this.createdTime = createdTime;
    }

    public Long getLastModifiedByUserId() {
        return this.lastModifiedByUserId;
    }

    public void setLastModifiedByUserId(Long lastModifiedByUserId) {
        this.lastModifiedByUserId = lastModifiedByUserId;
    }

    public Timestamp getLastModifiedTime() {
        return this.lastModifiedTime;
    }

    public void setLastModifiedTime(Timestamp lastModifiedTime) {
        this.lastModifiedTime = lastModifiedTime;
    }

    public Timestamp getStatusChangeTime() {
        return this.statusChangeTime;
    }

    public void setStatusChangeTime(Timestamp statusChangeTime) {
        this.statusChangeTime = statusChangeTime;
    }

    public Long getPackageGroupStatusId() {
        return this.packageGroupStatusId;
    }

    public void setPackageGroupStatusId(Long packageGroupStatusId) {
        this.packageGroupStatusId = packageGroupStatusId;
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

    public Long getTenantId() {
        return this.tenantId;
    }

    public void setTenantId(Long tenantId) {
        this.tenantId = tenantId;
    }

    public String getOrderId() {
        return this.orderId;
    }

    public void setOrderId(String orderId) {
        this.orderId = orderId;
    }

    public Boolean isDeleted() {
        return this.isDeleted;
    }

    public void setIsDeleted(Boolean isDeleted) {
        this.isDeleted = isDeleted;
    }

    public Long getPackageGroupRecipientId() {
        return this.packageGroupRecipientId;
    }

    public void setPackageGroupRecipientId(Long packageGroupRecipientId) {
        this.packageGroupRecipientId = packageGroupRecipientId;
    }

    public String getCustomerData() {
        return this.customerData;
    }

    public void setCustomerData(String customerData) {
        this.customerData = customerData;
    }

    public String getPasscode() {
        return this.passcode;
    }

    public void setPasscode(String passcode) {
        this.passcode = passcode;
    }

}
