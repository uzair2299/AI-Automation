package com.company.starter.modules.rbac.repository;

import com.company.starter.modules.rbac.entity.Permission;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

@Repository
public interface PermissionRepository extends JpaRepository<Permission, UUID> {

    Optional<Permission> findByCode(String code);

    boolean existsByCode(String code);

    List<Permission> findByResourceId(UUID resourceId);

    @Query("SELECT p FROM Permission p WHERE p.code IN :codes")
    List<Permission> findByCodeIn(@Param("codes") Collection<String> codes);

    @Query("SELECT DISTINCT p.code FROM RolePermission rp " +
            "JOIN rp.permission p " +
            "JOIN rp.role r " +
            "WHERE r.code IN :roleCodes AND r.deleted = false AND r.active = true")
    Set<String> findPermissionCodesByRoleCodes(@Param("roleCodes") Collection<String> roleCodes);
}

