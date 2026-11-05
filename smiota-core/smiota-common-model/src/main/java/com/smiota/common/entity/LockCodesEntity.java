package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "lock_codes")
public class LockCodesEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "lock_id", nullable = false)
    private Long lockId;

    @Column(name = "passcode", length = 10)
    private String passcode;

    @Column(name = "user_id")
    private Long userId;

    @Column(name = "time")
    private Timestamp time;

    public LockCodesEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getLockId() {
        return this.lockId;
    }

    public void setLockId(Long lockId) {
        this.lockId = lockId;
    }

    public String getPasscode() {
        return this.passcode;
    }

    public void setPasscode(String passcode) {
        this.passcode = passcode;
    }

    public Long getUserId() {
        return this.userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public Timestamp getTime() {
        return this.time;
    }

    public void setTime(Timestamp time) {
        this.time = time;
    }

}
