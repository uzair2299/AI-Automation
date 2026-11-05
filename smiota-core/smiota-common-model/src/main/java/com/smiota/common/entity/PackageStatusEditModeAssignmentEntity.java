package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "package_status_edit_mode_assignment")
public class PackageStatusEditModeAssignmentEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Integer id;

    @Column(name = "package_status_assignment_id", nullable = false)
    private Integer packageStatusAssignmentId;

    @Column(name = "edit_mode", nullable = false)
    private Integer editMode;

    public PackageStatusEditModeAssignmentEntity() {}

    public Integer getId() {
        return this.id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Integer getPackageStatusAssignmentId() {
        return this.packageStatusAssignmentId;
    }

    public void setPackageStatusAssignmentId(Integer packageStatusAssignmentId) {
        this.packageStatusAssignmentId = packageStatusAssignmentId;
    }

    public Integer getEditMode() {
        return this.editMode;
    }

    public void setEditMode(Integer editMode) {
        this.editMode = editMode;
    }

}
