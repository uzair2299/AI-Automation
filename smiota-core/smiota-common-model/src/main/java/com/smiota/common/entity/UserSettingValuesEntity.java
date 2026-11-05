package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "user_setting_values")
public class UserSettingValuesEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "user_setting_props_id")
    private Long userSettingPropsId;

    @Column(name = "value", nullable = false, length = 500)
    private String value;

    @Column(name = "created_time", nullable = false)
    private Timestamp createdTime;

    @Column(name = "user_id")
    private Long userId;

    public UserSettingValuesEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getUserSettingPropsId() {
        return this.userSettingPropsId;
    }

    public void setUserSettingPropsId(Long userSettingPropsId) {
        this.userSettingPropsId = userSettingPropsId;
    }

    public String getValue() {
        return this.value;
    }

    public void setValue(String value) {
        this.value = value;
    }

    public Timestamp getCreatedTime() {
        return this.createdTime;
    }

    public void setCreatedTime(Timestamp createdTime) {
        this.createdTime = createdTime;
    }

    public Long getUserId() {
        return this.userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

}
