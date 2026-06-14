---
name: caldav-calendar
version: 1.0.0
description: Read and write calendar events via CalDAV. Works with Google Calendar, Apple Calendar (iCloud), Fastmail, Nextcloud, and any CalDAV server. Create, update, delete events and manage availability.
tags: [calendar, caldav, ical, google-calendar, apple-calendar, scheduling, automation]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# CalDAV Calendar Skill

## Setup

```bash
pip install caldav icalendar python-dateutil pytz python-dotenv
```

### Server URLs

| Provider        | CalDAV URL pattern |
|-----------------|---------------------|
| Google Calendar | `https://www.google.com/calendar/dav/{email}/events/` |
| iCloud          | `https://caldav.icloud.com/` |
| Fastmail        | `https://caldav.fastmail.com/dav/` |
| Nextcloud       | `https://your-server/remote.php/dav/` |

`.env`:
```
CALDAV_URL=https://caldav.icloud.com/
CALDAV_USER=your@email.com
CALDAV_PASSWORD=app-specific-password
```

## Connect to CalDAV

```python
import caldav
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import pytz

load_dotenv()

def get_client():
    return caldav.DAVClient(
        url=os.getenv("CALDAV_URL"),
        username=os.getenv("CALDAV_USER"),
        password=os.getenv("CALDAV_PASSWORD")
    )

def get_calendars():
    """List all calendars available."""
    with get_client() as client:
        principal = client.principal()
        calendars = principal.calendars()
        return [{"name": cal.name, "url": str(cal.url)} for cal in calendars]

def get_calendar(name: str = None):
    """Get a specific calendar by name, or the first one."""
    with get_client() as client:
        principal = client.principal()
        calendars = principal.calendars()
        if name:
            return next((cal for cal in calendars if cal.name == name), None)
        return calendars[0] if calendars else None
```

## List Events

```python
def get_events(
    calendar_name: str = None,
    start: datetime = None,
    end: datetime = None,
    days_ahead: int = 7
):
    """Fetch calendar events in a date range."""
    start = start or datetime.now(pytz.UTC)
    end = end or (start + timedelta(days=days_ahead))

    with get_client() as client:
        principal = client.principal()
        calendars = principal.calendars()
        cal = next((c for c in calendars if c.name == calendar_name), calendars[0]) if calendar_name else calendars[0]

        events = cal.date_search(start=start, end=end, expand=True)
        results = []
        for event in events:
            ical = Calendar.from_ical(event.data)
            for component in ical.walk():
                if component.name == "VEVENT":
                    results.append({
                        "summary": str(component.get("SUMMARY", "No title")),
                        "start": component.get("DTSTART").dt,
                        "end": component.get("DTEND").dt,
                        "location": str(component.get("LOCATION", "")),
                        "description": str(component.get("DESCRIPTION", "")),
                        "uid": str(component.get("UID", "")),
                    })

        return sorted(results, key=lambda e: e["start"])

def get_today_events(calendar_name: str = None):
    """Get all events for today."""
    today = datetime.now(pytz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    return get_events(calendar_name=calendar_name, start=today, end=tomorrow)

def get_week_events(calendar_name: str = None):
    """Get all events for the next 7 days."""
    return get_events(calendar_name=calendar_name, days_ahead=7)
```

## Create Events

```python
import uuid

def create_event(
    summary: str,
    start: datetime,
    end: datetime,
    description: str = "",
    location: str = "",
    calendar_name: str = None,
    timezone: str = "Europe/Madrid"
):
    """Create a new calendar event."""
    tz = pytz.timezone(timezone)
    if start.tzinfo is None:
        start = tz.localize(start)
    if end.tzinfo is None:
        end = tz.localize(end)

    cal = Calendar()
    cal.add("prodid", "-//CalDAV Skill//EN")
    cal.add("version", "2.0")

    event = Event()
    event.add("summary", summary)
    event.add("dtstart", start)
    event.add("dtend", end)
    event.add("description", description)
    event.add("location", location)
    event.add("uid", str(uuid.uuid4()))
    event.add("dtstamp", datetime.now(pytz.UTC))

    cal.add_component(event)

    with get_client() as client:
        principal = client.principal()
        calendars = principal.calendars()
        target = next((c for c in calendars if c.name == calendar_name), calendars[0]) if calendar_name else calendars[0]
        target.save_event(cal.to_ical())

    return {"status": "created", "summary": summary, "start": str(start), "end": str(end)}

def create_all_day_event(summary: str, date: datetime, calendar_name: str = None):
    """Create an all-day event."""
    from datetime import date as date_type
    start = date.date() if isinstance(date, datetime) else date
    end = start + timedelta(days=1)

    cal = Calendar()
    cal.add("prodid", "-//CalDAV Skill//EN")
    cal.add("version", "2.0")

    event = Event()
    event.add("summary", summary)
    event.add("dtstart", start)
    event.add("dtend", end)
    event.add("uid", str(uuid.uuid4()))
    event.add("dtstamp", datetime.now(pytz.UTC))

    cal.add_component(event)

    with get_client() as client:
        principal = client.principal()
        calendars = principal.calendars()
        target = next((c for c in calendars if c.name == calendar_name), calendars[0]) if calendar_name else calendars[0]
        target.save_event(cal.to_ical())

    return {"status": "created", "summary": summary, "date": str(start)}
```

## Delete Events

```python
def delete_event_by_uid(uid: str, calendar_name: str = None):
    """Delete an event by its UID."""
    with get_client() as client:
        principal = client.principal()
        calendars = principal.calendars()
        cal = next((c for c in calendars if c.name == calendar_name), calendars[0]) if calendar_name else calendars[0]

        for event in cal.events():
            ical = Calendar.from_ical(event.data)
            for component in ical.walk():
                if component.name == "VEVENT" and str(component.get("UID")) == uid:
                    event.delete()
                    return {"status": "deleted", "uid": uid}

    return {"status": "not_found", "uid": uid}
```

## Availability Check

```python
def get_free_slots(
    date: datetime = None,
    slot_duration_minutes: int = 60,
    start_hour: int = 9,
    end_hour: int = 18,
    calendar_name: str = None
):
    """Find free time slots on a given day."""
    date = date or datetime.now()
    tz = pytz.timezone("Europe/Madrid")

    day_start = tz.localize(datetime(date.year, date.month, date.day, start_hour, 0))
    day_end = tz.localize(datetime(date.year, date.month, date.day, end_hour, 0))

    events = get_events(calendar_name=calendar_name, start=day_start, end=day_end)

    # Generate all possible slots
    slots = []
    current = day_start
    while current + timedelta(minutes=slot_duration_minutes) <= day_end:
        slot_end = current + timedelta(minutes=slot_duration_minutes)

        # Check if slot overlaps with any event
        is_free = True
        for event in events:
            ev_start = event["start"] if event["start"].tzinfo else tz.localize(event["start"])
            ev_end = event["end"] if event["end"].tzinfo else tz.localize(event["end"])
            if not (slot_end <= ev_start or current >= ev_end):
                is_free = False
                break

        if is_free:
            slots.append({"start": current.strftime("%H:%M"), "end": slot_end.strftime("%H:%M")})

        current += timedelta(minutes=30)  # 30-min resolution

    return slots
```

## Google Calendar via OAuth2

```python
# For Google Calendar with service account or OAuth2:
# pip install google-api-python-client google-auth

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

def get_google_calendar_service(service_account_file: str):
    creds = Credentials.from_service_account_file(
        service_account_file,
        scopes=["https://www.googleapis.com/auth/calendar"]
    )
    return build("calendar", "v3", credentials=creds)

def google_create_event(service, calendar_id: str, summary: str, start: str, end: str, timezone: str = "Europe/Madrid"):
    """Create event using Google Calendar API directly."""
    event = {
        "summary": summary,
        "start": {"dateTime": start, "timeZone": timezone},
        "end": {"dateTime": end, "timeZone": timezone},
    }
    return service.events().insert(calendarId=calendar_id, body=event).execute()
```

## Quick Usage Examples

```python
# List today's events
events = get_today_events()
for e in events:
    print(f"{e['start'].strftime('%H:%M')} — {e['summary']} @ {e['location']}")

# Create a meeting
create_event(
    summary="Team Sync",
    start=datetime(2025, 1, 20, 10, 0),
    end=datetime(2025, 1, 20, 11, 0),
    description="Weekly team sync meeting",
    location="Google Meet"
)

# Find free 1-hour slots tomorrow
from datetime import date, timedelta
tomorrow = datetime.now() + timedelta(days=1)
free = get_free_slots(date=tomorrow, slot_duration_minutes=60)
print("Free slots:", free)
```

## References
- [caldav Python library](https://caldav.readthedocs.io/) — Main library docs
- [CalDAV RFC 4791](https://datatracker.ietf.org/doc/html/rfc4791) — Protocol spec
- [iCloud CalDAV](https://support.apple.com/en-us/102637) — iCloud setup
- [Google Calendar API](https://developers.google.com/calendar/api) — Alternative to CalDAV
