package com.company.starter.security.annotation;

import java.lang.annotation.Documented;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * Method-level security annotation to enforce role checking.
 * Example: @HasRole("ADMIN")
 */
@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface HasRole {

    /**
     * Role name or array of role names required (e.g. "ADMIN" or "ROLE_ADMIN").
     */
    String[] value();
}

