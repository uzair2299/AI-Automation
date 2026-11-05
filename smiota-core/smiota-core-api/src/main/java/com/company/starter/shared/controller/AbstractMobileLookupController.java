package com.company.starter.shared.controller;

import com.company.starter.shared.dto.ApiResponse;
import com.company.starter.shared.dto.LookupRequest;
import com.company.starter.shared.dto.LookupResponse;
import com.company.starter.shared.service.GenericLookupService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

import java.util.List;
import java.util.UUID;

/**
 * Abstract Mobile/Staff Controller providing read-only access for authenticated mobile/staff clients.
 *
 * @param <REQ> Request DTO extending {@link LookupRequest}
 * @param <RES> Response DTO extending {@link LookupResponse}
 */
@RequiredArgsConstructor
@SecurityRequirement(name = "bearerAuth")
@PreAuthorize("isAuthenticated()")
public abstract class AbstractMobileLookupController<REQ extends LookupRequest, RES extends LookupResponse> {

    protected final GenericLookupService<REQ, RES> service;

    @GetMapping("/active")
    @Operation(summary = "Get all active records", description = "Retrieve all active non-deleted lookup records for mobile/staff")
    public ResponseEntity<ApiResponse<List<RES>>> getActive() {
        List<RES> list = service.getAllActive();
        return ResponseEntity.ok(ApiResponse.ok(list));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get record by ID", description = "Retrieve a specific lookup record by ID for mobile/staff")
    public ResponseEntity<ApiResponse<RES>> getById(@PathVariable UUID id) {
        RES response = service.getById(id);
        return ResponseEntity.ok(ApiResponse.ok(response));
    }
}

