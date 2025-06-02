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

# Import the Concur Profile SDK - Updated for Identity v4 + Travel Profile v2
from concur_profile_sdk import (
    ConcurSDK, IdentityUser, IdentityName, IdentityEmail, TravelProfile,
    AirPreferences, HotelPreferences, CarPreferences, RailPreferences, 
    LoyaltyProgram, RatePreference, DiscountCode, CustomField,
    AddressType, PhoneType, EmailType, LoyaltyProgramType, VisaType,
    SeatPreference, SeatSection, MealType, HotelRoomType, SmokingPreference,
    CarType, TransmissionType,
    ConcurProfileError, AuthenticationError, ProfileNotFoundError, ValidationError,
    IdentityPhoneNumber, IdentityEnterpriseInfo
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
You are a helpful assistant that can retrieve and update Concur profile information using the modern Concur SDK
with Identity v4 + Travel Profile v2 architecture.

# Modern SDK Architecture
The SDK uses two complementary APIs:
- **Identity v4**: User identity, contact info, enterprise data (SCIM 2.0 compliant)
- **Travel Profile v2**: Travel preferences, documents, loyalty programs, travel-specific data

# Available Tool Calls

## get_user_identity
Retrieves user identity information from Identity v4 API using the SDK.
- If no user_id or username is provided, gets the current authenticated user's identity
- Returns user identity data: name, title, emails, phone numbers, enterprise info
- Handles both user authentication and client credentials contexts

## get_travel_profile
Retrieves travel profile information from Travel Profile v2 API using the SDK.
- Requires login_id for client credentials authentication
- Returns complete travel data: preferences, documents, loyalty programs, TSA info
- Includes passports, visas, national IDs, driver's licenses

## create_user_identity
Creates a new user identity via Identity v4 API using the SDK.
- Requires user_name, given_name, and family_name (minimum)
- Supports comprehensive identity data including enterprise information
- **Note**: May be restricted in some environments due to permission requirements

## update_travel_profile
Updates basic travel profile information via Travel Profile v2 API.
- Updates rule_class, travel_config_id
- Requires login_id for client credentials authentication

## update_travel_preferences
Updates travel preferences (Air, Hotel, Car, Rail) via Travel Profile v2 API.
- Air: seat position, section, meal preferences, home airport
- Hotel: room type, amenities (gym, pool, room service, etc.)
- Car: type, transmission, GPS, smoking preference
- **Note**: Uses validation-compliant values and avoids problematic fields

## update_loyalty_program
Updates loyalty program information via Loyalty v1 API.
- **IMPORTANT**: Highly restricted API - typically only available to travel suppliers
- XML generation always works, but API updates may fail due to permissions
- Programs appear as AdvantageMemberships in XML, not LoyaltyPrograms

# Authentication Context Detection
The SDK automatically detects authentication type:

**User Authentication:**
- Can use current user methods without login_id
- Provides user-specific context
- Can call get_user_identity() without parameters

**Client Credentials Authentication:**
- Company-level access without user context
- Requires login_id for all travel profile operations
- Cannot use current user methods

# Key Features
- **Separation of Concerns**: Identity data vs Travel data are managed separately
- **Permission-Aware**: Operations adapt to available permissions
- **XML Validation**: Follows exact schema requirements discovered through testing  
- **Field Validation**: Avoids known problematic fields that cause API errors
- **Date Handling**: Proper date parsing for documents and TSA info

Be conversational and helpful. Explain any limitations clearly. When API restrictions occur, 
explain that this is often expected behavior based on authentication type and permissions.
"""

# Tool definitions for Claude - Updated for Identity v4 + Travel Profile v2 architecture
tools = [
    {
        "name": "get_user_identity",
        "description": "Retrieves user identity information from Identity v4 API using the SDK",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "Optional user ID to get specific user identity. If not provided, gets current user."
                },
                "username": {
                    "type": "string", 
                    "description": "Optional username to search for user identity."
                }
            }
        }
    },
    {
        "name": "get_travel_profile",
        "description": "Retrieves travel profile information from Travel Profile v2 API using the SDK",
        "input_schema": {
            "type": "object",
            "properties": {
                "login_id": {
                    "type": "string",
                    "description": "Login ID to get travel profile for. Required for client credentials auth."
                }
            }
        }
    },
    {
        "name": "create_user_identity",
        "description": "Creates a new user identity via Identity v4 API using the SDK",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_name": {
                    "type": "string",
                    "description": "Username/email for the new user"
                },
                "given_name": {
                    "type": "string",
                    "description": "User's first name"
                },
                "family_name": {
                    "type": "string", 
                    "description": "User's last name"
                },
                "middle_name": {
                    "type": "string",
                    "description": "User's middle name"
                },
                "display_name": {
                    "type": "string",
                    "description": "User's display name"
                },
                "title": {
                    "type": "string",
                    "description": "User's job title"
                },
                "email": {
                    "type": "string",
                    "description": "User's primary email address"
                },
                "phone": {
                    "type": "string",
                    "description": "User's primary phone number"
                },
                "employee_number": {
                    "type": "string",
                    "description": "User's employee number"
                },
                "department": {
                    "type": "string",
                    "description": "User's department"
                }
            },
            "required": ["user_name", "given_name", "family_name"]
        }
    },
    {
        "name": "update_travel_profile",
        "description": "Updates travel profile information via Travel Profile v2 API using the SDK",
        "input_schema": {
            "type": "object",
            "properties": {
                "login_id": {
                    "type": "string",
                    "description": "Login ID of user to update. Required for client credentials auth."
                },
                "rule_class": {
                    "type": "string",
                    "description": "Travel rule class"
                },
                "travel_config_id": {
                    "type": "string",
                    "description": "Travel configuration ID"
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
                    "description": "Other air preferences - use simple descriptive text (e.g., 'Prefer early morning flights'). Avoid timestamps or special characters to prevent validation errors."
                },
                "hotel_room_type": {
                    "type": "string",
                    "enum": ["King", "Queen", "Double", "Twin", "Single", "Disability", "DontCare"],
                    "description": "Preferred hotel room type"
                },
                "hotel_other": {
                    "type": "string",
                    "description": "Other hotel preferences - use simple descriptive text (e.g., 'Late checkout preferred'). Keep text simple to avoid validation issues."
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
                },
                "expiration_date": {
                    "type": "string",
                    "description": "Expiration date of the loyalty program"
                }
            },
            "required": ["program_type", "vendor_code", "account_number"]
        }
    }
]

def initialize_sdk():
    """Initialize the Concur Profile SDK"""
    global sdk
    try:
        sdk = ConcurSDK(
            client_id=CONCUR_CLIENT_ID,
            client_secret=CONCUR_CLIENT_SECRET,
            username=CONCUR_USERNAME,
            password=CONCUR_PASSWORD,
            base_url=CONCUR_BASE_URL
        )
        # Test authentication by getting current user identity
        identity = sdk.get_current_user_identity()
        return True, f"Connected as: {identity.display_name}"
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
        identity = sdk.get_current_user_identity()
        return identity.user_name
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
            if tool_name == "get_user_identity":
                user_id = tool_input.get("user_id")
                username = tool_input.get("username")
                
                if user_id:
                    identity = sdk.get_user_identity_by_id(user_id)
                elif username:
                    identity = sdk.find_user_by_username(username)
                else:
                    identity = sdk.get_current_user_identity()
                
                if identity:
                    # Convert identity to dictionary for JSON serialization
                    result = {
                        "id": identity.id,
                        "user_name": identity.user_name,
                        "display_name": identity.display_name,
                        "title": identity.title,
                        "active": identity.active,
                        "given_name": identity.name.given_name if identity.name else "",
                        "family_name": identity.name.family_name if identity.name else "",
                        "middle_name": identity.name.middle_name if identity.name else "",
                        "emails": [
                            {
                                "value": email.value,
                                "type": email.type,
                                "primary": email.primary
                            } for email in identity.emails
                        ],
                        "phone_numbers": [
                            {
                                "value": phone.value,
                                "type": phone.type,
                                "primary": phone.primary
                            } for phone in identity.phone_numbers
                        ],
                        "enterprise_info": {
                            "company_id": identity.enterprise_info.company_id if identity.enterprise_info else "",
                            "employee_number": identity.enterprise_info.employee_number if identity.enterprise_info else "",
                            "department": identity.enterprise_info.department if identity.enterprise_info else ""
                        } if identity.enterprise_info else None
                    }
                else:
                    result = {"error": "User not found"}
            
            elif tool_name == "get_travel_profile":
                login_id = tool_input.get("login_id")
                if not login_id:
                    login_id = get_current_user_login_id()
                    
                if not login_id:
                    result = {"error": "Login ID is required for travel profile access"}
                else:
                    travel_profile = sdk.get_travel_profile(login_id)
                    
                    # Convert travel profile to dictionary
                    result = {
                        "login_id": travel_profile.login_id,
                        "rule_class": travel_profile.rule_class,
                        "travel_config_id": travel_profile.travel_config_id,
                        "air_preferences": {
                            "seat_preference": travel_profile.air_preferences.seat_preference.value if travel_profile.air_preferences and travel_profile.air_preferences.seat_preference else None,
                            "seat_section": travel_profile.air_preferences.seat_section.value if travel_profile.air_preferences and travel_profile.air_preferences.seat_section else None,
                            "meal_preference": travel_profile.air_preferences.meal_preference.value if travel_profile.air_preferences and travel_profile.air_preferences.meal_preference else None,
                            "home_airport": travel_profile.air_preferences.home_airport if travel_profile.air_preferences else None,
                            "air_other": travel_profile.air_preferences.air_other if travel_profile.air_preferences else None
                        } if travel_profile.air_preferences else None,
                        "hotel_preferences": {
                            "room_type": travel_profile.hotel_preferences.room_type.value if travel_profile.hotel_preferences and travel_profile.hotel_preferences.room_type else None,
                            "hotel_other": travel_profile.hotel_preferences.hotel_other if travel_profile.hotel_preferences else None,
                            "prefer_foam_pillows": travel_profile.hotel_preferences.prefer_foam_pillows if travel_profile.hotel_preferences else None,
                            "prefer_gym": travel_profile.hotel_preferences.prefer_gym if travel_profile.hotel_preferences else None,
                            "prefer_pool": travel_profile.hotel_preferences.prefer_pool if travel_profile.hotel_preferences else None,
                            "prefer_room_service": travel_profile.hotel_preferences.prefer_room_service if travel_profile.hotel_preferences else None,
                            "prefer_early_checkin": travel_profile.hotel_preferences.prefer_early_checkin if travel_profile.hotel_preferences else None
                        } if travel_profile.hotel_preferences else None,
                        "car_preferences": {
                            "car_type": travel_profile.car_preferences.car_type.value if travel_profile.car_preferences and travel_profile.car_preferences.car_type else None,
                            "transmission": travel_profile.car_preferences.transmission.value if travel_profile.car_preferences and travel_profile.car_preferences.transmission else None,
                            "smoking_preference": travel_profile.car_preferences.smoking_preference.value if travel_profile.car_preferences and travel_profile.car_preferences.smoking_preference else None,
                            "gps": travel_profile.car_preferences.gps if travel_profile.car_preferences else None,
                            "ski_rack": travel_profile.car_preferences.ski_rack if travel_profile.car_preferences else None
                        } if travel_profile.car_preferences else None,
                        "loyalty_programs": [
                            {
                                "program_type": lp.program_type.value,
                                "vendor_code": lp.vendor_code,
                                "account_number": lp.account_number,
                                "status": lp.status,
                                "status_benefits": lp.status_benefits,
                                "point_total": lp.point_total,
                                "segment_total": lp.segment_total
                            } for lp in travel_profile.loyalty_programs
                        ],
                        "passports": [
                            {
                                "doc_number": passport.doc_number,
                                "nationality": passport.nationality,
                                "issue_country": passport.issue_country,
                                "issue_date": passport.issue_date.isoformat() if passport.issue_date else None,
                                "expiration_date": passport.expiration_date.isoformat() if passport.expiration_date else None
                            } for passport in travel_profile.passports
                        ],
                        "tsa_info": {
                            "known_traveler_number": travel_profile.tsa_info.known_traveler_number,
                            "gender": travel_profile.tsa_info.gender,
                            "redress_number": travel_profile.tsa_info.redress_number,
                            "no_middle_name": travel_profile.tsa_info.no_middle_name
                        } if travel_profile.tsa_info else None
                    }
            
            elif tool_name == "create_user_identity":
                # Create user identity object
                user = IdentityUser(
                    user_name=tool_input["user_name"],
                    display_name=tool_input.get("display_name", f"{tool_input['given_name']} {tool_input['family_name']}"),
                    title=tool_input.get("title", ""),
                    name=IdentityName(
                        given_name=tool_input["given_name"],
                        family_name=tool_input["family_name"],
                        middle_name=tool_input.get("middle_name", "")
                    ),
                    emails=[
                        IdentityEmail(value=tool_input.get("email", tool_input["user_name"]), primary=True)
                    ] if tool_input.get("email") else [],
                    phone_numbers=[
                        IdentityPhoneNumber(value=tool_input["phone"], primary=True)
                    ] if tool_input.get("phone") else [],
                    enterprise_info=IdentityEnterpriseInfo(
                        employee_number=tool_input.get("employee_number", ""),
                        department=tool_input.get("department", "")
                    )
                )
                
                created_user = sdk.create_user_identity(user)
                result = {
                    "success": True,
                    "message": f"User identity created successfully",
                    "user_id": created_user.id,
                    "user_name": created_user.user_name
                }
            
            elif tool_name == "update_travel_profile":
                login_id = tool_input.get("login_id", get_current_user_login_id())
                if not login_id:
                    result = {"error": "Could not determine user login ID"}
                else:
                    # Create travel profile with only the fields to update
                    profile = TravelProfile(login_id=login_id)
                    fields_to_update = []
                    
                    if "rule_class" in tool_input:
                        profile.rule_class = tool_input["rule_class"]
                        fields_to_update.append("rule_class")
                    if "travel_config_id" in tool_input:
                        profile.travel_config_id = tool_input["travel_config_id"]
                        fields_to_update.append("travel_config_id")
                    
                    if fields_to_update:
                        try:
                            response = sdk.update_travel_profile(profile, fields_to_update=fields_to_update)
                            result = {"success": True, "message": f"Updated travel profile: {', '.join(fields_to_update)}"}
                        except Exception as update_error:
                            result = {"error": f"Failed to update travel profile: {str(update_error)}"}
                    else:
                        result = {"error": "No travel profile information provided to update"}
            
            elif tool_name == "update_travel_preferences":
                login_id = tool_input.get("login_id", get_current_user_login_id())
                if not login_id:
                    result = {"error": "Could not determine user login ID"}
                else:
                    profile = TravelProfile(login_id=login_id)
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
                        try:
                            response = sdk.update_travel_profile(profile, fields_to_update=fields_to_update)
                            result = {"success": True, "message": f"Updated travel preferences: {', '.join(fields_to_update)}"}
                        except Exception as update_error:
                            result = {"error": f"Failed to update travel preferences: {str(update_error)}"}
                    else:
                        result = {"error": "No travel preferences provided to update"}
            
            elif tool_name == "update_loyalty_program":
                from datetime import datetime
                
                login_id = tool_input.get("login_id", get_current_user_login_id())
                
                # Parse expiration date if provided
                expiration = None
                if tool_input.get("expiration_date"):
                    expiration = datetime.strptime(tool_input["expiration_date"], "%Y-%m-%d").date()
                
                # Create loyalty program object
                program_type = LoyaltyProgramType(tool_input["program_type"])
                loyalty_program = LoyaltyProgram(
                    program_type=program_type,
                    vendor_code=tool_input["vendor_code"],
                    account_number=tool_input["account_number"],
                    status=tool_input.get("status", ""),
                    status_benefits=tool_input.get("status_benefits", ""),
                    point_total=tool_input.get("point_total", ""),
                    segment_total=tool_input.get("segment_total", ""),
                    expiration=expiration
                )
                
                response = sdk.update_loyalty_program(loyalty_program, login_id)
                if response.success:
                    result = {"success": True, "message": f"Updated {tool_input['vendor_code']} loyalty program"}
                else:
                    result = {"error": f"Failed to update loyalty program: {response.error}"}
            
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
    """Main chat function for Gradio interface - non-streaming version"""
    global conversation_history
    
    if not sdk or not client:
        history.append({"role": "assistant", "content": "❌ Error: Bot not initialized. Please check the status panel."})
        return history
    
    # Add user message to conversation history and display history
    conversation_history.append({"role": "user", "content": message})
    history.append({"role": "user", "content": message})
    
    try:
        # Process with Claude
        has_tool_calls = True
        
        while has_tool_calls:
            # Get response from Claude
            response = client.messages.create(
                model=MODEL_ID,
                messages=conversation_history,
                system=SYSTEM_PROMPT,
                tools=tools,
                max_tokens=2048
            )
            
            # Process the response
            assistant_content = ""
            tool_calls = []
            
            for content_block in response.content:
                if content_block.type == "text":
                    assistant_content += content_block.text
                elif content_block.type == "tool_use":
                    tool_calls.append({
                        "id": content_block.id,
                        "name": content_block.name,
                        "input": content_block.input
                    })
            
            # Add Claude's response to conversation history (this includes both text and tool_use blocks)
            conversation_history.append({
                "role": "assistant", 
                "content": response.content
            })
            
            # Add text response to display history if there is any
            if assistant_content:
                history.append({"role": "assistant", "content": assistant_content})
            
            # Handle tool calls if any
            if tool_calls:
                # Show tool usage in display
                tool_names = [tc["name"] for tc in tool_calls]
                history.append({"role": "assistant", "content": f"🔧 Using tools: {', '.join(tool_names)}"})
                
                # Execute tools
                tool_results = tool_handler(tool_calls)
                
                # Add tool results to conversation in the correct format
                tool_result_blocks = []
                for result in tool_results:
                    tool_result_blocks.append({
                        "type": "tool_result",
                        "tool_use_id": result["tool_call_id"],
                        "content": json.dumps(result["output"])
                    })
                
                conversation_history.append({
                    "role": "user",
                    "content": tool_result_blocks
                })
                
                # Update tool usage message in display
                history[-1] = {"role": "assistant", "content": f"✅ Used tools: {', '.join(tool_names)}"}
                
                # Continue the loop for Claude's response to tool results
            else:
                has_tool_calls = False
        
        return history
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        history.append({"role": "assistant", "content": error_msg})
        return history

def get_status():
    """Get current system status"""
    status_items = []
    
    # Check SDK status
    if sdk:
        try:
            identity = sdk.get_current_user_identity()
            status_items.append(f"✅ **Concur SDK**: Connected as {identity.display_name}")
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
    """Quick action to get identity and travel profile"""
    return "Show me my current identity and travel profile information"

def quick_action_preferences():
    """Quick action to get travel preferences"""
    return "What are my current travel preferences?"

def quick_action_update_job():
    """Quick action to update travel preferences"""
    return "Update my travel preferences - set my airline seat preference to window"

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
                    profile_btn = gr.Button("👤 Get Identity", size="sm")
                    prefs_btn = gr.Button("✈️ Travel Preferences", size="sm")
                with gr.Row():
                    update_btn = gr.Button("✏️ Update Preferences", size="sm")
                    clear_btn = gr.Button("🗑️ Clear Chat", size="sm", variant="secondary")
                
                # Help section
                gr.Markdown("""
                ### 💡 Example Commands
                
                **👤 Identity Management:**
                • "Show me my identity information"
                • "What's my current user profile?"
                • "Create a new user identity"
                
                **✈️ Travel Preferences:**
                • "Set my airline seat preference to window"
                • "I prefer king size beds in hotels"
                • "Update my car rental preference to compact"
                • "What are my current travel preferences?"
                
                **🏢 Travel Profile:**
                • "Show me my travel profile"
                • "Update my travel rule class"
                • "What loyalty programs do I have?"
                """)
        
        # Event handlers - non-streaming
        def submit_message(message, history):
            if message.strip():
                return chat_with_bot(message, history), ""
            return history, message
        
        # Submit on Enter or button click
        msg.submit(
            submit_message, 
            [msg, chatbot], 
            [chatbot, msg]
        )
        
        submit_btn.click(
            submit_message, 
            [msg, chatbot], 
            [chatbot, msg]
        )
        
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
    
    # Get port from environment (Railway sets this automatically)
    port = int(os.getenv("PORT", 7860))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Check environment variables
    if not CLAUDE_API_KEY:
        print("❌ Error: ANTHROPIC_API_KEY not found in environment variables")
        print("Please set the ANTHROPIC_API_KEY in your environment")
        return
    
    if not all([CONCUR_CLIENT_ID, CONCUR_CLIENT_SECRET, CONCUR_USERNAME, CONCUR_PASSWORD]):
        print("❌ Error: Concur API credentials not found in environment variables")
        print("Please ensure all required Concur API credentials are set in environment")
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
    print(f"📱 The web interface will be available at: {host}:{port}")
    print("🔄 Auto-reload: Restart the script manually when you make changes")
    
    # Railway-friendly launch configuration
    interface.launch(
        server_name=host,
        server_port=port,
        share=False,
        show_error=True,
        quiet=False,
        inbrowser=False  # Don't try to open browser in production
    )

if __name__ == "__main__":
    main() 