package com.company.starter.modules.identity.repository;

import com.company.starter.modules.identity.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface UserRepository extends JpaRepository<User, UUID>, JpaSpecificationExecutor<User> {

    @Query("SELECT u FROM User u LEFT JOIN FETCH u.profile WHERE u.username = :username AND u.deleted = false")
    Optional<User> findByUsername(@Param("username") String username);

    @Query("SELECT u FROM User u LEFT JOIN FETCH u.profile WHERE u.email = :email AND u.deleted = false")
    Optional<User> findByEmail(@Param("email") String email);

    @Query("SELECT u FROM User u LEFT JOIN FETCH u.profile WHERE (u.username = :identifier OR u.email = :identifier) AND u.deleted = false")
    Optional<User> findByUsernameOrEmail(@Param("identifier") String identifier);

    boolean existsByUsernameAndDeletedFalse(String username);

    boolean existsByEmailAndDeletedFalse(String email);

    boolean existsByUsername(String username);

    boolean existsByEmail(String email);

    @Query("SELECT u FROM User u LEFT JOIN FETCH u.profile WHERE u.id = :id AND u.deleted = false")
    Optional<User> findActiveById(@Param("id") UUID id);

    @Query("SELECT u FROM User u " +
            "LEFT JOIN u.profile p " +
            "WHERE u.deleted = false " +
            "AND (:search IS NULL OR LOWER(u.username) LIKE LOWER(CONCAT('%', :search, '%')) " +
            "     OR LOWER(u.email) LIKE LOWER(CONCAT('%', :search, '%')) " +
            "     OR LOWER(p.firstName) LIKE LOWER(CONCAT('%', :search, '%')) " +
            "     OR LOWER(p.lastName) LIKE LOWER(CONCAT('%', :search, '%')))")
    Page<User> searchUsers(@Param("search") String search, Pageable pageable);
}

