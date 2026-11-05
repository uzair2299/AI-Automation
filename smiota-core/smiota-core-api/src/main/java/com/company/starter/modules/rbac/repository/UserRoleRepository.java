package com.company.starter.modules.rbac.repository;

import com.company.starter.modules.rbac.entity.Role;
import com.company.starter.modules.rbac.entity.UserRole;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface UserRoleRepository extends JpaRepository<UserRole, UUID> {

    List<UserRole> findByUserId(UUID userId);

    @Query("SELECT ur.role FROM UserRole ur WHERE ur.user.id = :userId AND ur.role.deleted = false")
    List<Role> findRolesByUserId(@Param("userId") UUID userId);

    @Modifying
    @Query("DELETE FROM UserRole ur WHERE ur.user.id = :userId")
    void deleteByUserId(@Param("userId") UUID userId);

    boolean existsByUserIdAndRoleId(UUID userId, UUID roleId);
}

