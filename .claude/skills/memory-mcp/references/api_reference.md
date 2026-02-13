# Memory MCP API Reference

Complete reference for Memory MCP server operations.

## Core Operations

### Create Entities

**`mcp__memory__create_entities`**
- **Purpose**: Create multiple new entities in the knowledge graph
- **Parameters**:
  - `entities`: Array of entity objects
    - `name`: Entity name (required)
    - `entityType`: Type of entity (required)
    - `observations`: Array of observation strings (required)
- **Returns**: Created entity IDs
- **Example**:
  ```json
  {
    "entities": [
      {
        "name": "authentication-strategy",
        "entityType": "decision",
        "observations": [
          "Decided to use JWT tokens",
          "Refresh tokens expire after 7 days",
          "Access tokens expire after 1 hour"
        ]
      }
    ]
  }
  ```

### Create Relations

**`mcp__memory__create_relations`**
- **Purpose**: Create relationships between entities
- **Parameters**:
  - `relations`: Array of relation objects
    - `from`: Source entity name (required)
    - `to`: Target entity name (required)
    - `relationType`: Type of relationship (required)
- **Returns**: Created relation IDs
- **Example**:
  ```json
  {
    "relations": [
      {
        "from": "authentication-strategy",
        "to": "user-service",
        "relationType": "implements"
      }
    ]
  }
  ```

### Add Observations

**`mcp__memory__add_observations`**
- **Purpose**: Add new observations to existing entities
- **Parameters**:
  - `observations`: Array of observation objects
    - `entityName`: Entity to update (required)
    - `contents`: Array of observation strings (required)
- **Returns**: Success status
- **Example**:
  ```json
  {
    "observations": [
      {
        "entityName": "authentication-strategy",
        "contents": [
          "Added biometric authentication support",
          "Integrated with OAuth providers"
        ]
      }
    ]
  }
  ```

### Search Operations

**`mcp__memory__search_nodes`**
- **Purpose**: Search for entities in the knowledge graph
- **Parameters**:
  - `query`: Search query string (required)
- **Returns**: Matching entities with observations and relations
- **Example**:
  ```json
  {
    "query": "authentication"
  }
  ```
- **Returns**:
  ```json
  {
    "nodes": [
      {
        "name": "authentication-strategy",
        "entityType": "decision",
        "observations": ["..."],
        "relations": [...]
      }
    ]
  }
  ```

**`mcp__memory__open_nodes`**
- **Purpose**: Retrieve specific entities by name
- **Parameters**:
  - `names`: Array of entity names (required)
- **Returns**: Complete entity details
- **Example**:
  ```json
  {
    "names": ["authentication-strategy", "database-choice"]
  }
  ```

### Read Operations

**`mcp__memory__read_graph`**
- **Purpose**: Retrieve the entire knowledge graph
- **Parameters**: None
- **Returns**: All entities, observations, and relations
- **Use Case**: For comprehensive analysis or export
- **Example**:
  ```
  read_graph()
  → Returns complete graph structure
  ```

### Delete Operations

**`mcp__memory__delete_entities`**
- **Purpose**: Delete entities and their relations
- **Parameters**:
  - `entityNames`: Array of entity names to delete (required)
- **Returns**: Success status
- **Warning**: Deletes all associated relations
- **Example**:
  ```json
  {
    "entityNames": ["old-strategy", "deprecated-pattern"]
  }
  ```

**`mcp__memory__delete_observations`**
- **Purpose**: Delete specific observations from entities
- **Parameters**:
  - `deletions`: Array of deletion objects
    - `entityName`: Entity to modify (required)
    - `observations`: Array of observation strings to delete (required)
- **Returns**: Success status
- **Example**:
  ```json
  {
    "deletions": [
      {
        "entityName": "authentication-strategy",
        "observations": ["Outdated approach that was replaced"]
      }
    ]
  }
  ```

**`mcp__memory__delete_relations`**
- **Purpose**: Delete specific relationships
- **Parameters**:
  - `relations`: Array of relation objects to delete
- **Returns**: Success status
- **Example**:
  ```json
  {
    "relations": [
      {
        "from": "old-service",
        "to": "database",
        "relationType": "uses"
      }
    ]
  }
  ```

## Entity Types

### Recommended Entity Types

**Decisions**
```
entityType: "decision"
Use for: Architectural choices, technology selections, approach decisions
Example: "authentication-method", "database-choice", "deployment-strategy"
```

**Facts**
```
entityType: "fact"
Use for: Objective information, configuration values, constants
Example: "api-base-url", "server-port", "database-name"
```

**Patterns**
```
entityType: "pattern"
Use for: Coding patterns, design patterns, best practices
Example: "repository-pattern", "dependency-injection", "error-handling-approach"
```

**Preferences**
```
entityType: "preference"
Use for: Team preferences, style choices, subjective decisions
Example: "code-style", "testing-framework", "linting-rules"
```

**Components**
```
entityType: "component"
Use for: System components, services, modules
Example: "user-service", "auth-middleware", "payment-gateway"
```

**Features**
```
entityType: "feature"
Use for: Product features, capabilities
Example: "user-registration", "password-reset", "two-factor-auth"
```

## Relation Types

### Common Relation Types

- `implements`: Component implements decision/pattern
- `depends-on`: Entity depends on another
- `uses`: Entity uses another entity
- `part-of`: Entity is part of larger entity
- `replaced-by`: Entity was replaced by another
- `related-to`: General relationship
- `documented-in`: Links to documentation
- `tested-by`: Links to test coverage

## Usage Patterns

### Pattern 1: Store Architectural Decision
```json
// Create decision entity
{
  "entities": [{
    "name": "jwt-authentication",
    "entityType": "decision",
    "observations": [
      "Chose JWT for stateless authentication",
      "Access tokens: 1 hour expiry",
      "Refresh tokens: 7 day expiry",
      "HMAC SHA-256 signing algorithm"
    ]
  }]
}

// Link to component
{
  "relations": [{
    "from": "auth-service",
    "to": "jwt-authentication",
    "relationType": "implements"
  }]
}

// Link to ADR
{
  "observations": [{
    "entityName": "jwt-authentication",
    "contents": ["Documented in ADR-003"]
  }]
}
```

### Pattern 2: Store Component Information
```json
{
  "entities": [{
    "name": "user-service",
    "entityType": "component",
    "observations": [
      "FastAPI-based microservice",
      "Handles user CRUD operations",
      "PostgreSQL database with SQLModel ORM",
      "RESTful API at /api/v1/users"
    ]
  }]
}

{
  "relations": [
    {
      "from": "user-service",
      "to": "postgresql-database",
      "relationType": "uses"
    },
    {
      "from": "user-service",
      "to": "jwt-authentication",
      "relationType": "implements"
    }
  ]
}
```

### Pattern 3: Track Feature Evolution
```json
// Initial feature
{
  "entities": [{
    "name": "basic-login",
    "entityType": "feature",
    "observations": ["Email and password authentication"]
  }]
}

// Enhanced feature
{
  "entities": [{
    "name": "advanced-login",
    "entityType": "feature",
    "observations": [
      "Email and password authentication",
      "OAuth2 social login",
      "Two-factor authentication"
    ]
  }]
}

// Link evolution
{
  "relations": [{
    "from": "basic-login",
    "to": "advanced-login",
    "relationType": "replaced-by"
  }]
}
```

### Pattern 4: Cross-Session Context Restoration
```json
// At session start, search for current work
{
  "query": "user-profile feature"
}

// Returns related entities
→ user-profile-feature, user-service, database-schema, etc.

// Open specific entities
{
  "names": ["user-profile-feature", "profile-api-design"]
}

// Continue work with full context
```

## Best Practices

### Naming Conventions
- Use lowercase-with-hyphens: `authentication-strategy`
- Be descriptive: `jwt-auth-implementation` not `auth1`
- Use consistent prefixes for related entities:
  - `auth-*`: authentication-related
  - `db-*`: database-related
  - `api-*`: API-related

### Observation Content
- Write concise, factual statements
- One fact per observation
- Include dates for time-sensitive info
- Link to files/docs when relevant
- Avoid duplicating information in multiple observations

### Relation Organization
- Use consistent relation types across graph
- Create bidirectional relations when needed
- Link decisions to implementing components
- Connect features to components
- Link to documentation (specs, ADRs)

### Memory Hygiene
- Delete obsolete entities when decisions change
- Update observations rather than adding conflicting ones
- Consolidate related memories periodically
- Use specific entity types for better searchability
- Review and clean up after major refactoring

## Graph Structure Example

```
[authentication-strategy] (decision)
  ├─ implements → [auth-service] (component)
  ├─ documented-in → [ADR-003]
  └─ uses → [jwt-library] (dependency)

[auth-service] (component)
  ├─ part-of → [backend-system]
  ├─ uses → [user-database]
  └─ tested-by → [auth-test-suite]

[user-registration] (feature)
  ├─ implemented-by → [auth-service]
  └─ depends-on → [email-service]
```

## Error Handling

### Common Error Patterns

**Entity Not Found**
```
Error: Entity "xyz" not found
Solution: Create entity first or check name spelling
```

**Duplicate Entity**
```
Error: Entity "xyz" already exists
Solution: Use add_observations to update or delete old entity
```

**Invalid Relation**
```
Error: Cannot create relation - entity missing
Solution: Ensure both entities exist before creating relation
```

**Empty Observations**
```
Error: Observations array cannot be empty
Solution: Provide at least one observation when creating entity
```
