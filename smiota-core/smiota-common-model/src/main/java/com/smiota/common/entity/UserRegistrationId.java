package com.smiota.common.entity;

import java.io.Serializable;
import java.util.Objects;

public class UserRegistrationId implements Serializable {
    private static final long serialVersionUID = 1L;

    private Integer id;
    private Integer regStatusId;

    public UserRegistrationId() {}

    public UserRegistrationId(Integer id, Integer regStatusId) {
        this.id = id;
        this.regStatusId = regStatusId;
    }

    public Integer getId() { return this.id; }
    public void setId(Integer id) { this.id = id; }

    public Integer getRegStatusId() { return this.regStatusId; }
    public void setRegStatusId(Integer regStatusId) { this.regStatusId = regStatusId; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof UserRegistrationId)) return false;
        UserRegistrationId other = (UserRegistrationId) o;
        return Objects.equals(this.id, other.id) && Objects.equals(this.regStatusId, other.regStatusId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(this.id, this.regStatusId);
    }
}
