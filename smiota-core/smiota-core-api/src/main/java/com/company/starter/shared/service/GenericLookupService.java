package com.company.starter.shared.service;

import com.company.starter.shared.dto.RequestParamDto;
import org.springframework.data.domain.Page;

import java.util.List;
import java.util.UUID;

/**
 * Service contract for lookup and master domain entities.
 *
 * @param <REQ> Request DTO
 * @param <RES> Response DTO
 */
public interface GenericLookupService<REQ, RES> {

    /**
     * Create a new lookup record.
     */
    RES create(REQ request);

    /**
     * Update an existing lookup record by identifier.
     */
    RES update(UUID id, REQ request);

    /**
     * Retrieve a non-deleted lookup record by identifier.
     */
    RES getById(UUID id);

    /**
     * Retrieve all active non-deleted lookup records.
     */
    List<RES> getAllActive();

    /**
     * Retrieve a paginated list of non-deleted lookup records matching filters.
     */
    Page<RES> getAll(RequestParamDto paramDto);

    /**
     * Soft delete a lookup record (sets deleted = true and active = false).
     */
    void delete(UUID id);
}

