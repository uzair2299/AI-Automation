package com.company.starter.shared.mapper;

/**
 * Contract for entity-to-DTO and DTO-to-entity mapping.
 *
 * @param <E>   Entity type
 * @param <REQ> Request DTO type
 * @param <RES> Response DTO type
 */
public interface GenericMapper<E, REQ, RES> {

    /**
     * Map request DTO to new entity instance.
     */
    E toEntity(REQ request);

    /**
     * Map entity to response DTO.
     */
    RES toResponse(E entity);

    /**
     * Update existing entity instance from request DTO.
     */
    void updateEntityFromDto(REQ request, E entity);
}

