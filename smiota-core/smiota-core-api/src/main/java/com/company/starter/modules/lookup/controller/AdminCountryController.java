package com.company.starter.modules.lookup.controller;

import com.company.starter.modules.lookup.dto.CountryRequest;
import com.company.starter.modules.lookup.dto.CountryResponse;
import com.company.starter.modules.lookup.service.CountryService;
import com.company.starter.shared.controller.AbstractLookupController;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Admin CRUD controller for Country lookup domain.
 */
@RestController
@RequestMapping("/api/v1/admin/countries")
@Tag(name = "Admin Countries", description = "Admin CRUD endpoints for Country master data")
public class AdminCountryController extends AbstractLookupController<CountryRequest, CountryResponse> {

    public AdminCountryController(CountryService countryService) {
        super(countryService);
    }
}

