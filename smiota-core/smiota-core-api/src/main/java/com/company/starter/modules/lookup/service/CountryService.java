package com.company.starter.modules.lookup.service;

import com.company.starter.modules.lookup.dto.CountryRequest;
import com.company.starter.modules.lookup.dto.CountryResponse;
import com.company.starter.modules.lookup.entity.Country;
import com.company.starter.modules.lookup.mapper.CountryMapper;
import com.company.starter.modules.lookup.repository.CountryRepository;
import com.company.starter.shared.service.AbstractLookupService;
import org.springframework.stereotype.Service;

/**
 * Concrete service for {@link Country} master data, extending zero-boilerplate {@link AbstractLookupService}.
 */
@Service
public class CountryService extends AbstractLookupService<Country, CountryRequest, CountryResponse, CountryRepository> {

    public CountryService(CountryRepository repository, CountryMapper mapper) {
        super(repository, mapper, "Country");
    }
}

