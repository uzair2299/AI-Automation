# Enterprise Spring Boot Starter Template

A production-grade, modular, and cloud-ready Spring Boot 3 enterprise starter template crafted with Java 17, MySQL, Flyway, stateless JWT authentication, fine-grained Role-Based Access Control (RBAC), recursive dynamic UI navigation, and a zero-boilerplate generic lookup engine.

---

## 1. Architectural Highlights

### A. Triple-Controller Layer Pattern (Per Domain)
To guarantee strict enterprise boundary separation, every business domain or master/lookup table exposes three distinct, decoupled controller layers:
1. **Admin Controller** (`/api/v1/admin/{resource}`): Full CRUD (`POST`, `PUT`, `GET /{id}`, `GET`, `DELETE`). Secured by JWT Bearer token and requires `ROLE_ADMIN` authority.
2. **Mobile / Staff Controller** (`/api/v1/mobile/{resource}`): Read-only (`GET /active`, `GET /{id}`). Secured by JWT Bearer token for authenticated mobile, tablet, or handheld staff clients.
3. **Public Controller** (`/api/v1/public/{resource}`): Read-only (`GET /active`, `GET /{id}`). Completely anonymous and public (`permitAll`).

### B. Zero-Boilerplate Generic Engine (`shared/`)
New lookup/master tables require virtually zero code to achieve production-grade capabilities (auditing, soft-delete, paging, sorting, full-text search, and validation):
- **Base Entities**:
  - `BaseEntity`: Primary key `UUID id`, `@CreatedDate createdAt`, `@LastModifiedDate updatedAt`, `@Version version`.
  - `BaseAuditEntity`: Extends `BaseEntity` + `@CreatedBy createdBy`, `@LastModifiedBy updatedBy`.
  - `BaseSoftDeleteEntity`: Extends `BaseAuditEntity` + `deleted`, `deletedAt`, `deletedBy`.
  - `BaseLookupEntity`: Extends `BaseSoftDeleteEntity` + `code` (unique), `name`, `description`, `active`, `sortOrder`.
- **Base Repository**:
  - `BaseLookupRepository<E extends BaseLookupEntity>`: Extends `JpaRepository` and `JpaSpecificationExecutor`. Provides `existsByCode`, `existsByCodeAndIdNot`, `findAllActive`, and dynamic search filtering by keyword across code, name, and description.
- **Base Service**:
  - `AbstractLookupService<E, REQ, RES, REP>`: Complete transactional implementation of create, update, getById, getAllActive, getAll (with `RequestParamDto`), and soft-delete (`active = false`, `deleted = true`).
- **Base Controllers**:
  - `AbstractLookupController<REQ, RES>` (Admin full CRUD).
  - `AbstractMobileLookupController<REQ, RES>` (Mobile read-only).
  - `AbstractPublicLookupController<REQ, RES>` (Public read-only).

### C. Stateless Security & Fine-Grained RBAC
- Stateless Spring Security 6 filter chain with JSON Web Tokens (`jjwt 0.11.5`).
- Password hashing using `BCryptPasswordEncoder`.
- Enriched `CustomUserDetails` holding user IDs, emails, roles (`ROLE_...`), and granular permissions (`USER_READ`, `ROLE_CREATE`).
- Method-level security via `@CurrentUser`, `@HasRole`, `@HasPermission`, and Spring's `@PreAuthorize`.
- Standardized RFC-7807 compliant error responses handled by `@RestControllerAdvice GlobalExceptionHandler`.

### D. Dynamic UI Navigation Hierarchy
- Recursive self-referencing menu structure (`sec_menu_items`) with layout placement sections (`SIDEBAR`, `TOPBAR`, `PROFILE`).
- Filtered dynamically based on the current user's authenticated roles and permission grants.

---

## 2. Directory Structure

```text
src/
├── main/
│   ├── java/com/company/starter/
│   │   ├── StarterApplication.java
│   │   ├── bootstrap/
│   │   │   └── seeder/
│   │   │       └── SecurityDataSeeder.java
│   │   ├── config/
│   │   │   ├── database/
│   │   │   │   └── JpaAuditingConfig.java
│   │   │   ├── openapi/
│   │   │   │   └── OpenApiConfig.java
│   │   │   └── security/
│   │   │       └── SecurityConfig.java
│   │   ├── security/
│   │   │   ├── annotation/ (CurrentUser, HasRole, HasPermission, SecurityAspect)
│   │   │   ├── context/ (CustomUserDetails, SecurityUtils)
│   │   │   ├── controller/ (AuthController)
│   │   │   ├── dto/ (LoginRequest, LoginResponse, RegisterRequest)
│   │   │   ├── handler/ (CustomAccessDeniedHandler, CustomAuthenticationEntryPoint)
│   │   │   ├── jwt/ (JwtFilter, JwtProvider, JwtTokenUtil)
│   │   │   └── service/ (AuthService, CustomUserDetailsService)
│   │   ├── shared/
│   │   │   ├── controller/ (AbstractLookupController, AbstractMobileLookupController, AbstractPublicLookupController)
│   │   │   ├── dto/ (ApiResponse, RequestParamDto, ErrorResponse, LookupRequest, LookupResponse)
│   │   │   ├── entity/ (BaseEntity, BaseAuditEntity, BaseSoftDeleteEntity, BaseLookupEntity)
│   │   │   ├── exception/ (GlobalExceptionHandler, ResourceNotFoundException, ConflictException, BadRequestException, ForbiddenException)
│   │   │   ├── mapper/ (GenericMapper)
│   │   │   ├── repository/ (BaseLookupRepository)
│   │   │   └── service/ (GenericLookupService, AbstractLookupService)
│   │   └── modules/
│   │       ├── identity/ (User, UserProfile, Repositories, UserService, AdminUserController)
│   │       ├── rbac/ (Role, Permission, Resource, Module, UserRole, RolePermission, Repositories, Services, Controllers)
│   │       ├── navigation/ (MenuItem, NavigationService, NavigationController)
│   │       └── lookup/ (Sample Country domain demonstrating Triple-Controller pattern)
│   └── resources/
│       ├── application.properties
│       ├── application-dev.properties
│       ├── application-prod.properties
│       └── db/migration/
│           ├── V1__Initial_Schema.sql
│           └── V2__Seed_Data.sql
├── pom.xml
├── Dockerfile
├── .gitignore
└── README.md
```

---

## 3. Quick Start Guide

### Prerequisites
- **Java:** JDK 17+
- **Maven:** 3.8+
- **MySQL Database Server:** `10.128.15.219:3306`

### Database Configuration
The application is pre-configured to connect to the dedicated MySQL server:
- **Host:** `10.128.15.219`
- **Port:** `3306`
- **Database:** `usman-db-sdev2` (or configured via `${DB_NAME}`)
- **Username:** `usman-db-sdev2`
- **Password:** `Usman@123`
- **Driver:** `com.mysql.cj.jdbc.Driver`
- **JDBC URL:** `jdbc:mysql://10.128.15.219:3306/usman-db-sdev2?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=UTC&createDatabaseIfNotExist=true`

### Run the Application
```bash
mvn clean spring-boot:run
```

The application starts on port `8080` with the `dev` profile enabled by default. Flyway automatically executes database migrations against MySQL:
1. `V1__Initial_Schema.sql`: Creates core DDL schema and indexes.
2. `V2__Seed_Data.sql`: Seeds modules, resources, permissions, roles, and navigation trees.
3. `SecurityDataSeeder`: Bootstraps the root administrator account.

---

## 4. Default Seeded Credentials

| Account Role | Username | Password | Email |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `adminpassword` | `admin@company.com` |
| **Standard User** | `user` | `userpassword` | `user@company.com` |

---

## 5. API Documentation & Swagger UI

Once running, access Swagger UI in your browser:
- **Interactive Swagger UI:** [http://localhost:8080/swagger-ui.html](http://localhost:8080/swagger-ui.html)
- **OpenAPI 3 JSON Spec:** [http://localhost:8080/v3/api-docs](http://localhost:8080/v3/api-docs)

### Authorizing in Swagger UI
Click the **Authorize** button in Swagger UI and choose one of two methods:
1. **`bearerAuth`**: Paste `Bearer <token>` after logging in via `/api/v1/auth/login`.
2. **`oauth2Password`**: Provide username `admin` and password `adminpassword` directly into the OAuth2 dialog.

---

## 6. Example API Requests

### 1. Authenticate (Login)
```bash
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "adminpassword"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Authentication successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9...",
    "tokenType": "Bearer",
    "expiresIn": 86400,
    "userId": "...",
    "username": "admin",
    "email": "admin@company.com",
    "roles": ["ROLE_ADMIN"],
    "permissions": ["USER_READ", "ROLE_READ", "COUNTRY_READ", "..."]
  }
}
```

### 2. Fetch User Dynamic Navigation Tree
```bash
curl -X GET "http://localhost:8080/api/v1/navigation?section=SIDEBAR" \
  -H "Authorization: Bearer <TOKEN>"
```

### 3. Public Read-Only Master Data
```bash
curl -X GET http://localhost:8080/api/v1/public/countries/active
```

### 4. Admin CRUD Master Data
```bash
curl -X POST http://localhost:8080/api/v1/admin/countries \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "FR",
    "name": "France",
    "description": "French Republic",
    "active": true,
    "sortOrder": 6
  }'
```

---

## 7. How to Add a New Lookup Domain in 3 Minutes

Thanks to the **Generic Engine**, creating a new domain entity (e.g. `Department`) requires only 4 small classes:

### 1. Entity (`Department.java`)
```java
@Entity
@Table(name = "tbl_departments")
public class Department extends BaseLookupEntity {}
```

### 2. Repository (`DepartmentRepository.java`)
```java
@Repository
public interface DepartmentRepository extends BaseLookupRepository<Department> {}
```

### 3. Mapper & Service (`DepartmentService.java`)
```java
@Service
public class DepartmentService extends AbstractLookupService<Department, LookupRequest, LookupResponse, DepartmentRepository> {
    public DepartmentService(DepartmentRepository repository, GenericMapper<Department, LookupRequest, LookupResponse> mapper) {
        super(repository, mapper, "Department");
    }
}
```

### 4. Triple Controllers
```java
// 1. Admin Full CRUD
@RestController
@RequestMapping("/api/v1/admin/departments")
public class AdminDepartmentController extends AbstractLookupController<LookupRequest, LookupResponse> {
    public AdminDepartmentController(DepartmentService service) { super(service); }
}

// 2. Mobile Read-Only
@RestController
@RequestMapping("/api/v1/mobile/departments")
public class MobileDepartmentController extends AbstractMobileLookupController<LookupRequest, LookupResponse> {
    public MobileDepartmentController(DepartmentService service) { super(service); }
}

// 3. Public Read-Only
@RestController
@RequestMapping("/api/v1/public/departments")
public class PublicDepartmentController extends AbstractPublicLookupController<LookupRequest, LookupResponse> {
    public PublicDepartmentController(DepartmentService service) { super(service); }
}
```

That is all! You automatically inherit full validation, pagination, keyword search, optimistic locking, audit tracks, soft-delete, and OpenAPI documentation.

---

## 8. Multi-Stage Docker Build

To package and run the application as a production container:

```bash
docker build -t enterprise-starter:1.0.0 .
docker run -p 8080:8080 \
  -e DB_HOST=host.docker.internal \
  -e DB_PORT=5432 \
  -e DB_NAME=enterprise_db \
  -e DB_USER=postgres \
  -e DB_PASSWORD=postgrespassword \
  -e JWT_SECRET=404E635266556A586E3272357538782F413F4428472B4B6250645367566B5970 \
  -e SPRING_PROFILES_ACTIVE=prod \
  enterprise-starter:1.0.0
```

---

## 9. License
Internal Enterprise Template © 2026. All rights reserved.

