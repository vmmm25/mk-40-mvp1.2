---
name: security-monitor
version: 1.0.0
description: Monitorización continua de seguridad en tiempo real para aplicaciones y sistemas. Usa cuando necesites detectar anomalías, configurar alertas de seguridad, o implementar observabilidad de seguridad.
tags: [security, monitoring, siem, alerts, anomaly-detection, logging, observability]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Security Monitor Skill

## Cuándo usar esta skill
- Configurar alertas de seguridad para una aplicación
- Detectar comportamiento anómalo en tiempo real
- Configurar un sistema básico de SIEM
- Revisar logs de seguridad y detectar patrones sospechosos
- Preparar incident response

## Métricas de seguridad a monitorizar

### Autenticación
```
🔴 CRÍTICO:
- Múltiples intentos de login fallidos desde la misma IP (>10 en 5 min)
- Login exitoso desde país/IP nunca visto para ese usuario
- Múltiples cuentas comprometidas desde la misma IP
- Intentos de login admin fuera de horario normal

🟠 ALTO:
- Cambios de contraseña masivos en poco tiempo
- Nuevos tokens API creados fuera de horario
- Múltiples password resets en corto tiempo
```

### Acceso a datos
```
🔴 CRÍTICO:
- Acceso masivo a datos (descargas > umbral normal)
- Acceso a datos de usuarios no propios (insecure direct object reference)
- Consultas SQL lentas o con patrones de injection
- Acceso a endpoints de admin sin autorización apropiada

🟠 ALTO:
- Picos de tráfico anómalos en APIs internas  
- Acceso a rutas/archivos que no deberían existir (404 masivos)
- Cambios en configuración del sistema
```

### Infraestructura
```
🔴 CRÍTICO:
- Nuevos procesos con privilegios elevados
- Conexiones salientes a IPs en listas negras
- Cambios en archivos de sistema críticos
- Nuevas reglas de firewall añadidas

🟠 ALTO:
- Uso de CPU/memoria anómalo (posible crypto mining)
- Nuevos puertos en escucha no esperados
- Cambios en cron jobs o servicios systemd
```

## Implementación básica con Python

### Monitor de logs en tiempo real
```python
import re
import time
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityMonitor:
    def __init__(self):
        self.failed_logins: dict[str, list] = defaultdict(list)
        self.alerts_sent: set = set()
        
    def check_brute_force(self, ip: str, window_minutes: int = 5, threshold: int = 10) -> bool:
        """Detectar brute force por IP"""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        # Limpiar intentos fuera de la ventana
        self.failed_logins[ip] = [
            t for t in self.failed_logins[ip] 
            if t > window_start
        ]
        
        self.failed_logins[ip].append(now)
        
        count = len(self.failed_logins[ip])
        
        if count >= threshold:
            alert_key = f"brute_force_{ip}_{now.strftime('%Y%m%d%H')}"
            if alert_key not in self.alerts_sent:
                self.alerts_sent.add(alert_key)
                return True  # Trigger alert
        
        return False
    
    def parse_nginx_log(self, log_line: str) -> dict | None:
        """Parsear línea de log de Nginx"""
        pattern = r'(?P<ip>\S+) - \S+ \[(?P<time>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d+) (?P<bytes>\d+)'
        
        match = re.match(pattern, log_line)
        if match:
            return match.groupdict()
        return None
    
    def tail_log_file(self, log_path: str, callback):
        """Leer log en tiempo real (tail -f)"""
        with open(log_path, 'r') as f:
            f.seek(0, 2)  # Ir al final del archivo
            
            while True:
                line = f.readline()
                if line:
                    callback(line.strip())
                else:
                    time.sleep(0.1)
    
    def check_line(self, line: str):
        """Procesar una línea de log"""
        entry = self.parse_nginx_log(line)
        if not entry:
            return
        
        ip = entry['ip']
        status = int(entry['status'])
        path = entry['path']
        
        # Detectar intentos de acceso no autorizado
        if status == 401 or status == 403:
            if self.check_brute_force(ip):
                self.trigger_alert(
                    level="CRÍTICO",
                    message=f"Posible brute force desde {ip}: {len(self.failed_logins[ip])} intentos en 5 min",
                    data={"ip": ip, "attempts": len(self.failed_logins[ip]), "path": path}
                )
        
        # Detectar escaneos de rutas
        if status == 404 and any(p in path for p in ['/admin', '/.env', '/wp-admin', '/phpMyAdmin']):
            logger.warning(f"Sospechoso: {ip} intentando acceder a {path}")
    
    def trigger_alert(self, level: str, message: str, data: dict):
        """Disparar alerta"""
        logger.critical(f"[{level}] {message} | Data: {data}")
        
        # Aquí puedes integrar:
        # - Envío de email
        # - Mensaje de Slack/Teams
        # - WhatsApp (ver skill whatsapp-messaging)
        # - PagerDuty
        # - Webhook


monitor = SecurityMonitor()

# Uso en tiempo real
# monitor.tail_log_file('/var/log/nginx/access.log', monitor.check_line)
```

### Detección de anomalías en APIs
```python
import statistics
from typing import Optional

class APIAnomalyDetector:
    def __init__(self, window_size: int = 60):
        self.request_counts: list[int] = []
        self.window_size = window_size
        self.baseline_mean: Optional[float] = None
        self.baseline_std: Optional[float] = None
    
    def update_baseline(self, counts: list[int]):
        """Establecer baseline normal de tráfico"""
        self.baseline_mean = statistics.mean(counts)
        self.baseline_std = statistics.stdev(counts) if len(counts) > 1 else 0
    
    def is_anomalous(self, current_count: int, threshold_sigma: float = 3.0) -> bool:
        """
        Detectar si el tráfico actual es anómalos
        Usa Z-score: anomalía si está a más de N desviaciones estándar de la media
        """
        if self.baseline_mean is None or self.baseline_std is None:
            return False
        
        if self.baseline_std == 0:
            return current_count > self.baseline_mean * 2
        
        z_score = (current_count - self.baseline_mean) / self.baseline_std
        
        return abs(z_score) > threshold_sigma
```

## Configuración con herramientas existentes

### Fail2ban (Linux)
```bash
# Instalar
sudo apt install fail2ban

# Configurar /etc/fail2ban/jail.local
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime  = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port = ssh
maxretry = 3

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-login]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 10
findtime = 5m
EOF

# Reiniciar
sudo systemctl restart fail2ban

# Ver IPs baneadas
sudo fail2ban-client status nginx-login
```

### Alertas con Grafana + Prometheus
```yaml
# alert_rules.yml para Prometheus
groups:
  - name: security
    rules:
      - alert: HighFailedLoginRate
        expr: rate(auth_login_failures_total[5m]) > 0.5
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Alta tasa de logins fallidos"
          description: "{{ $value }} fallos/s en los últimos 5 min desde {{ $labels.instance }}"
      
      - alert: UnusualTrafficSpike
        expr: rate(http_requests_total[1m]) > 1000
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Pico de tráfico inusual"
```

## Checklist de incident response

Cuando se detecta un incidente de seguridad:

```
FASE 1 — IDENTIFICACIÓN (primeros 15 min)
□ ¿Cuál es el alcance? (un sistema, varios, toda la red)
□ ¿Qué datos están potencialmente comprometidos?
□ ¿Sigue activo el ataque o ya paró?
□ ¿Cuándo empezó? (revisar logs)

FASE 2 — CONTENCIÓN (primera hora)
□ Aislar sistemas afectados si es necesario (sin apagarlos aún — se pierden evidencias)
□ Bloquear IPs atacantes en firewall
□ Revocar credenciales comprometidas
□ Activar monitoring extra en sistemas relacionados

FASE 3 — ERRADICACIÓN
□ Identificar el vector de entrada
□ Aplicar parches o fixes necesarios
□ Limpiar archivos maliciosos si los hay
□ Restablecer credenciales de forma segura

FASE 4 — RECUPERACIÓN
□ Restaurar desde backup limpio si es necesario
□ Verificar integridad de los sistemas
□ Monitorizar de forma intensiva durante 72h
□ Confirmar que el vector está cerrado

FASE 5 — LECCIONES APRENDIDAS
□ Escribir post-mortem (qué pasó, cómo se detectó, cómo se resolvió)
□ Actualizar playbooks de respuesta
□ Implementar mejoras preventivas
□ Compartir lecciones con el equipo
```

## Referencias
- [OWASP Security Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [Fail2ban documentation](https://www.fail2ban.org/wiki/index.php/MANUAL_0_8)
- [Awesome SIEM](https://github.com/fabacab/awesome-cybersecurity-blueteam)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
