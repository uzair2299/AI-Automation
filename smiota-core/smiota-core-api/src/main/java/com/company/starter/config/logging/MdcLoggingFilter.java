package com.company.starter.config.logging;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.MDC;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.UUID;

/**
 * Filter populating MDC (Mapped Diagnostic Context) properties:
 * - correlationId
 * - userName
 * - AgentId
 * for structured and colorized log tracing across all threads.
 */
@Component
@Order(Ordered.HIGHEST_PRECEDENCE)
public class MdcLoggingFilter extends OncePerRequestFilter {

    public static final String CORRELATION_ID_KEY = "correlationId";
    public static final String USER_NAME_KEY = "userName";
    public static final String AGENT_ID_KEY = "AgentId";

    public static final String CORRELATION_ID_HEADER = "X-Correlation-Id";
    public static final String AGENT_ID_HEADER = "X-Agent-Id";

    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain filterChain) throws ServletException, IOException {

        try {
            // Correlation ID resolution
            String correlationId = request.getHeader(CORRELATION_ID_HEADER);
            if (!StringUtils.hasText(correlationId)) {
                correlationId = request.getHeader("X-Request-Id");
            }
            if (!StringUtils.hasText(correlationId)) {
                correlationId = UUID.randomUUID().toString();
            }

            MDC.put(CORRELATION_ID_KEY, correlationId);
            response.setHeader(CORRELATION_ID_HEADER, correlationId);

            // Agent ID resolution (if passed)
            String agentId = request.getHeader(AGENT_ID_HEADER);
            if (StringUtils.hasText(agentId)) {
                MDC.put(AGENT_ID_KEY, agentId);
            }

            // Default userName to anonymous until authentication takes place
            MDC.put(USER_NAME_KEY, "anonymous");

            filterChain.doFilter(request, response);
        } finally {
            MDC.clear();
        }
    }
}

