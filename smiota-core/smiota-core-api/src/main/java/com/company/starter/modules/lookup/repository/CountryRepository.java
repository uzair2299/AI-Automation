package com.company.starter.modules.lookup.repository;

import com.company.starter.modules.lookup.entity.Country;
import com.company.starter.shared.repository.BaseLookupRepository;
import org.springframework.stereotype.Repository;

/**
 * Repository interface for {@link Country}, inheriting full CRUD and dynamic search.
 */
@Repository
public interface CountryRepository extends BaseLookupRepository<Country> {
}

