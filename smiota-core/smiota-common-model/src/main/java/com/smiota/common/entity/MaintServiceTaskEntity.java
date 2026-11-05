package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "MAINT_SERVICE_TASK")
public class MaintServiceTaskEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "MAINT_SERVICE_ID", nullable = false)
    private Long maintServiceId;

    @Column(name = "MAINT_TASK_ID", nullable = false)
    private Long maintTaskId;

    @Column(name = "NOTE", length = 1000)
    private String note;

    @Column(name = "IS_COMPLETE")
    private Boolean isComplete;

    public MaintServiceTaskEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Long getMaintServiceId() {
        return this.maintServiceId;
    }

    public void setMaintServiceId(Long maintServiceId) {
        this.maintServiceId = maintServiceId;
    }

    public Long getMaintTaskId() {
        return this.maintTaskId;
    }

    public void setMaintTaskId(Long maintTaskId) {
        this.maintTaskId = maintTaskId;
    }

    public String getNote() {
        return this.note;
    }

    public void setNote(String note) {
        this.note = note;
    }

    public Boolean isComplete() {
        return this.isComplete;
    }

    public void setIsComplete(Boolean isComplete) {
        this.isComplete = isComplete;
    }

}
