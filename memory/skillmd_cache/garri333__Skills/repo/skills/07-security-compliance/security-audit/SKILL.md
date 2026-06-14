---
name: security-audit
version: 1.0.0
description: Auditoría de seguridad completa para aplicaciones web y configuraciones. Usa cuando necesites revisar la seguridad de un proyecto, detectar vulnerabilidades o preparar un sistema para producción.
tags: [security, audit, vulnerabilities, owasp, compliance, cybersecurity]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Security Audit Skill

## Cuándo usar esta skill
- Revisar código antes de pasar a producción
- Auditar la configuración de un servidor o servicio
- Preparar una aplicación para cumplimiento (ISO 27001, SOC 2)
- Revisar dependencias en busca de vulnerabilidades
- Evaluar el posture de seguridad general de un proyecto

## OWASP Top 10 — Checklist básica

### A01: Broken Access Control
```
□ Los endpoints verifican autenticación Y autorización
□ No se puede acceder a recursos de otros usuarios por manipular IDs
□ Las rutas de admin tienen protección adicional
□ CORS configurado correctamente (no Access-Control-Allow-Origin: *)
□ No se exponen endpoints no usados
```

### A02: Cryptographic Failures
```
□ HTTPS forzado en todas las rutas (HSTS habilitado)
□ Datos sensibles no en logs, URLs, o localStorage
□ Passwords hasheados con bcrypt/argon2 (no MD5/SHA1)
□ API keys y secrets en variables de entorno, no en código
□ Certificados TLS válidos y actualizados
```

### A03: Injection
```
□ Queries parametrizadas / ORM (no string concatenation)
□ Input validado y saneado antes de usar
□ Sin eval() con input de usuario
□ Sin shell commands con input no saneado
□ HTML escapado antes de renderizar (XSS prevention)
```

### A04: Insecure Design
```
□ Principio de mínimo privilegio (un usuario solo accede a lo que necesita)
□ Rate limiting en endpoints críticos (auth, reset password)
□ No se expone stack trace en producción
□ Datos sensibles no en responses de debug
□ Funcionalidades críticas tienen logs de auditoría
```

### A05: Security Misconfiguration
```
□ Software actualizado (dependencias, OS, runtime)
□ Configuración de producción diferente a desarrollo
□ Default credentials cambiadas
□ Security headers configurados (ver abajo)
□ Sin archivos de debug o configuración en público
```

### A06: Vulnerable and Outdated Components
```
□ npm audit / pip audit sin issues críticos o altos
□ Dockerfile usa imagen base con tag específico (no :latest)
□ Dependencias revisadas regularmente
□ CVE alerts configuradas en el repositorio
```

### A07: Identification and Authentication Failures
```
□ Passwords con requisitos mínimos (longitud, complejidad)
□ Protección contra brute force (lockout o captcha)
□ Multi-factor authentication disponible
□ Session tokens tienen TTL corto
□ Logout invalida la sesión en el servidor
□ Reset de password usa token de un solo uso
```

### A08: Software and Data Integrity Failures
```
□ CI/CD pipeline tiene checks de seguridad
□ No se ejecuta código de fuentes no confiables
□ Verificación de integridad de dependencias (package-lock.json)
□ Assets de CDN con SRI (Subresource Integrity) hashes
```

### A09: Security Logging and Monitoring Failures
```
□ Login attempts logueados (éxito y fallo)
□ Cambios de privilegio o acceso admin logueados
□ Alertas configuradas para patrones sospechosos
□ Logs no contienen passwords ni tokens
□ Logs centralizados y protegidos
```

### A10: Server-Side Request Forgery (SSRF)
```
□ URLs en requests del servidor validadas contra allowlist
□ No se permiten IPs internas en URLs de usuario
□ Metadata endpoints internos (169.254.169.254) bloqueados
```

## Security Headers

```http
# Añadir a todas las respuestas del servidor
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Content-Security-Policy: default-src 'self'; script-src 'self'; ...
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

### Verificar headers
```bash
# Comprobar headers de seguridad
curl -I https://tudominio.com
# O usar: https://securityheaders.com/
```

## Auditoría de dependencias

```bash
# Node.js
npm audit
npm audit --audit-level=high  # Solo issues high/critical
npm audit fix                  # Auto-fix cuando es posible

# Python
pip-audit                      # pip install pip-audit
safety check                   # pip install safety

# Herramienta multilenguaje
snyk test                      # snyk.io
```

## Buscar secrets en el código

```bash
# truffleHog — busca secrets en git history
docker run --rm -v $(pwd):/proj trufflesecurity/trufflehog:latest filesystem /proj

# gitleaks
gitleaks detect --source . --verbose

# detect-secrets (pre-commit hook)
detect-secrets scan
```

## Herramientas de escaneo

```bash
# SAST — Static Application Security Testing
semgrep scan --config=p/owasp-top-ten

# Para aplicaciones web (pentest básico)
nikto -h https://tudominio.com -ssl

# Port scanning
nmap -sV -sC tudominio.com  # Solo en sistemas que controlas

# SSL/TLS
testssl.sh https://tudominio.com
# O: https://www.ssllabs.com/ssltest/
```

## Configuraciones seguras por plataforma

### Node.js / Express
```javascript
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';

app.use(helmet());  // Security headers automáticos

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutos
  max: 100,                    // 100 requests por IP
  standardHeaders: true,
  legacyHeaders: false,
});

app.use('/api/', limiter);
app.use('/auth/', rateLimit({ windowMs: 15 * 60 * 1000, max: 5 })); // Más estricto en auth
```

### Docker
```dockerfile
# ✅ Imagen base específica (no :latest)
FROM node:20.11.0-alpine3.19

# ✅ No correr como root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# ✅ COPY mínimo (ignorar node_modules, .env, .git)
COPY --chown=appuser:appgroup package*.json ./
RUN npm ci --only=production  # Solo dependencias de producción
COPY --chown=appuser:appgroup . .

# ✅ Puerto no privilegiado
EXPOSE 3000
```

### Variables de entorno
```bash
# ✅ Nunca en el código, siempre en .env (no commiteado)
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore

# ✅ .env.example documentado (sin valores reales)
DATABASE_URL=postgresql://user:password@host:5432/db
JWT_SECRET=your-32-char-secret-here
STRIPE_API_KEY=sk_...
```

## Report de auditoría

Cuando hagas un audit, reporta:

```markdown
# Security Audit Report — [Proyecto] — [Fecha]

## Resumen ejecutivo
- Total issues: X (Critical: X, High: X, Medium: X, Low: X)
- Estado general: [PASS / NEEDS ATTENTION / FAIL]

## Issues críticos (requieren acción inmediata)
### CRIT-001: [Título]
- **Severidad:** Critical
- **Ubicación:** /src/api/users.js:45
- **Descripción:** SQL injection posible en endpoint de búsqueda
- **Impacto:** Acceso no autorizado a toda la base de datos
- **Remediación:** Usar query parametrizada: `db.query('SELECT * FROM users WHERE id = $1', [id])`

## Issues altos
...

## Recomendaciones generales
...
```

## Referencias
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Security Headers](https://securityheaders.com/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
