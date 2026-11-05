package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "SCIM_USER_MAP")
public class ScimUserMapEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "scim_user_id", nullable = false, length = 36)
    private String scimUserId;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    public ScimUserMapEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getScimUserId() {
        return this.scimUserId;
    }

    public void setScimUserId(String scimUserId) {
        this.scimUserId = scimUserId;
    }

    public Long getUserId() {
        return this.userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

}
