package com.company.starter.modules.lookup.entity;

import com.company.starter.shared.entity.BaseLookupEntity;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.experimental.SuperBuilder;

/**
 * Concrete lookup entity demonstrating zero-boilerplate master data modeling.
 */
@Getter
@Setter
@SuperBuilder
@NoArgsConstructor
@Entity
@Table(name = "tbl_countries")
public class Country extends BaseLookupEntity {
}

