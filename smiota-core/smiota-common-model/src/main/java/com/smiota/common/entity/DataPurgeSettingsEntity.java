package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "data_purge_settings")
public class DataPurgeSettingsEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "customer_id", nullable = false)
    private Long customerId;

    @Column(name = "enable_data_purge")
    private Boolean enableDataPurge;

    @Column(name = "data_purge_months", nullable = false)
    private Integer dataPurgeMonths;

    @Column(name = "data_purge_frequency_id", nullable = false)
    private Integer dataPurgeFrequencyId;

    @Column(name = "created_by")
    private Long createdBy;

    @Column(name = "last_modified_by")
    private Long lastModifiedBy;

    @Column(name = "created_time")
    private Timestamp createdTime;

    @Column(name = "last_modified_time")
    private Timestamp lastModifiedTime;

    @Column(name = "delete_courier_users")
    private Boolean deleteCourierUsers;

    @Column(name = "is_test_run")
    private Boolean isTestRun;

    @Column(name = "result_email", length = 1000)
    private String resultEmail;

    public DataPurgeSettingsEntity() {}

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

    public Boolean getEnableDataPurge() {
        return this.enableDataPurge;
    }

    public void setEnableDataPurge(Boolean enableDataPurge) {
        this.enableDataPurge = enableDataPurge;
    }

    public Integer getDataPurgeMonths() {
        return this.dataPurgeMonths;
    }

    public void setDataPurgeMonths(Integer dataPurgeMonths) {
        this.dataPurgeMonths = dataPurgeMonths;
    }

    public Integer getDataPurgeFrequencyId() {
        return this.dataPurgeFrequencyId;
    }

    public void setDataPurgeFrequencyId(Integer dataPurgeFrequencyId) {
        this.dataPurgeFrequencyId = dataPurgeFrequencyId;
    }

    public Long getCreatedBy() {
        return this.createdBy;
    }

    public void setCreatedBy(Long createdBy) {
        this.createdBy = createdBy;
    }

    public Long getLastModifiedBy() {
        return this.lastModifiedBy;
    }

    public void setLastModifiedBy(Long lastModifiedBy) {
        this.lastModifiedBy = lastModifiedBy;
    }

    public Timestamp getCreatedTime() {
        return this.createdTime;
    }

    public void setCreatedTime(Timestamp createdTime) {
        this.createdTime = createdTime;
    }

    public Timestamp getLastModifiedTime() {
        return this.lastModifiedTime;
    }

    public void setLastModifiedTime(Timestamp lastModifiedTime) {
        this.lastModifiedTime = lastModifiedTime;
    }

    public Boolean getDeleteCourierUsers() {
        return this.deleteCourierUsers;
    }

    public void setDeleteCourierUsers(Boolean deleteCourierUsers) {
        this.deleteCourierUsers = deleteCourierUsers;
    }

    public Boolean isTestRun() {
        return this.isTestRun;
    }

    public void setIsTestRun(Boolean isTestRun) {
        this.isTestRun = isTestRun;
    }

    public String getResultEmail() {
        return this.resultEmail;
    }

    public void setResultEmail(String resultEmail) {
        this.resultEmail = resultEmail;
    }

}
