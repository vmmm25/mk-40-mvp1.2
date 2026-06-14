---
name: linkedin-cli
version: 1.0.0
description: CLI para LinkedIn — buscar perfiles, ver mensajes y explorar el feed usando cookies de sesión. Usa cuando necesites automatizar acciones básicas en LinkedIn o extraer datos de perfiles.
tags: [linkedin, social-media, cli, automation, networking, recruiting, profiles]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# LinkedIn CLI Skill

## Instalación y autenticación

```bash
# Instalar bird-like LinkedIn CLI
npm install -g linkedin-bird
# O vía pip
pip install li-scrapi

# Autenticación con cookies (más estable que API)
# 1. Abrir DevTools en LinkedIn (F12)
# 2. Application → Cookies → linkedin.com
# 3. Copiar: li_at, JSESSIONID, liap
linkedin-bird auth --li-at "YOUR_COOKIE" --jsessionid "YOUR_JSESSIONID"
```

## Búsqueda de perfiles

```python
# pip install li-scrapi
from linkedin_api import Linkedin
import os

# Autenticar con email/password o cookies
api = Linkedin(
    username=os.getenv("LINKEDIN_EMAIL"),
    password=os.getenv("LINKEDIN_PASSWORD")
)


def search_profiles(keywords: str, limit: int = 10) -> list:
    """Buscar perfiles de LinkedIn"""
    results = api.search_people(
        keywords=keywords,
        limit=limit
    )
    
    profiles = []
    for r in results:
        profiles.append({
            "name": f"{r.get('firstName', '')} {r.get('lastName', '')}".strip(),
            "headline": r.get("headline", ""),
            "location": r.get("location", {}).get("name", ""),
            "public_id": r.get("publicIdentifier", ""),
            "url": f"https://linkedin.com/in/{r.get('publicIdentifier', '')}",
        })
    
    return profiles


def get_profile(public_id: str) -> dict:
    """Obtener datos completos de un perfil"""
    profile = api.get_profile(public_id)
    
    return {
        "name": f"{profile.get('firstName', '')} {profile.get('lastName', '')}",
        "headline": profile.get("headline", ""),
        "summary": profile.get("summary", ""),
        "location": profile.get("address", {}).get("geoLocationName", ""),
        "connections": profile.get("connectionsCount", 0),
        "experience": [
            {
                "title": exp.get("title", ""),
                "company": exp.get("companyName", ""),
                "duration": exp.get("timePeriod", {}),
            }
            for exp in profile.get("experience", [])
        ],
        "education": [
            {
                "school": edu.get("schoolName", ""),
                "degree": edu.get("degreeName", ""),
                "field": edu.get("fieldOfStudy", ""),
            }
            for edu in profile.get("education", [])
        ],
        "skills": [s.get("name", "") for s in profile.get("skills", [])],
    }
```

## Feed y mensajes

```python
def get_feed(limit: int = 20) -> list:
    """Obtener posts del feed personal"""
    feed = api.get_feed_posts(limit=limit)
    posts = []
    for post in feed:
        posts.append({
            "author": post.get("author", {}).get("name", ""),
            "text": post.get("commentary", {}).get("text", ""),
            "likes": post.get("socialDetail", {}).get("totalSocialActivityCounts", {}).get("numLikes", 0),
            "comments": post.get("socialDetail", {}).get("totalSocialActivityCounts", {}).get("numComments", 0),
        })
    return posts


def get_messages(limit: int = 20) -> list:
    """Leer conversaciones de mensajes"""
    conversations = api.get_conversations()
    messages = []
    for conv in conversations[:limit]:
        last_msg = conv.get("lastActivityAt", "")
        participants = [
            f"{p.get('firstName', '')} {p.get('lastName', '')}"
            for p in conv.get("participants", [])
        ]
        messages.append({
            "with": participants,
            "last_message": conv.get("lastMessage", {}).get("body", ""),
            "timestamp": last_msg,
        })
    return messages


def send_message(recipient_id: str, message: str) -> bool:
    """Enviar mensaje directo"""
    try:
        api.send_message(recipient_ids=[recipient_id], message_body=message)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
```

## Casos de uso de recruiting / outreach

```python
def find_ciso_barcelona() -> list:
    """Ejemplo: buscar CISOs en Barcelona para outreach"""
    results = search_profiles(
        keywords="CISO cybersecurity Barcelona",
        limit=20
    )
    
    # Filtrar por headline relevante
    cisos = [
        r for r in results
        if any(term in r["headline"].lower()
               for term in ["ciso", "chief information security", "cybersecurity"])
    ]
    
    return cisos


def profile_summary_for_outreach(public_id: str) -> str:
    """Generar resumen de perfil para personalizar mensaje"""
    profile = get_profile(public_id)
    
    current_role = profile["experience"][0] if profile["experience"] else {}
    
    return f"""
Nombre: {profile['name']}
Cargo actual: {current_role.get('title', '')} en {current_role.get('company', '')}
Sector: {profile['headline']}
Ubicación: {profile['location']}
Skills principales: {', '.join(profile['skills'][:5])}
"""
```

## Búsqueda con la API oficial (LinkedIn Marketing API)

```python
# Para uso oficial con API key (requiere app aprobada)
import requests

def search_company(company_name: str, access_token: str) -> dict:
    """Buscar empresa con API oficial"""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        "https://api.linkedin.com/v2/organizations",
        params={"q": "vanityName", "vanityName": company_name},
        headers=headers
    )
    return response.json()
```

## Notas importantes

```
⚠️ Web scraping de LinkedIn va contra sus ToS.
- Usar para investigación limitada y personal.
- Para uso comercial o recruiting masivo: usar LinkedIn Recruiter API oficial.
- Rate limits: no más de 100-200 requests/día para evitar bloqueos.
- Usar proxies rotativos si se hace uso intensivo.

✅ Alternativas legales:
- LinkedIn Sales Navigator API (corporativo)
- LinkedIn Partner Program (para herramientas de HR)
- Hunter.io, Clearbit para datos de empresa (sin scraping directo)
```

## Referencias
- [li-scrapi](https://github.com/tomquirk/linkedin-api) — API no oficial vía cookies
- [LinkedIn Official API](https://developer.linkedin.com/) — Para uso corporativo
- [Hunter.io](https://hunter.io/) — Alternativa legal para encontrar emails
