package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "USER_ROLE")
public class UserRoleEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Integer id;

    @Column(name = "ROLE_ID")
    private Integer roleId;

    @Column(name = "USER_ID")
    private Long userId;

    @Column(name = "SCOPE")
    private Long scope;

    @Column(name = "SCOPE_ID", length = 36)
    private String scopeId;

    @Column(name = "LAST_MODIFIED_TIME")
    private Timestamp lastModifiedTime;

    @Column(name = "v_scope")
    private Long vScope;

    @Column(name = "v_scope_id", length = 36)
    private String vScopeId;

    public UserRoleEntity() {}

    public Integer getId() {
        return this.id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getRoleId() {
        return this.roleId;
    }

    public void setRoleId(Integer roleId) {
        this.roleId = roleId;
    }

    public Long getUserId() {
        return this.userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public Long getScope() {
        return this.scope;
    }

    public void setScope(Long scope) {
        this.scope = scope;
    }

    public String getScopeId() {
        return this.scopeId;
    }

    public void setScopeId(String scopeId) {
        this.scopeId = scopeId;
    }

    public Timestamp getLastModifiedTime() {
        return this.lastModifiedTime;
    }

    public void setLastModifiedTime(Timestamp lastModifiedTime) {
        this.lastModifiedTime = lastModifiedTime;
    }

    public Long getVScope() {
        return this.vScope;
    }

    public void setVScope(Long vScope) {
        this.vScope = vScope;
    }

    public String getVScopeId() {
        return this.vScopeId;
    }

    public void setVScopeId(String vScopeId) {
        this.vScopeId = vScopeId;
    }

}
