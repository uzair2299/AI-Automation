package com.company.starter.shared.service;

import com.company.starter.security.context.SecurityUtils;
import com.company.starter.shared.dto.LookupRequest;
import com.company.starter.shared.dto.LookupResponse;
import com.company.starter.shared.dto.RequestParamDto;
import com.company.starter.shared.entity.BaseLookupEntity;
import com.company.starter.shared.exception.ConflictException;
import com.company.starter.shared.exception.ResourceNotFoundException;
import com.company.starter.shared.mapper.GenericMapper;
import com.company.starter.shared.repository.BaseLookupRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

/**
 * Generic reusable service implementing complete CRUD, pagination, search, and soft-delete for lookup entities.
 *
 * @param <E>   Entity type extending {@link BaseLookupEntity}
 * @param <REQ> Request DTO extending {@link LookupRequest}
 * @param <RES> Response DTO extending {@link LookupResponse}
 * @param <REP> Repository extending {@link BaseLookupRepository}
 */
@Slf4j
@Transactional(readOnly = true)
public abstract class AbstractLookupService<
        E extends BaseLookupEntity,
        REQ extends LookupRequest,
        RES extends LookupResponse,
        REP extends BaseLookupRepository<E>>
        implements GenericLookupService<REQ, RES> {

    protected final REP repository;
    protected final GenericMapper<E, REQ, RES> mapper;
    protected final String resourceName;

    public AbstractLookupService(REP repository, GenericMapper<E, REQ, RES> mapper) {
        this.repository = repository;
        this.mapper = mapper;
        this.resourceName = "Resource";
    }

    public AbstractLookupService(REP repository, GenericMapper<E, REQ, RES> mapper, String resourceName) {
        this.repository = repository;
        this.mapper = mapper;
        this.resourceName = resourceName;
    }

    @Override
    @Transactional
    public RES create(REQ request) {
        log.info("Creating new {} with code: {}", resourceName, request.getCode());
        if (repository.existsByCode(request.getCode())) {
            throw new ConflictException(String.format("%s with code '%s' already exists", resourceName, request.getCode()));
        }

        E entity = mapper.toEntity(request);
        entity.setDeleted(Boolean.FALSE);
        if (entity.getActive() == null) {
            entity.setActive(Boolean.TRUE);
        }

        E saved = repository.save(entity);
        log.info("{} successfully created with ID: {}", resourceName, saved.getId());
        return mapper.toResponse(saved);
    }

    @Override
    @Transactional
    public RES update(UUID id, REQ request) {
        log.info("Updating {} with ID: {}", resourceName, id);
        E entity = findEntityById(id);

        if (repository.existsByCodeAndIdNot(request.getCode(), id)) {
            throw new ConflictException(String.format("%s with code '%s' already exists", resourceName, request.getCode()));
        }

        mapper.updateEntityFromDto(request, entity);
        E updated = repository.save(entity);
        log.info("{} successfully updated with ID: {}", resourceName, updated.getId());
        return mapper.toResponse(updated);
    }

    @Override
    public RES getById(UUID id) {
        log.debug("Fetching {} with ID: {}", resourceName, id);
        E entity = findEntityById(id);
        return mapper.toResponse(entity);
    }

    @Override
    public List<RES> getAllActive() {
        log.debug("Fetching all active non-deleted {}", resourceName);
        return repository.findAllActive()
                .stream()
                .map(mapper::toResponse)
                .toList();
    }

    @Override
    public Page<RES> getAll(RequestParamDto paramDto) {
        log.debug("Fetching paginated {} with parameters: {}", resourceName, paramDto);
        Page<E> entityPage = repository.findBySearch(
                paramDto.getSearch(),
                paramDto.getActive(),
                paramDto.toPageable()
        );
        return entityPage.map(mapper::toResponse);
    }

    @Override
    @Transactional
    public void delete(UUID id) {
        log.info("Soft-deleting {} with ID: {}", resourceName, id);
        E entity = findEntityById(id);

        entity.setDeleted(Boolean.TRUE);
        entity.setDeletedAt(Instant.now());
        entity.setDeletedBy(SecurityUtils.getCurrentUsername());
        entity.setActive(Boolean.FALSE);

        repository.save(entity);
        log.info("{} soft-deleted successfully with ID: {}", resourceName, id);
    }

    /**
     * Helper method to find an active, non-deleted entity by id or throw {@link ResourceNotFoundException}.
     */
    protected E findEntityById(UUID id) {
        return repository.findById(id)
                .filter(e -> !Boolean.TRUE.equals(e.getDeleted()))
                .orElseThrow(() -> new ResourceNotFoundException(resourceName, "id", id));
    }
}
