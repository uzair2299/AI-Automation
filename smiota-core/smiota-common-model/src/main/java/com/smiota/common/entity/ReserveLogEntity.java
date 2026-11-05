package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "reserve_log")
public class ReserveLogEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @Column(name = "id", length = 36)
    private String id;

    @Column(name = "reserve_id", nullable = false, length = 36)
    private String reserveId;

    @Column(name = "reserve_status_id", nullable = false, length = 36)
    private String reserveStatusId;

    @Column(name = "start_time", nullable = false)
    private Timestamp startTime;

    @Column(name = "end_time", nullable = false)
    private Timestamp endTime;

    @Column(name = "hold_start_time", nullable = false)
    private Timestamp holdStartTime;

    @Column(name = "hold_end_time", nullable = false)
    private Timestamp holdEndTime;

    @Column(name = "created_at", nullable = false)
    private Timestamp createdAt;

    @Column(name = "created_by_user_id")
    private Long createdByUserId;

    @Column(name = "notes", length = 128)
    private String notes;

    public ReserveLogEntity() {}

    public String getId() {
        return this.id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getReserveId() {
        return this.reserveId;
    }

    public void setReserveId(String reserveId) {
        this.reserveId = reserveId;
    }

    public String getReserveStatusId() {
        return this.reserveStatusId;
    }

    public void setReserveStatusId(String reserveStatusId) {
        this.reserveStatusId = reserveStatusId;
    }

    public Timestamp getStartTime() {
        return this.startTime;
    }

    public void setStartTime(Timestamp startTime) {
        this.startTime = startTime;
    }

    public Timestamp getEndTime() {
        return this.endTime;
    }

    public void setEndTime(Timestamp endTime) {
        this.endTime = endTime;
    }

    public Timestamp getHoldStartTime() {
        return this.holdStartTime;
    }

    public void setHoldStartTime(Timestamp holdStartTime) {
        this.holdStartTime = holdStartTime;
    }

    public Timestamp getHoldEndTime() {
        return this.holdEndTime;
    }

    public void setHoldEndTime(Timestamp holdEndTime) {
        this.holdEndTime = holdEndTime;
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

    public String getNotes() {
        return this.notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }

}
