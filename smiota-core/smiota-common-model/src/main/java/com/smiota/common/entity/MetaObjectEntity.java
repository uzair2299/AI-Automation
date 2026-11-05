package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.util.Objects;

@Entity
@Table(name = "META_OBJECT")
public class MetaObjectEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "ID")
    private Long id;

    @Column(name = "NAME", length = 255)
    private String name;

    @Column(name = "DISPLAY_NAME", length = 255)
    private String displayName;

    @Column(name = "DISPLAY_NAME_PLURAL", length = 255)
    private String displayNamePlural;

    @Column(name = "PRIMARY_DISPLAY_COLUMN", length = 100)
    private String primaryDisplayColumn;

    public MetaObjectEntity() {}

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

    public String getDisplayName() {
        return this.displayName;
    }

    public void setDisplayName(String displayName) {
        this.displayName = displayName;
    }

    public String getDisplayNamePlural() {
        return this.displayNamePlural;
    }

    public void setDisplayNamePlural(String displayNamePlural) {
        this.displayNamePlural = displayNamePlural;
    }

    public String getPrimaryDisplayColumn() {
        return this.primaryDisplayColumn;
    }

    public void setPrimaryDisplayColumn(String primaryDisplayColumn) {
        this.primaryDisplayColumn = primaryDisplayColumn;
    }

}
