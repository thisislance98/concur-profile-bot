# Concur Profile SDK - Comprehensive Guide

## Table of Contents

1. [Overview](#overview)
2. [Installation and Setup](#installation-and-setup)
3. [Authentication](#authentication)
4. [Core Concepts](#core-concepts)
5. [Basic Operations](#basic-operations)
6. [Profile Management](#profile-management)
7. [Contact Information](#contact-information)
8. [Identity Documents](#identity-documents)
9. [Travel Preferences](#travel-preferences)
10. [Loyalty Programs](#loyalty-programs)
11. [Advanced Features](#advanced-features)
12. [Error Handling](#error-handling)
13. [Best Practices](#best-practices)
14. [API Limitations](#api-limitations)
15. [Examples](#examples)

## Overview

The Concur Profile SDK is a comprehensive Python library for interacting with SAP Concur's Profile APIs. It provides strongly-typed, object-oriented access to all Profile v2 and Loyalty Program v1 functionality, including:

- **Complete CRUD operations** on user profiles
- **Full profile schema** with all available fields
- **Travel preferences** (Air, Hotel, Car, Rail)
- **Loyalty program management**
- **Profile summary listing** with pagination
- **Advanced features** like TSA info, custom fields, emergency contacts
- **Comprehensive error handling** and validation

### Key Features

- **Strongly Typed**: Uses Python dataclasses and enums for type safety
- **XML Handling**: Built with lxml for robust XML processing
- **Schema Compliant**: Follows Concur's XSD schema requirements exactly
- **Production Ready**: Includes comprehensive error handling and logging
- **Well Tested**: Extensive integration test suite

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
CONCUR_TRAVEL_CONFIG_ID=your_travel_config_id
```

### Basic Initialization

```python
from concur_profile_sdk_improved import ConcurProfileSDK

sdk = ConcurProfileSDK(
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
profile = sdk.get_current_user_profile()
print(f"Authenticated as: {profile.first_name} {profile.last_name}")
```

### Authentication Features

- **Automatic token refresh** when tokens expire
- **Error handling** for authentication failures
- **Token caching** for performance

## Core Concepts

### UserProfile Class

The `UserProfile` class is the central data structure containing all user information:

```python
from concur_profile_sdk_improved import UserProfile

profile = UserProfile(
    login_id="user@example.com",
    first_name="John",
    last_name="Doe",
    travel_config_id="your-config-id"
)
```

### Enums for Type Safety

The SDK uses enums for all constrained values:

```python
from concur_profile_sdk_improved import (
    AddressType, PhoneType, EmailType, 
    SeatPreference, MealType, CarType
)

# Type-safe enum usage
address_type = AddressType.HOME
seat_pref = SeatPreference.WINDOW
meal_pref = MealType.VEGETARIAN
```

### Data Classes

All complex data is represented by dataclasses:

```python
from concur_profile_sdk_improved import Address, Phone, Email

address = Address(
    type=AddressType.HOME,
    street="123 Main St",
    city="Seattle",
    state_province="WA",
    postal_code="98101",
    country_code="US"
)
```

## Basic Operations

### Get Current User Profile

```python
# Get complete profile of authenticated user
profile = sdk.get_current_user_profile()

print(f"Name: {profile.first_name} {profile.last_name}")
print(f"Company: {profile.company_name}")
print(f"Job Title: {profile.job_title}")
print(f"Addresses: {len(profile.addresses)}")
print(f"Loyalty Programs: {len(profile.loyalty_programs)}")
```

### Get Profile by Login ID

```python
try:
    profile = sdk.get_profile_by_login_id("user@example.com")
    print(f"Found user: {profile.first_name} {profile.last_name}")
except ProfileNotFoundError:
    print("User not found")
```

### List Profile Summaries

```python
from datetime import datetime, timedelta

# Get profiles modified in last 30 days
last_modified = datetime.now() - timedelta(days=30)

summaries = sdk.list_profile_summaries(
    last_modified_date=last_modified,
    page=1,
    limit=50,
    active_only=True
)

print(f"Found {len(summaries.profile_summaries)} profiles")
for summary in summaries.profile_summaries:
    print(f"  {summary.login_id} - {summary.status.value}")
```

## Profile Management

### Creating Users

#### Basic User Creation

```python
from concur_profile_sdk_improved import UserProfile

profile = UserProfile(
    login_id="newuser@example.com",
    first_name="Jane",
    last_name="Smith", 
    travel_config_id="your-travel-config-id"
)

response = sdk.create_user(profile, password="SecurePass123!")
print(f"Created user with UUID: {response.uuid}")
```

#### Comprehensive User Creation

```python
from concur_profile_sdk_improved import (
    UserProfile, Address, Phone, Email, EmergencyContact,
    AddressType, PhoneType, EmailType
)

# Create user with full contact information
profile = UserProfile(
    login_id="comprehensive@example.com",
    first_name="John",
    last_name="Comprehensive",
    middle_name="Middle",
    job_title="Senior Manager",
    company_name="Example Corp",
    employee_id="EMP12345",
    travel_config_id="your-travel-config-id",
    
    # Contact information
    addresses=[
        Address(
            type=AddressType.HOME,
            street="123 Home Street",
            city="Seattle",
            state_province="WA", 
            postal_code="98101",
            country_code="US"
        ),
        Address(
            type=AddressType.WORK,
            street="456 Work Avenue",
            city="Seattle",
            state_province="WA",
            postal_code="98102", 
            country_code="US"
        )
    ],
    
    phones=[
        Phone(
            type=PhoneType.HOME,
            phone_number="206-555-0123",
            country_code="1"
        ),
        Phone(
            type=PhoneType.WORK,
            phone_number="206-555-0124",
            country_code="1"
        )
    ],
    
    emails=[
        Email(
            type=EmailType.BUSINESS,
            email_address="john.work@example.com"
        ),
        Email(
            type=EmailType.PERSONAL,
            email_address="john.personal@example.com"
        )
    ],
    
    emergency_contacts=[
        EmergencyContact(
            name="Jane Doe",
            relationship="Spouse",
            phone="206-555-0125"
        )
    ]
)

response = sdk.create_user(profile, password="SecurePass123!")
```

### Updating Users

#### Update Specific Fields

```python
# Update only job title and company
profile = UserProfile(
    login_id="user@example.com",
    job_title="Senior Director",
    company_name="New Company Inc"
)

response = sdk.update_user(
    profile, 
    fields_to_update=["job_title", "company_name"]
)
```

#### Update All Non-Empty Fields

```python
# Update all fields that have values
profile = UserProfile(
    login_id="user@example.com",
    first_name="Updated",
    last_name="Name",
    job_title="New Title"
)

response = sdk.update_user(profile)  # Updates all non-empty fields
```

## Contact Information

### Addresses

```python
from concur_profile_sdk_improved import Address, AddressType

addresses = [
    Address(
        type=AddressType.HOME,
        street="123 Main Street",
        city="Seattle", 
        state_province="WA",
        postal_code="98101",
        country_code="US"
    ),
    Address(
        type=AddressType.WORK,
        street="456 Business Ave",
        city="Bellevue",
        state_province="WA", 
        postal_code="98004",
        country_code="US"
    )
]

profile = UserProfile(
    login_id="user@example.com",
    addresses=addresses
)

sdk.update_user(profile, fields_to_update=["addresses"])
```

### Phone Numbers

```python
from concur_profile_sdk_improved import Phone, PhoneType

phones = [
    Phone(
        type=PhoneType.HOME,
        phone_number="206-555-0123",
        country_code="1"
    ),
    Phone(
        type=PhoneType.WORK,
        phone_number="206-555-0124", 
        country_code="1",
        extension="1234"
    ),
    Phone(
        type=PhoneType.CELL,
        phone_number="206-555-0125",
        country_code="1"
    )
]

profile = UserProfile(
    login_id="user@example.com",
    phones=phones
)

sdk.update_user(profile, fields_to_update=["phones"])
```

### Email Addresses

```python
from concur_profile_sdk_improved import Email, EmailType

emails = [
    Email(
        type=EmailType.BUSINESS,
        email_address="john.work@example.com"
    ),
    Email(
        type=EmailType.PERSONAL,
        email_address="john.personal@gmail.com"
    ),
    Email(
        type=EmailType.SUPERVISOR,
        email_address="supervisor@example.com"
    )
]

profile = UserProfile(
    login_id="user@example.com",
    emails=emails
)

sdk.update_user(profile, fields_to_update=["emails"])
```

### Emergency Contacts

```python
from concur_profile_sdk_improved import EmergencyContact

emergency_contacts = [
    EmergencyContact(
        name="Jane Doe",
        relationship="Spouse",
        phone="206-555-0125",
        mobile_phone="206-555-0126",
        email="jane@example.com"
    ),
    EmergencyContact(
        name="Bob Smith",
        relationship="Parent",
        phone="206-555-0127"
    )
]

profile = UserProfile(
    login_id="user@example.com",
    emergency_contacts=emergency_contacts
)

sdk.update_user(profile, fields_to_update=["emergency_contacts"])
```

## Identity Documents

### Passports

```python
from concur_profile_sdk_improved import Passport
from datetime import date

passports = [
    Passport(
        doc_number="123456789",
        nationality="US",
        issue_country="US",
        issue_date=date(2020, 1, 15),
        expiration_date=date(2030, 1, 15),
        primary=True
    )
]

profile = UserProfile(
    login_id="user@example.com",
    passports=passports
)

sdk.update_user(profile, fields_to_update=["passports"])
```

### Visas

```python
from concur_profile_sdk_improved import Visa, VisaType
from datetime import date

visas = [
    Visa(
        visa_nationality="US",
        visa_number="V123456789",
        visa_type=VisaType.MULTI_ENTRY,
        visa_country_issued="GB",
        visa_date_issued=date(2023, 6, 1),
        visa_expiration=date(2025, 6, 1)
    )
]

profile = UserProfile(
    login_id="user@example.com", 
    visas=visas
)

sdk.update_user(profile, fields_to_update=["visas"])
```

### National IDs and Driver's Licenses

```python
from concur_profile_sdk_improved import NationalID, DriversLicense

# National IDs
national_ids = [
    NationalID(
        id_number="123-45-6789",
        country_code="US"
    )
]

# Driver's Licenses
drivers_licenses = [
    DriversLicense(
        license_number="D123456789",
        country_code="US",
        state_province="WA"
    )
]

profile = UserProfile(
    login_id="user@example.com",
    national_ids=national_ids,
    drivers_licenses=drivers_licenses
)

sdk.update_user(profile, fields_to_update=["national_ids", "drivers_licenses"])
```

### TSA Information

```python
from concur_profile_sdk_improved import TSAInfo
from datetime import date

tsa_info = TSAInfo(
    known_traveler_number="12345678901",
    gender="Male",
    date_of_birth=date(1985, 6, 15),
    redress_number="987654321",
    no_middle_name=False
)

profile = UserProfile(
    login_id="user@example.com",
    tsa_info=tsa_info
)

sdk.update_user(profile, fields_to_update=["tsa_info"])
```

## Travel Preferences

### Air Travel Preferences

```python
from concur_profile_sdk_improved import (
    AirPreferences, SeatPreference, SeatSection, MealType
)

air_preferences = AirPreferences(
    seat_preference=SeatPreference.WINDOW,
    seat_section=SeatSection.FORWARD,
    meal_preference=MealType.VEGETARIAN,
    home_airport="SEA",
    air_other="Prefer early morning flights"
)

profile = UserProfile(
    login_id="user@example.com",
    air_preferences=air_preferences
)

sdk.update_user(profile, fields_to_update=["air_preferences"])
```

### Hotel Preferences

```python
from concur_profile_sdk_improved import (
    HotelPreferences, HotelRoomType, SmokingPreference
)

hotel_preferences = HotelPreferences(
    room_type=HotelRoomType.KING,
    hotel_other="Late checkout preferred",
    prefer_foam_pillows=True,
    prefer_gym=True,
    prefer_pool=True,
    prefer_room_service=True,
    prefer_early_checkin=True
)

profile = UserProfile(
    login_id="user@example.com",
    hotel_preferences=hotel_preferences
)

sdk.update_user(profile, fields_to_update=["hotel_preferences"])
```

### Car Rental Preferences

```python
from concur_profile_sdk_improved import (
    CarPreferences, CarType, TransmissionType, SmokingPreference
)

car_preferences = CarPreferences(
    car_type=CarType.INTERMEDIATE,
    transmission=TransmissionType.AUTOMATIC,
    smoking_preference=SmokingPreference.NON_SMOKING,
    gps=True,
    ski_rack=False
)

profile = UserProfile(
    login_id="user@example.com",
    car_preferences=car_preferences
)

# Note: Car preferences should be updated individually
# The SDK handles this automatically
sdk.update_user(profile, fields_to_update=["car_preferences"])
```

### Rail Travel Preferences

```python
from concur_profile_sdk_improved import RailPreferences

rail_preferences = RailPreferences(
    seat="Window",
    coach="First Class",
    noise_comfort="Quiet",
    bed="Upper",
    special_meals="Vegetarian"
)

profile = UserProfile(
    login_id="user@example.com",
    rail_preferences=rail_preferences
)

sdk.update_user(profile, fields_to_update=["rail_preferences"])
```

### Rate Preferences and Discount Codes

```python
from concur_profile_sdk_improved import RatePreference, DiscountCode

rate_preferences = RatePreference(
    aaa_rate=True,
    aarp_rate=False,
    govt_rate=True,
    military_rate=False
)

discount_codes = [
    DiscountCode(vendor="HZ", code="CDP123456"),
    DiscountCode(vendor="AV", code="AWD987654")
]

profile = UserProfile(
    login_id="user@example.com",
    rate_preferences=rate_preferences,
    discount_codes=discount_codes
)

sdk.update_user(profile, fields_to_update=["rate_preferences", "discount_codes"])
```

## Loyalty Programs

### Using the Dedicated Loyalty API

The SDK provides a dedicated Loyalty v1 API for managing loyalty programs:

```python
from concur_profile_sdk_improved import LoyaltyProgram, LoyaltyProgramType

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

## Advanced Features

### Custom Fields

```python
from concur_profile_sdk_improved import CustomField

custom_fields = [
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

profile = UserProfile(
    login_id="user@example.com",
    custom_fields=custom_fields
)

sdk.update_user(profile, fields_to_update=["custom_fields"])
```

### Unused Tickets

```python
from concur_profile_sdk_improved import UnusedTicket

unused_tickets = [
    UnusedTicket(
        ticket_number="1234567890123",
        airline_code="UA",
        amount="500.00",
        currency="USD"
    )
]

profile = UserProfile(
    login_id="user@example.com",
    unused_tickets=unused_tickets
)

sdk.update_user(profile, fields_to_update=["unused_tickets"])
```

## Error Handling

### Exception Types

The SDK provides specific exception types for different error conditions:

```python
from concur_profile_sdk_improved import (
    ConcurProfileError,
    AuthenticationError,
    ProfileNotFoundError,
    ValidationError
)

try:
    profile = sdk.get_profile_by_login_id("nonexistent@example.com")
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
response = sdk.create_user(profile)

if response.success:
    print(f"User created with UUID: {response.uuid}")
else:
    print(f"Failed to create user: {response.message}")
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

### 1. User Creation Strategy

Use a two-step approach for comprehensive user creation:

```python
# Step 1: Create user with minimal required fields
basic_profile = UserProfile(
    login_id="user@example.com",
    first_name="John",
    last_name="Doe",
    travel_config_id="your-config-id"
)

response = sdk.create_user(basic_profile)

# Step 2: Update with additional fields after creation
if response.success:
    # Wait for user to be available
    time.sleep(5)
    
    # Update with additional fields
    full_profile = UserProfile(
        login_id="user@example.com",
        job_title="Manager",
        company_name="Example Corp",
        addresses=[...],
        phones=[...]
    )
    
    sdk.update_user(full_profile)
```

### 2. Field-Specific Updates

Update sensitive fields individually:

```python
# Update car preferences one field at a time
car_type_profile = UserProfile(
    login_id="user@example.com",
    car_preferences=CarPreferences(car_type=CarType.INTERMEDIATE)
)
sdk.update_user(car_type_profile, fields_to_update=["car_preferences"])

time.sleep(2)  # Allow processing time

transmission_profile = UserProfile(
    login_id="user@example.com", 
    car_preferences=CarPreferences(transmission=TransmissionType.AUTOMATIC)
)
sdk.update_user(transmission_profile, fields_to_update=["car_preferences"])
```

### 3. Loyalty Program Management

Use the dedicated Loyalty API for loyalty programs:

```python
# Don't include loyalty programs in profile updates
# Use the dedicated API instead
loyalty_program = LoyaltyProgram(
    program_type=LoyaltyProgramType.AIR,
    vendor_code="UA",
    account_number="123456789"
)

response = sdk.update_loyalty_program(loyalty_program)
```

### 4. Error Recovery

Implement retry logic for transient failures:

```python
import time

def create_user_with_retry(profile, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = sdk.create_user(profile)
            return response
        except ConcurProfileError as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise e
```

### 5. Data Validation

Validate data before API calls:

```python
def validate_profile(profile):
    if not profile.login_id:
        raise ValidationError("login_id is required")
    if not profile.first_name:
        raise ValidationError("first_name is required")
    if not profile.last_name:
        raise ValidationError("last_name is required")
    if not profile.travel_config_id:
        raise ValidationError("travel_config_id is required")

# Use validation
try:
    validate_profile(profile)
    response = sdk.create_user(profile)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## API Limitations

### 1. Loyalty Program Restrictions

The Loyalty v1 API has significant restrictions:

- **Travel Suppliers**: Only available to travel suppliers who have completed SAP Concur application review
- **Scope Limitations**: Travel suppliers can only update their OWN loyalty program information
- **TMC Access**: TMCs can update any loyalty program for users

### 2. Field Support Variations

Some documented fields are not supported by all API versions:

```python
# These fields are documented but NOT supported:
# - HotelPreferences.smoking_preference (causes XML validation error)
# - HotelPreferences.prefer_restaurant (causes XML validation error)
# - CarPreferences fields may need individual updates

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
```

### 3. Schema Order Requirements

XML elements must appear in exact schema order:

```python
# The SDK handles this automatically, but be aware that
# field order matters in XML generation
```

### 4. User Availability Delays

Newly created users may not be immediately available:

```python
# Always wait after user creation
response = sdk.create_user(profile)
if response.success:
    time.sleep(5)  # Wait for user to be available
    # Now safe to update or retrieve user
```

## Examples

### Complete User Lifecycle

```python
from concur_profile_sdk_improved import *
from datetime import date
import time

# 1. Create comprehensive user
login_id = "complete.user@example.com"

profile = UserProfile(
    login_id=login_id,
    first_name="Complete",
    last_name="User",
    middle_name="Test",
    job_title="Senior Manager",
    company_name="Example Corporation",
    employee_id="EMP12345",
    travel_config_id="your-travel-config-id",
    
    # Contact information
    addresses=[
        Address(
            type=AddressType.HOME,
            street="123 Home Street",
            city="Seattle",
            state_province="WA",
            postal_code="98101",
            country_code="US"
        )
    ],
    
    phones=[
        Phone(
            type=PhoneType.WORK,
            phone_number="206-555-0123",
            country_code="1"
        )
    ],
    
    emails=[
        Email(
            type=EmailType.BUSINESS,
            email_address="complete.work@example.com"
        )
    ],
    
    # Emergency contact
    emergency_contacts=[
        EmergencyContact(
            name="Emergency Contact",
            relationship="Spouse",
            phone="206-555-0124"
        )
    ],
    
    # Travel preferences
    air_preferences=AirPreferences(
        seat_preference=SeatPreference.WINDOW,
        meal_preference=MealType.VEGETARIAN,
        home_airport="SEA"
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

# Create user
try:
    response = sdk.create_user(profile, password="SecurePass123!")
    print(f"✅ User created: {response.uuid}")
    
    # Wait for availability
    time.sleep(10)
    
    # 2. Verify creation
    created_profile = sdk.get_profile_by_login_id(login_id)
    print(f"✅ User verified: {created_profile.first_name} {created_profile.last_name}")
    
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
    
    # 4. Update profile
    updated_profile = UserProfile(
        login_id=login_id,
        job_title="Director",
        medical_alerts="No known allergies"
    )
    
    update_response = sdk.update_user(updated_profile, fields_to_update=["job_title", "medical_alerts"])
    print(f"✅ Profile updated: {update_response.message}")
    
    # 5. Final verification
    final_profile = sdk.get_profile_by_login_id(login_id)
    print(f"✅ Final verification: {final_profile.job_title}")
    
except Exception as e:
    print(f"❌ Error: {e}")
```

### Bulk Profile Processing

```python
from datetime import datetime, timedelta

# Get recent profile changes
last_modified = datetime.now() - timedelta(days=7)

summaries = sdk.list_profile_summaries(
    last_modified_date=last_modified,
    limit=100,
    active_only=True
)

print(f"Processing {len(summaries.profile_summaries)} profiles...")

for summary in summaries.profile_summaries:
    try:
        # Get full profile
        profile = sdk.get_profile_by_login_id(summary.login_id)
        
        # Process profile data
        print(f"Profile: {profile.first_name} {profile.last_name}")
        print(f"  Company: {profile.company_name}")
        print(f"  Loyalty Programs: {len(profile.loyalty_programs)}")
        print(f"  Last Modified: {summary.profile_last_modified_utc}")
        
        # Example: Update job title if missing
        if not profile.job_title and profile.company_name:
            update_profile = UserProfile(
                login_id=profile.login_id,
                job_title="Employee"
            )
            sdk.update_user(update_profile, fields_to_update=["job_title"])
            print(f"  ✅ Updated job title")
        
    except ProfileNotFoundError:
        print(f"  ⚠️ Profile not found: {summary.login_id}")
    except Exception as e:
        print(f"  ❌ Error processing {summary.login_id}: {e}")
```

This comprehensive guide covers all aspects of the Concur Profile SDK. The SDK provides a robust, type-safe way to interact with Concur's Profile APIs while handling the complexities of XML schema compliance and API limitations. 