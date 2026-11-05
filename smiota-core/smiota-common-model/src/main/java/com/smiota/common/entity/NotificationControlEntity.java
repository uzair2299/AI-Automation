package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "notification_control")
public class NotificationControlEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Integer id;

    @Column(name = "notification_template_id")
    private Integer notificationTemplateId;

    @Column(name = "tag_id")
    private Integer tagId;

    @Column(name = "to_actual_recipient")
    private Integer toActualRecipient;

    @Column(name = "to_delegated_recipient")
    private Integer toDelegatedRecipient;

    @Column(name = "to_alternate_recipient")
    private Integer toAlternateRecipient;

    @Column(name = "to_location_admin")
    private Integer toLocationAdmin;

    @Column(name = "to_external_recipients")
    private Integer toExternalRecipients;

    @Column(name = "to_external_emails")
    private Integer toExternalEmails;

    @Column(name = "disable_all_notifications")
    private Integer disableAllNotifications;

    public NotificationControlEntity() {}

    public Integer getId() {
        return this.id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getNotificationTemplateId() {
        return this.notificationTemplateId;
    }

    public void setNotificationTemplateId(Integer notificationTemplateId) {
        this.notificationTemplateId = notificationTemplateId;
    }

    public Integer getTagId() {
        return this.tagId;
    }

    public void setTagId(Integer tagId) {
        this.tagId = tagId;
    }

    public Integer getToActualRecipient() {
        return this.toActualRecipient;
    }

    public void setToActualRecipient(Integer toActualRecipient) {
        this.toActualRecipient = toActualRecipient;
    }

    public Integer getToDelegatedRecipient() {
        return this.toDelegatedRecipient;
    }

    public void setToDelegatedRecipient(Integer toDelegatedRecipient) {
        this.toDelegatedRecipient = toDelegatedRecipient;
    }

    public Integer getToAlternateRecipient() {
        return this.toAlternateRecipient;
    }

    public void setToAlternateRecipient(Integer toAlternateRecipient) {
        this.toAlternateRecipient = toAlternateRecipient;
    }

    public Integer getToLocationAdmin() {
        return this.toLocationAdmin;
    }

    public void setToLocationAdmin(Integer toLocationAdmin) {
        this.toLocationAdmin = toLocationAdmin;
    }

    public Integer getToExternalRecipients() {
        return this.toExternalRecipients;
    }

    public void setToExternalRecipients(Integer toExternalRecipients) {
        this.toExternalRecipients = toExternalRecipients;
    }

    public Integer getToExternalEmails() {
        return this.toExternalEmails;
    }

    public void setToExternalEmails(Integer toExternalEmails) {
        this.toExternalEmails = toExternalEmails;
    }

    public Integer getDisableAllNotifications() {
        return this.disableAllNotifications;
    }

    public void setDisableAllNotifications(Integer disableAllNotifications) {
        this.disableAllNotifications = disableAllNotifications;
    }

}
