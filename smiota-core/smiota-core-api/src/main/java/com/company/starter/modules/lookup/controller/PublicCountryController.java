package com.company.starter.modules.lookup.controller;

import com.company.starter.modules.lookup.dto.CountryRequest;
import com.company.starter.modules.lookup.dto.CountryResponse;
import com.company.starter.modules.lookup.service.CountryService;
import com.company.starter.shared.controller.AbstractPublicLookupController;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Public unauthenticated read-only controller for Country lookup domain.
 */
@RestController
@RequestMapping("/api/v1/public/countries")
@Tag(name = "Public Countries", description = "Public read-only endpoints for Country master data")
public class PublicCountryController extends AbstractPublicLookupController<CountryRequest, CountryResponse> {

    public PublicCountryController(CountryService countryService) {
        super(countryService);
    }
}

