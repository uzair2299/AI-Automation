package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "PACKAGE_RELEASE_BLOBS")
public class PackageReleaseBlobsEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "PACKAGE_ID")
    private Long packageId;

    @Column(name = "SIGNATURE")
    private byte[] signature;

    @Column(name = "ID_PHOTO")
    private byte[] idPhoto;

    @Column(name = "PACKAGE_STATUS_LOG_ID")
    private Long packageStatusLogId;

    @Column(name = "PACKAGE_STATUS_ID")
    private Integer packageStatusId;

    @Column(name = "CREATED_TIME")
    private Timestamp createdTime;

    @Column(name = "CREATED_BY_USER_ID")
    private Long createdByUserId;

    @Column(name = "SOURCE_APP_ID", length = 50)
    private String sourceAppId;

    public PackageReleaseBlobsEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getPackageId() {
        return this.packageId;
    }

    public void setPackageId(Long packageId) {
        this.packageId = packageId;
    }

    public byte[] getSignature() {
        return this.signature;
    }

    public void setSignature(byte[] signature) {
        this.signature = signature;
    }

    public byte[] getIdPhoto() {
        return this.idPhoto;
    }

    public void setIdPhoto(byte[] idPhoto) {
        this.idPhoto = idPhoto;
    }

    public Long getPackageStatusLogId() {
        return this.packageStatusLogId;
    }

    public void setPackageStatusLogId(Long packageStatusLogId) {
        this.packageStatusLogId = packageStatusLogId;
    }

    public Integer getPackageStatusId() {
        return this.packageStatusId;
    }

    public void setPackageStatusId(Integer packageStatusId) {
        this.packageStatusId = packageStatusId;
    }

    public Timestamp getCreatedTime() {
        return this.createdTime;
    }

    public void setCreatedTime(Timestamp createdTime) {
        this.createdTime = createdTime;
    }

    public Long getCreatedByUserId() {
        return this.createdByUserId;
    }

    public void setCreatedByUserId(Long createdByUserId) {
        this.createdByUserId = createdByUserId;
    }

    public String getSourceAppId() {
        return this.sourceAppId;
    }

    public void setSourceAppId(String sourceAppId) {
        this.sourceAppId = sourceAppId;
    }

}
