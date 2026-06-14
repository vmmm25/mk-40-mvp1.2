---
name: api-design
version: 1.0.0
description: Principios y patrones para diseñar APIs REST robustas, consistentes y fáciles de usar. Usa cuando diseñes, revises o documentes APIs.
tags: [api, rest, backend, design, http, openapi, documentation]
author: garri333
license: MIT
---

# API Design Guidelines

## Principios fundamentales

1. **Consistencia sobre conveniencia** — Mejor ser predecible que inteligente
2. **Diseña para el consumidor** — La API es un producto; los developers son tu cliente
3. **Explícito > implícito** — Los nombres deben ser obvios, no necesitar documentación
4. **Evolucionabilidad** — Diseña pensando en que tendrás que cambiarla sin romper clientes

## Recursos y URLs

### Nombrado de recursos
```
✅ Sustantivos en plural, minúsculas, kebab-case:
GET /users
GET /users/123
GET /users/123/orders
GET /blog-posts

❌ Verbos en la URL:
GET /getUsers
POST /createUser
GET /fetchUserOrders
```

### Jerarquía de recursos (máx. 2-3 niveles)
```
/users                    — Colección de usuarios
/users/{id}               — Usuario específico
/users/{id}/orders        — Órdenes del usuario
/users/{id}/orders/{id}   — Orden específica del usuario

⚠️ Evita más de 3 niveles — es señal de mal diseño
```

### Filtrado, paginación y ordenación (query params)
```
GET /users?role=admin&status=active           — Filtros
GET /users?page=2&per_page=20                 — Paginación (cursor mejor)
GET /users?cursor=abc123&limit=20             — Cursor pagination (para listas grandes)
GET /products?sort=price&order=asc            — Ordenación
GET /users?fields=id,name,email               — Proyección de campos
GET /search?q=javascript&category=courses     — Búsqueda
```

## HTTP Methods

| Método | Uso | Idempotente | Safe |
|--------|-----|-------------|------|
| GET | Leer recurso | Sí | Sí |
| POST | Crear recurso | No | No |
| PUT | Reemplazar recurso completo | Sí | No |
| PATCH | Actualizar parcialmente | No | No |
| DELETE | Eliminar recurso | Sí | No |

## HTTP Status Codes

### Éxito (2xx)
```
200 OK           — Respuesta genérica de éxito para GET/PUT/PATCH
201 Created      — Recurso creado con POST (incluir Location header)
204 No Content   — Éxito sin cuerpo de respuesta (DELETE)
```

### Errores de cliente (4xx)
```
400 Bad Request       — Payload inválido o malformado
401 Unauthorized      — No autenticado
403 Forbidden         — Autenticado pero sin permisos
404 Not Found         — Recurso no existe
409 Conflict          — Conflicto (ej: email duplicado)
422 Unprocessable     — Falla de validación semántica
429 Too Many Requests — Rate limit alcanzado
```

### Errores de servidor (5xx)
```
500 Internal Server Error — Error genérico de servidor
503 Service Unavailable   — Servicio temporalmente no disponible
```

## Estructura de respuesta

### Respuesta exitosa
```json
{
  "data": {
    "id": "user_123",
    "name": "Oriol García",
    "email": "oriol@example.com",
    "createdAt": "2026-02-18T10:00:00Z"
  }
}
```

### Respuesta de lista
```json
{
  "data": [...],
  "pagination": {
    "total": 247,
    "page": 2,
    "perPage": 20,
    "nextCursor": "eyJpZCI6IjEyMCJ9"
  }
}
```

### Respuesta de error
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "El campo 'email' es requerido",
    "details": [
      {
        "field": "email",
        "message": "Es un campo requerido",
        "code": "REQUIRED"
      }
    ]
  }
}
```

## Naming conventions

```json
// ✅ camelCase para JSON (estándar en JS ecosystems)
{
  "userId": "123",
  "firstName": "Oriol",
  "createdAt": "2026-02-18T10:00:00Z",
  "isActive": true
}

// ✅ snake_case para Python/Ruby ecosystems
{
  "user_id": "123",
  "first_name": "Oriol"
}

// Elige uno y sé consistente en toda la API
```

## Fechas y timestamps

```json
// ✅ Siempre ISO 8601 en UTC
"createdAt": "2026-02-18T10:30:00Z"
"updatedAt": "2026-02-18T15:45:22.123Z"

// ❌ Evitar
"createdAt": 1708254600        // Unix timestamp → poco legible
"createdAt": "18/02/2026"     // Formato ambiguo de fecha
"createdAt": "Feb 18, 2026"   // No estandarizado
```

## Versionado

### URL versioning (más explícito y fácil de usar)
```
/v1/users
/v2/users

// Los clientes controlan cuándo migran
// Simple de entender y cacheable
```

### Header versioning (más "purista")
```
Accept: application/vnd.myapi.v1+json
API-Version: 2026-01-01
```

### Compatibilidad hacia atrás
- Añadir nuevos campos: ✅ siempre seguro
- Cambiar tipo de campo: ❌ breaking change → nueva versión
- Eliminar campo: ❌ breaking change → deprecar primero, luego eliminar
- Cambiar nombre de campo: ❌ breaking change

## Autenticación

```http
# API Key (más simple, buena para M2M)
Authorization: Bearer api_key_here
X-API-Key: api_key_here

# JWT (para usuarios autenticados)
Authorization: Bearer eyJhbGci...
```

### Refresh de tokens
```
1. POST /auth/login → { accessToken, refreshToken }
2. accessToken: TTL corto (15 min - 1 hora)
3. POST /auth/refresh → { accessToken } (usando refresh token)
4. refreshToken: TTL largo (7-30 días), single-use (rotation)
```

## Rate limiting

Incluir headers en la respuesta:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1708254600
Retry-After: 60   # Solo cuando rate limit alcanzado (429)
```

## Documentación (OpenAPI / Swagger)

```yaml
openapi: 3.0.3
info:
  title: Mi API
  version: 1.0.0

paths:
  /users/{id}:
    get:
      summary: Obtener usuario por ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Usuario encontrado
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: Usuario no encontrado
```

## Checklist de diseño

- [ ] URLs son sustantivos en plural, sin verbos
- [ ] HTTP methods usados correctamente (GET no modifica estado)
- [ ] Status codes apropiados (no siempre 200)
- [ ] Errores tienen estructura consistente con `code` legible
- [ ] Paginación implementada para listas
- [ ] Timestamps en ISO 8601 UTC
- [ ] Autenticación documentada
- [ ] Rate limiting implementado y documentado
- [ ] Versioning strategy definida
- [ ] OpenAPI spec actualizada

## Referencias
- [Stripe API Design](https://stripe.com/docs/api)
- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines/blob/vNext/azure/Guidelines.md)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [API Design Patterns — JJ Geewax](https://www.manning.com/books/api-design-patterns)
