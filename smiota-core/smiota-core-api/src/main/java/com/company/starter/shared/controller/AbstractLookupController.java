package com.company.starter.shared.controller;

import com.company.starter.shared.dto.ApiResponse;
import com.company.starter.shared.dto.LookupRequest;
import com.company.starter.shared.dto.LookupResponse;
import com.company.starter.shared.dto.RequestParamDto;
import com.company.starter.shared.service.GenericLookupService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;

import java.util.UUID;

/**
 * Abstract Admin CRUD Controller secured by JWT and Admin RBAC (ROLE_ADMIN).
 *
 * @param <REQ> Request DTO extending {@link LookupRequest}
 * @param <RES> Response DTO extending {@link LookupResponse}
 */
@RequiredArgsConstructor
@SecurityRequirement(name = "bearerAuth")
@PreAuthorize("hasRole('ADMIN')")
public abstract class AbstractLookupController<REQ extends LookupRequest, RES extends LookupResponse> {

    protected final GenericLookupService<REQ, RES> service;

    @PostMapping
    @Operation(summary = "Create record", description = "Create a new lookup record (Admin only)")
    public ResponseEntity<ApiResponse<RES>> create(@Valid @RequestBody REQ request) {
        RES response = service.create(request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.created("Record created successfully", response));
    }

    @PutMapping("/{id}")
    @Operation(summary = "Update record", description = "Update an existing lookup record by ID (Admin only)")
    public ResponseEntity<ApiResponse<RES>> update(@PathVariable UUID id, @Valid @RequestBody REQ request) {
        RES response = service.update(id, request);
        return ResponseEntity.ok(ApiResponse.ok("Record updated successfully", response));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get record by ID", description = "Retrieve a specific lookup record by ID (Admin only)")
    public ResponseEntity<ApiResponse<RES>> getById(@PathVariable UUID id) {
        RES response = service.getById(id);
        return ResponseEntity.ok(ApiResponse.ok(response));
    }

    @GetMapping
    @Operation(summary = "Get paginated records", description = "Retrieve paginated records with optional search filter (Admin only)")
    public ResponseEntity<ApiResponse<Page<RES>>> getAll(@ModelAttribute RequestParamDto paramDto) {
        Page<RES> page = service.getAll(paramDto);
        return ResponseEntity.ok(ApiResponse.ok(page));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Soft delete record", description = "Soft delete a lookup record by ID (Admin only)")
    public ResponseEntity<ApiResponse<Void>> delete(@PathVariable UUID id) {
        service.delete(id);
        return ResponseEntity.ok(ApiResponse.noContent("Record soft-deleted successfully"));
    }
}

