package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "SCIM_GROUP_MEMBERS")
public class ScimGroupMembersEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "scim_group_id", nullable = false, length = 36)
    private String scimGroupId;

    @Column(name = "scim_resource_id", nullable = false, length = 36)
    private String scimResourceId;

    public ScimGroupMembersEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getScimGroupId() {
        return this.scimGroupId;
    }

    public void setScimGroupId(String scimGroupId) {
        this.scimGroupId = scimGroupId;
    }

    public String getScimResourceId() {
        return this.scimResourceId;
    }

    public void setScimResourceId(String scimResourceId) {
        this.scimResourceId = scimResourceId;
    }

}
