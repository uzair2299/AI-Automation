package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "user_purge_results")
public class UserPurgeResultsEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "customer_id", nullable = false)
    private Long customerId;

    @Column(name = "location_id", nullable = false)
    private Long locationId;

    @Column(name = "num_of_users", nullable = false)
    private Integer numOfUsers;

    @Column(name = "num_of_user_sessions", nullable = false)
    private Integer numOfUserSessions;

    @Column(name = "num_of_emails", nullable = false)
    private Integer numOfEmails;

    @Column(name = "num_of_sms", nullable = false)
    private Integer numOfSms;

    @Column(name = "purge_time", nullable = false)
    private Timestamp purgeTime;

    @Column(name = "expire_purge_time", nullable = false)
    private Timestamp expirePurgeTime;

    @Column(name = "is_ran_at_expire_time", nullable = false)
    private Boolean isRanAtExpireTime;

    public UserPurgeResultsEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    public Long getLocationId() {
        return this.locationId;
    }

    public void setLocationId(Long locationId) {
        this.locationId = locationId;
    }

    public Integer getNumOfUsers() {
        return this.numOfUsers;
    }

    public void setNumOfUsers(Integer numOfUsers) {
        this.numOfUsers = numOfUsers;
    }

    public Integer getNumOfUserSessions() {
        return this.numOfUserSessions;
    }

    public void setNumOfUserSessions(Integer numOfUserSessions) {
        this.numOfUserSessions = numOfUserSessions;
    }

    public Integer getNumOfEmails() {
        return this.numOfEmails;
    }

    public void setNumOfEmails(Integer numOfEmails) {
        this.numOfEmails = numOfEmails;
    }

    public Integer getNumOfSms() {
        return this.numOfSms;
    }

    public void setNumOfSms(Integer numOfSms) {
        this.numOfSms = numOfSms;
    }

    public Timestamp getPurgeTime() {
        return this.purgeTime;
    }

    public void setPurgeTime(Timestamp purgeTime) {
        this.purgeTime = purgeTime;
    }

    public Timestamp getExpirePurgeTime() {
        return this.expirePurgeTime;
    }

    public void setExpirePurgeTime(Timestamp expirePurgeTime) {
        this.expirePurgeTime = expirePurgeTime;
    }

    public Boolean isRanAtExpireTime() {
        return this.isRanAtExpireTime;
    }

    public void setIsRanAtExpireTime(Boolean isRanAtExpireTime) {
        this.isRanAtExpireTime = isRanAtExpireTime;
    }

}
