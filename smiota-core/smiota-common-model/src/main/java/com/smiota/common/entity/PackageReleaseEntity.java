package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "PACKAGE_RELEASE")
public class PackageReleaseEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "PACKAGE_ID")
    private Long packageId;

    @Column(name = "RELEASE_TO_USER_ID")
    private Long releaseToUserId;

    @Column(name = "RELEASE_TO_NAME", length = 300)
    private String releaseToName;

    @Column(name = "RELEASE_TO_EXTERNAL")
    private Boolean releaseToExternal;

    @Column(name = "RELEASED_BY_USER_ID")
    private Long releasedByUserId;

    @Column(name = "TIME_RELEASED")
    private Timestamp timeReleased;

    @Column(name = "NOTES", length = 1000)
    private String notes;

    @Column(name = "ID_NUMBER", length = 200)
    private String idNumber;

    @Column(name = "ID_TYPE", length = 200)
    private String idType;

    @Column(name = "CUSTOMER_ID")
    private Long customerId;

    @Column(name = "LOCATION_ID")
    private Long locationId;

    @Column(name = "LAST_MODIFIED_TIME")
    private Timestamp lastModifiedTime;

    public PackageReleaseEntity() {}

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

    public Long getReleaseToUserId() {
        return this.releaseToUserId;
    }

    public void setReleaseToUserId(Long releaseToUserId) {
        this.releaseToUserId = releaseToUserId;
    }

    public String getReleaseToName() {
        return this.releaseToName;
    }

    public void setReleaseToName(String releaseToName) {
        this.releaseToName = releaseToName;
    }

    public Boolean getReleaseToExternal() {
        return this.releaseToExternal;
    }

    public void setReleaseToExternal(Boolean releaseToExternal) {
        this.releaseToExternal = releaseToExternal;
    }

    public Long getReleasedByUserId() {
        return this.releasedByUserId;
    }

    public void setReleasedByUserId(Long releasedByUserId) {
        this.releasedByUserId = releasedByUserId;
    }

    public Timestamp getTimeReleased() {
        return this.timeReleased;
    }

    public void setTimeReleased(Timestamp timeReleased) {
        this.timeReleased = timeReleased;
    }

    public String getNotes() {
        return this.notes;
    }

    public void setNotes(String notes) {
        this.notes = notes;
    }

    public String getIdNumber() {
        return this.idNumber;
    }

    public void setIdNumber(String idNumber) {
        this.idNumber = idNumber;
    }

    public String getIdType() {
        return this.idType;
    }

    public void setIdType(String idType) {
        this.idType = idType;
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

    public Timestamp getLastModifiedTime() {
        return this.lastModifiedTime;
    }

    public void setLastModifiedTime(Timestamp lastModifiedTime) {
        this.lastModifiedTime = lastModifiedTime;
    }

}
