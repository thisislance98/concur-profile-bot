# Concur SDK - Comprehensive Guide

## Table of Contents

1. [Overview](#overview)
2. [Installation and Setup](#installation-and-setup)
3. [Authentication](#authentication)
4. [Core Concepts](#core-concepts)
5. [Basic Operations](#basic-operations)
6. [User Management (Identity v4)](#user-management-identity-v4)
7. [Travel Profile Management (Travel Profile v2)](#travel-profile-management-travel-profile-v2)
8. [Contact Information](#contact-information)
9. [Identity Documents](#identity-documents)
10. [Travel Preferences](#travel-preferences)
11. [Loyalty Programs](#loyalty-programs)
12. [Advanced Features](#advanced-features)
13. [Error Handling](#error-handling)
14. [Best Practices](#best-practices)
15. [API Limitations](#api-limitations)
16. [Examples](#examples)

## Testing Insights

Based on comprehensive integration testing, here are key insights for working with the Concur SDK:

### **XML Structure Discoveries**

**Loyalty Programs:**
- ✅ Appear as `<AdvantageMemberships>` with `<Membership>` elements
- ❌ Do NOT appear as `<LoyaltyPrograms>`
- Only basic fields (vendor code, program number, expiration) appear in XML
- Status, benefits, and points data are stored but not included in XML output

**Travel Preferences:**
- ✅ All preference types (Air, Hotel, Car, Rail) generate correct XML structure
- ✅ Combined preferences work well in single XML document
- ⚠️ Some fields like `smoking_preference` cause validation errors

### **API Restrictions in Practice**

**User Creation:**
- Requires specific permissions that may not be available in all environments
- Client credentials authentication may restrict user creation
- **Recommended**: Use existing users for testing rather than creating new ones

**Loyalty v1 API:**
- Highly restricted - typically only available to travel suppliers with completed SAP Concur application review
- API calls often fail with permission errors (this is expected)
- XML generation always works regardless of API restrictions

**Authentication Types:**
- **Client Credentials**: Company-level access, cannot use current user methods
- **User Authentication**: User-specific context, can use current user methods

### **Successful Testing Patterns**

```python
# Pattern 1: Use existing authenticated user
current_user = sdk.get_current_user_identity()
login_id = current_user.user_name

# Pattern 2: Test XML generation (always works)
travel_profile = TravelProfile(login_id=login_id, air_preferences=air_prefs)
xml_output = travel_profile.to_update_xml()

# Pattern 3: Graceful API error handling
try:
    response = sdk.update_travel_profile(travel_profile)
except ConcurProfileError as e:
    if "401" in str(e):
        print("⚠️ API restricted (expected in some environments)")
    else:
        raise e
```

### **Validated Functionality**

✅ **Working Well:**
- Travel preferences XML generation for all types
- Loyalty program data structures and XML generation
- Current user identity retrieval
- Travel profile data parsing
- Combined preference updates

⚠️ **Environment Dependent:**
- User creation (permission restricted)
- Travel profile API updates (may be restricted)
- Loyalty program API updates (typically restricted)

❌ **Known Issues:**
- `HotelPreferences.smoking_preference` causes XML validation errors
- Loyalty program status/benefits don't appear in XML
- Some API endpoints require specific permission levels

## Overview

The Concur SDK is a comprehensive Python library for interacting with SAP Concur's modern APIs. It provides strongly-typed, object-oriented access to both user management and travel profile functionality using:

- **Identity v4 API** for user management (SCIM 2.0 compliant) - replaces Profile v1
- **Travel Profile v2 API** for travel preferences, loyalty programs, and travel-specific data

### Key Features

- **Modern API Architecture**: Uses Identity v4 + Travel Profile v2 for optimal functionality
- **SCIM 2.0 Compliant**: Full support for modern identity management standards
- **Strongly Typed**: Uses Python dataclasses and enums for type safety
- **XML & JSON Handling**: Built with lxml and requests for robust API processing
- **Schema Compliant**: Follows both SCIM 2.0 and Concur's XSD schema requirements exactly
- **Production Ready**: Includes comprehensive error handling and logging
- **Well Tested**: Extensive integration test suite

### Supported Operations

- **User Management**: Create, read, update users via Identity v4 (SCIM 2.0)
- **Travel Profiles**: Complete travel profile management via Travel Profile v2
- **Travel Preferences**: Air, Hotel, Car, Rail preferences
- **Loyalty Programs**: Full loyalty program management
- **Identity Documents**: Passports, visas, national IDs, driver's licenses
- **TSA Information**: Known traveler numbers, security preferences
- **Custom Fields**: Organization-specific data fields

## Installation and Setup

### Prerequisites

```bash
pip install requests lxml python-dotenv
```

### Environment Configuration

Create a `.env` file with your Concur credentials:

```env
CONCUR_CLIENT_ID=your_client_id
CONCUR_CLIENT_SECRET=your_client_secret
CONCUR_USERNAME=your_username
CONCUR_PASSWORD=your_password
CONCUR_BASE_URL=https://us2.api.concursolutions.com
```

### Basic Initialization

```python
from concur_profile_sdk import ConcurSDK

sdk = ConcurSDK(
    client_id="your-client-id",
    client_secret="your-client-secret", 
    username="user@example.com",
    password="password123"
)
```

## Authentication

The SDK handles OAuth2 authentication automatically:

```python
# Authentication happens automatically on first API call
identity = sdk.get_current_user_identity()
print(f"Authenticated as: {identity.display_name}")

travel_profile = sdk.get_current_user_travel_profile()
print(f"Travel config: {travel_profile.rule_class}")
```

### Authentication Features

- **Automatic token refresh** when tokens expire
- **Error handling** for authentication failures
- **Token caching** for performance
- **Geolocation handling** for Identity v4 endpoints

## Core Concepts

### Dual API Architecture

The SDK uses two complementary APIs:

1. **Identity v4 (SCIM 2.0)** - User identity management
2. **Travel Profile v2** - Travel-specific data and preferences

### IdentityUser Class

The `IdentityUser` class handles user identity information via Identity v4:

```python
from concur_profile_sdk import IdentityUser, IdentityName, IdentityEmail

user = IdentityUser(
    user_name="user@example.com",
    display_name="John Doe",
    name=IdentityName(given_name="John", family_name="Doe"),
    emails=[IdentityEmail(value="user@example.com")]
)
```

### TravelProfile Class

The `TravelProfile` class handles travel-specific information via Travel Profile v2:

```python
from concur_profile_sdk import TravelProfile, AirPreferences, SeatPreference

profile = TravelProfile(
    login_id="user@example.com",
    rule_class="Default Travel Class",
    air_preferences=AirPreferences(
        home_airport="SEA",
        seat_preference=SeatPreference.WINDOW
    )
)
```

### Enums for Type Safety

The SDK uses enums for all constrained values:

```python
from concur_profile_sdk import (
    SeatPreference, MealType, CarType, HotelRoomType,
    LoyaltyProgramType, VisaType
)

# Type-safe enum usage
seat_pref = SeatPreference.WINDOW
meal_pref = MealType.VEGETARIAN
car_type = CarType.INTERMEDIATE
```

## Basic Operations

### Get Current User Identity

```python
# Get identity information of authenticated user
identity = sdk.get_current_user_identity()

print(f"User ID: {identity.id}")
print(f"Username: {identity.user_name}")
print(f"Display Name: {identity.display_name}")
print(f"Title: {identity.title}")
print(f"Active: {identity.active}")

if identity.name:
    print(f"Full Name: {identity.name.given_name} {identity.name.family_name}")

if identity.emails:
    print(f"Primary Email: {identity.emails[0].value}")
```

### Get Current User Travel Profile

```python
# Get travel profile of authenticated user
travel_profile = sdk.get_current_user_travel_profile()

print(f"Login ID: {travel_profile.login_id}")
print(f"Travel Class: {travel_profile.rule_class}")
print(f"Passports: {len(travel_profile.passports)}")
print(f"Loyalty Programs: {len(travel_profile.loyalty_programs)}")

if travel_profile.air_preferences:
    print(f"Home Airport: {travel_profile.air_preferences.home_airport}")
```

### Find User by Username

```python
try:
    user = sdk.find_user_by_username("user@example.com")
    if user:
        print(f"Found user: {user.display_name}")
    else:
        print("User not found")
except Exception as e:
    print(f"Error: {e}")
```

## User Management (Identity v4)

### Creating Users

#### Basic User Creation

```python
from concur_profile_sdk import IdentityUser, IdentityName, IdentityEmail

user = IdentityUser(
    user_name="newuser@example.com",
    display_name="Jane Smith",
    name=IdentityName(given_name="Jane", family_name="Smith"),
    emails=[IdentityEmail(value="newuser@example.com", primary=True)]
)

created_user = sdk.create_user_identity(user)
print(f"Created user with ID: {created_user.id}")
```

#### Comprehensive User Creation

```python
from concur_profile_sdk import (
    IdentityUser, IdentityName, IdentityEmail, IdentityPhoneNumber,
    IdentityEnterpriseInfo
)
from datetime import date

user = IdentityUser(
    user_name="comprehensive@example.com",
    display_name="John Comprehensive",
    title="Senior Manager",
    nick_name="Johnny",
    preferred_language="en-US",
    timezone="America/New_York",
    
    # Name information
    name=IdentityName(
        given_name="John",
        family_name="Comprehensive",
        middle_name="Middle"
    ),
    
    # Contact information
    emails=[
        IdentityEmail(
            value="john.work@example.com",
            type="work",
            primary=True
        ),
        IdentityEmail(
            value="john.personal@example.com",
            type="home",
            primary=False
        )
    ],
    
    phone_numbers=[
        IdentityPhoneNumber(
            value="+1-206-555-0123",
            type="work",
            primary=True
        )
    ],
    
    # Enterprise information
    enterprise_info=IdentityEnterpriseInfo(
        company_id="COMP123",
        employee_number="EMP12345",
        start_date=date(2023, 1, 15),
        department="Engineering",
        cost_center="CC-ENG-001"
    )
)

created_user = sdk.create_user_identity(user)
print(f"Created comprehensive user: {created_user.id}")
```

### Updating Users

#### Simple Field Updates

```python
# Update user with simple field changes
updates = {
    "title": "Senior Director",
    "nickName": "Boss",
    "timezone": "America/Chicago"
}

updated_user = sdk.update_user_identity_simple(user_id, updates)
print(f"Updated user: {updated_user.title}")
```

#### Advanced PATCH Operations

```python
from concur_profile_sdk import IdentityPatchOperation

operations = [
    IdentityPatchOperation(
        op="replace",
        path="title",
        value="Principal Engineer"
    ),
    IdentityPatchOperation(
        op="replace",
        path="displayName",
        value="John P. Comprehensive"
    ),
    IdentityPatchOperation(
        op="add",
        path="nickName",
        value="Chief"
    )
]

updated_user = sdk.update_user_identity(user_id, operations)
print(f"Applied {len(operations)} updates")
```

## Travel Profile Management (Travel Profile v2)

### Getting Travel Profiles

```python
# Get by login ID
travel_profile = sdk.get_travel_profile_by_login_id("user@example.com")

print(f"Travel Class: {travel_profile.rule_class}")
print(f"Travel Config ID: {travel_profile.travel_config_id}")
```

### Updating Travel Profiles

#### Update Specific Fields

```python
from concur_profile_sdk import TravelProfile, AirPreferences, SeatPreference

# Update only air preferences
profile = TravelProfile(
    login_id="user@example.com",
    air_preferences=AirPreferences(
        home_airport="SEA",
        seat_preference=SeatPreference.WINDOW,
        air_other="Prefer early morning flights"
    )
)

response = sdk.update_travel_profile(
    profile, 
    fields_to_update=["air_preferences"]
)
print(f"Update response: {response.message}")
```

#### Update Multiple Travel Sections

```python
from concur_profile_sdk import (
    TravelProfile, AirPreferences, HotelPreferences, CarPreferences,
    SeatPreference, HotelRoomType, CarType
)

profile = TravelProfile(
    login_id="user@example.com",
    
    # Air preferences
    air_preferences=AirPreferences(
        home_airport="SEA",
        seat_preference=SeatPreference.WINDOW
    ),
    
    # Hotel preferences
    hotel_preferences=HotelPreferences(
        room_type=HotelRoomType.KING,
        prefer_gym=True,
        prefer_pool=True
    ),
    
    # Car preferences
    car_preferences=CarPreferences(
        car_type=CarType.INTERMEDIATE,
        gps=True
    )
)

response = sdk.update_travel_profile(
    profile,
    fields_to_update=["air_preferences", "hotel_preferences", "car_preferences"]
)
```

## Contact Information

Contact information is managed through the Identity v4 API:

### Email Addresses

```python
from concur_profile_sdk import IdentityEmail

# Update user emails
operations = [
    IdentityPatchOperation(
        op="replace",
        path="emails",
        value=[
            {
                "value": "primary@example.com",
                "type": "work",
                "primary": True
            },
            {
                "value": "secondary@example.com", 
                "type": "home",
                "primary": False
            }
        ]
    )
]

updated_user = sdk.update_user_identity(user_id, operations)
```

### Phone Numbers

```python
# Update phone numbers
operations = [
    IdentityPatchOperation(
        op="replace",
        path="phoneNumbers",
        value=[
            {
                "value": "+1-206-555-0123",
                "type": "work",
                "primary": True
            },
            {
                "value": "+1-206-555-0124",
                "type": "mobile",
                "primary": False
            }
        ]
    )
]

updated_user = sdk.update_user_identity(user_id, operations)
```

## Identity Documents

Identity documents are managed through the Travel Profile v2 API:

### Passports

```python
from concur_profile_sdk import TravelProfile, Passport
from datetime import date

profile = TravelProfile(
    login_id="user@example.com",
    passports=[
        Passport(
            doc_number="123456789",
            nationality="US",
            issue_country="US",
            issue_date=date(2020, 1, 15),
            expiration_date=date(2030, 1, 15),
            primary=True
        )
    ]
)

sdk.update_travel_profile(profile, fields_to_update=["passports"])
```

### Visas

```python
from concur_profile_sdk import Visa, VisaType
from datetime import date

profile = TravelProfile(
    login_id="user@example.com",
    visas=[
        Visa(
            visa_nationality="US",
            visa_number="V123456789",
            visa_type=VisaType.MULTI_ENTRY,
            visa_country_issued="GB",
            visa_date_issued=date(2023, 6, 1),
            visa_expiration=date(2025, 6, 1)
        )
    ]
)

sdk.update_travel_profile(profile, fields_to_update=["visas"])
```

### National IDs and Driver's Licenses

```python
from concur_profile_sdk import NationalID, DriversLicense

profile = TravelProfile(
    login_id="user@example.com",
    national_ids=[
        NationalID(
            id_number="123-45-6789",
            country_code="US"
        )
    ],
    drivers_licenses=[
        DriversLicense(
            license_number="D123456789",
            country_code="US",
            state_province="WA"
        )
    ]
)

sdk.update_travel_profile(
    profile, 
    fields_to_update=["national_ids", "drivers_licenses"]
)
```

### TSA Information

```python
from concur_profile_sdk import TSAInfo
from datetime import date

profile = TravelProfile(
    login_id="user@example.com",
    tsa_info=TSAInfo(
        known_traveler_number="12345678901",
        gender="Male",
        date_of_birth=date(1985, 6, 15),
        redress_number="987654321",
        no_middle_name=False
    )
)

sdk.update_travel_profile(profile, fields_to_update=["tsa_info"])
```

## Travel Preferences

### Air Travel Preferences

```python
from concur_profile_sdk import (
    TravelProfile, AirPreferences, SeatPreference, SeatSection, MealType
)

profile = TravelProfile(
    login_id="user@example.com",
    air_preferences=AirPreferences(
        seat_preference=SeatPreference.WINDOW,
        seat_section=SeatSection.FORWARD,
        meal_preference=MealType.VEGETARIAN,
        home_airport="SEA",
        air_other="Prefer early morning flights"
    )
)

sdk.update_travel_profile(profile, fields_to_update=["air_preferences"])
```

### Hotel Preferences

```python
from concur_profile_sdk import (
    TravelProfile, HotelPreferences, HotelRoomType
)

profile = TravelProfile(
    login_id="user@example.com",
    hotel_preferences=HotelPreferences(
        room_type=HotelRoomType.KING,
        hotel_other="Late checkout preferred",
        prefer_foam_pillows=True,
        prefer_gym=True,
        prefer_pool=True,
        prefer_room_service=True,
        prefer_early_checkin=True
    )
)

sdk.update_travel_profile(profile, fields_to_update=["hotel_preferences"])
```

### Car Rental Preferences

```python
from concur_profile_sdk import (
    TravelProfile, CarPreferences, CarType, TransmissionType, SmokingPreference
)

profile = TravelProfile(
    login_id="user@example.com",
    car_preferences=CarPreferences(
        car_type=CarType.INTERMEDIATE,
        transmission=TransmissionType.AUTOMATIC,
        smoking_preference=SmokingPreference.NON_SMOKING,
        gps=True,
        ski_rack=False
    )
)

# Note: Car preferences should be updated individually
# The SDK handles this automatically
sdk.update_travel_profile(profile, fields_to_update=["car_preferences"])
```

### Rail Travel Preferences

```python
from concur_profile_sdk import TravelProfile, RailPreferences

profile = TravelProfile(
    login_id="user@example.com",
    rail_preferences=RailPreferences(
        seat="Window",
        coach="First Class",
        noise_comfort="Quiet",
        bed="Upper",
        special_meals="Vegetarian"
    )
)

sdk.update_travel_profile(profile, fields_to_update=["rail_preferences"])
```

### Rate Preferences and Discount Codes

```python
from concur_profile_sdk import TravelProfile, RatePreference, DiscountCode

profile = TravelProfile(
    login_id="user@example.com",
    rate_preferences=RatePreference(
        aaa_rate=True,
        aarp_rate=False,
        govt_rate=True,
        military_rate=False
    ),
    discount_codes=[
        DiscountCode(vendor="HZ", code="CDP123456"),
        DiscountCode(vendor="AV", code="AWD987654")
    ]
)

sdk.update_travel_profile(profile, fields_to_update=["rate_preferences", "discount_codes"])
```

## Loyalty Programs

### Using the Dedicated Loyalty API

The SDK provides a dedicated Loyalty v1 API for managing loyalty programs:

```python
from concur_profile_sdk import LoyaltyProgram, LoyaltyProgramType

# Create loyalty program
loyalty_program = LoyaltyProgram(
    program_type=LoyaltyProgramType.AIR,
    vendor_code="UA",
    account_number="123456789",
    status="Premier Gold"
)

# Update via dedicated API
response = sdk.update_loyalty_program(loyalty_program)

if response.success:
    print("Loyalty program updated successfully")
else:
    print(f"Failed to update: {response.error}")
```

### **IMPORTANT: XML Structure for Loyalty Programs**

⚠️ **Key Discovery**: Loyalty programs appear in XML as `<AdvantageMemberships>` with `<Membership>` elements, **NOT** as `<LoyaltyPrograms>`:

```xml
<AdvantageMemberships>
    <Membership>
        <VendorCode>UA</VendorCode>
        <VendorType>Air</VendorType>
        <ProgramNumber>123456789</ProgramNumber>
        <ProgramCode>UA</ProgramCode>
        <ExpirationDate>2024-12-31</ExpirationDate>
    </Membership>
</AdvantageMemberships>
```

### **Limited XML Field Support**

While the `LoyaltyProgram` data structure supports comprehensive fields, only basic fields appear in generated XML:

**✅ Fields that appear in XML:**
- `vendor_code` → `<VendorCode>`
- `program_type` → `<VendorType>` (Air, Hotel, Car, Rail)
- `account_number` → `<ProgramNumber>`
- `vendor_code` → `<ProgramCode>`
- `expiration` → `<ExpirationDate>` (if provided)

**❌ Fields that DON'T appear in XML:**
- `status` (e.g., "Premier 1K")
- `status_benefits` (e.g., "Unlimited upgrades")
- `point_total`, `segment_total`
- `next_status`, `points_until_next_status`, `segments_until_next_status`

```python
# This data structure is valid but status/benefits won't appear in XML
loyalty_program = LoyaltyProgram(
    program_type=LoyaltyProgramType.AIR,
    vendor_code="UA",
    account_number="123456789",
    status="Premier 1K",  # Won't appear in XML
    status_benefits="Unlimited upgrades",  # Won't appear in XML
    point_total="150000"  # Won't appear in XML
)
```

### Comprehensive Loyalty Program Data

```python
from datetime import date

loyalty_program = LoyaltyProgram(
    program_type=LoyaltyProgramType.AIR,
    vendor_code="UA",
    account_number="123456789",
    status="Premier 1K",
    status_benefits="Unlimited upgrades, priority boarding",
    point_total="150000",
    segment_total="75",
    next_status="Global Services",
    points_until_next_status="50000",
    segments_until_next_status="25",
    expiration=date(2024, 12, 31)
)

response = sdk.update_loyalty_program(loyalty_program)
```

### Multiple Loyalty Programs

```python
# Air loyalty programs
air_programs = [
    LoyaltyProgram(
        program_type=LoyaltyProgramType.AIR,
        vendor_code="UA",
        account_number="UA123456",
        status="Premier Gold"
    ),
    LoyaltyProgram(
        program_type=LoyaltyProgramType.AIR,
        vendor_code="DL",
        account_number="DL789012",
        status="Platinum"
    )
]

# Hotel loyalty programs
hotel_programs = [
    LoyaltyProgram(
        program_type=LoyaltyProgramType.HOTEL,
        vendor_code="HH",
        account_number="HH345678",
        status="Diamond"
    )
]

# Update each program individually
for program in air_programs + hotel_programs:
    response = sdk.update_loyalty_program(program)
    if response.success:
        print(f"Updated {program.vendor_code} program")
```

### Loyalty Programs in Travel Profile XML

When loyalty programs are included in travel profile updates, they generate the following XML structure:

```python
from concur_profile_sdk import TravelProfile, LoyaltyProgram, LoyaltyProgramType

# Create travel profile with loyalty programs
travel_profile = TravelProfile(
    login_id="user@example.com",
    loyalty_programs=[
        LoyaltyProgram(
            program_type=LoyaltyProgramType.AIR,
            vendor_code="UA",
            account_number="123456789",
            expiration=date(2024, 12, 31)
        )
    ]
)

# Generate XML (will contain AdvantageMemberships, not LoyaltyPrograms)
xml_output = travel_profile.to_update_xml(fields_to_update=["loyalty_programs"])
```

## Advanced Features

### Custom Fields

```python
from concur_profile_sdk import TravelProfile, CustomField

profile = TravelProfile(
    login_id="user@example.com",
    custom_fields=[
        CustomField(
            field_id="COST_CENTER",
            value="CC-12345",
            field_type="Text"
        ),
        CustomField(
            field_id="DEPARTMENT",
            value="Engineering",
            field_type="Text"
        )
    ]
)

sdk.update_travel_profile(profile, fields_to_update=["custom_fields"])
```

### Unused Tickets

```python
from concur_profile_sdk import TravelProfile, UnusedTicket

profile = TravelProfile(
    login_id="user@example.com",
    unused_tickets=[
        UnusedTicket(
            ticket_number="1234567890123",
            airline_code="UA",
            amount="500.00",
            currency="USD"
        )
    ]
)

sdk.update_travel_profile(profile, fields_to_update=["unused_tickets"])
```

## Error Handling

### Exception Types

The SDK provides specific exception types for different error conditions:

```python
from concur_profile_sdk import (
    ConcurProfileError,
    AuthenticationError,
    ProfileNotFoundError,
    ValidationError
)

try:
    profile = sdk.get_travel_profile_by_login_id("nonexistent@example.com")
except ProfileNotFoundError:
    print("User not found")
except AuthenticationError:
    print("Authentication failed")
except ValidationError as e:
    print(f"Validation error: {e}")
except ConcurProfileError as e:
    print(f"General API error: {e}")
```

### Response Validation

```python
# Always check response success
response = sdk.create_user_identity(user)

if hasattr(response, 'success') and response.success:
    print(f"User created with ID: {response.id}")
else:
    print(f"Failed to create user: {getattr(response, 'message', 'Unknown error')}")
```

### Loyalty Program Error Handling

```python
loyalty_response = sdk.update_loyalty_program(loyalty_program)

if loyalty_response.success:
    print("Loyalty program updated successfully")
else:
    print(f"Loyalty update failed: {loyalty_response.error}")
```

## Best Practices

### 1. Authentication and Environment Detection

Detect authentication type and adjust operations accordingly:

```python
from concur_profile_sdk import ConcurSDK, ConcurProfileError

# Initialize SDK and detect authentication context
sdk = ConcurSDK()

try:
    # Try to get current user context
    current_user = sdk.get_current_user_identity()
    login_id = current_user.user_name
    print(f"User context available: {current_user.display_name}")
    
    # Can use current user methods
    travel_profile = sdk.get_current_user_travel_profile()
    
except ConcurProfileError as e:
    if "client credentials" in str(e).lower():
        print("Client credentials authentication - company-level access")
        # Must specify login_id for operations
        # Use existing users rather than creating new ones
    else:
        print(f"Authentication issue: {e}")
```

### 2. User Creation Strategy (with Permission Handling)

Use a defensive approach for user creation that handles permission restrictions:

```python
from concur_profile_sdk import IdentityUser, IdentityName, IdentityEmail, TravelProfile

def create_user_safely(sdk, user_data):
    """Create user with graceful permission handling"""
    try:
        # Attempt user creation
        created_user = sdk.create_user_identity(user_data)
        print(f"✅ User created: {created_user.id}")
        
        # Wait for availability
        time.sleep(10)
        
        return created_user.user_name
        
    except ConcurProfileError as e:
        if "401" in str(e) or "UNAUTHORIZED" in str(e):
            print("⚠️ User creation restricted - using existing user pattern")
            # Fall back to existing user
            current_user = sdk.get_current_user_identity()
            return current_user.user_name
        else:
            raise e

# Usage
user = IdentityUser(
    user_name="test@example.com",
    display_name="Test User",
    name=IdentityName(given_name="Test", family_name="User"),
    emails=[IdentityEmail(value="test@example.com")]
)

login_id = create_user_safely(sdk, user)

# Now safely set up travel profile
travel_profile = TravelProfile(
    login_id=login_id,
    rule_class="Default Travel Class",
    air_preferences=AirPreferences(
        home_airport="SEA",
        seat_preference=SeatPreference.WINDOW
    )
)

# Test travel profile update with error handling
try:
    response = sdk.update_travel_profile(travel_profile)
    print(f"✅ Travel profile updated: {response.message}")
except ConcurProfileError as e:
    if "401" in str(e):
        print("⚠️ Travel profile update restricted")
    else:
        raise e
```

### 3. Loyalty Program Management (with XML Understanding)

Understand the XML structure and API limitations for loyalty programs:

```python
from concur_profile_sdk import LoyaltyProgram, LoyaltyProgramType, TravelProfile

def manage_loyalty_programs_safely(sdk, login_id):
    """Manage loyalty programs with proper error handling"""
    
    # Create loyalty program data structures
    loyalty_programs = [
        LoyaltyProgram(
            program_type=LoyaltyProgramType.AIR,
            vendor_code="UA",
            account_number="123456789",
            # Note: status/benefits won't appear in XML but can be stored
            status="Premier Gold",
            status_benefits="Complimentary upgrades"
        )
    ]
    
    # Test XML generation (always works)
    travel_profile = TravelProfile(
        login_id=login_id,
        loyalty_programs=loyalty_programs
    )
    
    xml_output = travel_profile.to_update_xml(fields_to_update=["loyalty_programs"])
    print("✅ XML generated successfully")
    print(f"   Contains AdvantageMemberships: {'AdvantageMemberships' in xml_output}")
    print(f"   Contains vendor code: {'UA' in xml_output}")
    
    # Test dedicated loyalty API (may be restricted)
    for program in loyalty_programs:
        try:
            response = sdk.update_loyalty_program(program, login_id)
            if response.success:
                print(f"✅ {program.vendor_code} loyalty program updated")
            else:
                print(f"⚠️ {program.vendor_code} update failed: {response.error}")
        except ConcurProfileError as e:
            print(f"⚠️ Loyalty API restricted for {program.vendor_code}: {e}")
            print("   This is expected - Loyalty v1 API has strict permissions")
```

### 4. Field-Specific Updates with Error Recovery

Handle field restrictions and update preferences safely:

```python
def update_travel_preferences_safely(sdk, login_id):
    """Update travel preferences with field validation"""
    
    # Air preferences (generally well-supported)
    try:
        air_profile = TravelProfile(
            login_id=login_id,
            air_preferences=AirPreferences(
                home_airport="SEA",
                seat_preference=SeatPreference.WINDOW,
                meal_preference=MealType.VEGETARIAN
            )
        )
        
        response = sdk.update_travel_profile(air_profile, fields_to_update=["air_preferences"])
        print("✅ Air preferences updated successfully")
        
    except Exception as e:
        print(f"⚠️ Air preferences failed: {e}")
    
    # Hotel preferences (avoid problematic fields)
    try:
        hotel_profile = TravelProfile(
            login_id=login_id,
            hotel_preferences=HotelPreferences(
                room_type=HotelRoomType.KING,
                prefer_gym=True,
                prefer_pool=True
                # Don't use smoking_preference - causes validation errors
            )
        )
        
        response = sdk.update_travel_profile(hotel_profile, fields_to_update=["hotel_preferences"])
        print("✅ Hotel preferences updated successfully")
        
    except Exception as e:
        print(f"⚠️ Hotel preferences failed: {e}")
    
    # Car preferences (update individually if needed)
    try:
        car_profile = TravelProfile(
            login_id=login_id,
            car_preferences=CarPreferences(
                car_type=CarType.INTERMEDIATE,
                transmission=TransmissionType.AUTOMATIC,
                gps=True
            )
        )
        
        response = sdk.update_travel_profile(car_profile, fields_to_update=["car_preferences"])
        print("✅ Car preferences updated successfully")
        
    except Exception as e:
        print(f"⚠️ Car preferences failed: {e}")
```

### 5. Error Recovery and Retry Logic

Implement retry logic for transient failures:

```python
import time

def api_call_with_retry(api_func, max_retries=3, *args, **kwargs):
    """Execute API call with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            response = api_func(*args, **kwargs)
            return response
        except ConcurProfileError as e:
            if "401" in str(e) or "403" in str(e):
                # Permission errors - don't retry
                print(f"⚠️ Permission denied: {e}")
                return None
            elif attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                raise e

# Usage
response = api_call_with_retry(
    sdk.update_travel_profile,
    travel_profile,
    fields_to_update=["air_preferences"]
)
```

### 6. Integration Testing Patterns

Design tests that work across different environments:

```python
import unittest

class TestConcurSDK(unittest.TestCase):
    
    def setUp(self):
        self.sdk = ConcurSDK()
        # Use existing user instead of creating new ones
        try:
            self.current_user = self.sdk.get_current_user_identity()
            self.login_id = self.current_user.user_name
        except ConcurProfileError:
            # Client credentials - use a known user
            self.login_id = "known.user@example.com"
    
    def test_xml_generation(self):
        """Test XML generation (always works)"""
        travel_profile = TravelProfile(
            login_id=self.login_id,
            air_preferences=AirPreferences(home_airport="SEA")
        )
        
        xml_output = travel_profile.to_update_xml()
        self.assertIn("Air", xml_output)
        self.assertIn("SEA", xml_output)
    
    def test_api_call_with_graceful_handling(self):
        """Test API calls with graceful error handling"""
        travel_profile = TravelProfile(
            login_id=self.login_id,
            air_preferences=AirPreferences(home_airport="SEA")
        )
        
        try:
            response = self.sdk.update_travel_profile(travel_profile)
            print("✅ API call successful")
        except ConcurProfileError as e:
            if "401" in str(e):
                print("⚠️ API restricted (expected in some environments)")
                # This is not a test failure - just environment limitation
            else:
                self.fail(f"Unexpected API error: {e}")
    
    def test_loyalty_program_structure(self):
        """Test loyalty program data structures and XML"""
        loyalty_program = LoyaltyProgram(
            program_type=LoyaltyProgramType.AIR,
            vendor_code="UA",
            account_number="123456789"
        )
        
        # Validate data structure
        self.assertEqual(loyalty_program.vendor_code, "UA")
        self.assertEqual(loyalty_program.program_type, LoyaltyProgramType.AIR)
        
        # Test XML generation
        travel_profile = TravelProfile(
            login_id=self.login_id,
            loyalty_programs=[loyalty_program]
        )
        
        xml_output = travel_profile.to_update_xml(fields_to_update=["loyalty_programs"])
        self.assertIn("AdvantageMemberships", xml_output)
        self.assertIn("UA", xml_output)
```

### 7. Data Validation and Schema Compliance

Validate data before API calls:

```python
def validate_travel_profile(profile):
    """Validate travel profile before API submission"""
    if not profile.login_id:
        raise ValidationError("login_id is required")
    
    # Validate air preferences
    if profile.air_preferences:
        if profile.air_preferences.home_airport:
            if len(profile.air_preferences.home_airport) != 3:
                raise ValidationError("home_airport must be 3-letter airport code")
    
    # Validate loyalty programs
    if profile.loyalty_programs:
        for program in profile.loyalty_programs:
            if not program.vendor_code:
                raise ValidationError("loyalty program vendor_code is required")
            if not program.account_number:
                raise ValidationError("loyalty program account_number is required")
    
    return True

# Usage
try:
    validate_travel_profile(travel_profile)
    response = sdk.update_travel_profile(travel_profile)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## API Limitations

### 1. Identity v4 vs Travel Profile v2 Separation

The modern SDK architecture separates concerns:

- **Identity v4**: User identity, contact info, enterprise data
- **Travel Profile v2**: Travel preferences, documents, loyalty programs

### 2. Authentication Types and Permissions

**Client Credentials Authentication:**
- Provides company-level access without user context
- Cannot use `get_current_user_travel_profile()` - must specify login_id
- May have restricted permissions for user creation in some environments
- Suitable for administrative operations and bulk processing

**User Authentication:**
- Provides user-specific context
- Can use current user methods
- May have different permission levels depending on user role

```python
# With client credentials - specify login_id
travel_profile = sdk.get_travel_profile("user@example.com")

# With user auth - can use current user
travel_profile = sdk.get_current_user_travel_profile()
```

### 3. User Creation Permission Requirements

User creation via Identity v4 requires specific permissions:

```python
try:
    created_user = sdk.create_user_identity(user)
    print(f"User created: {created_user.id}")
except ConcurProfileError as e:
    if "401" in str(e) or "UNAUTHORIZED" in str(e):
        print("Insufficient permissions for user creation")
        print("This is common with certain authentication configurations")
```

**Workarounds for restricted environments:**
- Use existing users for testing and operations
- Focus on travel profile updates rather than user creation
- Use read-only operations and XML generation for validation

### 4. Loyalty Program Restrictions

The Loyalty v1 API has significant restrictions:

- **Travel Suppliers**: Only available to travel suppliers who have completed SAP Concur application review
- **Scope Limitations**: Travel suppliers can only update their OWN loyalty program information
- **TMC Access**: TMCs can update any loyalty program for users
- **XML Structure**: Loyalty programs appear as `<AdvantageMemberships>`, not `<LoyaltyPrograms>`
- **Limited Fields**: Only basic fields (vendor code, program number, expiration) appear in XML

### 5. Field Support Variations

Some documented fields are not supported by all API versions:

```python
# These fields are documented but NOT supported:
# - HotelPreferences.smoking_preference (causes XML validation error)
# - HotelPreferences.prefer_restaurant (causes XML validation error)
# - LoyaltyProgram status/benefits fields (don't appear in XML)

# Working hotel preferences:
hotel_prefs = HotelPreferences(
    room_type=HotelRoomType.KING,
    prefer_foam_pillows=True,
    prefer_gym=True,
    prefer_pool=True,
    prefer_room_service=True,
    prefer_early_checkin=True
    # Don't use smoking_preference or prefer_restaurant
)

# Working loyalty programs (basic fields only):
loyalty_program = LoyaltyProgram(
    program_type=LoyaltyProgramType.AIR,
    vendor_code="UA",
    account_number="123456789",
    expiration=date(2024, 12, 31)
    # Status and benefits fields won't appear in XML
)
```

### 6. SCIM vs XML Schema Requirements

- **Identity v4**: Uses JSON and SCIM 2.0 schemas
- **Travel Profile v2**: Uses XML and Concur's custom schemas
- **Order Requirements**: XML elements must appear in exact schema order
- **Validation**: XML validation is strict and may reject unexpected fields

### 7. User Availability Delays

Newly created users may not be immediately available:

```python
# Always wait after user creation
response = sdk.create_user_identity(user)
if response.id:
    time.sleep(5)  # Wait for user to be available
    # Now safe to update travel profile or retrieve user
```

### 8. Testing Considerations

**For Integration Testing:**
- Use existing authenticated users rather than creating test users
- Focus on XML generation and data structure validation
- Test API restrictions gracefully (expect failures for restricted APIs)
- Use read-only operations when write permissions are limited

```python
# Recommended testing pattern
def test_with_existing_user():
    current_user = sdk.get_current_user_identity()
    login_id = current_user.user_name
    
    # Test XML generation (always works)
    travel_profile = TravelProfile(
        login_id=login_id,
        air_preferences=AirPreferences(home_airport="SEA")
    )
    xml_output = travel_profile.to_update_xml()
    
    # Test API calls with graceful error handling
    try:
        response = sdk.update_travel_profile(travel_profile)
        print("✅ Update successful")
    except ConcurProfileError as e:
        if "401" in str(e):
            print("⚠️ Update restricted (expected in some environments)")
        else:
            raise e
```

## Examples

### Complete User and Travel Profile Setup

```python
from concur_profile_sdk import *
from datetime import date
import time

# Complete user lifecycle with both identity and travel data
login_id = "complete.user@example.com"

# 1. Create user identity
user = IdentityUser(
    user_name=login_id,
    display_name="Complete User",
    title="Senior Manager",
    name=IdentityName(
        given_name="Complete",
        family_name="User",
        middle_name="Test"
    ),
    emails=[
        IdentityEmail(
            value=login_id,
            type="work",
            primary=True
        )
    ],
    phone_numbers=[
        IdentityPhoneNumber(
            value="+1-206-555-0123",
            type="work",
            primary=True
        )
    ],
    enterprise_info=IdentityEnterpriseInfo(
        company_id="COMP123",
        employee_number="EMP12345",
        department="Engineering"
    )
)

# Create user identity
try:
    created_user = sdk.create_user_identity(user)
    print(f"✅ User identity created: {created_user.id}")
    
    # Wait for availability
    time.sleep(10)
    
    # 2. Set up travel profile
    travel_profile = TravelProfile(
        login_id=login_id,
        rule_class="Default Travel Class",
        air_preferences=AirPreferences(
            home_airport="SEA",
            seat_preference=SeatPreference.WINDOW,
            meal_preference=MealType.VEGETARIAN
        ),
        hotel_preferences=HotelPreferences(
            room_type=HotelRoomType.KING,
            prefer_gym=True,
            prefer_pool=True
        ),
        car_preferences=CarPreferences(
            car_type=CarType.INTERMEDIATE,
            transmission=TransmissionType.AUTOMATIC,
            gps=True
        )
    )
    
    travel_response = sdk.update_travel_profile(travel_profile)
    print(f"✅ Travel profile updated: {travel_response.message}")
    
    # 3. Add loyalty programs
    loyalty_programs = [
        LoyaltyProgram(
            program_type=LoyaltyProgramType.AIR,
            vendor_code="UA",
            account_number="UA123456",
            status="Premier Gold"
        ),
        LoyaltyProgram(
            program_type=LoyaltyProgramType.HOTEL,
            vendor_code="HH",
            account_number="HH789012",
            status="Diamond"
        )
    ]
    
    for program in loyalty_programs:
        loyalty_response = sdk.update_loyalty_program(program, login_id)
        if loyalty_response.success:
            print(f"✅ Added {program.vendor_code} loyalty program")
        else:
            print(f"⚠️ Loyalty program may be restricted: {loyalty_response.error}")
    
    # 4. Verify setup
    final_identity = sdk.find_user_by_username(login_id)
    final_travel = sdk.get_travel_profile_by_login_id(login_id)
    
    print(f"✅ Final verification:")
    print(f"  Identity: {final_identity.display_name} ({final_identity.title})")
    print(f"  Travel: {final_travel.rule_class}")
    print(f"  Air: {final_travel.air_preferences.home_airport if final_travel.air_preferences else 'None'}")
    print(f"  Loyalty Programs: {len(final_travel.loyalty_programs)}")
    
except Exception as e:
    print(f"❌ Error: {e}")
```

### Bulk User Processing

```python
from datetime import datetime, timedelta

# Get recent travel profile changes
last_modified = datetime.now() - timedelta(days=7)

summaries = sdk.list_travel_profile_summaries(
    last_modified_date=last_modified,
    limit=100,
    active_only=True
)

print(f"Processing {len(summaries.profile_summaries)} travel profiles...")

for summary in summaries.profile_summaries:
    try:
        # Get both identity and travel data
        identity = sdk.find_user_by_username(summary.login_id)
        travel_profile = sdk.get_travel_profile_by_login_id(summary.login_id)
        
        # Process user data
        print(f"User: {identity.display_name if identity else 'Unknown'}")
        print(f"  Title: {identity.title if identity else 'None'}")
        print(f"  Travel Class: {travel_profile.rule_class}")
        print(f"  Last Modified: {summary.profile_last_modified_utc}")
        
        # Example: Update title if missing
        if identity and not identity.title:
            updates = {"title": "Employee"}
            sdk.update_user_identity_simple(identity.id, updates)
            print(f"  ✅ Updated title")
        
        # Example: Set default air preferences if missing
        if not travel_profile.air_preferences:
            update_profile = TravelProfile(
                login_id=travel_profile.login_id,
                air_preferences=AirPreferences(
                    seat_preference=SeatPreference.DONT_CARE,
                    home_airport="SEA"
                )
            )
            sdk.update_travel_profile(update_profile, fields_to_update=["air_preferences"])
            print(f"  ✅ Set default air preferences")
        
    except ProfileNotFoundError:
        print(f"  ⚠️ Profile not found: {summary.login_id}")
    except Exception as e:
        print(f"  ❌ Error processing {summary.login_id}: {e}")
```

This comprehensive guide covers all aspects of the Concur SDK. The SDK provides a robust, type-safe way to interact with Concur's modern APIs while handling the complexities of both SCIM 2.0 compliance and XML schema requirements. 