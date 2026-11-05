package com.company.starter.modules.rbac.repository;

import com.company.starter.modules.rbac.entity.Resource;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface ResourceRepository extends JpaRepository<Resource, UUID> {

    Optional<Resource> findByCode(String code);

    boolean existsByCode(String code);

    List<Resource> findByModuleId(UUID moduleId);
}

