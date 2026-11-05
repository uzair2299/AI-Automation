package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "PACKAGE_GROUP_STATUS_TO_PACKAGE_STATUS")
public class PackageGroupStatusToPackageStatusEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Integer id;

    @Column(name = "package_group_status_id")
    private Long packageGroupStatusId;

    @Column(name = "package_status_id")
    private Integer packageStatusId;

    @Column(name = "customerid")
    private Long customerid;

    @Column(name = "locationid")
    private Long locationid;

    public PackageGroupStatusToPackageStatusEntity() {}

    public Integer getId() {
        return this.id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Long getPackageGroupStatusId() {
        return this.packageGroupStatusId;
    }

    public void setPackageGroupStatusId(Long packageGroupStatusId) {
        this.packageGroupStatusId = packageGroupStatusId;
    }

    public Integer getPackageStatusId() {
        return this.packageStatusId;
    }

    public void setPackageStatusId(Integer packageStatusId) {
        this.packageStatusId = packageStatusId;
    }

    public Long getCustomerid() {
        return this.customerid;
    }

    public void setCustomerid(Long customerid) {
        this.customerid = customerid;
    }

    public Long getLocationid() {
        return this.locationid;
    }

    public void setLocationid(Long locationid) {
        this.locationid = locationid;
    }

}
