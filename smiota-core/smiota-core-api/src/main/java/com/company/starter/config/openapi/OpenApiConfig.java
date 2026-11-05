package com.company.starter.config.openapi;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.security.OAuthFlow;
import io.swagger.v3.oas.models.security.OAuthFlows;
import io.swagger.v3.oas.models.security.Scopes;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * OpenAPI 3 specification configuration supporting both Bearer JWT and OAuth2 Password grant flows.
 */
@Configuration
public class OpenApiConfig {

    private static final String BEARER_AUTH = "bearerAuth";
    private static final String OAUTH2_PASSWORD = "oauth2Password";

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Enterprise Starter API")
                        .version("1.0.0")
                        .description("Production-Ready Enterprise Spring Boot Starter Template with RBAC, Dynamic Navigation, and Zero-Boilerplate Generic Engine")
                        .contact(new Contact().name("Enterprise Architecture Team").email("architecture@company.com"))
                        .license(new License().name("Apache 2.0").url("https://www.apache.org/licenses/LICENSE-2.0")))
                .addSecurityItem(new SecurityRequirement().addList(BEARER_AUTH))
                .components(new Components()
                        .addSecuritySchemes(BEARER_AUTH, new SecurityScheme()
                                .name(BEARER_AUTH)
                                .type(SecurityScheme.Type.HTTP)
                                .scheme("bearer")
                                .bearerFormat("JWT")
                                .description("Enter JWT token directly or using Bearer prefix."))
                        .addSecuritySchemes(OAUTH2_PASSWORD, new SecurityScheme()
                                .type(SecurityScheme.Type.OAUTH2)
                                .description("OAuth2 Password Grant Authentication Flow via /api/v1/auth/login")
                                .flows(new OAuthFlows()
                                        .password(new OAuthFlow()
                                                .tokenUrl("/api/v1/auth/login")
                                                .scopes(new Scopes()
                                                        .addString("read", "Read access to resources")
                                                        .addString("write", "Write access to resources"))))));
    }
}

