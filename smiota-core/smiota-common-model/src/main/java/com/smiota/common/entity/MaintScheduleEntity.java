package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.sql.Time;
import java.util.Objects;

@Entity
@Table(name = "MAINT_SCHEDULE")
public class MaintScheduleEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "MAINT_LOCATION_ID", nullable = false)
    private Long maintLocationId;

    @Column(name = "INACTIVE", nullable = false)
    private Boolean inactive;

    @Column(name = "MAINT_FREQUENCY_ID", nullable = false)
    private Integer maintFrequencyId;

    @Column(name = "MAINT_FREQUENCY_VALUE", length = 128)
    private String maintFrequencyValue;

    @Column(name = "START_TIME")
    private Time startTime;

    @Column(name = "END_TIME")
    private Time endTime;

    @Column(name = "CREATED_TIME")
    private Timestamp createdTime;

    @Column(name = "CREATED_BY", nullable = false)
    private Long createdBy;

    @Column(name = "MODIFIED_TIME")
    private Timestamp modifiedTime;

    @Column(name = "UPDATED_BY", nullable = false)
    private Long updatedBy;

    public MaintScheduleEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getMaintLocationId() {
        return this.maintLocationId;
    }

    public void setMaintLocationId(Long maintLocationId) {
        this.maintLocationId = maintLocationId;
    }

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
    }

    public Integer getMaintFrequencyId() {
        return this.maintFrequencyId;
    }

    public void setMaintFrequencyId(Integer maintFrequencyId) {
        this.maintFrequencyId = maintFrequencyId;
    }

    public String getMaintFrequencyValue() {
        return this.maintFrequencyValue;
    }

    public void setMaintFrequencyValue(String maintFrequencyValue) {
        this.maintFrequencyValue = maintFrequencyValue;
    }

    public Time getStartTime() {
        return this.startTime;
    }

    public void setStartTime(Time startTime) {
        this.startTime = startTime;
    }

    public Time getEndTime() {
        return this.endTime;
    }

    public void setEndTime(Time endTime) {
        this.endTime = endTime;
    }

    public Timestamp getCreatedTime() {
        return this.createdTime;
    }

    public void setCreatedTime(Timestamp createdTime) {
        this.createdTime = createdTime;
    }

    public Long getCreatedBy() {
        return this.createdBy;
    }

    public void setCreatedBy(Long createdBy) {
        this.createdBy = createdBy;
    }

    public Timestamp getModifiedTime() {
        return this.modifiedTime;
    }

    public void setModifiedTime(Timestamp modifiedTime) {
        this.modifiedTime = modifiedTime;
    }

    public Long getUpdatedBy() {
        return this.updatedBy;
    }

    public void setUpdatedBy(Long updatedBy) {
        this.updatedBy = updatedBy;
    }

}
