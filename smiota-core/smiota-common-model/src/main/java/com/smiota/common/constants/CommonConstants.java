package com.smiota.common.constants;

public final class CommonConstants {

    private CommonConstants() {
        // utility class
    }

    public static final String DATE_TIME_FORMAT = "yyyy-MM-dd HH:mm:ss";
    public static final String DATE_FORMAT = "yyyy-MM-dd";
    public static final String CORRELATION_ID_HEADER = "X-Correlation-Id";
    public static final String MDC_CORRELATION_ID = "correlationId";
    public static final String MDC_USER_NAME = "userName";
    public static final String MDC_AGENT_ID = "AgentId";
}
