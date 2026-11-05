package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "PACKAGE_COMMUNICATION_SMS")
public class PackageCommunicationSmsEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "MESSAGE_ID", length = 300)
    private String messageId;

    @Column(name = "FROM_PHONE", length = 20)
    private String fromPhone;

    @Column(name = "TO_PHONE", length = 20)
    private String toPhone;

    @Column(name = "BODY", length = 2000)
    private String body;

    @Column(name = "STATUS")
    private Integer status;

    @Column(name = "STATUS_MESSAGE", length = 1000)
    private String statusMessage;

    @Column(name = "TIME_SENT")
    private Timestamp timeSent;

    @Column(name = "CUSTOMER_ID")
    private Long customerId;

    @Column(name = "provider", length = 100)
    private String provider;

    public PackageCommunicationSmsEntity() {}

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

    public String getFromPhone() {
        return this.fromPhone;
    }

    public void setFromPhone(String fromPhone) {
        this.fromPhone = fromPhone;
    }

    public String getToPhone() {
        return this.toPhone;
    }

    public void setToPhone(String toPhone) {
        this.toPhone = toPhone;
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

    public String getStatusMessage() {
        return this.statusMessage;
    }

    public void setStatusMessage(String statusMessage) {
        this.statusMessage = statusMessage;
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

    public String getProvider() {
        return this.provider;
    }

    public void setProvider(String provider) {
        this.provider = provider;
    }

}
