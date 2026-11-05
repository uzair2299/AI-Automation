package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "USER_REGISTRATION_STATUS_LOG")
@IdClass(UserRegistrationStatusLogId.class)
public class UserRegistrationStatusLogEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @Column(name = "id")
    private Integer id;

    @Column(name = "user_id")
    private Long userId;

    @Id
    @Column(name = "reg_status_id")
    private Integer regStatusId;

    @Column(name = "created_by_user_id")
    private Long createdByUserId;

    @Column(name = "created_by_user_time")
    private Timestamp createdByUserTime;

    public UserRegistrationStatusLogEntity() {}

    public Integer getId() {
        return this.id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Long getUserId() {
        return this.userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public Integer getRegStatusId() {
        return this.regStatusId;
    }

    public void setRegStatusId(Integer regStatusId) {
        this.regStatusId = regStatusId;
    }

    public Long getCreatedByUserId() {
        return this.createdByUserId;
    }

    public void setCreatedByUserId(Long createdByUserId) {
        this.createdByUserId = createdByUserId;
    }

    public Timestamp getCreatedByUserTime() {
        return this.createdByUserTime;
    }

    public void setCreatedByUserTime(Timestamp createdByUserTime) {
        this.createdByUserTime = createdByUserTime;
    }

}
