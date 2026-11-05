package com.company.starter.shared.controller;

import com.company.starter.shared.dto.ApiResponse;
import com.company.starter.shared.dto.LookupRequest;
import com.company.starter.shared.dto.LookupResponse;
import com.company.starter.shared.service.GenericLookupService;
import io.swagger.v3.oas.annotations.Operation;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

import java.util.List;
import java.util.UUID;

/**
 * Abstract Public Controller providing unauthenticated, read-only access to lookup data.
 *
 * @param <REQ> Request DTO extending {@link LookupRequest}
 * @param <RES> Response DTO extending {@link LookupResponse}
 */
@RequiredArgsConstructor
public abstract class AbstractPublicLookupController<REQ extends LookupRequest, RES extends LookupResponse> {

    protected final GenericLookupService<REQ, RES> service;

    @GetMapping("/active")
    @Operation(summary = "Get all active records (Public)", description = "Public read-only endpoint returning all active lookup records")
    public ResponseEntity<ApiResponse<List<RES>>> getActive() {
        List<RES> list = service.getAllActive();
        return ResponseEntity.ok(ApiResponse.ok(list));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get record by ID (Public)", description = "Public read-only endpoint returning a single lookup record by ID")
    public ResponseEntity<ApiResponse<RES>> getById(@PathVariable UUID id) {
        RES response = service.getById(id);
        return ResponseEntity.ok(ApiResponse.ok(response));
    }
}

