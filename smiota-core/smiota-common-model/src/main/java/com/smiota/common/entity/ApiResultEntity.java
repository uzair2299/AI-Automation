package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "api_result")
public class ApiResultEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "base_url", length = 255)
    private String baseUrl;

    @Column(name = "context_path", length = 255)
    private String contextPath;

    @Column(name = "method", length = 7)
    private String method;

    @Column(name = "headers", length = 2000)
    private String headers;

    @Column(name = "request_data", length = 2000)
    private String requestData;

    @Column(name = "request_data_type", length = 128)
    private String requestDataType;

    @Column(name = "status_code")
    private Integer statusCode;

    @Column(name = "is_success")
    private Boolean isSuccess;

    @Column(name = "response_data")
    private String responseData;

    @Column(name = "request_time", nullable = false)
    private Timestamp requestTime;

    @Column(name = "customer_id")
    private Long customerId;

    @Column(name = "location_id")
    private Long locationId;

    @Column(name = "last_retry_time")
    private Timestamp lastRetryTime;

    @Column(name = "retry")
    private Boolean retry;

    @Column(name = "created_time", nullable = false)
    private Timestamp createdTime;

    @Column(name = "response_time")
    private Timestamp responseTime;

    @Column(name = "transaction_id", length = 2000)
    private String transactionId;

    public ApiResultEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getBaseUrl() {
        return this.baseUrl;
    }

    public void setBaseUrl(String baseUrl) {
        this.baseUrl = baseUrl;
    }

    public String getContextPath() {
        return this.contextPath;
    }

    public void setContextPath(String contextPath) {
        this.contextPath = contextPath;
    }

    public String getMethod() {
        return this.method;
    }

    public void setMethod(String method) {
        this.method = method;
    }

    public String getHeaders() {
        return this.headers;
    }

    public void setHeaders(String headers) {
        this.headers = headers;
    }

    public String getRequestData() {
        return this.requestData;
    }

    public void setRequestData(String requestData) {
        this.requestData = requestData;
    }

    public String getRequestDataType() {
        return this.requestDataType;
    }

    public void setRequestDataType(String requestDataType) {
        this.requestDataType = requestDataType;
    }

    public Integer getStatusCode() {
        return this.statusCode;
    }

    public void setStatusCode(Integer statusCode) {
        this.statusCode = statusCode;
    }

    public Boolean isSuccess() {
        return this.isSuccess;
    }

    public void setIsSuccess(Boolean isSuccess) {
        this.isSuccess = isSuccess;
    }

    public String getResponseData() {
        return this.responseData;
    }

    public void setResponseData(String responseData) {
        this.responseData = responseData;
    }

    public Timestamp getRequestTime() {
        return this.requestTime;
    }

    public void setRequestTime(Timestamp requestTime) {
        this.requestTime = requestTime;
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

    public Timestamp getLastRetryTime() {
        return this.lastRetryTime;
    }

    public void setLastRetryTime(Timestamp lastRetryTime) {
        this.lastRetryTime = lastRetryTime;
    }

    public Boolean getRetry() {
        return this.retry;
    }

    public void setRetry(Boolean retry) {
        this.retry = retry;
    }

    public Timestamp getCreatedTime() {
        return this.createdTime;
    }

    public void setCreatedTime(Timestamp createdTime) {
        this.createdTime = createdTime;
    }

    public Timestamp getResponseTime() {
        return this.responseTime;
    }

    public void setResponseTime(Timestamp responseTime) {
        this.responseTime = responseTime;
    }

    public String getTransactionId() {
        return this.transactionId;
    }

    public void setTransactionId(String transactionId) {
        this.transactionId = transactionId;
    }

}
