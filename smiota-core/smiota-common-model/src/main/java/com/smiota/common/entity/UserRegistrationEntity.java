package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "USER_REGISTRATION")
@IdClass(UserRegistrationId.class)
public class UserRegistrationEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @Column(name = "id")
    private Integer id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Id
    @Column(name = "reg_status_id")
    private Integer regStatusId;

    @Column(name = "last_modified_time", nullable = false)
    private Timestamp lastModifiedTime;

    @Column(name = "last_modified_user_id")
    private Long lastModifiedUserId;

    public UserRegistrationEntity() {}

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

    public Timestamp getLastModifiedTime() {
        return this.lastModifiedTime;
    }

    public void setLastModifiedTime(Timestamp lastModifiedTime) {
        this.lastModifiedTime = lastModifiedTime;
    }

    public Long getLastModifiedUserId() {
        return this.lastModifiedUserId;
    }

    public void setLastModifiedUserId(Long lastModifiedUserId) {
        this.lastModifiedUserId = lastModifiedUserId;
    }

}
