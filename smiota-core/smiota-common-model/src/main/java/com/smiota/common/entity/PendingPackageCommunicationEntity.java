package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "PENDING_PACKAGE_COMMUNICATION")
public class PendingPackageCommunicationEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "PACKAGE_ID")
    private Long packageId;

    @Column(name = "TRIED_BUT_FAILED")
    private Boolean triedButFailed;

    @Column(name = "ERROR_MSG", length = 300)
    private String errorMsg;

    @Column(name = "CUSTOMER_ID")
    private Long customerId;

    public PendingPackageCommunicationEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getPackageId() {
        return this.packageId;
    }

    public void setPackageId(Long packageId) {
        this.packageId = packageId;
    }

    public Boolean getTriedButFailed() {
        return this.triedButFailed;
    }

    public void setTriedButFailed(Boolean triedButFailed) {
        this.triedButFailed = triedButFailed;
    }

    public String getErrorMsg() {
        return this.errorMsg;
    }

    public void setErrorMsg(String errorMsg) {
        this.errorMsg = errorMsg;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

}
