package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "reserve_status_transition")
public class ReserveStatusTransitionEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @Column(name = "id", length = 36)
    private String id;

    @Column(name = "reserve_status_id", nullable = false, length = 36)
    private String reserveStatusId;

    @Column(name = "reserve_allowed_status_id", nullable = false, length = 36)
    private String reserveAllowedStatusId;

    public ReserveStatusTransitionEntity() {}

    public String getId() {
        return this.id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getReserveStatusId() {
        return this.reserveStatusId;
    }

    public void setReserveStatusId(String reserveStatusId) {
        this.reserveStatusId = reserveStatusId;
    }

    public String getReserveAllowedStatusId() {
        return this.reserveAllowedStatusId;
    }

    public void setReserveAllowedStatusId(String reserveAllowedStatusId) {
        this.reserveAllowedStatusId = reserveAllowedStatusId;
    }

}
