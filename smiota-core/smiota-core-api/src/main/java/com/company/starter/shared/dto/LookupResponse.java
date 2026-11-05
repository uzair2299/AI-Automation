package com.company.starter.shared.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

import java.time.Instant;
import java.util.UUID;

/**
 * Base response DTO for lookup/master entities.
 */
@Data
@SuperBuilder
@NoArgsConstructor
@AllArgsConstructor
public class LookupResponse {

    @Schema(description = "Primary identifier (UUID)", example = "3fa85f64-5717-4562-b3fc-2c963f66afa6")
    private UUID id;

    @Schema(description = "Unique business code", example = "US")
    private String code;

    @Schema(description = "Display name", example = "United States")
    private String name;

    @Schema(description = "Detailed description", example = "United States of America")
    private String description;

    @Schema(description = "Status indicating whether the record is active", example = "true")
    private Boolean active;

    @Schema(description = "Display ordering index", example = "1")
    private Integer sortOrder;

    @Schema(description = "Creation timestamp")
    private Instant createdAt;

    @Schema(description = "Last update timestamp")
    private Instant updatedAt;
}

