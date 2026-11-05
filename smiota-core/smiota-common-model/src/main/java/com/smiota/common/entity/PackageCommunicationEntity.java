package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "PACKAGE_COMMUNICATION")
public class PackageCommunicationEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "PACKAGE_ID")
    private Long packageId;

    @Column(name = "COMMUNICATION_ID")
    private Long communicationId;

    @Column(name = "COMMUNICATION_TYPE")
    private Integer communicationType;

    @Column(name = "CUSTOMER_ID")
    private Long customerId;

    @Column(name = "TIME_SENT")
    private Timestamp timeSent;

    @Column(name = "USER_ID")
    private Long userId;

    @Column(name = "NOTIFICATION_TYPE_ID")
    private Long notificationTypeId;

    @Column(name = "STATUS_LOG_ID")
    private Long statusLogId;

    public PackageCommunicationEntity() {}

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

    public Long getCommunicationId() {
        return this.communicationId;
    }

    public void setCommunicationId(Long communicationId) {
        this.communicationId = communicationId;
    }

    public Integer getCommunicationType() {
        return this.communicationType;
    }

    public void setCommunicationType(Integer communicationType) {
        this.communicationType = communicationType;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    public Timestamp getTimeSent() {
        return this.timeSent;
    }

    public void setTimeSent(Timestamp timeSent) {
        this.timeSent = timeSent;
    }

    public Long getUserId() {
        return this.userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public Long getNotificationTypeId() {
        return this.notificationTypeId;
    }

    public void setNotificationTypeId(Long notificationTypeId) {
        this.notificationTypeId = notificationTypeId;
    }

    public Long getStatusLogId() {
        return this.statusLogId;
    }

    public void setStatusLogId(Long statusLogId) {
        this.statusLogId = statusLogId;
    }

}
