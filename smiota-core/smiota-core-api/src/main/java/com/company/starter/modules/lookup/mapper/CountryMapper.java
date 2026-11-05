package com.company.starter.modules.lookup.mapper;

import com.company.starter.modules.lookup.dto.CountryRequest;
import com.company.starter.modules.lookup.dto.CountryResponse;
import com.company.starter.modules.lookup.entity.Country;
import com.company.starter.shared.mapper.GenericMapper;
import org.springframework.stereotype.Component;

/**
 * Mapper for {@link Country} entity and its corresponding DTOs.
 */
@Component
public class CountryMapper implements GenericMapper<Country, CountryRequest, CountryResponse> {

    @Override
    public Country toEntity(CountryRequest request) {
        if (request == null) return null;
        return Country.builder()
                .code(request.getCode().trim().toUpperCase())
                .name(request.getName().trim())
                .description(request.getDescription())
                .active(request.getActive() != null ? request.getActive() : Boolean.TRUE)
                .sortOrder(request.getSortOrder() != null ? request.getSortOrder() : 0)
                .deleted(Boolean.FALSE)
                .build();
    }

    @Override
    public CountryResponse toResponse(Country entity) {
        if (entity == null) return null;
        return CountryResponse.builder()
                .id(entity.getId())
                .code(entity.getCode())
                .name(entity.getName())
                .description(entity.getDescription())
                .active(entity.getActive())
                .sortOrder(entity.getSortOrder())
                .createdAt(entity.getCreatedAt())
                .updatedAt(entity.getUpdatedAt())
                .build();
    }

    @Override
    public void updateEntityFromDto(CountryRequest request, Country entity) {
        if (request == null || entity == null) return;
        entity.setCode(request.getCode().trim().toUpperCase());
        entity.setName(request.getName().trim());
        entity.setDescription(request.getDescription());
        if (request.getActive() != null) {
            entity.setActive(request.getActive());
        }
        if (request.getSortOrder() != null) {
            entity.setSortOrder(request.getSortOrder());
        }
    }
}

