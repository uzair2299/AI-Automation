package com.company.starter.modules.lookup.dto;

import com.company.starter.shared.dto.LookupResponse;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

@Data
@SuperBuilder
@NoArgsConstructor
@EqualsAndHashCode(callSuper = true)
public class CountryResponse extends LookupResponse {
}

