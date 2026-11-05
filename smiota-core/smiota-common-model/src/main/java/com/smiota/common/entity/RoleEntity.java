package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "ROLE")
public class RoleEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @Column(name = "ID")
    private Integer id;

    @Column(name = "NAME", nullable = false, length = 100)
    private String name;

    @Column(name = "COMMENT", length = 1000)
    private String comment;

    @Column(name = "DISPLAY_NAME", length = 64)
    private String displayName;

    @Column(name = "ROLE_LEVEL_ID")
    private Integer roleLevelId;

    public RoleEntity() {}

    public Integer getId() {
        return this.id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getName() {
        return this.name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getComment() {
        return this.comment;
    }

    public void setComment(String comment) {
        this.comment = comment;
    }

    public String getDisplayName() {
        return this.displayName;
    }

    public void setDisplayName(String displayName) {
        this.displayName = displayName;
    }

    public Integer getRoleLevelId() {
        return this.roleLevelId;
    }

    public void setRoleLevelId(Integer roleLevelId) {
        this.roleLevelId = roleLevelId;
    }

}
