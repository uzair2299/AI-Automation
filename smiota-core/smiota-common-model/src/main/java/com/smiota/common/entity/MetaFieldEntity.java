package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "META_FIELD")
public class MetaFieldEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "OBJECT_NAME", length = 255)
    private String objectName;

    @Column(name = "COLUMN_NAME", length = 100)
    private String columnName;

    @Column(name = "COLUMN_DISPLAY_NAME", length = 255)
    private String columnDisplayName;

    @Column(name = "REQUIRED")
    private Boolean required;

    @Column(name = "HIDDEN")
    private Boolean hidden;

    @Column(name = "READ_ONLY")
    private Boolean readOnly;

    @Column(name = "HASHED")
    private Boolean hashed;

    @Column(name = "DISPLAY_TYPE")
    private Integer displayType;

    public MetaFieldEntity() {}

    public Long getId() {
        return this.id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getObjectName() {
        return this.objectName;
    }

    public void setObjectName(String objectName) {
        this.objectName = objectName;
    }

    public String getColumnName() {
        return this.columnName;
    }

    public void setColumnName(String columnName) {
        this.columnName = columnName;
    }

    public String getColumnDisplayName() {
        return this.columnDisplayName;
    }

    public void setColumnDisplayName(String columnDisplayName) {
        this.columnDisplayName = columnDisplayName;
    }

    public Boolean getRequired() {
        return this.required;
    }

    public void setRequired(Boolean required) {
        this.required = required;
    }

    public Boolean getHidden() {
        return this.hidden;
    }

    public void setHidden(Boolean hidden) {
        this.hidden = hidden;
    }

    public Boolean getReadOnly() {
        return this.readOnly;
    }

    public void setReadOnly(Boolean readOnly) {
        this.readOnly = readOnly;
    }

    public Boolean getHashed() {
        return this.hashed;
    }

    public void setHashed(Boolean hashed) {
        this.hashed = hashed;
    }

    public Integer getDisplayType() {
        return this.displayType;
    }

    public void setDisplayType(Integer displayType) {
        this.displayType = displayType;
    }

}
