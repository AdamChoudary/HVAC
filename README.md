# Scott Valley HVAC Voice Agent System

✅ **PRODUCTION READY** - AI-powered voice automation system for HVAC business operations using Vapi.ai, GoHighLevel, and Twilio.

## 🎯 Current Status

- ✅ **GHL Integration**: Complete and working
- ✅ **Vapi.ai Integration**: Complete (assistants created)
- ✅ **Server Deployment**: Live on Fly.io
- ✅ **All Function Endpoints**: Working
- ⚠️ **Twilio**: Optional (for warm transfer only)

**Server URL**: https://scott-valley-hvac-api.fly.dev

## Quick Start

### 1. Install Dependencies

```bash
uv sync
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `VAPI_API_KEY` - Your Vapi.ai API key
- `GHL_API` or `GHL_API_KEY` - GoHighLevel API key (use GHL_API)
- `GHL_LOCATION_ID` - GHL location ID
- `TWILIO_ACCOUNT_SID` - Twilio account SID
- `TWILIO_AUTH_TOKEN` - Twilio auth token
- `TWILIO_PHONE_NUMBER` - Your Twilio phone number
- `WEBHOOK_BASE_URL` - Your public server URL (for webhooks)

### 3. Run Server

```bash
uv run python main.py
```

Or with uvicorn directly:

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Set Up GoHighLevel CRM

Configure GHL automatically using API:

```bash
uv run python scripts/ghl_setup_complete.py
```

This creates:
- Service & Sales pipelines with stages
- Service & Sales calendars
- All required custom fields
- Webhook configuration

Verify setup:
```bash
uv run python scripts/verify_ghl_setup.py
```

### 5. Set Up Vapi Assistants

After deploying your server (with public URL), run:

```bash
uv run python scripts/setup_vapi.py
```

This creates the inbound and outbound assistants in Vapi.

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
HVAC/
├── src/
│   ├── config/          # Configuration and settings
│   ├── integrations/    # GHL, Twilio, Vapi clients
│   ├── functions/       # 7 Vapi function handlers
│   ├── models/          # Pydantic models
│   ├── webhooks/        # Webhook handlers
│   ├── utils/           # Utilities (logging, errors, validation)
│   └── main.py          # FastAPI application
├── scripts/             # Setup and utility scripts
├── tests/               # Test files
└── logs/                # Application logs
```

## Features

- ✅ 7 Vapi function endpoints
- ✅ GHL integration (contacts, calendars, appointments)
- ✅ Twilio integration (SMS, warm transfers)
- ✅ Webhook handlers for GHL events
- ✅ Comprehensive error handling
- ✅ Logging system
- ✅ Input validation

## Testing

```bash
uv run pytest
```

## Deployment

1. Set `ENVIRONMENT=production` in `.env`
2. Set `WEBHOOK_BASE_URL` to your public server URL
3. Deploy to your hosting platform (Railway, Render, AWS, etc.)
4. Run `setup_vapi.py` to create assistants
5. Configure phone number in Vapi dashboard
6. Set up GHL webhooks pointing to your server

## Support

Check logs in `logs/` directory for debugging.

