# =============================================================================
# Stage 1: Build stage with Maven and Eclipse Temurin JDK 17
# =============================================================================
FROM maven:3-eclipse-temurin-17 AS builder

WORKDIR /app

# Cache dependencies layer
COPY pom.xml .
RUN mvn dependency:go-offline -B || true

# Copy source code and package application
COPY src ./src
RUN mvn clean package -DskipTests -B

# =============================================================================
# Stage 2: Production runtime image with Eclipse Temurin JDK 17 Jammy
# =============================================================================
FROM eclipse-temurin:17-jdk-jammy

WORKDIR /app

# Create non-root system user for security
RUN groupadd -r spring && useradd -r -g spring spring

# Copy compiled artifact from builder stage
COPY --from=builder /app/target/enterprise-starter-*.jar app.jar

# Set ownership to unprivileged user
RUN chown -R spring:spring /app
USER spring:spring

# Expose HTTP port
EXPOSE 8080

# Production JVM options and entry point
ENTRYPOINT ["java", "-XX:+UseG1GC", "-XX:MaxRAMPercentage=75.0", "-Djava.security.egd=file:/dev/./urandom", "-jar", "app.jar"]

