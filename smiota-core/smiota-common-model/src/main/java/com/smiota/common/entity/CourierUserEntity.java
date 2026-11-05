package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "COURIER_USER")
public class CourierUserEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "COURIER_ID")
    private Integer courierId;

    @Column(name = "USER_ID")
    private Long userId;

    @Column(name = "CUSTOMER_ID")
    private Long customerId;

    @Column(name = "CAN_PICK_UP_PACKAGES")
    private Boolean canPickUpPackages;

    @Column(name = "label", length = 100)
    private String label;

    @Column(name = "IS_MASTER_COURIER")
    private Boolean isMasterCourier;

    @Column(name = "enable_outgoing_notification")
    private Boolean enableOutgoingNotification;

    public CourierUserEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Integer getCourierId() {
        return this.courierId;
    }

    public void setCourierId(Integer courierId) {
        this.courierId = courierId;
    }

    public Long getUserId() {
        return this.userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    public Boolean getCanPickUpPackages() {
        return this.canPickUpPackages;
    }

    public void setCanPickUpPackages(Boolean canPickUpPackages) {
        this.canPickUpPackages = canPickUpPackages;
    }

    public String getLabel() {
        return this.label;
    }

    public void setLabel(String label) {
        this.label = label;
    }

    public Boolean isMasterCourier() {
        return this.isMasterCourier;
    }

    public void setIsMasterCourier(Boolean isMasterCourier) {
        this.isMasterCourier = isMasterCourier;
    }

    public Boolean getEnableOutgoingNotification() {
        return this.enableOutgoingNotification;
    }

    public void setEnableOutgoingNotification(Boolean enableOutgoingNotification) {
        this.enableOutgoingNotification = enableOutgoingNotification;
    }

}
