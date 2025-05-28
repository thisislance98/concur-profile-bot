# 🤖 Concur Profile Bot - Gradio Web Interface

A user-friendly web interface for the Concur Profile Bot, powered by Gradio and Claude AI.

## 🌟 Features

- **Chat Interface**: Natural language conversation with the bot
- **Real-time Status**: Live connection status for Concur SDK and Claude API
- **Quick Actions**: One-click buttons for common tasks
- **Conversation History**: Persistent chat history during your session
- **Modern UI**: Clean, responsive design with helpful examples
- **Tool Integration**: Seamless integration with Concur Profile SDK

## 🚀 Quick Start

### Prerequisites

1. **Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Environment Variables**: Ensure your `.env_tools` file contains:
   ```
   ANTHROPIC_API_KEY=your_claude_api_key
   CONCUR_CLIENT_ID=your_concur_client_id
   CONCUR_CLIENT_SECRET=your_concur_client_secret
   CONCUR_USERNAME=your_concur_username
   CONCUR_PASSWORD=your_concur_password
   CONCUR_BASE_URL=https://us2.api.concursolutions.com
   ```

### Installation & Launch

**Option 1: Using the Launcher (Recommended)**
```bash
python launch_gradio_bot.py
```

**Option 2: Manual Setup**
```bash
# Install dependencies
pip install -r requirements_gradio.txt

# Launch the interface
python gradio_bot_interface.py
```

The web interface will open automatically in your browser at `http://localhost:7860`

## 🎯 How to Use

### Chat Interface

Simply type natural language requests in the chat box:

- **"Show me my profile"** - View your current profile information
- **"Update my job title to Senior Engineer"** - Update basic profile details
- **"Set my airline seat preference to window"** - Update travel preferences
- **"I prefer king size beds in hotels"** - Update hotel preferences
- **"Show profiles updated in the last week"** - List recent profile changes

### Quick Actions

Use the quick action buttons for common tasks:
- 📋 **Get Profile** - Instantly view your profile
- ✈️ **Travel Preferences** - Check your travel settings
- ✏️ **Update Job Title** - Quick job title update
- 🗑️ **Clear Chat** - Start a fresh conversation

### Status Panel

Monitor system health in real-time:
- ✅ **Concur SDK**: Connection status and authenticated user
- ✅ **Claude API**: API connection status
- 🕒 **Last Updated**: Timestamp of last status check

## 🛠️ What the Bot Can Do

### Profile Management
- View complete profile information
- Update basic details (name, job title, company, etc.)
- Manage employee information

### Travel Preferences
- **Air Travel**: Seat preferences, meal types, airline preferences
- **Hotels**: Room types, smoking preferences, amenities
- **Car Rentals**: Vehicle types, transmission preferences
- **Rail Travel**: Seat preferences and accommodations

### Contact Information
- Manage addresses (home, work)
- Update phone numbers (work, cell, home)
- Handle email addresses (business, personal)

### Advanced Features
- List and search profiles
- Filter by modification dates
- Bulk operations support
- Error handling and validation

## 🔧 Technical Details

### Architecture
- **Frontend**: Gradio web interface
- **Backend**: Anthropic Claude with tool calling
- **Integration**: Concur Profile SDK
- **Authentication**: OAuth 2.0 with Concur API

### Files Structure
```
├── gradio_bot_interface.py    # Main Gradio interface
├── launch_gradio_bot.py       # Simple launcher script
├── requirements_gradio.txt    # Gradio-specific dependencies
├── concur_profile_bot_fixed.py # Original CLI bot
├── concur_profile_sdk_improved.py # Concur SDK
└── .env_tools                 # Environment variables
```

### Dependencies
- `gradio>=4.0.0` - Web interface framework
- `anthropic>=0.7.0` - Claude AI API client
- `python-dotenv>=1.0.0` - Environment variable management
- `requests>=2.31.0` - HTTP client for API calls

## 🎨 Interface Features

### Modern Design
- Clean, professional appearance
- Responsive layout for different screen sizes
- Intuitive navigation and controls
- Real-time status indicators

### User Experience
- Auto-complete and suggestions
- Error handling with helpful messages
- Progress indicators for long operations
- Conversation persistence during session

### Accessibility
- Keyboard navigation support
- Screen reader friendly
- High contrast mode compatible
- Mobile device responsive

## 🔍 Example Conversations

### Getting Profile Information
```
User: Show me my current profile
Bot: I'll retrieve your profile information for you.
🔧 Using tools: get_profile
Here's your current profile:
- Name: John Doe
- Job Title: Software Engineer
- Company: Acme Corp
- Login ID: john.doe@acme.com
...
```

### Updating Travel Preferences
```
User: I prefer window seats and vegetarian meals on flights
Bot: I'll update your air travel preferences.
🔧 Using tools: update_travel_preferences
✅ Successfully updated your preferences:
- Seat preference: Window
- Meal preference: Vegetarian
```

### Complex Multi-step Operations
```
User: Update my job title to Senior Engineer and set my hotel preference to king beds
Bot: I'll help you update both your job title and hotel preferences.
🔧 Using tools: update_profile, update_travel_preferences
✅ Updates completed:
1. Job title changed to "Senior Engineer"
2. Hotel room preference set to "King"
```

## 🚨 Troubleshooting

### Common Issues

**"Bot not initialized" Error**
- Check the Status Panel for connection issues
- Verify your `.env_tools` file has all required credentials
- Click "Refresh Status" to retry connections

**Gradio Not Found**
- Run: `pip install -r requirements_gradio.txt`
- Ensure you're in the correct virtual environment

**API Connection Errors**
- Verify your Anthropic API key is valid
- Check Concur credentials and permissions
- Ensure network connectivity

### Getting Help

1. Check the Status Panel for specific error messages
2. Review the console output for detailed error logs
3. Verify all environment variables are correctly set
4. Test the original CLI bot to isolate issues

## 🔒 Security Notes

- API keys are loaded from environment variables only
- No credentials are stored in the interface
- All communications use HTTPS
- Session data is not persisted between restarts

## 📝 Development

### Extending the Interface

The Gradio interface is modular and can be extended:

1. **Add New Tools**: Update the `tools` list and `tool_handler` function
2. **Custom UI Components**: Modify the `create_interface()` function
3. **Additional Quick Actions**: Add new buttons and handlers
4. **Enhanced Status**: Extend the `get_status()` function

### Contributing

1. Follow the existing code style
2. Test all changes thoroughly
3. Update documentation as needed
4. Ensure compatibility with the existing SDK

---

**Happy Profiling! 🎉**

For more information about the underlying bot capabilities, see the main project documentation. 