package com.company.starter.shared.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;

/**
 * Standard request parameter DTO for pagination, sorting, and search queries.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RequestParamDto {

    @Schema(description = "Page number (0-based index)", example = "0", defaultValue = "0")
    @Builder.Default
    private int page = 0;

    @Schema(description = "Number of items per page", example = "20", defaultValue = "20")
    @Builder.Default
    private int size = 20;

    @Schema(description = "Property to sort by", example = "createdAt", defaultValue = "createdAt")
    @Builder.Default
    private String sortBy = "createdAt";

    @Schema(description = "Sort direction (ASC or DESC)", example = "DESC", defaultValue = "DESC")
    @Builder.Default
    private String direction = "DESC";

    @Schema(description = "Keyword search term", example = "active")
    private String search;

    @Schema(description = "Filter by active status", example = "true")
    private Boolean active;

    public Pageable toPageable() {
        Sort.Direction sortDirection = Sort.Direction.DESC;
        if (direction != null && direction.equalsIgnoreCase("ASC")) {
            sortDirection = Sort.Direction.ASC;
        }

        String field = (sortBy != null && !sortBy.trim().isEmpty()) ? sortBy : "createdAt";
        int safePage = Math.max(0, page);
        int safeSize = (size <= 0 || size > 1000) ? 20 : size;

        return PageRequest.of(safePage, safeSize, Sort.by(sortDirection, field));
    }
}

