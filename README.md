---
title: Concur Profile Bot
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.1
app_file: gradio_bot_interface.py
pinned: false
license: mit
---

# 🤖 Concur Profile Bot

An intelligent AI assistant for managing Concur travel profiles using natural language commands.

## Features

- **Profile Management**: View and update basic profile information
- **Travel Preferences**: Manage airline, hotel, and car rental preferences  
- **Contact Information**: Update addresses, phone numbers, and emails
- **Loyalty Programs**: Manage frequent traveler programs
- **Natural Language Interface**: Chat with the bot using plain English

## Usage

Simply type your requests in natural language:
- "Show me my profile"
- "Update my job title to Senior Engineer"
- "Set my airline seat preference to window"
- "Add my home address"

## Environment Variables

To run this app, you'll need to set the following environment variables:

- `CONCUR_CLIENT_ID`: Your Concur API client ID
- `CONCUR_CLIENT_SECRET`: Your Concur API client secret  
- `CONCUR_USERNAME`: Your Concur username
- `CONCUR_PASSWORD`: Your Concur password
- `CONCUR_BASE_URL`: Concur API base URL (default: https://us2.api.concursolutions.com)
- `ANTHROPIC_API_KEY`: Your Claude API key

## Deployment

### Hugging Face Spaces (Recommended)
```bash
gradio deploy
```

### Local Development
```bash
python gradio_bot_interface.py
```

## Security Note

This app handles sensitive travel and personal information. Ensure all API keys are properly secured and never commit them to version control. 