package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "package_advanced_properties")
public class PackageAdvancedPropertiesEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Integer id;

    @Column(name = "package_id", nullable = false)
    private Long packageId;

    @Column(name = "po_number", length = 255)
    private String poNumber;

    @Column(name = "deliver_to_recipient")
    private Long deliverToRecipient;

    @Column(name = "package_content_type")
    private Integer packageContentType;

    @Column(name = "package_problem_reason")
    private Integer packageProblemReason;

    @Column(name = "is_perishable")
    private Boolean isPerishable;

    @Column(name = "number_of_subitems")
    private Integer numberOfSubitems;

    @Column(name = "locker_size_id")
    private Integer lockerSizeId;

    @Column(name = "locker_type_id")
    private Integer lockerTypeId;

    @Column(name = "pickup_delivery_external_id", length = 128)
    private String pickupDeliveryExternalId;

    @Column(name = "receive_transaction_id")
    private Long receiveTransactionId;

    @Column(name = "release_transaction_id")
    private Long releaseTransactionId;

    public PackageAdvancedPropertiesEntity() {}

    public Integer getId() {
        return this.id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Long getPackageId() {
        return this.packageId;
    }

    public void setPackageId(Long packageId) {
        this.packageId = packageId;
    }

    public String getPoNumber() {
        return this.poNumber;
    }

    public void setPoNumber(String poNumber) {
        this.poNumber = poNumber;
    }

    public Long getDeliverToRecipient() {
        return this.deliverToRecipient;
    }

    public void setDeliverToRecipient(Long deliverToRecipient) {
        this.deliverToRecipient = deliverToRecipient;
    }

    public Integer getPackageContentType() {
        return this.packageContentType;
    }

    public void setPackageContentType(Integer packageContentType) {
        this.packageContentType = packageContentType;
    }

    public Integer getPackageProblemReason() {
        return this.packageProblemReason;
    }

    public void setPackageProblemReason(Integer packageProblemReason) {
        this.packageProblemReason = packageProblemReason;
    }

    public Boolean isPerishable() {
        return this.isPerishable;
    }

    public void setIsPerishable(Boolean isPerishable) {
        this.isPerishable = isPerishable;
    }

    public Integer getNumberOfSubitems() {
        return this.numberOfSubitems;
    }

    public void setNumberOfSubitems(Integer numberOfSubitems) {
        this.numberOfSubitems = numberOfSubitems;
    }

    public Integer getLockerSizeId() {
        return this.lockerSizeId;
    }

    public void setLockerSizeId(Integer lockerSizeId) {
        this.lockerSizeId = lockerSizeId;
    }

    public Integer getLockerTypeId() {
        return this.lockerTypeId;
    }

    public void setLockerTypeId(Integer lockerTypeId) {
        this.lockerTypeId = lockerTypeId;
    }

    public String getPickupDeliveryExternalId() {
        return this.pickupDeliveryExternalId;
    }

    public void setPickupDeliveryExternalId(String pickupDeliveryExternalId) {
        this.pickupDeliveryExternalId = pickupDeliveryExternalId;
    }

    public Long getReceiveTransactionId() {
        return this.receiveTransactionId;
    }

    public void setReceiveTransactionId(Long receiveTransactionId) {
        this.receiveTransactionId = receiveTransactionId;
    }

    public Long getReleaseTransactionId() {
        return this.releaseTransactionId;
    }

    public void setReleaseTransactionId(Long releaseTransactionId) {
        this.releaseTransactionId = releaseTransactionId;
    }

}
