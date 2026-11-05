package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "location_role")
public class LocationRoleEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "location_id", nullable = false)
    private Long locationId;

    @Column(name = "role_id", nullable = false)
    private Integer roleId;

    @Column(name = "refresh_token_expiration_interval", nullable = false)
    private Long refreshTokenExpirationInterval;

    public LocationRoleEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getLocationId() {
        return this.locationId;
    }

    public void setLocationId(Long locationId) {
        this.locationId = locationId;
    }

    public Integer getRoleId() {
        return this.roleId;
    }

    public void setRoleId(Integer roleId) {
        this.roleId = roleId;
    }

    public Long getRefreshTokenExpirationInterval() {
        return this.refreshTokenExpirationInterval;
    }

    public void setRefreshTokenExpirationInterval(Long refreshTokenExpirationInterval) {
        this.refreshTokenExpirationInterval = refreshTokenExpirationInterval;
    }

}
