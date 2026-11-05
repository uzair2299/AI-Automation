package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "reserve_package_log")
public class ReservePackageLogEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @Column(name = "id", length = 36)
    private String id;

    @Column(name = "reserve_package_id", nullable = false, length = 36)
    private String reservePackageId;

    @Column(name = "reserve_id", nullable = false, length = 36)
    private String reserveId;

    @Column(name = "package_id", nullable = false)
    private Long packageId;

    @Column(name = "locker_id")
    private Long lockerId;

    @Column(name = "created_at", nullable = false)
    private Timestamp createdAt;

    @Column(name = "created_by_user_id", nullable = false)
    private Long createdByUserId;

    public ReservePackageLogEntity() {}

    public String getId() {
        return this.id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getReservePackageId() {
        return this.reservePackageId;
    }

    public void setReservePackageId(String reservePackageId) {
        this.reservePackageId = reservePackageId;
    }

    public String getReserveId() {
        return this.reserveId;
    }

    public void setReserveId(String reserveId) {
        this.reserveId = reserveId;
    }

    public Long getPackageId() {
        return this.packageId;
    }

    public void setPackageId(Long packageId) {
        this.packageId = packageId;
    }

    public Long getLockerId() {
        return this.lockerId;
    }

    public void setLockerId(Long lockerId) {
        this.lockerId = lockerId;
    }

    public Timestamp getCreatedAt() {
        return this.createdAt;
    }

    public void setCreatedAt(Timestamp createdAt) {
        this.createdAt = createdAt;
    }

    public Long getCreatedByUserId() {
        return this.createdByUserId;
    }

    public void setCreatedByUserId(Long createdByUserId) {
        this.createdByUserId = createdByUserId;
    }

}
