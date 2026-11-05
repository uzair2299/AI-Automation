package com.company.starter.modules.navigation.entity;

import com.company.starter.modules.navigation.dto.NavigationSection;
import com.company.starter.shared.entity.BaseSoftDeleteEntity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import jakarta.persistence.OrderBy;
import jakarta.persistence.Table;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.SuperBuilder;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/**
 * Recursive navigation menu item entity with self-referencing hierarchy.
 */
@Getter
@Setter
@SuperBuilder
@NoArgsConstructor
@Entity
@Table(name = "sec_menu_items")
public class MenuItem extends BaseSoftDeleteEntity {

    @Column(name = "parent_id")
    private UUID parentId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_id", insertable = false, updatable = false)
    private MenuItem parent;

    @Builder.Default
    @OneToMany(mappedBy = "parent")
    @OrderBy("sortOrder ASC")
    private Set<MenuItem> children = new HashSet<>();

    @Column(name = "title", nullable = false, length = 100)
    private String title;

    @Column(name = "icon", length = 100)
    private String icon;

    @Column(name = "path", length = 255)
    private String path;

    @Column(name = "permission_code", length = 100)
    private String permissionCode;

    @Builder.Default
    @Enumerated(EnumType.STRING)
    @Column(name = "layout_section", nullable = false, length = 50)
    private NavigationSection layoutSection = NavigationSection.SIDEBAR;

    @Builder.Default
    @Column(name = "sort_order")
    private Integer sortOrder = 0;

    @Builder.Default
    @Column(name = "active", nullable = false)
    private Boolean active = Boolean.TRUE;
}

