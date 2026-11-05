package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "BUILDING")
public class BuildingEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "NAME", length = 255)
    private String name;

    @Column(name = "INACTIVE")
    private Boolean inactive;

    @Column(name = "PHONE", length = 20)
    private String phone;

    @Column(name = "EMAIL", length = 255)
    private String email;

    @Column(name = "ADDRESS_LINE1", length = 100)
    private String addressLine1;

    @Column(name = "ADDRESS_LINE2", length = 100)
    private String addressLine2;

    @Column(name = "CITY", length = 100)
    private String city;

    @Column(name = "POST_CODE", length = 10)
    private String postCode;

    @Column(name = "LOCATION_ID", nullable = false)
    private Long locationId;

    @Column(name = "CUSTOMER_ID", nullable = false)
    private Long customerId;

    @Column(name = "LAST_MODIFIED_TIME")
    private Timestamp lastModifiedTime;

    @Column(name = "external_id", length = 100)
    private String externalId;

    @Column(name = "is_receiving_hub")
    private Boolean isReceivingHub;

    @Column(name = "has_package_desk")
    private Boolean hasPackageDesk;

    @Column(name = "HAS_PACKAGE_ROOM")
    private Boolean hasPackageRoom;

    @Column(name = "PACKAGE_ROOM_DISPLAY_NAME", nullable = false, length = 100)
    private String packageRoomDisplayName;

    @Column(name = "PACKAGE_DOESNT_FIT_PACKAGE_LOCATION_MESSAGE_IN_EMAIL", length = 250)
    private String packageDoesntFitPackageLocationMessageInEmail;

    @Column(name = "MAILROOM_DISPLAY_NAME", length = 50)
    private String mailroomDisplayName;

    @Column(name = "OFFICE_HOURS", length = 1000)
    private String officeHours;

    @Column(name = "UUID", length = 36)
    private String uuid;

    public BuildingEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return this.name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Boolean getInactive() {
        return this.inactive;
    }

    public void setInactive(Boolean inactive) {
        this.inactive = inactive;
    }

    public String getPhone() {
        return this.phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getEmail() {
        return this.email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getAddressLine1() {
        return this.addressLine1;
    }

    public void setAddressLine1(String addressLine1) {
        this.addressLine1 = addressLine1;
    }

    public String getAddressLine2() {
        return this.addressLine2;
    }

    public void setAddressLine2(String addressLine2) {
        this.addressLine2 = addressLine2;
    }

    public String getCity() {
        return this.city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    public String getPostCode() {
        return this.postCode;
    }

    public void setPostCode(String postCode) {
        this.postCode = postCode;
    }

    public Long getLocationId() {
        return this.locationId;
    }

    public void setLocationId(Long locationId) {
        this.locationId = locationId;
    }

    public Long getCustomerId() {
        return this.customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    public Timestamp getLastModifiedTime() {
        return this.lastModifiedTime;
    }

    public void setLastModifiedTime(Timestamp lastModifiedTime) {
        this.lastModifiedTime = lastModifiedTime;
    }

    public String getExternalId() {
        return this.externalId;
    }

    public void setExternalId(String externalId) {
        this.externalId = externalId;
    }

    public Boolean isReceivingHub() {
        return this.isReceivingHub;
    }

    public void setIsReceivingHub(Boolean isReceivingHub) {
        this.isReceivingHub = isReceivingHub;
    }

    public Boolean getHasPackageDesk() {
        return this.hasPackageDesk;
    }

    public void setHasPackageDesk(Boolean hasPackageDesk) {
        this.hasPackageDesk = hasPackageDesk;
    }

    public Boolean getHasPackageRoom() {
        return this.hasPackageRoom;
    }

    public void setHasPackageRoom(Boolean hasPackageRoom) {
        this.hasPackageRoom = hasPackageRoom;
    }

    public String getPackageRoomDisplayName() {
        return this.packageRoomDisplayName;
    }

    public void setPackageRoomDisplayName(String packageRoomDisplayName) {
        this.packageRoomDisplayName = packageRoomDisplayName;
    }

    public String getPackageDoesntFitPackageLocationMessageInEmail() {
        return this.packageDoesntFitPackageLocationMessageInEmail;
    }

    public void setPackageDoesntFitPackageLocationMessageInEmail(String packageDoesntFitPackageLocationMessageInEmail) {
        this.packageDoesntFitPackageLocationMessageInEmail = packageDoesntFitPackageLocationMessageInEmail;
    }

    public String getMailroomDisplayName() {
        return this.mailroomDisplayName;
    }

    public void setMailroomDisplayName(String mailroomDisplayName) {
        this.mailroomDisplayName = mailroomDisplayName;
    }

    public String getOfficeHours() {
        return this.officeHours;
    }

    public void setOfficeHours(String officeHours) {
        this.officeHours = officeHours;
    }

    public String getUuid() {
        return this.uuid;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }

}
