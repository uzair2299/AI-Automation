package com.company.starter.shared.repository;

import com.company.starter.shared.entity.BaseLookupEntity;
import jakarta.persistence.criteria.Predicate;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.repository.NoRepositoryBean;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Generic repository for lookup entities extending {@link BaseLookupEntity}.
 *
 * @param <E> Entity type
 */
@NoRepositoryBean
public interface BaseLookupRepository<E extends BaseLookupEntity>
        extends JpaRepository<E, UUID>, JpaSpecificationExecutor<E> {

    /**
     * Check if a record exists with the specified code.
     */
    boolean existsByCode(String code);

    /**
     * Check if another record exists with the same code (used during updates).
     */
    boolean existsByCodeAndIdNot(String code, UUID id);

    /**
     * Find entity by unique business code.
     */
    Optional<E> findByCode(String code);

    /**
     * Find all non-deleted, active records ordered by sort order.
     */
    List<E> findAllByDeletedFalseAndActiveTrueOrderBySortOrderAsc();

    /**
     * Default convenience method to find all active non-deleted records.
     */
    default List<E> findAllActive() {
        return findAllByDeletedFalseAndActiveTrueOrderBySortOrderAsc();
    }

    /**
     * Search non-deleted records by keyword across code, name, and description with active flag filter.
     */
    default Page<E> findBySearch(String keyword, Boolean active, Pageable pageable) {
        Specification<E> spec = (root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();
            predicates.add(cb.equal(root.get("deleted"), false));

            if (active != null) {
                predicates.add(cb.equal(root.get("active"), active));
            }

            if (keyword != null && !keyword.trim().isEmpty()) {
                String pattern = "%" + keyword.toLowerCase().trim() + "%";
                predicates.add(cb.or(
                        cb.like(cb.lower(root.get("code")), pattern),
                        cb.like(cb.lower(root.get("name")), pattern),
                        cb.like(cb.lower(root.get("description")), pattern)
                ));
            }

            return cb.and(predicates.toArray(new Predicate[0]));
        };
        return findAll(spec, pageable);
    }

    /**
     * Search non-deleted records by keyword across code, name, and description.
     */
    default Page<E> findBySearch(String keyword, Pageable pageable) {
        return findBySearch(keyword, null, pageable);
    }
}

