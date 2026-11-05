# =============================================================================
# Smiota Core API - Multi-Module Maven Dockerfile
# =============================================================================

# --- Stage 1: Build Java Modules ---
FROM maven:3-eclipse-temurin-17 AS builder
WORKDIR /build

# Copy parent pom and all module source codes
COPY pom.xml .
COPY smiota-common-model/ ./smiota-common-model/
COPY smiota-core-api/ ./smiota-core-api/

# Build all modules and package the Spring Boot executable jar
RUN mvn clean package -DskipTests -B

# --- Stage 2: Runtime Image ---
FROM eclipse-temurin:17-jdk-jammy
WORKDIR /app

# Run as unprivileged system user
RUN groupadd -r spring && useradd -r -g spring spring

# Copy Spring Boot runnable jar
COPY --from=builder /build/smiota-core-api/target/*.jar app.jar
RUN chown -R spring:spring /app
USER spring:spring

EXPOSE 8080

ENTRYPOINT ["java", "-XX:+UseG1GC", "-XX:MaxRAMPercentage=75.0", "-Djava.security.egd=file:/dev/./urandom", "-jar", "app.jar"]
