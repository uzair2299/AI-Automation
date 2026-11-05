package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "SUPER_LOCKER_ADMINS")
public class SuperLockerAdminsEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @Column(name = "ID")
    private Integer id;

    @Column(name = "FIRST_NAME", length = 255)
    private String firstName;

    @Column(name = "LAST_NAME", length = 255)
    private String lastName;

    @Column(name = "PHONE", length = 255)
    private String phone;

    @Column(name = "EMAIL", length = 255)
    private String email;

    @Column(name = "INACTIVE")
    private Boolean inactive;

    @Column(name = "NOTIFY_ON_ERROR")
    private Boolean notifyOnError;

    public SuperLockerAdminsEntity() {}

    public Integer getId() {
        return this.id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getFirstName() {
        return this.firstName;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public String getLastName() {
        return this.lastName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public String getPhone() {
        return this.phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getEmail() {
        return this.email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
    }

    public Boolean getNotifyOnError() {
        return this.notifyOnError;
    }

    public void setNotifyOnError(Boolean notifyOnError) {
        this.notifyOnError = notifyOnError;
    }

}
