package com.company.starter.modules.identity.repository;

import com.smiota.common.dto.user.SmiotaUserAuthProjection;
import com.smiota.common.entity.AccountEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Repository executing the Smiota multi-table authentication query.
 */
@Repository
public interface SmiotaAccountRepository extends JpaRepository<AccountEntity, Long> {

    @Query(value = """
        SELECT USER.ID AS id, 
               USER.LOCATION_ID AS locationId, 
               USER.CUSTOMER_ID AS customerId, 
               USER.FIRST_NAME AS firstName,
               USER.LAST_NAME AS lastName,
               USER.EMAIL AS email,
               ACCOUNT.password_hash AS passwordHash, 
               ACCOUNT.hashed_password AS hashedPassword, 
               ACCOUNT.IS_LOCKED AS isLocked, 
               ACCOUNT.NUM_LOGIN_RETRIES AS numLoginRetries
        FROM USER 
        INNER JOIN ACCOUNT ON USER.ACCOUNT_ID = ACCOUNT.ID
        INNER JOIN LOCATION ON USER.LOCATION_ID = LOCATION.ID
        INNER JOIN CUSTOMER ON USER.CUSTOMER_ID = CUSTOMER.ID
        WHERE ACCOUNT.LOGIN = :login 
          AND (USER.INACTIVE IS NULL OR USER.INACTIVE = 0)
          AND (ACCOUNT.INACTIVE IS NULL OR ACCOUNT.INACTIVE = 0)
          AND (LOCATION.INACTIVE IS NULL OR LOCATION.INACTIVE = 0)
          AND (CUSTOMER.INACTIVE IS NULL OR CUSTOMER.INACTIVE = 0)
        LIMIT 1
        """, nativeQuery = true)
    Optional<SmiotaUserAuthProjection> findAuthUserByLogin(@Param("login") String login);

    @Query(value = """
        SELECT r.NAME 
        FROM USER_ROLE ur
        INNER JOIN ROLE r ON ur.ROLE_ID = r.ID
        WHERE ur.USER_ID = :userId
        """, nativeQuery = true)
    List<String> findRoleNamesByUserId(@Param("userId") Long userId);
}
