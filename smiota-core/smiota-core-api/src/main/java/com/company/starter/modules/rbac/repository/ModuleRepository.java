package com.company.starter.modules.rbac.repository;

import com.company.starter.modules.rbac.entity.Module;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface ModuleRepository extends JpaRepository<Module, UUID> {

    Optional<Module> findByCode(String code);

    boolean existsByCode(String code);

    @Query("SELECT DISTINCT m FROM Module m LEFT JOIN FETCH m.resources r LEFT JOIN FETCH r.permissions WHERE m.active = true ORDER BY m.sortOrder ASC")
    List<Module> findAllWithResourcesAndPermissions();
}

