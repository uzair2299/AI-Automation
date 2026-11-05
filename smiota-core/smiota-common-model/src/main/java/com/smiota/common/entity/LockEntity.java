package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "lock")
public class LockEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "label", length = 255)
    private String label;

    @Column(name = "inactive")
    private Boolean inactive;

    @Column(name = "is_defective")
    private Boolean isDefective;

    @Column(name = "battery_percentage")
    private Boolean batteryPercentage;

    @Column(name = "passcode", length = 10)
    private String passcode;

    @Column(name = "is_wheelchair_accessible")
    private Boolean isWheelchairAccessible;

    @Column(name = "serial", length = 255)
    private String serial;

    @Column(name = "customer_id", nullable = false)
    private Long customerId;

    @Column(name = "day_use_pod_id")
    private Long dayUsePodId;

    @Column(name = "UUID", length = 36)
    private String uuid;

    @Column(name = "assigned_to")
    private Long assignedTo;

    @Column(name = "last_modified_time")
    private Timestamp lastModifiedTime;

    @Column(name = "updated_by")
    private Long updatedBy;

    @Column(name = "assignment_start")
    private Timestamp assignmentStart;

    @Column(name = "assignment_end")
    private Timestamp assignmentEnd;

    public LockEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getLabel() {
        return this.label;
    }

    public void setLabel(String label) {
        this.label = label;
    }

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
    }

    public Boolean isDefective() {
        return this.isDefective;
    }

    public void setIsDefective(Boolean isDefective) {
        this.isDefective = isDefective;
    }

    public Boolean getBatteryPercentage() {
        return this.batteryPercentage;
    }

    public void setBatteryPercentage(Boolean batteryPercentage) {
        this.batteryPercentage = batteryPercentage;
    }

    public String getPasscode() {
        return this.passcode;
    }

    public void setPasscode(String passcode) {
        this.passcode = passcode;
    }

    public Boolean isWheelchairAccessible() {
        return this.isWheelchairAccessible;
    }

    public void setIsWheelchairAccessible(Boolean isWheelchairAccessible) {
        this.isWheelchairAccessible = isWheelchairAccessible;
    }

    public String getSerial() {
        return this.serial;
    }

    public void setSerial(String serial) {
        this.serial = serial;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    public Long getDayUsePodId() {
        return this.dayUsePodId;
    }

    public void setDayUsePodId(Long dayUsePodId) {
        this.dayUsePodId = dayUsePodId;
    }

    public String getUuid() {
        return this.uuid;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }

    public Long getAssignedTo() {
        return this.assignedTo;
    }

    public void setAssignedTo(Long assignedTo) {
        this.assignedTo = assignedTo;
    }

    public Timestamp getLastModifiedTime() {
        return this.lastModifiedTime;
    }

    public void setLastModifiedTime(Timestamp lastModifiedTime) {
        this.lastModifiedTime = lastModifiedTime;
    }

    public Long getUpdatedBy() {
        return this.updatedBy;
    }

    public void setUpdatedBy(Long updatedBy) {
        this.updatedBy = updatedBy;
    }

    public Timestamp getAssignmentStart() {
        return this.assignmentStart;
    }

    public void setAssignmentStart(Timestamp assignmentStart) {
        this.assignmentStart = assignmentStart;
    }

    public Timestamp getAssignmentEnd() {
        return this.assignmentEnd;
    }

    public void setAssignmentEnd(Timestamp assignmentEnd) {
        this.assignmentEnd = assignmentEnd;
    }

}
