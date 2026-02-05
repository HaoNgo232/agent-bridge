# Api Patterns

**Activation:** Model Decision
**Description:** Rules for api patterns

---
> API design principles and decision-making for 2025.
> **Learn to THINK, not copy fixed patterns.**

## 🎯 Selective Reading Rule

**Read ONLY files relevant to the request!** Check the content map, find what you need.

---

## 📑 Content Map

| File | Description | When to Read |
|------|-------------|--------------|
| `api-style.md` | REST vs GraphQL vs tRPC decision tree | Choosing API type |
| `rest.md` | Resource naming, HTTP methods, status codes | Designing REST API |
| `response.md` | Envelope pattern, error format, pagination | Response structure |
| `graphql.md` | Schema design, when to use, security | Considering GraphQL |
| `trpc.md` | TypeScript monorepo, type safety | TS fullstack projects |
| `versioning.md` | URI/Header/Query versioning | API evolution planning |
| `auth.md` | JWT, OAuth, Passkey, API Keys | Auth pattern selection |
| `rate-limiting.md` | Token bucket, sliding window | API protection |
| `documentation.md` | OpenAPI/Swagger best practices | Documentation |
| `security-testing.md` | OWASP API Top 10, auth/authz testing | Security audits |

---

## 🔗 Related Skills

| Need | Skill |
|------|-------|
| API implementation | `@[skills/backend-development]` |
| Data structure | `@[skills/database-design]` |
| Security details | `@[skills/security-hardening]` |

---

## ✅ Decision Checklist

Before designing an API:

- [ ] **Asked user about API consumers?**
- [ ] **Chosen API style for THIS context?** (REST/GraphQL/tRPC)
- [ ] **Defined consistent response format?**
- [ ] **Planned versioning strategy?**
- [ ] **Considered authentication needs?**
- [ ] **Planned rate limiting?**
- [ ] **Documentation approach defined?**

---

## ❌ Anti-Patterns

**DON'T:**
- Default to REST for everything
- Use verbs in REST endpoints (/getUsers)
- Return inconsistent response formats
- Expose internal errors to clients
- Skip rate limiting

**DO:**
- Choose API style based on context
- Ask about client requirements
- Document thoroughly
- Use appropriate status codes

---

## Script

| Script | Purpose | Command |
|--------|---------|---------|
| `scripts/api_validator.py` | API endpoint validation | `python scripts/api_validator.py <project_path>` |



---

# API Style Selection (2025)

> REST vs GraphQL vs tRPC - Hangi durumda hangisi?

## Decision Tree

```
Who are the API consumers?
│
├── Public API / Multiple platforms
│   └── REST + OpenAPI (widest compatibility)
│
├── Complex data needs / Multiple frontends
│   └── GraphQL (flexible queries)
│
├── TypeScript frontend + backend (monorepo)
│   └── tRPC (end-to-end type safety)
│
├── Real-time / Event-driven
│   └── WebSocket + AsyncAPI
│
└── Internal microservices
    └── gRPC (performance) or REST (simplicity)
```

## Comparison

| Factor | REST | GraphQL | tRPC |
|--------|------|---------|------|
| **Best for** | Public APIs | Complex apps | TS monorepos |
| **Learning curve** | Low | Medium | Low (if TS) |
| **Over/under fetching** | Common | Solved | Solved |
| **Type safety** | Manual (OpenAPI) | Schema-based | Automatic |
| **Caching** | HTTP native | Complex | Client-based |

## Selection Questions

1. Who are the API consumers?
2. Is the frontend TypeScript?
3. How complex are the data relationships?
4. Is caching critical?
5. Public or internal API?


---

# Authentication Patterns

> Choose auth pattern based on use case.

## Selection Guide

| Pattern | Best For |
|---------|----------|
| **JWT** | Stateless, microservices |
| **Session** | Traditional web, simple |
| **OAuth 2.0** | Third-party integration |
| **API Keys** | Server-to-server, public APIs |
| **Passkey** | Modern passwordless (2025+) |

## JWT Principles

```
Important:
├── Always verify signature
├── Check expiration
├── Include minimal claims
├── Use short expiry + refresh tokens
└── Never store sensitive data in JWT
```


---

# API Documentation Principles

> Good docs = happy developers = API adoption.

## OpenAPI/Swagger Essentials

```
Include:
├── All endpoints with examples
├── Request/response schemas
├── Authentication requirements
├── Error response formats
└── Rate limiting info
```

## Good Documentation Has

```
Essentials:
├── Quick start / Getting started
├── Authentication guide
├── Complete API reference
├── Error handling guide
├── Code examples (multiple languages)
└── Changelog
```


---

# GraphQL Principles

> Flexible queries for complex, interconnected data.

## When to Use

```
✅ Good fit:
├── Complex, interconnected data
├── Multiple frontend platforms
├── Clients need flexible queries
├── Evolving data requirements
└── Reducing over-fetching matters

❌ Poor fit:
├── Simple CRUD operations
├── File upload heavy
├── HTTP caching important
└── Team unfamiliar with GraphQL
```

## Schema Design Principles

```
Principles:
├── Think in graphs, not endpoints
├── Design for evolvability (no versions)
├── Use connections for pagination
├── Be specific with types (not generic "data")
└── Handle nullability thoughtfully
```

## Security Considerations

```
Protect against:
├── Query depth attacks → Set max depth
├── Query complexity → Calculate cost
├── Batching abuse → Limit batch size
├── Introspection → Disable in production
```


---

# Rate Limiting Principles

> Protect your API from abuse and overload.

## Why Rate Limit

```
Protect against:
├── Brute force attacks
├── Resource exhaustion
├── Cost overruns (if pay-per-use)
└── Unfair usage
```

## Strategy Selection

| Type | How | When |
|------|-----|------|
| **Token bucket** | Burst allowed, refills over time | Most APIs |
| **Sliding window** | Smooth distribution | Strict limits |
| **Fixed window** | Simple counters per window | Basic needs |

## Response Headers

```
Include in headers:
├── X-RateLimit-Limit (max requests)
├── X-RateLimit-Remaining (requests left)
├── X-RateLimit-Reset (when limit resets)
└── Return 429 when exceeded
```


---

# Response Format Principles

> Consistency is key - choose a format and stick to it.

## Common Patterns

```
Choose one:
├── Envelope pattern ({ success, data, error })
├── Direct data (just return the resource)
└── HAL/JSON:API (hypermedia)
```

## Error Response

```
Include:
├── Error code (for programmatic handling)
├── User message (for display)
├── Details (for debugging, field-level errors)
├── Request ID (for support)
└── NOT internal details (security!)
```

## Pagination Types

| Type | Best For | Trade-offs |
|------|----------|------------|
| **Offset** | Simple, jumpable | Performance on large datasets |
| **Cursor** | Large datasets | Can't jump to page |
| **Keyset** | Performance critical | Requires sortable key |

### Selection Questions

1. How large is the dataset?
2. Do users need to jump to specific pages?
3. Is data frequently changing?


---

# REST Principles

> Resource-based API design - nouns not verbs.

## Resource Naming Rules

```
Principles:
├── Use NOUNS, not verbs (resources, not actions)
├── Use PLURAL forms (/users not /user)
├── Use lowercase with hyphens (/user-profiles)
├── Nest for relationships (/users/123/posts)
└── Keep shallow (max 3 levels deep)
```

## HTTP Method Selection

| Method | Purpose | Idempotent? | Body? |
|--------|---------|-------------|-------|
| **GET** | Read resource(s) | Yes | No |
| **POST** | Create new resource | No | Yes |
| **PUT** | Replace entire resource | Yes | Yes |
| **PATCH** | Partial update | No | Yes |
| **DELETE** | Remove resource | Yes | No |

## Status Code Selection

| Situation | Code | Why |
|-----------|------|-----|
| Success (read) | 200 | Standard success |
| Created | 201 | New resource created |
| No content | 204 | Success, nothing to return |
| Bad request | 400 | Malformed request |
| Unauthorized | 401 | Missing/invalid auth |
| Forbidden | 403 | Valid auth, no permission |
| Not found | 404 | Resource doesn't exist |
| Conflict | 409 | State conflict (duplicate) |
| Validation error | 422 | Valid syntax, invalid data |
| Rate limited | 429 | Too many requests |
| Server error | 500 | Our fault |


---

# API Security Testing

> Principles for testing API security. OWASP API Top 10, authentication, authorization testing.

---

## OWASP API Security Top 10

| Vulnerability | Test Focus |
|---------------|------------|
| **API1: BOLA** | Access other users' resources |
| **API2: Broken Auth** | JWT, session, credentials |
| **API3: Property Auth** | Mass assignment, data exposure |
| **API4: Resource Consumption** | Rate limiting, DoS |
| **API5: Function Auth** | Admin endpoints, role bypass |
| **API6: Business Flow** | Logic abuse, automation |
| **API7: SSRF** | Internal network access |
| **API8: Misconfiguration** | Debug endpoints, CORS |
| **API9: Inventory** | Shadow APIs, old versions |
| **API10: Unsafe Consumption** | Third-party API trust |

---

## Authentication Testing

### JWT Testing

| Check | What to Test |
|-------|--------------|
| Algorithm | None, algorithm confusion |
| Secret | Weak secrets, brute force |
| Claims | Expiration, issuer, audience |
| Signature | Manipulation, key injection |

### Session Testing

| Check | What to Test |
|-------|--------------|
| Generation | Predictability |
| Storage | Client-side security |
| Expiration | Timeout enforcement |
| Invalidation | Logout effectiveness |

---

## Authorization Testing

| Test Type | Approach |
|-----------|----------|
| **Horizontal** | Access peer users' data |
| **Vertical** | Access higher privilege functions |
| **Context** | Access outside allowed scope |

### BOLA/IDOR Testing

1. Identify resource IDs in requests
2. Capture request with user A's session
3. Replay with user B's session
4. Check for unauthorized access

---

## Input Validation Testing

| Injection Type | Test Focus |
|----------------|------------|
| SQL | Query manipulation |
| NoSQL | Document queries |
| Command | System commands |
| LDAP | Directory queries |

**Approach:** Test all parameters, try type coercion, test boundaries, check error messages.

---

## Rate Limiting Testing

| Aspect | Check |
|--------|-------|
| Existence | Is there any limit? |
| Bypass | Headers, IP rotation |
| Scope | Per-user, per-IP, global |

**Bypass techniques:** X-Forwarded-For, different HTTP methods, case variations, API versioning.

---

## GraphQL Security

| Test | Focus |
|------|-------|
| Introspection | Schema disclosure |
| Batching | Query DoS |
| Nesting | Depth-based DoS |
| Authorization | Field-level access |

---

## Security Testing Checklist

**Authentication:**
- [ ] Test for bypass
- [ ] Check credential strength
- [ ] Verify token security

**Authorization:**
- [ ] Test BOLA/IDOR
- [ ] Check privilege escalation
- [ ] Verify function access

**Input:**
- [ ] Test all parameters
- [ ] Check for injection

**Config:**
- [ ] Check CORS
- [ ] Verify headers
- [ ] Test error handling

---

> **Remember:** APIs are the backbone of modern apps. Test them like attackers will.


---

# tRPC Principles

> End-to-end type safety for TypeScript monorepos.

## When to Use

```
✅ Perfect fit:
├── TypeScript on both ends
├── Monorepo structure
├── Internal tools
├── Rapid development
└── Type safety critical

❌ Poor fit:
├── Non-TypeScript clients
├── Public API
├── Need REST conventions
└── Multiple language backends
```

## Key Benefits

```
Why tRPC:
├── Zero schema maintenance
├── End-to-end type inference
├── IDE autocomplete across stack
├── Instant API changes reflected
└── No code generation step
```

## Integration Patterns

```
Common setups:
├── Next.js + tRPC (most common)
├── Monorepo with shared types
├── Remix + tRPC
└── Any TS frontend + backend
```


---

# Versioning Strategies

> Plan for API evolution from day one.

## Decision Factors

| Strategy | Implementation | Trade-offs |
|----------|---------------|------------|
| **URI** | /v1/users 

... (truncated)
