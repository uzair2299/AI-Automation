package com.company.starter.modules.rbac.repository;

import com.company.starter.modules.rbac.entity.Role;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

@Repository
public interface RoleRepository extends JpaRepository<Role, UUID> {

    Optional<Role> findByCodeAndDeletedFalse(String code);

    Optional<Role> findByCode(String code);

    Optional<Role> findByName(String name);

    boolean existsByCodeAndDeletedFalse(String code);

    boolean existsByCodeAndIdNotAndDeletedFalse(String code, UUID id);

    List<Role> findAllByDeletedFalseAndActiveTrue();

    @Query("SELECT r FROM UserRole ur JOIN ur.role r WHERE ur.user.id = :userId AND r.deleted = false AND r.active = true")
    Set<Role> findRolesByUserId(@Param("userId") UUID userId);

    @Query("SELECT r FROM Role r WHERE r.deleted = false AND " +
            "(:search IS NULL OR LOWER(r.name) LIKE LOWER(CONCAT('%', :search, '%')) OR LOWER(r.code) LIKE LOWER(CONCAT('%', :search, '%')))")
    Page<Role> searchRoles(@Param("search") String search, Pageable pageable);
}

