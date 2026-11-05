package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "twilio_incoming_message")
public class TwilioIncomingMessageEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "to", length = 20)
    private String to;

    @Column(name = "customer_id")
    private Long customerId;

    @Column(name = "from", length = 20)
    private String from;

    @Column(name = "body", length = 300)
    private String body;

    @Column(name = "action_type", length = 20)
    private String actionType;

    @Column(name = "response", length = 300)
    private String response;

    @Column(name = "received_time", nullable = false)
    private Timestamp receivedTime;

    @Column(name = "created_time")
    private Timestamp createdTime;

    @Column(name = "is_twilio_keyword")
    private Boolean isTwilioKeyword;

    @Column(name = "is_delayed")
    private Boolean isDelayed;

    public TwilioIncomingMessageEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getTo() {
        return this.to;
    }

    public void setTo(String to) {
        this.to = to;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    public String getFrom() {
        return this.from;
    }

    public void setFrom(String from) {
        this.from = from;
    }

    public String getBody() {
        return this.body;
    }

    public void setBody(String body) {
        this.body = body;
    }

    public String getActionType() {
        return this.actionType;
    }

    public void setActionType(String actionType) {
        this.actionType = actionType;
    }

    public String getResponse() {
        return this.response;
    }

    public void setResponse(String response) {
        this.response = response;
    }

    public Timestamp getReceivedTime() {
        return this.receivedTime;
    }

    public void setReceivedTime(Timestamp receivedTime) {
        this.receivedTime = receivedTime;
    }

    public Timestamp getCreatedTime() {
        return this.createdTime;
    }

    public void setCreatedTime(Timestamp createdTime) {
        this.createdTime = createdTime;
    }

    public Boolean isTwilioKeyword() {
        return this.isTwilioKeyword;
    }

    public void setIsTwilioKeyword(Boolean isTwilioKeyword) {
        this.isTwilioKeyword = isTwilioKeyword;
    }

    public Boolean isDelayed() {
        return this.isDelayed;
    }

    public void setIsDelayed(Boolean isDelayed) {
        this.isDelayed = isDelayed;
    }

}
