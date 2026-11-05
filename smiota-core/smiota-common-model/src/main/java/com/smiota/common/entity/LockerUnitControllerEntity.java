package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "LOCKER_UNIT_CONTROLLER")
public class LockerUnitControllerEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "LOCKER_UNIT_ID")
    private Long lockerUnitId;

    @Column(name = "LOCKER_CONTROLLER_ID")
    private Integer lockerControllerId;

    @Column(name = "CUSTOMER_ID", nullable = false)
    private Long customerId;

    @Column(name = "IP_ADDRESS", length = 25)
    private String ipAddress;

    @Column(name = "PORT_NUM", length = 10)
    private String portNum;

    public LockerUnitControllerEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getLockerUnitId() {
        return this.lockerUnitId;
    }

    public void setLockerUnitId(Long lockerUnitId) {
        this.lockerUnitId = lockerUnitId;
    }

    public Integer getLockerControllerId() {
        return this.lockerControllerId;
    }

    public void setLockerControllerId(Integer lockerControllerId) {
        this.lockerControllerId = lockerControllerId;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    public String getIpAddress() {
        return this.ipAddress;
    }

    public void setIpAddress(String ipAddress) {
        this.ipAddress = ipAddress;
    }

    public String getPortNum() {
        return this.portNum;
    }

    public void setPortNum(String portNum) {
        this.portNum = portNum;
    }

}
