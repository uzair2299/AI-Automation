package com.company.starter.modules.navigation.repository;

import com.company.starter.modules.navigation.dto.NavigationSection;
import com.company.starter.modules.navigation.entity.MenuItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface MenuItemRepository extends JpaRepository<MenuItem, UUID> {

    List<MenuItem> findByDeletedFalseAndActiveTrueOrderBySortOrderAsc();

    List<MenuItem> findByDeletedFalseAndActiveTrueAndLayoutSectionOrderBySortOrderAsc(NavigationSection layoutSection);

    List<MenuItem> findByDeletedFalseAndParentIdIsNullAndActiveTrueOrderBySortOrderAsc();

    List<MenuItem> findByDeletedFalseAndParentIdAndActiveTrueOrderBySortOrderAsc(UUID parentId);
}

