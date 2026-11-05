package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "PACKAGE_COMMUNICATION_APP")
public class PackageCommunicationAppEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "MESSAGE_ID", length = 36)
    private String messageId;

    @Column(name = "AUTH_TOKEN", length = 36)
    private String authToken;

    @Column(name = "DEVICE_TOKEN", length = 1024)
    private String deviceToken;

    @Column(name = "BODY", length = 1024)
    private String body;

    @Column(name = "STATUS")
    private Integer status;

    @Column(name = "TIME_SENT")
    private Timestamp timeSent;

    @Column(name = "CUSTOMER_ID")
    private Long customerId;

    public PackageCommunicationAppEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getMessageId() {
        return this.messageId;
    }

    public void setMessageId(String messageId) {
        this.messageId = messageId;
    }

    public String getAuthToken() {
        return this.authToken;
    }

    public void setAuthToken(String authToken) {
        this.authToken = authToken;
    }

    public String getDeviceToken() {
        return this.deviceToken;
    }

    public void setDeviceToken(String deviceToken) {
        this.deviceToken = deviceToken;
    }

    public String getBody() {
        return this.body;
    }

    public void setBody(String body) {
        this.body = body;
    }

    public Integer getStatus() {
        return this.status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public Timestamp getTimeSent() {
        return this.timeSent;
    }

    public void setTimeSent(Timestamp timeSent) {
        this.timeSent = timeSent;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

}
