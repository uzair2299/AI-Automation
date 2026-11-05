package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "integration_retry")
public class IntegrationRetryEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Integer id;

    @Column(name = "type", nullable = false, length = 255)
    private String type;

    @Column(name = "data", nullable = false)
    private String data;

    @Column(name = "retrycount")
    private Integer retrycount;

    public IntegrationRetryEntity() {}

    public Integer getId() {
        return this.id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getType() {
        return this.type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getData() {
        return this.data;
    }

    public void setData(String data) {
        this.data = data;
    }

    public Integer getRetrycount() {
        return this.retrycount;
    }

    public void setRetrycount(Integer retrycount) {
        this.retrycount = retrycount;
    }

}
