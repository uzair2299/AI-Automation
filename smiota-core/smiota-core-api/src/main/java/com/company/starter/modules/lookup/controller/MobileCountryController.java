package com.company.starter.modules.lookup.controller;

import com.company.starter.modules.lookup.dto.CountryRequest;
import com.company.starter.modules.lookup.dto.CountryResponse;
import com.company.starter.modules.lookup.service.CountryService;
import com.company.starter.shared.controller.AbstractMobileLookupController;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Mobile read-only controller for Country lookup domain.
 */
@RestController
@RequestMapping("/api/v1/mobile/countries")
@Tag(name = "Mobile Countries", description = "Authenticated Mobile/Staff read-only endpoints for Country master data")
public class MobileCountryController extends AbstractMobileLookupController<CountryRequest, CountryResponse> {

    public MobileCountryController(CountryService countryService) {
        super(countryService);
    }
}

