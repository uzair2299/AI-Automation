package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "STATUS_LOG")
public class StatusLogEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "AUTH_TOKEN", length = 36)
    private String authToken;

    @Column(name = "LOCKER_ID")
    private Long lockerId;

    @Column(name = "MESSAGE", length = 2000)
    private String message;

    @Column(name = "RECEIVED_TIME")
    private Timestamp receivedTime;

    @Column(name = "CUSTOMER_ID")
    private Long customerId;

    @Column(name = "STATUS_CODE", length = 64)
    private String statusCode;

    @Column(name = "LOCKER_UNIT_ID")
    private Long lockerUnitId;

    @Column(name = "LOCKER_DEVICE_ADDRESS_ID")
    private Long lockerDeviceAddressId;

    public StatusLogEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getAuthToken() {
        return this.authToken;
    }

    public void setAuthToken(String authToken) {
        this.authToken = authToken;
    }

    public Long getLockerId() {
        return this.lockerId;
    }

    public void setLockerId(Long lockerId) {
        this.lockerId = lockerId;
    }

    public String getMessage() {
        return this.message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public Timestamp getReceivedTime() {
        return this.receivedTime;
    }

    public void setReceivedTime(Timestamp receivedTime) {
        this.receivedTime = receivedTime;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    public String getStatusCode() {
        return this.statusCode;
    }

    public void setStatusCode(String statusCode) {
        this.statusCode = statusCode;
    }

    public Long getLockerUnitId() {
        return this.lockerUnitId;
    }

    public void setLockerUnitId(Long lockerUnitId) {
        this.lockerUnitId = lockerUnitId;
    }

    public Long getLockerDeviceAddressId() {
        return this.lockerDeviceAddressId;
    }

    public void setLockerDeviceAddressId(Long lockerDeviceAddressId) {
        this.lockerDeviceAddressId = lockerDeviceAddressId;
    }

}
