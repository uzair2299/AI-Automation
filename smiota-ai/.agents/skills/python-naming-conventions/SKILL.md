---
name: python-naming-conventions
description: Enforces standard Python PEP 8 naming conventions for files, modules, classes, functions, variables, constants, packages, private members, and type variables. Use when creating, editing, reviewing, or refactoring Python code.
---

# Python Naming Conventions Skill

## Objective

Follow Python PEP 8 naming conventions consistently across the entire project. Apply these rules whenever generating, modifying, reviewing, or refactoring Python code.

## Naming Rules

### 1. Files and Modules
- Use `snake_case` for Python filenames and module names.
- Use descriptive, lowercase names.
- Prefer names that communicate the file's responsibility.

Examples:
- `chat_service.py`
- `user_repository.py`
- `customer_agent.py`
- `chat_message_schema.py`
- `database_config.py`

Incorrect:
- `ChatService.py`
- `UserRepository.py`
- `chatService.py`

### 2. Classes
- Use `PascalCase` for class names.
- Use descriptive nouns that represent the class responsibility.
- Use one primary class per file when it improves clarity, but do not enforce this as an absolute rule.

Examples:
- `ChatService`
- `UserRepository`
- `CustomerAgent`
- `ChatSession`
- `DatabaseConfig`

Incorrect:
- `chat_service`
- `chatService`
- `CHAT_SERVICE`

### 3. Functions and Methods
- Use `snake_case`.
- Prefer descriptive names that indicate an action or outcome.
- Use verbs for operations.

Examples:
- `get_chat_history()`
- `create_chat_session()`
- `validate_access_token()`
- `retrieve_package_status()`
- `close_database_connection()`

Incorrect:
- `GetChatHistory()`
- `getChatHistory()`
- `GET_CHAT_HISTORY()`

### 4. Variables and Parameters
- Use `snake_case`.
- Choose meaningful names instead of vague abbreviations.
- Keep names concise but understandable.

Examples:
- `user_id`
- `chat_session`
- `tracking_number`
- `access_token`
- `conversation_history`

Incorrect:
- `userId`
- `ChatSession`
- `tn`
- `x1`

### 5. Constants
- Use `UPPER_SNAKE_CASE`.
- Define module-level constants in uppercase.
- Keep configuration values in the appropriate configuration module or settings class.

Examples:
- `MAX_RETRY_COUNT`
- `DEFAULT_SESSION_TTL`
- `DATABASE_URL`
- `MAX_MESSAGE_LENGTH`

### 6. Packages and Directories
- Prefer short, descriptive, lowercase names.
- Use underscores only when necessary for readability.
- Avoid unnecessary abbreviations.

Examples:
- `services/`
- `repositories/`
- `routers/`
- `schemas/`
- `agents/`
- `core/`

### 7. Private Members
- Prefix internal implementation details with a single underscore.
- Do not use double underscores unless Python name mangling is specifically required.

Examples:
- `_validate_token()`
- `_connection_pool`
- `_load_configuration()`

A leading underscore indicates internal use; it does not enforce access restrictions.

### 8. Type Variables
- Use `PascalCase` for type variables.
- Choose descriptive names and use a `T` suffix when useful.

Examples:
- `ResponseT`
- `ModelT`
- `RequestT`

### 9. Boolean Names
- Prefer names that clearly communicate true or false.
- Use prefixes such as `is_`, `has_`, `can_`, or `should_` where appropriate.

Examples:
- `is_authenticated`
- `has_access`
- `can_send_message`
- `should_retry`

### 10. Exception Classes
- Use `PascalCase`.
- End custom exception class names with `Error` when appropriate.

Examples:
- `ChatSessionError`
- `TokenValidationError`
- `PackageNotFoundError`

## FastAPI Project Conventions

Prefer names that communicate each component's responsibility:

| Component | Example filename | Example class |
|---|---|---|
| Router | `chat_router.py` | `ChatRouter` (if a class is needed) |
| Service | `chat_service.py` | `ChatService` |
| Repository | `chat_repository.py` | `ChatRepository` |
| Schema | `chat_message_schema.py` | `ChatMessageRequest` |
| Configuration | `config.py` | `Settings` |
| Agent | `customer_agent.py` | `CustomerAgent` |
| Exception | `chat_exceptions.py` | `ChatSessionError` |

For FastAPI endpoints, ordinary functions are preferred unless a class is justified. Use Pydantic model names in `PascalCase`, such as `ChatMessageRequest` and `ChatMessageResponse`.

## Enforcement Instructions

Whenever creating or modifying code:

1. Check the applicable naming rules before introducing new identifiers.
2. Follow existing project architecture and naming patterns when they are consistent with these conventions.
3. Correct naming violations in files being modified.
4. Avoid unrelated renaming or large-scale refactoring.
5. Never rename public APIs, database columns, environment variables, serialized fields, or externally consumed identifiers without assessing compatibility and obtaining approval when necessary.
6. Preserve Python framework requirements, third-party interfaces, and established protocol names.
7. Do not change business logic solely to enforce naming conventions.
8. Use Ruff to check code quality when available.

## Validation

Run these commands when Ruff is installed:

```bash
ruff check .
ruff format --check .
```

To automatically format Python code:

```bash
ruff format .
```

Note that formatting does not automatically correct every naming violation. Review identifiers separately and use suitable linting rules where necessary.

## Final Checklist

Before completing a coding task, verify:

- [ ] Python filenames use `snake_case`.
- [ ] Class names use `PascalCase`.
- [ ] Functions and methods use `snake_case`.
- [ ] Variables and parameters use `snake_case`.
- [ ] Constants use `UPPER_SNAKE_CASE`.
- [ ] Package and directory names are lowercase and descriptive.
- [ ] Private implementation details use a leading underscore where appropriate.
- [ ] Type variables use `PascalCase`.
- [ ] Boolean names clearly express their meaning.
- [ ] Existing integrations and public interfaces remain compatible.
- [ ] No unrelated business logic or functionality has changed.
