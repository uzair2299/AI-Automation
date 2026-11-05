package com.company.starter.shared.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

/**
 * Base request DTO for lookup/master entities.
 */
@Data
@SuperBuilder
@NoArgsConstructor
@AllArgsConstructor
public class LookupRequest {

    @NotBlank(message = "Code is required")
    @Size(max = 100, message = "Code must not exceed 100 characters")
    @Schema(description = "Unique business code", example = "US")
    private String code;

    @NotBlank(message = "Name is required")
    @Size(max = 255, message = "Name must not exceed 255 characters")
    @Schema(description = "Display name", example = "United States")
    private String name;

    @Size(max = 1000, message = "Description must not exceed 1000 characters")
    @Schema(description = "Detailed description", example = "United States of America")
    private String description;

    @Builder.Default
    @Schema(description = "Status indicating whether the record is active", example = "true", defaultValue = "true")
    private Boolean active = Boolean.TRUE;

    @Builder.Default
    @Schema(description = "Display ordering index", example = "0", defaultValue = "0")
    private Integer sortOrder = 0;
}

