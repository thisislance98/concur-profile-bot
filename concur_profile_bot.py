#!/usr/bin/env python3
"""
Concur Profile Chatbot using Anthropic Claude with Tool Calling

This script creates a chatbot powered by Claude that can retrieve and update
Concur profile information through natural language requests using the modern Concur SDK
with Identity v4 + Travel Profile v2 architecture.
"""

import os
import sys
import json
import anthropic
import argparse
from datetime import datetime, date
from dotenv import load_dotenv

# Add the SDK to the path
sys.path.insert(0, os.path.dirname(__file__))

# Import the modern Concur SDK with Identity v4 + Travel Profile v2
from concur_profile_sdk import (
    ConcurSDK, IdentityUser, TravelProfile, IdentityName, IdentityEmail, IdentityPhoneNumber,
    Address, Phone, Email, EmergencyContact, Passport, Visa, NationalID, DriversLicense, TSAInfo,
    AirPreferences, HotelPreferences, CarPreferences, RailPreferences,
    LoyaltyProgram, RatePreference, DiscountCode, CustomField,
    AddressType, PhoneType, EmailType, LoyaltyProgramType, VisaType,
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
CONCUR_COMPANY_UUID = os.getenv("CONCUR_COMPANY_UUID")

# Anthropic API key
CLAUDE_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL_ID = "claude-3-5-sonnet-20241022"  # Use the latest stable model

# Initialize the SDK
sdk = None
user_context = None  # Store current user context

def initialize_sdk():
    """Initialize the modern Concur SDK with Identity v4 + Travel Profile v2"""
    global sdk, user_context
    try:
        sdk = ConcurSDK(
            client_id=CONCUR_CLIENT_ID,
            client_secret=CONCUR_CLIENT_SECRET,
            username=CONCUR_USERNAME,
            password=CONCUR_PASSWORD,
            base_url=CONCUR_BASE_URL,
            company_id=CONCUR_COMPANY_UUID
        )
        
        # Try to get current user context
        try:
            identity = sdk.get_current_user_identity()
            user_context = {
                "type": "user",
                "login_id": identity.user_name,
                "display_name": identity.display_name
            }
            print(f"SDK initialized successfully. User context: {identity.display_name}")
        except ConcurProfileError as e:
            if "client credentials" in str(e).lower():
                user_context = {
                    "type": "client_credentials", 
                    "login_id": None,
                    "display_name": "Company Admin"
                }
                print("SDK initialized with client credentials (company-level access)")
            else:
                user_context = {"type": "unknown", "login_id": None, "display_name": "Unknown"}
                print(f"SDK initialized with unknown context: {e}")
        
        return True
    except Exception as e:
        print(f"Failed to initialize SDK: {e}")
        return False

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

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
        "description": "Updates travel preferences (Air, Hotel, Car, Rail) via Travel Profile v2 API. Based on extensive testing: uses validation-compliant values, avoids problematic fields like hotel smoking preferences, and ensures proper XML structure with required elements like <Seat> in air preferences.",
        "input_schema": {
            "type": "object",
            "properties": {
                "login_id": {
                    "type": "string",
                    "description": "Login ID of user to update. Required for client credentials auth."
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
                    "description": "Preferred airline meal type (meal codes)"
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
        "name": "update_identity_documents",
        "description": "Updates identity documents (passports, visas, IDs) via Travel Profile v2 API",
        "input_schema": {
            "type": "object",
            "properties": {
                "login_id": {
                    "type": "string",
                    "description": "Login ID of user to update. Required for client credentials auth."
                },
                "passport_number": {
                    "type": "string",
                    "description": "Passport number"
                },
                "passport_nationality": {
                    "type": "string",
                    "description": "Passport nationality (e.g., 'US')"
                },
                "passport_issue_country": {
                    "type": "string",
                    "description": "Passport issuing country"
                },
                "passport_issue_date": {
                    "type": "string",
                    "description": "Passport issue date (YYYY-MM-DD)"
                },
                "passport_expiration_date": {
                    "type": "string",
                    "description": "Passport expiration date (YYYY-MM-DD)"
                },
                "visa_nationality": {
                    "type": "string",
                    "description": "Visa nationality"
                },
                "visa_number": {
                    "type": "string",
                    "description": "Visa number"
                },
                "visa_type": {
                    "type": "string",
                    "enum": ["Unknown", "SE", "DE", "ME", "ES", "ET", "SH"],
                    "description": "Visa type code"
                },
                "visa_country_issued": {
                    "type": "string",
                    "description": "Visa issuing country"
                },
                "national_id_number": {
                    "type": "string",
                    "description": "National ID number"
                },
                "national_id_country": {
                    "type": "string",
                    "description": "National ID issuing country"
                },
                "drivers_license_number": {
                    "type": "string",
                    "description": "Driver's license number"
                },
                "drivers_license_country": {
                    "type": "string",
                    "description": "Driver's license issuing country"
                },
                "drivers_license_state": {
                    "type": "string",
                    "description": "Driver's license issuing state/province"
                }
            }
        }
    },
    {
        "name": "update_loyalty_program",
        "description": "Updates loyalty program information via Loyalty v1 API (restricted to travel suppliers)",
        "input_schema": {
            "type": "object",
            "properties": {
                "login_id": {
                    "type": "string",
                    "description": "Login ID of user to update. Required for client credentials auth."
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
                    "description": "Program expiration date (YYYY-MM-DD)"
                }
            },
            "required": ["program_type", "vendor_code", "account_number"]
        }
    },
    {
        "name": "update_tsa_info",
        "description": "Updates TSA/security information via Travel Profile v2 API",
        "input_schema": {
            "type": "object",
            "properties": {
                "login_id": {
                    "type": "string",
                    "description": "Login ID of user to update. Required for client credentials auth."
                },
                "known_traveler_number": {
                    "type": "string",
                    "description": "TSA PreCheck Known Traveler Number"
                },
                "redress_number": {
                    "type": "string",
                    "description": "TSA Redress Number"
                },
                "gender": {
                    "type": "string",
                    "enum": ["Male", "Female", "Undisclosed", "Unknown", "Unspecified"],
                    "description": "Gender for TSA purposes"
                },
                "date_of_birth": {
                    "type": "string",
                    "description": "Date of birth for TSA (YYYY-MM-DD)"
                },
                "no_middle_name": {
                    "type": "boolean",
                    "description": "Indicate if user has no middle name"
                }
            }
        }
    }
]

# System prompt updated for Identity v4 + Travel Profile v2 architecture
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
- **Note**: Avoids problematic fields like hotel smoking_preference which cause validation errors

## update_identity_documents
Updates identity documents (passports, visas, IDs) via Travel Profile v2 API.
- Passports: number, nationality, issue/expiration dates
- Visas: nationality, number, type, issuing country
- National IDs and driver's licenses
- Handles date parsing and validation

## update_loyalty_program
Updates loyalty program information via Loyalty v1 API.
- **IMPORTANT**: Highly restricted API - typically only available to travel suppliers
- XML generation always works, but API updates may fail due to permissions
- Programs appear as AdvantageMemberships in XML, not LoyaltyPrograms
- Only basic fields (vendor code, program number, expiration) appear in XML output

## update_tsa_info
Updates TSA/security information via Travel Profile v2 API.
- Known traveler number, redress number
- Gender, date of birth for security purposes
- No middle name indicator

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

# Key Features and Discoveries

## XML Structure Insights (from testing)
**Loyalty Programs:**
- ✅ Appear as `<AdvantageMemberships>` with `<Membership>` elements
- ❌ Do NOT appear as `<LoyaltyPrograms>`
- Only basic fields appear in XML: vendor code, program number, expiration
- Status/benefits fields are stored but don't appear in XML output

**Travel Preferences:**
- ✅ All preference types generate correct XML structure
- ✅ Combined preferences work well in single document
- ⚠️ Hotel smoking_preference causes validation errors (avoided by SDK)

## API Restrictions (gracefully handled)
- User creation may be restricted based on authentication type
- Loyalty v1 API is highly restricted (this is expected)
- Some documented fields are not supported by all API versions
- XML generation always works regardless of API restrictions

## Error Handling Patterns
The SDK implements graceful error handling:
- Permission errors are caught and reported clearly
- Validation errors include helpful details
- API restrictions are expected and handled appropriately
- XML structure issues are avoided through testing insights

# Important Notes

1. **Separation of Concerns**: Identity data vs Travel data are managed separately
2. **Permission-Aware**: Operations adapt to available permissions
3. **XML Validation**: Follows exact schema requirements discovered through testing  
4. **Field Validation**: Avoids known problematic fields that cause API errors
5. **Date Handling**: Proper date parsing for documents and TSA info
6. **Enum Validation**: Type-safe enum usage throughout

# Usage Patterns

**For User Information:**
- Use get_user_identity for basic user data
- Use get_travel_profile for travel-specific information

**For Updates:**
- Use appropriate tool based on data type (identity vs travel)
- Provide login_id when using client credentials authentication
- Handle permission errors gracefully (they're often expected)

**For Complex Operations:**
- User creation may require specific permissions
- Loyalty program updates are often restricted
- Document updates work well with proper date formatting

Be conversational and helpful. Explain any limitations clearly. When API restrictions occur, 
explain that this is often expected behavior based on authentication type and permissions.
"""

def get_current_user_login_id():
    """Get the current user's login ID"""
    try:
        if user_context and user_context.get("login_id"):
            return user_context["login_id"]
        identity = sdk.get_current_user_identity()
        return identity.user_name
    except Exception as e:
        print(f"Error getting current user login ID: {e}")
        return None

def tool_handler(tool_calls):
    """Handle tool calls from Claude using the modern SDK with Identity v4 + Travel Profile v2"""
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
                if not login_id and user_context["type"] == "user":
                    login_id = user_context["login_id"]
                    
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
                from concur_profile_sdk import IdentityUser, IdentityName, IdentityEmail, IdentityPhoneNumber, IdentityEnterpriseInfo
                from datetime import date
                
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
            
            elif tool_name == "update_identity_documents":
                from datetime import datetime
                
                login_id = tool_input.get("login_id", get_current_user_login_id())
                if not login_id:
                    result = {"error": "Could not determine user login ID"}
                else:
                    profile = TravelProfile(login_id=login_id)
                    fields_to_update = []
                    
                    # Handle passport updates
                    if any(field in tool_input for field in ["passport_number", "passport_nationality", "passport_issue_country", "passport_issue_date", "passport_expiration_date"]):
                        issue_date = None
                        expiration_date = None
                        
                        if tool_input.get("passport_issue_date"):
                            issue_date = datetime.strptime(tool_input["passport_issue_date"], "%Y-%m-%d").date()
                        if tool_input.get("passport_expiration_date"):
                            expiration_date = datetime.strptime(tool_input["passport_expiration_date"], "%Y-%m-%d").date()
                        
                        passport = Passport(
                            doc_number=tool_input.get("passport_number", ""),
                            nationality=tool_input.get("passport_nationality", ""),
                            issue_country=tool_input.get("passport_issue_country", ""),
                            issue_date=issue_date,
                            expiration_date=expiration_date
                        )
                        profile.passports = [passport]
                        fields_to_update.append("passports")
                    
                    # Handle visa updates
                    if any(field in tool_input for field in ["visa_nationality", "visa_number", "visa_type", "visa_country_issued"]):
                        visa = Visa(
                            visa_nationality=tool_input.get("visa_nationality", ""),
                            visa_number=tool_input.get("visa_number", ""),
                            visa_type=VisaType(tool_input.get("visa_type", "Unknown")),
                            visa_country_issued=tool_input.get("visa_country_issued", "")
                        )
                        profile.visas = [visa]
                        fields_to_update.append("visas")
                    
                    # Handle national ID updates
                    if any(field in tool_input for field in ["national_id_number", "national_id_country"]):
                        national_id = NationalID(
                            id_number=tool_input.get("national_id_number", ""),
                            country_code=tool_input.get("national_id_country", "")
                        )
                        profile.national_ids = [national_id]
                        fields_to_update.append("national_ids")
                    
                    # Handle driver's license updates
                    if any(field in tool_input for field in ["drivers_license_number", "drivers_license_country", "drivers_license_state"]):
                        drivers_license = DriversLicense(
                            license_number=tool_input.get("drivers_license_number", ""),
                            country_code=tool_input.get("drivers_license_country", ""),
                            state_province=tool_input.get("drivers_license_state", "")
                        )
                        profile.drivers_licenses = [drivers_license]
                        fields_to_update.append("drivers_licenses")
                    
                    if fields_to_update:
                        response = sdk.update_travel_profile(profile, fields_to_update=fields_to_update)
                        result = {"success": True, "message": f"Updated identity documents: {', '.join(fields_to_update)}"}
                    else:
                        result = {"error": "No identity document information provided to update"}
            
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
            
            elif tool_name == "update_tsa_info":
                from datetime import datetime
                
                login_id = tool_input.get("login_id", get_current_user_login_id())
                
                # Parse date of birth if provided
                dob = None
                if tool_input.get("date_of_birth"):
                    dob = datetime.strptime(tool_input["date_of_birth"], "%Y-%m-%d").date()
                
                # Create TSAInfo object
                tsa_info = TSAInfo(
                    known_traveler_number=tool_input.get("known_traveler_number", ""),
                    redress_number=tool_input.get("redress_number", ""),
                    gender=tool_input.get("gender", ""),
                    date_of_birth=dob,
                    no_middle_name=tool_input.get("no_middle_name", False)
                )
                
                # Update via travel profile
                profile = TravelProfile(login_id=login_id, tsa_info=tsa_info)
                response = sdk.update_travel_profile(profile, fields_to_update=["tsa_info"])
                result = {"success": True, "message": "Updated TSA/security information"}
            
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

def chat_with_claude():
    """Run an interactive chat session with Claude using the SDK"""
    print("Concur Profile Assistant (powered by Claude + SDK)")
    print("Type 'exit' or 'quit' to end the session")
    print("------------------------------------------")
    
    # Initialize with empty conversation history
    messages = []
    
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        
        # Add user message to conversation
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Call Claude and handle tool calls until no more tool calls are present
        try:
            has_tool_calls = True
            
            while has_tool_calls:
                # Get response from Claude
                response = client.messages.create(
                    model=MODEL_ID,
                    messages=messages,
                    system=SYSTEM_PROMPT,
                    tools=tools,
                    max_tokens=2048
                )
                
                # Add Claude's response to the conversation
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                
                # Check for tool calls
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
                        print(f"\n[Using SDK tool: {content_block.name}]")
                
                # Print Claude's text response
                if content_text:
                    print(f"\nAssistant: {content_text}")
                
                # If no tool calls, break the loop
                if not tool_calls:
                    has_tool_calls = False
                    break
                
                # Handle tool calls
                tool_results = tool_handler(tool_calls)
                
                # Add tool results to the conversation
                tool_result_content = []
                for result in tool_results:
                    tool_result_content.append({
                        "type": "tool_result",
                        "tool_use_id": result["tool_call_id"],
                        "content": json.dumps(result["output"])
                    })
                
                messages.append({
                    "role": "user",
                    "content": tool_result_content
                })
        
        except Exception as e:
            print(f"\nError communicating with Claude: {str(e)}")
            continue

def main():
    """Main entry point with command-line interface"""
    parser = argparse.ArgumentParser(description='Concur Profile Bot powered by Claude + Modern SDK (Identity v4 + Travel Profile v2)')
    
    # Mode selection
    parser.add_argument('--interactive', action='store_true', help='Run in interactive chat mode (default)')
    
    # Direct command options
    subparsers = parser.add_subparsers(dest='command', help='Direct commands')
    
    # get-identity command
    get_identity_parser = subparsers.add_parser('get-identity', help='Get user identity information')
    get_identity_parser.add_argument('--user-id', help='User ID to get identity for')
    get_identity_parser.add_argument('--username', help='Username to search for')
    
    # get-travel-profile command
    get_travel_parser = subparsers.add_parser('get-travel-profile', help='Get travel profile information')
    get_travel_parser.add_argument('--login-id', help='Login ID to get travel profile for (required for client credentials)')
    
    # prompt command
    prompt_parser = subparsers.add_parser('prompt', help='Send a specific prompt to Claude')
    prompt_parser.add_argument('text', help='Prompt text to send to Claude')
    
    args = parser.parse_args()
    
    # Verify we have the necessary API keys
    if not CLAUDE_API_KEY:
        print("Error: ANTHROPIC_API_KEY not found in environment variables or .env file")
        print("Please set the ANTHROPIC_API_KEY environment variable to your Anthropic API key")
        sys.exit(1)
    
    if not all([CONCUR_CLIENT_ID, CONCUR_CLIENT_SECRET]):
        print("Error: Concur API credentials not found in environment variables or .env file")
        print("Please ensure CONCUR_CLIENT_ID and CONCUR_CLIENT_SECRET are set")
        sys.exit(1)
    
    # Initialize the SDK
    if not initialize_sdk():
        print("Failed to initialize Concur SDK")
        sys.exit(1)
    
    # Handle direct commands
    if args.command == 'get-identity':
        try:
            if args.user_id:
                identity = sdk.get_user_identity_by_id(args.user_id)
            elif args.username:
                identity = sdk.find_user_by_username(args.username)
            else:
                identity = sdk.get_current_user_identity()
            
            if identity:
                print(f"User Identity: {identity.display_name}")
                print(f"User ID: {identity.id}")
                print(f"Username: {identity.user_name}")
                print(f"Title: {identity.title}")
                print(f"Active: {identity.active}")
                
                if identity.name:
                    print(f"Full Name: {identity.name.given_name} {identity.name.family_name}")
                
                if identity.emails:
                    print(f"Primary Email: {identity.emails[0].value}")
                
                if identity.enterprise_info:
                    print(f"Company ID: {identity.enterprise_info.company_id}")
                    print(f"Employee Number: {identity.enterprise_info.employee_number}")
                    print(f"Department: {identity.enterprise_info.department}")
            else:
                print("User not found")
                
        except Exception as e:
            print(f"Error getting user identity: {e}")
    
    elif args.command == 'get-travel-profile':
        try:
            login_id = args.login_id
            if not login_id and user_context["type"] == "user":
                login_id = user_context["login_id"]
            
            if not login_id:
                print("Error: Login ID is required for travel profile access")
                print("Use --login-id parameter or ensure user authentication context")
                sys.exit(1)
            
            travel_profile = sdk.get_travel_profile(login_id)
            
            print(f"Travel Profile for: {travel_profile.login_id}")
            print(f"Travel Class: {travel_profile.rule_class}")
            print(f"Travel Config ID: {travel_profile.travel_config_id}")
            
            if travel_profile.air_preferences:
                print(f"Home Airport: {travel_profile.air_preferences.home_airport}")
                print(f"Seat Preference: {travel_profile.air_preferences.seat_preference}")
            
            if travel_profile.hotel_preferences:
                print(f"Hotel Room Type: {travel_profile.hotel_preferences.room_type}")
            
            if travel_profile.car_preferences:
                print(f"Car Type: {travel_profile.car_preferences.car_type}")
            
            print(f"Passports: {len(travel_profile.passports)}")
            print(f"Loyalty Programs: {len(travel_profile.loyalty_programs)}")
            
            if travel_profile.tsa_info:
                print(f"Known Traveler Number: {travel_profile.tsa_info.known_traveler_number}")
            
        except Exception as e:
            print(f"Error getting travel profile: {e}")
        
    elif args.command == 'prompt':
        # Start a chat session with just one prompt
        messages = []
        
        # Add user message to conversation
        messages.append({
            "role": "user",
            "content": args.text
        })
        
        # Process the prompt with tool calls
        has_tool_calls = True
        
        while has_tool_calls:
            # Get response from Claude
            response = client.messages.create(
                model=MODEL_ID,
                messages=messages,
                system=SYSTEM_PROMPT,
                tools=tools,
                max_tokens=2048
            )
            
            # Add Claude's response to the conversation
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Check for tool calls
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
                    print(f"\n[Using SDK tool: {content_block.name}]")
            
            # Print Claude's text response
            if content_text:
                print(f"\nClaude: {content_text}")
            
            # If no tool calls, break the loop
            if not tool_calls:
                has_tool_calls = False
                break
            
            # Handle tool calls
            tool_results = tool_handler(tool_calls)
            
            # Add tool results to the conversation
            tool_result_content = []
            for result in tool_results:
                tool_result_content.append({
                    "type": "tool_result",
                    "tool_use_id": result["tool_call_id"],
                    "content": json.dumps(result["output"])
                })
            
            messages.append({
                "role": "user",
                "content": tool_result_content
            })
    
    else:
        # Interactive mode is the default
        chat_with_claude()

if __name__ == "__main__":
    main() 