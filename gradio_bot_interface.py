#!/usr/bin/env python3
"""
Gradio Web Interface for Concur Profile Bot

This creates a user-friendly web interface for the Concur Profile Bot
using Gradio, allowing users to interact with the bot through a chat interface.
"""

import os
import sys
import json
import gradio as gr
import anthropic
from datetime import datetime
from dotenv import load_dotenv
import threading
import time

# Add the current directory to path to import the bot modules
sys.path.insert(0, os.path.dirname(__file__))

# Import the Concur Profile SDK
from concur_profile_sdk_improved import (
    ConcurProfileSDK, UserProfile, Address, Phone, Email, EmergencyContact,
    AirPreferences, HotelPreferences, CarPreferences, RailPreferences,
    LoyaltyProgram, RatePreference, DiscountCode,
    AddressType, PhoneType, EmailType, LoyaltyProgramType,
    SeatPreference, SeatSection, MealType, HotelRoomType, SmokingPreference,
    CarType, TransmissionType,
    ConcurProfileError, AuthenticationError, ProfileNotFoundError, ValidationError
)

# Load credentials from .env file
load_dotenv(".env_tools")

# Concur API Credentials
CONCUR_CLIENT_ID = os.getenv("CONCUR_CLIENT_ID")
CONCUR_CLIENT_SECRET = os.getenv("CONCUR_CLIENT_SECRET")
CONCUR_USERNAME = os.getenv("CONCUR_USERNAME")
CONCUR_PASSWORD = os.getenv("CONCUR_PASSWORD")
CONCUR_BASE_URL = os.getenv("CONCUR_BASE_URL", "https://us2.api.concursolutions.com")

# Anthropic API key
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL_ID = "claude-3-5-sonnet-20241022"

# Global variables
sdk = None
client = None
conversation_history = []

# System prompt for Claude
SYSTEM_PROMPT = """
You are a helpful assistant that can retrieve and update Concur profile information for users using the Concur Profile SDK.
You can help users access and modify their travel profiles using natural language requests.

# Available Tool Calls
You have access to the following tool calls that use the Concur Profile SDK:

## get_profile
Retrieves the user's complete profile information from Concur using the SDK.
- If no login_id is provided, gets the current authenticated user's profile
- Returns comprehensive profile data including basic info, travel preferences, loyalty programs, etc.

## update_profile
Updates basic profile fields like name, job title, company information using the SDK.
- Updates are applied using the SDK's robust update mechanism
- Handles XML schema compliance automatically

## update_contact_info
Updates contact information (addresses, phones, emails) using the SDK.
- Supports multiple address types (Home, Work)
- Supports multiple phone types (Home, Work, Cell, etc.)
- Supports multiple email types (Business, Personal, etc.)

## update_travel_preferences
Updates travel preferences using the SDK.
- Air preferences: seat position, section, meal preferences, home airport
- Hotel preferences: room type, amenities (gym, pool, room service, etc.)
- Car preferences: type, transmission, GPS, smoking preference
- Note: The SDK handles complex car preference updates automatically

## update_loyalty_program
Updates loyalty program information using the SDK's dedicated Loyalty v1 API.
- Supports Air, Hotel, Car, and Rail programs
- IMPORTANT: This functionality has API restrictions - only available to travel suppliers who have completed SAP Concur application review
- The SDK will handle the API restrictions gracefully

## list_profile_summaries
Lists profile summaries with pagination using the SDK.
- Gets profiles modified within a specified time period
- Supports pagination and filtering

# SDK Features and Benefits
The SDK provides:
- Automatic authentication and token management
- XML schema compliance
- Comprehensive error handling
- Type safety with enums and dataclasses
- Proper field ordering for API requirements
- Automatic retry logic for certain operations

# Important Notes
1. The SDK handles all the complex XML generation and API communication
2. Car preferences are updated individually by the SDK to handle API limitations
3. Loyalty program updates may fail due to API restrictions (this is expected)
4. The SDK automatically waits for user availability after creation
5. All enum values are validated by the SDK

When helping users:
- Use the appropriate tool for their request
- Explain any limitations (especially for loyalty programs)
- Confirm successful updates
- Handle errors gracefully and explain what went wrong

Be conversational and helpful in your responses.
"""

# Tool definitions for Claude - Updated to match SDK capabilities
tools = [
    {
        "name": "get_profile",
        "description": "Retrieves the user's profile information from Concur using the SDK",
        "input_schema": {
            "type": "object",
            "properties": {
                "login_id": {
                    "type": "string",
                    "description": "Optional login ID to get specific user profile. If not provided, gets current user."
                }
            }
        }
    },
    {
        "name": "update_profile",
        "description": "Updates specific fields in the user's Concur profile using the SDK",
        "input_schema": {
            "type": "object",
            "properties": {
                "login_id": {
                    "type": "string",
                    "description": "Login ID of user to update. If not provided, updates current user."
                },
                "first_name": {
                    "type": "string",
                    "description": "User's first name"
                },
                "last_name": {
                    "type": "string",
                    "description": "User's last name"
                },
                "middle_name": {
                    "type": "string",
                    "description": "User's middle name"
                },
                "job_title": {
                    "type": "string",
                    "description": "User's job title"
                },
                "company_name": {
                    "type": "string",
                    "description": "User's company name"
                },
                "employee_id": {
                    "type": "string",
                    "description": "User's employee ID"
                },
                "medical_alerts": {
                    "type": "string",
                    "description": "User's medical alerts"
                }
            }
        }
    },
    {
        "name": "update_contact_info",
        "description": "Updates contact information (addresses, phones, emails) using the SDK",
        "input_schema": {
            "type": "object",
            "properties": {
                "login_id": {
                    "type": "string",
                    "description": "Login ID of user to update. If not provided, updates current user."
                },
                "address_type": {
                    "type": "string",
                    "enum": ["Home", "Work"],
                    "description": "Type of address to update"
                },
                "street": {
                    "type": "string",
                    "description": "Street address"
                },
                "city": {
                    "type": "string",
                    "description": "City"
                },
                "state_province": {
                    "type": "string",
                    "description": "State or province"
                },
                "postal_code": {
                    "type": "string",
                    "description": "Postal/zip code"
                },
                "country_code": {
                    "type": "string",
                    "description": "Country code (e.g., 'US')"
                },
                "phone_type": {
                    "type": "string",
                    "enum": ["Home", "Work", "Cell", "Fax", "Pager", "Other"],
                    "description": "Type of phone number"
                },
                "phone_number": {
                    "type": "string",
                    "description": "Phone number"
                },
                "phone_country_code": {
                    "type": "string",
                    "description": "Phone country code (e.g., '1' for US)"
                },
                "phone_extension": {
                    "type": "string",
                    "description": "Phone extension"
                },
                "email_type": {
                    "type": "string",
                    "enum": ["Business", "Personal", "Supervisor", "TravelArranger", "Business2", "Other1", "Other2"],
                    "description": "Type of email address"
                },
                "email_address": {
                    "type": "string",
                    "description": "Email address"
                }
            }
        }
    },
    {
        "name": "update_travel_preferences",
        "description": "Updates the user's travel preferences using the SDK",
        "input_schema": {
            "type": "object",
            "properties": {
                "login_id": {
                    "type": "string",
                    "description": "Login ID of user to update. If not provided, updates current user."
                },
                "air_seat_preference": {
                    "type": "string",
                    "enum": ["Window", "Aisle", "Middle", "DontCare"],
                    "description": "Preferred airline seat position"
                },
                "air_seat_section": {
                    "type": "string",
                    "enum": ["Bulkhead", "Forward", "Rear", "ExitRow", "DontCare"],
                    "description": "Preferred airline seat section"
                },
                "air_meal_preference": {
                    "type": "string",
                    "enum": ["BLML", "CHML", "DBML", "FPML", "GFML", "HNML", "BBML", "KSML", "LCML", "LSML", "MOML", "NSML", "NLML", "PFML", "SFML", "VLML", "VGML", "KVML", "RVML", "AVML"],
                    "description": "Preferred airline meal type (use meal codes)"
                },
                "air_home_airport": {
                    "type": "string",
                    "description": "Home airport code (e.g., 'SEA')"
                },
                "air_other": {
                    "type": "string",
                    "description": "Other air preferences"
                },
                "hotel_room_type": {
                    "type": "string",
                    "enum": ["King", "Queen", "Double", "Twin", "Single", "Disability", "DontCare"],
                    "description": "Preferred hotel room type"
                },
                "hotel_other": {
                    "type": "string",
                    "description": "Other hotel preferences"
                },
                "hotel_prefer_foam_pillows": {
                    "type": "boolean",
                    "description": "Prefer foam pillows"
                },
                "hotel_prefer_crib": {
                    "type": "boolean",
                    "description": "Prefer crib"
                },
                "hotel_prefer_rollaway_bed": {
                    "type": "boolean",
                    "description": "Prefer rollaway bed"
                },
                "hotel_prefer_gym": {
                    "type": "boolean",
                    "description": "Prefer gym access"
                },
                "hotel_prefer_pool": {
                    "type": "boolean",
                    "description": "Prefer pool access"
                },
                "hotel_prefer_room_service": {
                    "type": "boolean",
                    "description": "Prefer room service"
                },
                "hotel_prefer_early_checkin": {
                    "type": "boolean",
                    "description": "Prefer early check-in"
                },
                "car_type": {
                    "type": "string",
                    "enum": ["Economy", "Compact", "Intermediate", "Standard", "FullSize", "Premium", "Luxury", "SUV", "MiniVan", "Convertible", "DontCare"],
                    "description": "Preferred car type"
                },
                "car_transmission": {
                    "type": "string",
                    "enum": ["Automatic", "Manual", "DontCare"],
                    "description": "Preferred car transmission"
                },
                "car_smoking_preference": {
                    "type": "string",
                    "enum": ["NonSmoking", "Smoking", "DontCare"],
                    "description": "Car smoking preference"
                },
                "car_gps": {
                    "type": "boolean",
                    "description": "Require GPS in rental cars"
                },
                "car_ski_rack": {
                    "type": "boolean",
                    "description": "Require ski rack in rental cars"
                }
            }
        }
    },
    {
        "name": "update_loyalty_program",
        "description": "Updates the user's loyalty program information using the SDK",
        "input_schema": {
            "type": "object",
            "properties": {
                "login_id": {
                    "type": "string",
                    "description": "Login ID of user to update. If not provided, updates current user."
                },
                "program_type": {
                    "type": "string",
                    "enum": ["Air", "Hotel", "Car", "Rail"],
                    "description": "Type of loyalty program"
                },
                "vendor_code": {
                    "type": "string",
                    "description": "Vendor code for the loyalty program (e.g., 'UA' for United Airlines)"
                },
                "account_number": {
                    "type": "string",
                    "description": "User's membership number for the loyalty program"
                },
                "status": {
                    "type": "string",
                    "description": "User's status level in the loyalty program (e.g., 'Gold', 'Platinum')"
                },
                "status_benefits": {
                    "type": "string",
                    "description": "Benefits description for the status level"
                },
                "point_total": {
                    "type": "string",
                    "description": "Total points in the program"
                },
                "segment_total": {
                    "type": "string",
                    "description": "Total segments in the program"
                }
            },
            "required": ["program_type", "vendor_code", "account_number"]
        }
    },
    {
        "name": "list_profile_summaries",
        "description": "Lists profile summaries with pagination using the SDK",
        "input_schema": {
            "type": "object",
            "properties": {
                "days_back": {
                    "type": "integer",
                    "description": "Number of days back to look for modified profiles (default: 30)",
                    "default": 30
                },
                "page": {
                    "type": "integer",
                    "description": "Page number (default: 1)",
                    "default": 1
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of profiles per page (max: 200, default: 50)",
                    "default": 50
                },
                "active_only": {
                    "type": "boolean",
                    "description": "Only return active users (default: true)",
                    "default": True
                }
            }
        }
    }
]

def initialize_sdk():
    """Initialize the Concur Profile SDK"""
    global sdk
    try:
        sdk = ConcurProfileSDK(
            client_id=CONCUR_CLIENT_ID,
            client_secret=CONCUR_CLIENT_SECRET,
            username=CONCUR_USERNAME,
            password=CONCUR_PASSWORD,
            base_url=CONCUR_BASE_URL
        )
        # Test authentication
        profile = sdk.get_current_user_profile()
        return True, f"Connected as: {profile.first_name} {profile.last_name}"
    except Exception as e:
        return False, f"Failed to initialize SDK: {e}"

def initialize_claude():
    """Initialize the Anthropic client"""
    global client
    try:
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        return True, "Claude API initialized successfully"
    except Exception as e:
        return False, f"Failed to initialize Claude: {e}"

def get_current_user_login_id():
    """Get the current user's login ID"""
    try:
        profile = sdk.get_current_user_profile()
        return profile.login_id
    except Exception as e:
        print(f"Error getting current user login ID: {e}")
        return None

def tool_handler(tool_calls):
    """Handle tool calls from Claude using the SDK"""
    if not sdk:
        return [{"tool_call_id": tc["id"], "output": {"error": "SDK not initialized"}} for tc in tool_calls]
    
    tool_results = []
    
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_input = tool_call["input"]
        tool_call_id = tool_call["id"]
        
        result = None
        
        try:
            if tool_name == "get_profile":
                login_id = tool_input.get("login_id")
                if login_id:
                    profile = sdk.get_profile_by_login_id(login_id)
                else:
                    profile = sdk.get_current_user_profile()
                
                # Convert profile to dictionary for JSON serialization
                result = {
                    "login_id": profile.login_id,
                    "first_name": profile.first_name,
                    "last_name": profile.last_name,
                    "middle_name": profile.middle_name,
                    "job_title": profile.job_title,
                    "company_name": profile.company_name,
                    "employee_id": profile.employee_id,
                    "medical_alerts": profile.medical_alerts,
                    "addresses": [
                        {
                            "type": addr.type.value,
                            "street": addr.street,
                            "city": addr.city,
                            "state_province": addr.state_province,
                            "postal_code": addr.postal_code,
                            "country_code": addr.country_code
                        } for addr in profile.addresses
                    ],
                    "phones": [
                        {
                            "type": phone.type.value,
                            "phone_number": phone.phone_number,
                            "country_code": phone.country_code,
                            "extension": phone.extension
                        } for phone in profile.phones
                    ],
                    "emails": [
                        {
                            "type": email.type.value,
                            "email_address": email.email_address
                        } for email in profile.emails
                    ],
                    "emergency_contacts": [
                        {
                            "name": ec.name,
                            "relationship": ec.relationship,
                            "phone": ec.phone,
                            "mobile_phone": ec.mobile_phone,
                            "email": ec.email
                        } for ec in profile.emergency_contacts
                    ],
                    "air_preferences": {
                        "seat_preference": profile.air_preferences.seat_preference.value if profile.air_preferences and profile.air_preferences.seat_preference else None,
                        "seat_section": profile.air_preferences.seat_section.value if profile.air_preferences and profile.air_preferences.seat_section else None,
                        "meal_preference": profile.air_preferences.meal_preference.value if profile.air_preferences and profile.air_preferences.meal_preference else None,
                        "home_airport": profile.air_preferences.home_airport if profile.air_preferences else None,
                        "air_other": profile.air_preferences.air_other if profile.air_preferences else None
                    } if profile.air_preferences else None,
                    "hotel_preferences": {
                        "room_type": profile.hotel_preferences.room_type.value if profile.hotel_preferences and profile.hotel_preferences.room_type else None,
                        "hotel_other": profile.hotel_preferences.hotel_other if profile.hotel_preferences else None,
                        "prefer_foam_pillows": profile.hotel_preferences.prefer_foam_pillows if profile.hotel_preferences else None,
                        "prefer_gym": profile.hotel_preferences.prefer_gym if profile.hotel_preferences else None,
                        "prefer_pool": profile.hotel_preferences.prefer_pool if profile.hotel_preferences else None,
                        "prefer_room_service": profile.hotel_preferences.prefer_room_service if profile.hotel_preferences else None,
                        "prefer_early_checkin": profile.hotel_preferences.prefer_early_checkin if profile.hotel_preferences else None
                    } if profile.hotel_preferences else None,
                    "car_preferences": {
                        "car_type": profile.car_preferences.car_type.value if profile.car_preferences and profile.car_preferences.car_type else None,
                        "transmission": profile.car_preferences.transmission.value if profile.car_preferences and profile.car_preferences.transmission else None,
                        "smoking_preference": profile.car_preferences.smoking_preference.value if profile.car_preferences and profile.car_preferences.smoking_preference else None,
                        "gps": profile.car_preferences.gps if profile.car_preferences else None,
                        "ski_rack": profile.car_preferences.ski_rack if profile.car_preferences else None
                    } if profile.car_preferences else None,
                    "loyalty_programs": [
                        {
                            "program_type": lp.program_type.value,
                            "vendor_code": lp.vendor_code,
                            "account_number": lp.account_number,
                            "status": lp.status,
                            "status_benefits": lp.status_benefits,
                            "point_total": lp.point_total,
                            "segment_total": lp.segment_total
                        } for lp in profile.loyalty_programs
                    ]
                }
            
            elif tool_name == "update_profile":
                login_id = tool_input.get("login_id") or get_current_user_login_id()
                if not login_id:
                    result = {"error": "Could not determine user login ID"}
                else:
                    # Create profile with only the fields to update
                    profile = UserProfile(login_id=login_id)
                    fields_to_update = []
                    
                    if "first_name" in tool_input:
                        profile.first_name = tool_input["first_name"]
                        fields_to_update.append("first_name")
                    if "last_name" in tool_input:
                        profile.last_name = tool_input["last_name"]
                        fields_to_update.append("last_name")
                    if "middle_name" in tool_input:
                        profile.middle_name = tool_input["middle_name"]
                        fields_to_update.append("middle_name")
                    if "job_title" in tool_input:
                        profile.job_title = tool_input["job_title"]
                        fields_to_update.append("job_title")
                    if "company_name" in tool_input:
                        profile.company_name = tool_input["company_name"]
                        fields_to_update.append("company_name")
                    if "employee_id" in tool_input:
                        profile.employee_id = tool_input["employee_id"]
                        fields_to_update.append("employee_id")
                    if "medical_alerts" in tool_input:
                        profile.medical_alerts = tool_input["medical_alerts"]
                        fields_to_update.append("medical_alerts")
                    
                    if fields_to_update:
                        response = sdk.update_user(profile, fields_to_update=fields_to_update)
                        result = {"success": True, "message": f"Updated fields: {', '.join(fields_to_update)}"}
                    else:
                        result = {"error": "No fields provided to update"}
            
            elif tool_name == "update_contact_info":
                login_id = tool_input.get("login_id") or get_current_user_login_id()
                if not login_id:
                    result = {"error": "Could not determine user login ID"}
                else:
                    profile = UserProfile(login_id=login_id)
                    fields_to_update = []
                    
                    # Handle address updates
                    if any(field in tool_input for field in ["address_type", "street", "city", "state_province", "postal_code", "country_code"]):
                        address_type = AddressType(tool_input.get("address_type", "Home"))
                        address = Address(
                            type=address_type,
                            street=tool_input.get("street", ""),
                            city=tool_input.get("city", ""),
                            state_province=tool_input.get("state_province", ""),
                            postal_code=tool_input.get("postal_code", ""),
                            country_code=tool_input.get("country_code", "US")
                        )
                        profile.addresses = [address]
                        fields_to_update.append("addresses")
                    
                    # Handle phone updates
                    if any(field in tool_input for field in ["phone_type", "phone_number", "phone_country_code", "phone_extension"]):
                        phone_type = PhoneType(tool_input.get("phone_type", "Work"))
                        phone = Phone(
                            type=phone_type,
                            phone_number=tool_input.get("phone_number", ""),
                            country_code=tool_input.get("phone_country_code", ""),
                            extension=tool_input.get("phone_extension", "")
                        )
                        profile.phones = [phone]
                        fields_to_update.append("phones")
                    
                    # Handle email updates
                    if any(field in tool_input for field in ["email_type", "email_address"]):
                        email_type = EmailType(tool_input.get("email_type", "Business"))
                        email = Email(
                            type=email_type,
                            email_address=tool_input.get("email_address", "")
                        )
                        profile.emails = [email]
                        fields_to_update.append("emails")
                    
                    if fields_to_update:
                        response = sdk.update_user(profile, fields_to_update=fields_to_update)
                        result = {"success": True, "message": f"Updated contact info: {', '.join(fields_to_update)}"}
                    else:
                        result = {"error": "No contact information provided to update"}
            
            elif tool_name == "update_travel_preferences":
                login_id = tool_input.get("login_id") or get_current_user_login_id()
                if not login_id:
                    result = {"error": "Could not determine user login ID"}
                else:
                    profile = UserProfile(login_id=login_id)
                    fields_to_update = []
                    
                    # Handle air preferences
                    air_fields = ["air_seat_preference", "air_seat_section", "air_meal_preference", "air_home_airport", "air_other"]
                    if any(field in tool_input for field in air_fields):
                        air_prefs = AirPreferences()
                        if "air_seat_preference" in tool_input:
                            air_prefs.seat_preference = SeatPreference(tool_input["air_seat_preference"])
                        if "air_seat_section" in tool_input:
                            air_prefs.seat_section = SeatSection(tool_input["air_seat_section"])
                        if "air_meal_preference" in tool_input:
                            air_prefs.meal_preference = MealType(tool_input["air_meal_preference"])
                        if "air_home_airport" in tool_input:
                            air_prefs.home_airport = tool_input["air_home_airport"]
                        if "air_other" in tool_input:
                            air_prefs.air_other = tool_input["air_other"]
                        
                        profile.air_preferences = air_prefs
                        fields_to_update.append("air_preferences")
                    
                    # Handle hotel preferences
                    hotel_fields = ["hotel_room_type", "hotel_other", "hotel_prefer_foam_pillows", "hotel_prefer_crib", 
                                   "hotel_prefer_rollaway_bed", "hotel_prefer_gym", "hotel_prefer_pool", 
                                   "hotel_prefer_room_service", "hotel_prefer_early_checkin"]
                    if any(field in tool_input for field in hotel_fields):
                        hotel_prefs = HotelPreferences()
                        if "hotel_room_type" in tool_input:
                            hotel_prefs.room_type = HotelRoomType(tool_input["hotel_room_type"])
                        if "hotel_other" in tool_input:
                            hotel_prefs.hotel_other = tool_input["hotel_other"]
                        if "hotel_prefer_foam_pillows" in tool_input:
                            hotel_prefs.prefer_foam_pillows = tool_input["hotel_prefer_foam_pillows"]
                        if "hotel_prefer_crib" in tool_input:
                            hotel_prefs.prefer_crib = tool_input["hotel_prefer_crib"]
                        if "hotel_prefer_rollaway_bed" in tool_input:
                            hotel_prefs.prefer_rollaway_bed = tool_input["hotel_prefer_rollaway_bed"]
                        if "hotel_prefer_gym" in tool_input:
                            hotel_prefs.prefer_gym = tool_input["hotel_prefer_gym"]
                        if "hotel_prefer_pool" in tool_input:
                            hotel_prefs.prefer_pool = tool_input["hotel_prefer_pool"]
                        if "hotel_prefer_room_service" in tool_input:
                            hotel_prefs.prefer_room_service = tool_input["hotel_prefer_room_service"]
                        if "hotel_prefer_early_checkin" in tool_input:
                            hotel_prefs.prefer_early_checkin = tool_input["hotel_prefer_early_checkin"]
                        
                        profile.hotel_preferences = hotel_prefs
                        fields_to_update.append("hotel_preferences")
                    
                    # Handle car preferences
                    car_fields = ["car_type", "car_transmission", "car_smoking_preference", "car_gps", "car_ski_rack"]
                    if any(field in tool_input for field in car_fields):
                        car_prefs = CarPreferences()
                        if "car_type" in tool_input:
                            car_prefs.car_type = CarType(tool_input["car_type"])
                        if "car_transmission" in tool_input:
                            car_prefs.transmission = TransmissionType(tool_input["car_transmission"])
                        if "car_smoking_preference" in tool_input:
                            car_prefs.smoking_preference = SmokingPreference(tool_input["car_smoking_preference"])
                        if "car_gps" in tool_input:
                            car_prefs.gps = tool_input["car_gps"]
                        if "car_ski_rack" in tool_input:
                            car_prefs.ski_rack = tool_input["car_ski_rack"]
                        
                        profile.car_preferences = car_prefs
                        fields_to_update.append("car_preferences")
                    
                    if fields_to_update:
                        response = sdk.update_user(profile, fields_to_update=fields_to_update)
                        result = {"success": True, "message": f"Updated travel preferences: {', '.join(fields_to_update)}"}
                    else:
                        result = {"error": "No travel preferences provided to update"}
            
            elif tool_name == "update_loyalty_program":
                login_id = tool_input.get("login_id") or get_current_user_login_id()
                
                # Create loyalty program object
                program_type = LoyaltyProgramType(tool_input["program_type"])
                loyalty_program = LoyaltyProgram(
                    program_type=program_type,
                    vendor_code=tool_input["vendor_code"],
                    account_number=tool_input["account_number"],
                    status=tool_input.get("status", ""),
                    status_benefits=tool_input.get("status_benefits", ""),
                    point_total=tool_input.get("point_total", ""),
                    segment_total=tool_input.get("segment_total", "")
                )
                
                response = sdk.update_loyalty_program(loyalty_program, login_id)
                if response.success:
                    result = {"success": True, "message": f"Updated {tool_input['vendor_code']} loyalty program"}
                else:
                    result = {"error": f"Failed to update loyalty program: {response.error}"}
            
            elif tool_name == "list_profile_summaries":
                from datetime import datetime, timedelta
                
                days_back = tool_input.get("days_back", 30)
                page = tool_input.get("page", 1)
                limit = min(tool_input.get("limit", 50), 200)  # API max is 200
                active_only = tool_input.get("active_only", True)
                
                last_modified_date = datetime.now() - timedelta(days=days_back)
                
                summaries = sdk.list_profile_summaries(
                    last_modified_date=last_modified_date,
                    page=page,
                    limit=limit,
                    active_only=active_only
                )
                
                result = {
                    "total_items": summaries.metadata.total_items if summaries.metadata else 0,
                    "total_pages": summaries.metadata.total_pages if summaries.metadata else 0,
                    "current_page": summaries.metadata.page if summaries.metadata else page,
                    "items_per_page": summaries.metadata.items_per_page if summaries.metadata else limit,
                    "profiles": [
                        {
                            "login_id": summary.login_id,
                            "status": summary.status.value,
                            "xml_profile_sync_id": summary.xml_profile_sync_id,
                            "profile_last_modified_utc": summary.profile_last_modified_utc.isoformat() if summary.profile_last_modified_utc else None
                        } for summary in summaries.profile_summaries
                    ]
                }
            
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
        
        except ProfileNotFoundError as e:
            result = {"error": f"Profile not found: {str(e)}"}
        except ValidationError as e:
            result = {"error": f"Validation error: {str(e)}"}
        except AuthenticationError as e:
            result = {"error": f"Authentication error: {str(e)}"}
        except ConcurProfileError as e:
            result = {"error": f"Concur API error: {str(e)}"}
        except Exception as e:
            result = {"error": f"Unexpected error: {str(e)}"}
        
        tool_results.append({
            "tool_call_id": tool_call_id,
            "output": result
        })
    
    return tool_results

def chat_with_bot(message, history):
    """Main chat function for Gradio interface"""
    global conversation_history
    
    if not sdk or not client:
        return history + [{"role": "assistant", "content": "❌ Error: Bot not initialized. Please check the status panel."}]
    
    # Add user message to conversation
    conversation_history.append({
        "role": "user",
        "content": message
    })
    
    try:
        # Process with Claude
        has_tool_calls = True
        assistant_response = ""
        
        while has_tool_calls:
            # Get response from Claude
            response = client.messages.create(
                model=MODEL_ID,
                messages=conversation_history,
                system=SYSTEM_PROMPT,
                tools=tools,
                max_tokens=2048
            )
            
            # Add Claude's response to conversation
            conversation_history.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Process response content
            tool_calls = []
            content_text = ""
            
            for content_block in response.content:
                if content_block.type == "text":
                    content_text += content_block.text
                elif content_block.type == "tool_use":
                    tool_calls.append({
                        "id": content_block.id,
                        "name": content_block.name,
                        "input": content_block.input
                    })
            
            # Accumulate assistant response
            if content_text:
                assistant_response += content_text
            
            # Handle tool calls if any
            if tool_calls:
                # Add tool usage indicator
                tool_names = [tc["name"] for tc in tool_calls]
                assistant_response += f"\n\n🔧 *Using tools: {', '.join(tool_names)}*\n"
                
                # Execute tools
                tool_results = tool_handler(tool_calls)
                
                # Add tool results to conversation
                tool_result_content = []
                for result in tool_results:
                    tool_result_content.append({
                        "type": "tool_result",
                        "tool_use_id": result["tool_call_id"],
                        "content": json.dumps(result["output"])
                    })
                
                conversation_history.append({
                    "role": "user",
                    "content": tool_result_content
                })
            else:
                has_tool_calls = False
        
        # Update chat history with new message format
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": assistant_response})
        return history
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": error_msg})
        return history

def get_status():
    """Get current system status"""
    status_items = []
    
    # Check SDK status
    if sdk:
        try:
            profile = sdk.get_current_user_profile()
            status_items.append(f"✅ **Concur SDK**: Connected as {profile.first_name} {profile.last_name}")
        except:
            status_items.append("❌ **Concur SDK**: Connection error")
    else:
        status_items.append("❌ **Concur SDK**: Not initialized")
    
    # Check Claude status
    if client:
        status_items.append("✅ **Claude API**: Connected")
    else:
        status_items.append("❌ **Claude API**: Not initialized")
    
    # Add timestamp
    status_items.append(f"🕒 **Last updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return "\n\n".join(status_items)

def clear_conversation():
    """Clear the conversation history"""
    global conversation_history
    conversation_history = []
    return []

def quick_action_profile():
    """Quick action to get profile"""
    return "Show me my current profile information"

def quick_action_preferences():
    """Quick action to get travel preferences"""
    return "What are my current travel preferences?"

def quick_action_update_job():
    """Quick action to update job title"""
    return "Update my job title to "

def create_interface():
    """Create the Gradio interface"""
    
    # Use the Ocean theme - known for professional appearance with blue-green gradients
    theme = gr.themes.Ocean(
        primary_hue="blue",
        secondary_hue="cyan", 
        neutral_hue="slate",
        spacing_size="md",
        radius_size="sm",
        text_size="md",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "sans-serif"],
        font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace", "monospace"]
    )
    
    with gr.Blocks(title="Concur Profile Bot", theme=theme) as interface:
        # Header section
        gr.Markdown("""
        # 🚀 Concur Profile Bot
        ### Your intelligent travel profile assistant powered by AI
        
        Manage your travel preferences, update profile information, and get instant help with your Concur profile using natural language commands.
        """)
        
        with gr.Row():
            # Main chat area
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="💬 Chat with your Profile Bot",
                    height=500,
                    container=True,
                    type="messages",
                    avatar_images=("🧑‍💼", "🤖")
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="💭 Ask me anything about your Concur profile...",
                        scale=4,
                        container=False,
                        show_label=False
                    )
                    submit_btn = gr.Button("Send", variant="primary", scale=1)
            
            # Sidebar
            with gr.Column(scale=2):
                # Status panel
                gr.Markdown("### 📊 System Status")
                status_display = gr.Markdown(get_status())
                refresh_status_btn = gr.Button("🔄 Refresh Status", size="sm")
                
                # Quick actions
                gr.Markdown("### ⚡ Quick Actions")
                with gr.Row():
                    profile_btn = gr.Button("📋 Get Profile", size="sm")
                    prefs_btn = gr.Button("✈️ Travel Preferences", size="sm")
                with gr.Row():
                    update_btn = gr.Button("✏️ Update Job Title", size="sm")
                    clear_btn = gr.Button("🗑️ Clear Chat", size="sm", variant="secondary")
                
                # Help section
                gr.Markdown("""
                ### 💡 Example Commands
                
                **👤 Profile Management:**
                • "Show me my profile"
                • "Update my job title to Senior Engineer"
                
                **✈️ Travel Preferences:**
                • "Set my airline seat preference to window"
                • "I prefer king size beds in hotels"
                • "Update my car rental preference to compact"
                
                **📞 Contact Info:**
                • "Update my work phone number"
                • "Add my home address"
                • "Change my business email"
                """)
        
        # Event handlers
        def submit_message(message, history):
            if message.strip():
                return chat_with_bot(message, history), ""
            return history, message
        
        # Submit on Enter or button click
        msg.submit(submit_message, [msg, chatbot], [chatbot, msg])
        submit_btn.click(submit_message, [msg, chatbot], [chatbot, msg])
        
        # Quick action buttons
        profile_btn.click(lambda: quick_action_profile(), outputs=msg)
        prefs_btn.click(lambda: quick_action_preferences(), outputs=msg)
        update_btn.click(lambda: quick_action_update_job(), outputs=msg)
        clear_btn.click(clear_conversation, outputs=chatbot)
        
        # Status refresh
        refresh_status_btn.click(get_status, outputs=status_display)
        
        # Auto-refresh status every 30 seconds
        interface.load(get_status, outputs=status_display)
    
    return interface

def main():
    """Main function to start the Gradio interface"""
    print("🚀 Starting Concur Profile Bot Web Interface...")
    
    # Check environment variables
    if not CLAUDE_API_KEY:
        print("❌ Error: ANTHROPIC_API_KEY not found in environment variables")
        print("Please set the ANTHROPIC_API_KEY in your .env_tools file")
        return
    
    if not all([CONCUR_CLIENT_ID, CONCUR_CLIENT_SECRET, CONCUR_USERNAME, CONCUR_PASSWORD]):
        print("❌ Error: Concur API credentials not found in environment variables")
        print("Please ensure all required Concur API credentials are set in .env_tools")
        return
    
    # Initialize systems
    print("🔧 Initializing Concur SDK...")
    sdk_success, sdk_msg = initialize_sdk()
    if sdk_success:
        print(f"✅ {sdk_msg}")
    else:
        print(f"❌ {sdk_msg}")
        return
    
    print("🔧 Initializing Claude API...")
    claude_success, claude_msg = initialize_claude()
    if claude_success:
        print(f"✅ {claude_msg}")
    else:
        print(f"❌ {claude_msg}")
        return
    
    # Create and launch interface
    print("🌐 Creating web interface...")
    interface = create_interface()
    
    print("🎉 Launching Concur Profile Bot!")
    print("📱 The web interface will open in your browser")
    print("🔗 You can also access it at: http://localhost:7860")
    print("🔄 Auto-reload: Restart the script manually when you make changes")
    
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False,
        inbrowser=True
    )

if __name__ == "__main__":
    main() 