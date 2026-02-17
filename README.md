# Competitor Gen AI Analyzer

Analyze competitors' Gen AI implementations and get recommendations powered by AWS Bedrock Nova Pro.

## Features

- 🔍 Automatic competitor discovery
- 🌐 Website content extraction
- 🤖 AI-powered analysis using AWS Bedrock Nova Pro
- 🎨 Clean, responsive UI
- 📊 Structured recommendations
- 🔒 Secure AWS integration
- 📝 Comprehensive logging

## Prerequisites

- Python 3.8+
- AWS Account with Bedrock access
- AWS CLI configured with credentials

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure AWS credentials:**
```bash
aws configure
```

3. **Create environment file:**
```bash
cp .env.example .env
```

Edit `.env` and set your AWS region and profile.

4. **Enable Bedrock Nova Pro:**
   - Go to AWS Console → Bedrock → Model access
   - Request access to `amazon.nova-pro-v1:0`

## Usage

1. **Start the application:**
```bash
python app.py
```

2. **Open browser:**
```
http://localhost:5000
```

3. **Enter company URL** (e.g., samsung.com) and click Analyze

## Architecture

```
app.py                          # Flask application
├── services/
│   ├── competitor_finder.py   # Find competitors
│   ├── content_extractor.py   # Extract website content
│   └── bedrock_analyzer.py    # AWS Bedrock integration
└── templates/
    └── index.html              # UI
```

## Security Best Practices

- AWS credentials via environment variables
- No hardcoded secrets
- Input validation
- Error handling
- Request timeouts
- Content length limits

## Logging

Logs are written to console with timestamps. Adjust `LOG_LEVEL` in `.env`:
- DEBUG: Detailed information
- INFO: General information (default)
- WARNING: Warning messages
- ERROR: Error messages

## Troubleshooting

**Bedrock access denied:**
- Ensure model access is enabled in AWS Console
- Check IAM permissions for `bedrock:InvokeModel`

**Competitor not found:**
- System uses fallback competitor mapping
- Add custom mappings in `competitor_finder.py`

**Content extraction fails:**
- Some websites block scraping
- Check network connectivity
- Review logs for specific errors
