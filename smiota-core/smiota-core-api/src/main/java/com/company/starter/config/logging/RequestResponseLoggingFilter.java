package com.company.starter.config.logging;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.MediaType;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;
import org.springframework.util.AntPathMatcher;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.web.util.ContentCachingRequestWrapper;
import org.springframework.web.util.ContentCachingResponseWrapper;

import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Collections;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

/**
 * Filter intercepting incoming HTTP requests and outgoing HTTP responses to log
 * method, URI, headers, timing, and cached payloads with sensitive data masking.
 */
@Slf4j
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 1)
public class RequestResponseLoggingFilter extends OncePerRequestFilter {

    @Value("${logging.http.payload.enabled:true}")
    private boolean payloadLoggingEnabled;

    @Value("${logging.http.payload.max-length:10000}")
    private int maxPayloadLength;

    @Value("${logging.http.payload.include-headers:true}")
    private boolean includeHeaders;

    private final AntPathMatcher pathMatcher = new AntPathMatcher();

    private static final List<String> EXCLUDED_PATHS = List.of(
            "/actuator/**",
            "/swagger-ui/**",
            "/swagger-ui.html",
            "/v3/api-docs/**",
            "/v3/api-docs.yaml",
            "/favicon.ico",
            "/*.css",
            "/*.js",
            "/*.png"
    );

    private static final Set<String> SENSITIVE_HEADERS = Set.of(
            "authorization",
            "proxy-authorization",
            "cookie",
            "set-cookie",
            "x-api-key"
    );

    private static final Pattern SENSITIVE_JSON_PATTERN = Pattern.compile(
            "\"(?i)(password|secret|token|accessToken|refreshToken|apiKey|clientSecret|credentials)\"\\s*:\\s*\"([^\"]*)\""
    );

    private static final List<MediaType> LOGGABLE_MEDIA_TYPES = List.of(
            MediaType.APPLICATION_JSON,
            MediaType.APPLICATION_XML,
            MediaType.TEXT_PLAIN,
            MediaType.TEXT_XML,
            MediaType.TEXT_HTML,
            MediaType.APPLICATION_FORM_URLENCODED
    );

    @Override
    protected boolean shouldNotFilter(@NonNull HttpServletRequest request) {
        String path = request.getRequestURI();
        return EXCLUDED_PATHS.stream().anyMatch(pattern -> pathMatcher.match(pattern, path));
    }

    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain filterChain) throws ServletException, IOException {

        if (!payloadLoggingEnabled || !log.isDebugEnabled()) {
            filterChain.doFilter(request, response);
            return;
        }

        ContentCachingRequestWrapper requestWrapper = new ContentCachingRequestWrapper(request);
        ContentCachingResponseWrapper responseWrapper = new ContentCachingResponseWrapper(response);

        long startTime = System.currentTimeMillis();

        try {
            filterChain.doFilter(requestWrapper, responseWrapper);
        } finally {
            long duration = System.currentTimeMillis() - startTime;
            logRequest(requestWrapper);
            logResponse(requestWrapper, responseWrapper, duration);
            responseWrapper.copyBodyToResponse();
        }
    }

    private void logRequest(ContentCachingRequestWrapper request) {
        String uri = request.getRequestURI();
        String queryString = request.getQueryString();
        String fullPath = queryString != null ? uri + "?" + queryString : uri;

        StringBuilder sb = new StringBuilder();
        sb.append("HTTP REQUEST -> ").append(request.getMethod()).append(" ").append(fullPath);

        if (includeHeaders) {
            Map<String, String> headers = extractHeaders(request);
            sb.append(" | Headers: ").append(headers);
        }

        String payload = getPayload(request.getContentAsByteArray(), request.getCharacterEncoding(), request.getContentType());
        if (StringUtils.hasText(payload)) {
            sb.append(" | Payload: ").append(maskSensitiveFields(payload));
        }

        log.debug(sb.toString());
    }

    private void logResponse(ContentCachingRequestWrapper request, ContentCachingResponseWrapper response, long durationMs) {
        int status = response.getStatus();

        StringBuilder sb = new StringBuilder();
        sb.append("HTTP RESPONSE <- [").append(status).append("] ")
                .append(request.getMethod()).append(" ")
                .append(request.getRequestURI())
                .append(" (").append(durationMs).append("ms)");

        if (includeHeaders) {
            Map<String, String> headers = new HashMap<>();
            for (String headerName : response.getHeaderNames()) {
                headers.put(headerName, maskHeader(headerName, response.getHeader(headerName)));
            }
            sb.append(" | Headers: ").append(headers);
        }

        String payload = getPayload(response.getContentAsByteArray(), response.getCharacterEncoding(), response.getContentType());
        if (StringUtils.hasText(payload)) {
            sb.append(" | Payload: ").append(maskSensitiveFields(payload));
        }

        log.debug(sb.toString());
    }

    private String getPayload(byte[] content, String characterEncoding, String contentType) {
        if (content == null || content.length == 0) {
            return null;
        }

        if (!isLoggableMediaType(contentType)) {
            return "[Binary or non-text payload: " + (contentType != null ? contentType : "unknown") + ", size: " + content.length + " bytes]";
        }

        try {
            int length = Math.min(content.length, maxPayloadLength);
            String encoding = characterEncoding != null ? characterEncoding : StandardCharsets.UTF_8.name();
            String payload = new String(content, 0, length, encoding).replaceAll("[\\r\\n]+", " ").trim();

            if (content.length > maxPayloadLength) {
                payload += "... [truncated (" + content.length + " bytes total)]";
            }
            return payload;
        } catch (UnsupportedEncodingException e) {
            return "[Unsupported Encoding: " + e.getMessage() + "]";
        }
    }

    private boolean isLoggableMediaType(String contentType) {
        if (!StringUtils.hasText(contentType)) {
            return true; // default to text representation
        }
        try {
            MediaType mediaType = MediaType.parseMediaType(contentType);
            return LOGGABLE_MEDIA_TYPES.stream().anyMatch(mediaType::isCompatibleWith);
        } catch (Exception e) {
            return false;
        }
    }

    private Map<String, String> extractHeaders(HttpServletRequest request) {
        Map<String, String> headers = new HashMap<>();
        Enumeration<String> headerNames = request.getHeaderNames();
        if (headerNames != null) {
            while (headerNames.hasMoreElements()) {
                String headerName = headerNames.nextElement();
                String headerValue = request.getHeader(headerName);
                headers.put(headerName, maskHeader(headerName, headerValue));
            }
        }
        return headers;
    }

    private String maskHeader(String headerName, String headerValue) {
        if (headerName == null || headerValue == null) {
            return null;
        }
        if (SENSITIVE_HEADERS.contains(headerName.toLowerCase())) {
            if (headerName.equalsIgnoreCase("authorization") && headerValue.startsWith("Bearer ")) {
                return "Bearer ********";
            }
            return "********";
        }
        return headerValue;
    }

    private String maskSensitiveFields(String payload) {
        if (!StringUtils.hasText(payload)) {
            return payload;
        }
        return SENSITIVE_JSON_PATTERN.matcher(payload).replaceAll("\"$1\":\"********\"");
    }
}

