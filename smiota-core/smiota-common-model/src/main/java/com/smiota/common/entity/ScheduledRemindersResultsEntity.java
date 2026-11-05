package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "scheduled_reminders_results")
public class ScheduledRemindersResultsEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "customer_id", nullable = false)
    private Long customerId;

    @Column(name = "location_id", nullable = false)
    private Long locationId;

    @Column(name = "num_of_users", nullable = false)
    private Integer numOfUsers;

    @Column(name = "process_time", nullable = false)
    private Timestamp processTime;

    @Column(name = "scheduled_time", nullable = false)
    private Timestamp scheduledTime;

    @Column(name = "is_ran_at_scheduled_time", nullable = false)
    private Boolean isRanAtScheduledTime;

    public ScheduledRemindersResultsEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    public Long getLocationId() {
        return this.locationId;
    }

    public void setLocationId(Long locationId) {
        this.locationId = locationId;
    }

    public Integer getNumOfUsers() {
        return this.numOfUsers;
    }

    public void setNumOfUsers(Integer numOfUsers) {
        this.numOfUsers = numOfUsers;
    }

    public Timestamp getProcessTime() {
        return this.processTime;
    }

    public void setProcessTime(Timestamp processTime) {
        this.processTime = processTime;
    }

    public Timestamp getScheduledTime() {
        return this.scheduledTime;
    }

    public void setScheduledTime(Timestamp scheduledTime) {
        this.scheduledTime = scheduledTime;
    }

    public Boolean isRanAtScheduledTime() {
        return this.isRanAtScheduledTime;
    }

    public void setIsRanAtScheduledTime(Boolean isRanAtScheduledTime) {
        this.isRanAtScheduledTime = isRanAtScheduledTime;
    }

}
