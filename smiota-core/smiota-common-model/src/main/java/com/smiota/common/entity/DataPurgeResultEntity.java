package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "data_purge_result")
public class DataPurgeResultEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "customer_id", nullable = false)
    private Long customerId;

    @Column(name = "start_time", nullable = false)
    private Timestamp startTime;

    @Column(name = "end_time")
    private Timestamp endTime;

    @Column(name = "settings_json", length = 500)
    private String settingsJson;

    @Column(name = "count_json")
    private String countJson;

    @Column(name = "errors_json")
    private String errorsJson;

    @Column(name = "is_test_run")
    private Boolean isTestRun;

    public DataPurgeResultEntity() {}

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

    public String getSettingsJson() {
        return this.settingsJson;
    }

    public void setSettingsJson(String settingsJson) {
        this.settingsJson = settingsJson;
    }

    public String getCountJson() {
        return this.countJson;
    }

    public void setCountJson(String countJson) {
        this.countJson = countJson;
    }

    public String getErrorsJson() {
        return this.errorsJson;
    }

    public void setErrorsJson(String errorsJson) {
        this.errorsJson = errorsJson;
    }

    public Boolean isTestRun() {
        return this.isTestRun;
    }

    public void setIsTestRun(Boolean isTestRun) {
        this.isTestRun = isTestRun;
    }

}
