# Home Assistant Integration Guide

Home Assistant provides superior integration compared to Siri Shortcuts alone, offering advanced automation, scheduling, and voice assistant compatibility through a single platform.

## Why Home Assistant?

- **Multiple Voice Assistants**: Works with Siri, Google Assistant, Alexa
- **Advanced Automation**: Time-based, sensor-based, presence-based triggers
- **Beautiful UI**: Mobile app and web interface
- **Scheduling**: Built-in scheduler for timed lighting changes
- **Scenes**: Save and recall complex lighting configurations
- **Integration Hub**: Connect with other smart home devices

## Prerequisites

1. **Home Assistant** installed (Home Assistant OS, Core, or Supervised)
2. **Raspberry Pi** running your lights API server
3. **Network access** between Home Assistant and your lights API

## Step 1: Configure REST Commands

Add these to your Home Assistant `configuration.yaml`:

```yaml
rest_command:
  # Basic light controls
  lights_on:
    url: "http://YOUR_PI_IP:5000/api/lights/on"
    method: POST
    
  lights_off:
    url: "http://YOUR_PI_IP:5000/api/lights/off"
    method: POST
    
  # Scene modes
  lights_party_mode:
    url: "http://YOUR_PI_IP:5000/api/party-mode"
    method: POST
    
  lights_ambient_mode:
    url: "http://YOUR_PI_IP:5000/api/ambient-mode"
    method: POST
    
  lights_reading_mode:
    url: "http://YOUR_PI_IP:5000/api/reading-mode"
    method: POST
    
  lights_movie_mode:
    url: "http://YOUR_PI_IP:5000/api/movie-mode"
    method: POST
    
  lights_energize_mode:
    url: "http://YOUR_PI_IP:5000/api/energize-mode"
    method: POST
    
  lights_sleep_mode:
    url: "http://YOUR_PI_IP:5000/api/sleep-mode"
    method: POST
  
  # Pattern controls
  lights_set_pattern:
    url: "http://YOUR_PI_IP:5000/api/patterns/{{ pattern }}"
    method: POST
    
  # Brightness control
  lights_set_brightness:
    url: "http://YOUR_PI_IP:5000/api/brightness"
    method: POST
    payload: '{"brightness": {{ brightness }}}'
    headers:
      Content-Type: "application/json"
      
  # Saturation control
  lights_set_saturation:
    url: "http://YOUR_PI_IP:5000/api/saturation"
    method: POST
    payload: '{"saturation": {{ saturation }}}'
    headers:
      Content-Type: "application/json"
      
  # Speed control
  lights_set_speed:
    url: "http://YOUR_PI_IP:5000/api/speed"
    method: POST
    payload: '{"speed": {{ speed }}}'
    headers:
      Content-Type: "application/json"
      
  # Sync lights
  lights_sync:
    url: "http://YOUR_PI_IP:5000/api/sync"
    method: POST
```

## Step 2: Create Custom Light Entity

Add a custom light entity to `configuration.yaml`:

```yaml
light:
  - platform: template
    lights:
      led_strip:
        friendly_name: "LED Strip"
        turn_on:
          service: rest_command.lights_on
        turn_off:
          service: rest_command.lights_off
        set_level:
          service: rest_command.lights_set_brightness
          data:
            brightness: "{{ brightness / 255.0 }}"
```

## Step 3: Add RESTful Sensors for Status

Monitor your lights status by adding sensors:

```yaml
sensor:
  - platform: rest
    name: "LED Strip Status"
    resource: "http://YOUR_PI_IP:5000/api/status"
    method: GET
    value_template: "{{ value_json.status.pattern if value_json.success else 'offline' }}"
    json_attributes_path: "$.status"
    json_attributes:
      - brightness
      - saturation
      - speed_factor
      - tempo
      - alt_mode
      - mute
      - pattern
    scan_interval: 30
    
  - platform: rest
    name: "LED Strip Health"
    resource: "http://YOUR_PI_IP:5000/api/health"
    method: GET
    value_template: "{{ 'online' if value_json.success else 'offline' }}"
    scan_interval: 60
```

## Step 4: Create Scripts for Complex Actions

Add to `configuration.yaml`:

```yaml
script:
  # Morning routine
  lights_morning:
    alias: "Morning Lights"
    sequence:
      - service: rest_command.lights_energize_mode
      - delay: '00:00:02'
      - service: rest_command.lights_set_brightness
        data:
          brightness: 0.7
          
  # Evening routine  
  lights_evening:
    alias: "Evening Lights"
    sequence:
      - service: rest_command.lights_ambient_mode
      - delay: '00:00:02'
      - service: rest_command.lights_set_brightness
        data:
          brightness: 0.4
          
  # Bedtime routine
  lights_bedtime:
    alias: "Bedtime Lights"
    sequence:
      - service: rest_command.lights_sleep_mode
      - delay: '00:10:00'  # 10 minutes
      - service: rest_command.lights_off
      
  # Dynamic pattern cycling
  lights_cycle_patterns:
    alias: "Cycle Light Patterns"
    sequence:
      - service: rest_command.lights_set_pattern
        data:
          pattern: "pulse"
      - delay: '00:00:30'
      - service: rest_command.lights_set_pattern
        data:
          pattern: "sparks"
      - delay: '00:00:30'
      - service: rest_command.lights_set_pattern
        data:
          pattern: "orbits"
```

## Step 5: Set Up Automations

Add automated lighting behaviors:

```yaml
automation:
  # Sunrise automation
  - id: lights_sunrise
    alias: "Lights Sunrise"
    trigger:
      - platform: sun
        event: sunrise
        offset: "00:30:00"  # 30 minutes after sunrise
    action:
      - service: script.lights_morning
      
  # Sunset automation  
  - id: lights_sunset
    alias: "Lights Sunset"
    trigger:
      - platform: sun
        event: sunset
        offset: "-00:30:00"  # 30 minutes before sunset
    action:
      - service: script.lights_evening
      
  # Bedtime automation
  - id: lights_bedtime
    alias: "Lights Bedtime"
    trigger:
      - platform: time
        at: "22:30:00"  # 10:30 PM
    action:
      - service: script.lights_bedtime
      
  # Party mode on weekends
  - id: lights_weekend_party
    alias: "Weekend Party Lights"
    trigger:
      - platform: time
        at: "20:00:00"  # 8:00 PM
    condition:
      - condition: time
        weekday:
          - sat
          - sun
    action:
      - service: rest_command.lights_party_mode
      
  # Movie mode when TV turns on
  - id: lights_movie_mode
    alias: "Movie Mode When TV On"
    trigger:
      - platform: state
        entity_id: media_player.your_tv  # Replace with your TV entity
        to: "on"
    action:
      - service: rest_command.lights_movie_mode
      
  # Reading lights on voice command
  - id: lights_reading_voice
    alias: "Reading Lights Voice"
    trigger:
      - platform: conversation
        command: "reading lights"
    action:
      - service: rest_command.lights_reading_mode
```

## Step 6: Create Dashboard Cards

Add to your Lovelace dashboard:

```yaml
type: entities
entities:
  - entity_id: light.led_strip
    name: LED Strip
  - entity_id: sensor.led_strip_status  
    name: Current Pattern
  - entity_id: sensor.led_strip_health
    name: Status

---

type: horizontal-stack
cards:
  - type: button
    tap_action:
      action: call-service
      service: rest_command.lights_party_mode
    name: Party
    icon: mdi:party-popper
    
  - type: button
    tap_action:
      action: call-service
      service: rest_command.lights_ambient_mode
    name: Ambient
    icon: mdi:lightbulb-outline
    
  - type: button
    tap_action:
      action: call-service
      service: rest_command.lights_reading_mode
    name: Reading
    icon: mdi:book-open
    
  - type: button
    tap_action:
      action: call-service
      service: rest_command.lights_movie_mode
    name: Movie
    icon: mdi:movie

---

type: entities
title: Light Controls
entities:
  - entity_id: input_number.light_brightness
    name: Brightness
  - entity_id: input_select.light_pattern
    name: Pattern
  - entity_id: script.lights_morning
    name: Morning Routine
  - entity_id: script.lights_evening  
    name: Evening Routine
  - entity_id: script.lights_bedtime
    name: Bedtime Routine
```

## Step 7: Voice Assistant Integration

Once configured in Home Assistant, you can use:

### With Siri (via HomeKit integration)
- "Hey Siri, turn on the LED strip"
- "Hey Siri, set LED strip to 50%"
- "Hey Siri, activate party mode" (via scenes)

### With Google Assistant  
- "Hey Google, turn on LED strip"
- "Hey Google, run morning lights"
- "Hey Google, set LED strip brightness to 75%"

### With Alexa
- "Alexa, turn on LED strip"
- "Alexa, run bedtime routine"
- "Alexa, activate reading lights"

## Step 8: Advanced Features

### Music Sync Integration
```yaml
automation:
  - id: lights_music_sync
    alias: "Sync Lights to Music"
    trigger:
      - platform: state
        entity_id: media_player.spotify
        to: "playing"
    action:
      - service: rest_command.lights_party_mode
      - service: rest_command.lights_set_speed
        data:
          speed: 1.5
```

### Presence-Based Lighting
```yaml
automation:
  - id: lights_presence
    alias: "Lights When Home"
    trigger:
      - platform: state
        entity_id: person.your_name
        to: "home"
    condition:
      - condition: sun
        after: sunset
    action:
      - service: script.lights_evening
```

### Weather-Responsive Lighting
```yaml
automation:
  - id: lights_weather_storm
    alias: "Storm Lighting"
    trigger:
      - platform: state
        entity_id: weather.home
        attribute: condition
        to: "lightning-rainy"
    action:
      - service: rest_command.lights_set_pattern
        data:
          pattern: "sparks"
      - service: rest_command.lights_set_speed
        data:
          speed: 3.0
```

## Benefits Over Siri Shortcuts

1. **Unified Control**: All voice assistants work through one system
2. **Complex Automations**: Time, weather, presence, and device state triggers  
3. **Visual Interface**: Beautiful mobile app and web dashboard
4. **Scheduling**: Built-in cron-like scheduling
5. **Scenes**: Save complex multi-device configurations
6. **Integration**: Works with hundreds of other smart home devices
7. **Offline Operation**: Many automations work without internet
8. **Logging**: Track usage patterns and troubleshoot issues

## Troubleshooting

### REST Commands Not Working
- Check the IP address and port in URLs
- Verify Home Assistant can reach your Raspberry Pi
- Test endpoints manually with curl
- Check Home Assistant logs for error messages

### Sensors Showing Unavailable
- Verify the API endpoints return valid JSON
- Check the `value_template` syntax
- Ensure scan_interval isn't too aggressive
- Monitor network connectivity between devices

### Voice Commands Not Working  
- Ensure entities are exposed to your voice assistant
- Check entity naming for clarity
- Verify voice assistant integration is configured
- Test commands through Home Assistant first

Home Assistant transforms your LED lights into a full smart home lighting system with professional-grade automation capabilities!