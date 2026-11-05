package com.company.starter.modules.lookup.dto;

import com.company.starter.shared.dto.LookupRequest;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

@Data
@SuperBuilder
@NoArgsConstructor
@EqualsAndHashCode(callSuper = true)
public class CountryRequest extends LookupRequest {
}

