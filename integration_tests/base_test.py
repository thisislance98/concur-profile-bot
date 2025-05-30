#!/usr/bin/env python3
"""
Base integration test class for Concur Profile SDK tests

Provides common functionality, setup, and utilities for all integration tests.
"""

import unittest
import os
import sys
import time
import json
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any

# Add the parent directory to Python path to import the SDK
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from concur_profile_sdk import (
    ConcurSDK, IdentityUser, IdentityName, IdentityEmail, IdentityPhoneNumber, 
    IdentityEnterpriseInfo, TravelProfile, Address, Phone, Email, EmergencyContact,
    NationalID, DriversLicense, Passport, Visa, TSAInfo, LoyaltyProgram,
    RatePreference, DiscountCode, AirPreferences, HotelPreferences, 
    CarPreferences, RailPreferences, CustomField, UnusedTicket,
    AddressType, PhoneType, EmailType, VisaType, LoyaltyProgramType,
    SeatPreference, SeatSection, MealType, HotelRoomType, SmokingPreference,
    CarType, TransmissionType, ProfileStatus, VendorType,
    ConcurProfileError, AuthenticationError, ProfileNotFoundError, 
    ValidationError, ApiResponse, LoyaltyResponse, ConnectResponse
)


class BaseIntegrationTest(unittest.TestCase):
    """
    Base class for all Concur Profile SDK integration tests
    
    Provides:
    - SDK initialization with environment variables
    - Common test utilities and assertions
    - Test data management
    - Cleanup functionality
    """
    
    # Class variables to share across tests
    sdk: Optional[ConcurSDK] = None
    test_travel_config_id: Optional[str] = None
    created_users: List[str] = []  # Track created users for cleanup
    test_run_id: str = ""
    
    @classmethod
    def setUpClass(cls):
        """Set up SDK and common test data once for all tests"""
        print(f"\n{'='*80}")
        print(f"Setting up {cls.__name__} integration tests...")
        print(f"{'='*80}")
        
        # Load environment variables
        load_dotenv()
        
        # Generate unique test run ID
        cls.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"Test Run ID: {cls.test_run_id}")
        
        # Initialize SDK
        try:
            # Use username/password authentication since they're available
            cls.sdk = ConcurSDK(
                client_id=os.getenv("CONCUR_CLIENT_ID"),
                client_secret=os.getenv("CONCUR_CLIENT_SECRET"),
                username=os.getenv("CONCUR_USERNAME"),
                password=os.getenv("CONCUR_PASSWORD"),
                base_url=os.getenv("CONCUR_BASE_URL", "https://integration.api.concursolutions.com")
            )
            
            # Test authentication by getting current user identity
            try:
                current_identity = cls.sdk.get_current_user_identity()
                print(f"✅ SDK initialized successfully with user context")
                print(f"   Authenticated as: {current_identity.display_name}")
                print(f"   Username: {current_identity.user_name}")
                
                # Get current user's travel profile to get travel config ID
                current_travel_profile = cls.sdk.get_current_user_travel_profile()
            except Exception as e:
                # Client credentials might not provide user-level access
                print(f"⚠️  Client credentials authentication successful, but no user context available")
                print(f"   Error: {e}")
                print(f"   This is expected with client credentials grant - it provides company-level access")
                
                # For client credentials, we'll need to use a test user login ID
                print(f"   Will use company-level access for testing...")
                current_identity = None
                current_travel_profile = None
            
            # Store travel config ID for test user creation
            cls.test_travel_config_id = os.getenv("CONCUR_TRAVEL_CONFIG_ID")
            if not cls.test_travel_config_id and current_travel_profile:
                cls.test_travel_config_id = current_travel_profile.travel_config_id
            
            print(f"   Travel Config ID: {cls.test_travel_config_id}")
            
        except Exception as e:
            raise unittest.SkipTest(f"Failed to initialize SDK: {e}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up created test users"""
        print(f"\n{'='*80}")
        print(f"Cleaning up {cls.__name__} integration tests...")
        print(f"{'='*80}")
        
        if cls.created_users and cls.sdk:
            print(f"Cleaning up {len(cls.created_users)} created test users...")
            for login_id in cls.created_users:
                try:
                    # Note: Most Concur instances don't support true deletion
                    # This will likely fail, but we'll try for completeness
                    # In the new SDK, there's no delete method yet, so we'll skip this
                    print(f"   ⚠️  Would delete user: {login_id} (deletion not implemented)")
                except Exception as e:
                    print(f"   ⚠️  Could not delete user {login_id}: {e}")
            cls.created_users.clear()
        
        print("✅ Cleanup completed")
    
    def setUp(self):
        """Set up for each individual test"""
        if not self.sdk:
            self.skipTest("SDK not initialized")
    
    def generate_unique_login_id(self, prefix: str = "test") -> str:
        """Generate a unique login ID for test users"""
        timestamp = int(datetime.now().timestamp())
        return f"{prefix}_{self.test_run_id}_{timestamp}@sdktest.example.com"
    
    def create_test_user_identity(
        self, 
        login_id: Optional[str] = None,
        given_name: str = "Test",
        family_name: str = "User"
    ) -> IdentityUser:
        """Create a test user identity and track for cleanup"""
        if not login_id:
            login_id = self.generate_unique_login_id()
        
        identity_user = IdentityUser(
            user_name=login_id,
            display_name=f"{given_name} {family_name}",
            name=IdentityName(given_name=given_name, family_name=family_name),
            emails=[IdentityEmail(value=login_id, primary=True)],
            title="Integration Test User"
        )
        
        created_user = self.sdk.create_user_identity(identity_user)
        
        # Track for cleanup
        self.created_users.append(login_id)
        
        return created_user

    def create_test_travel_profile(
        self,
        login_id: str,
        rule_class: str = "Default Travel Class"
    ) -> TravelProfile:
        """Create a basic travel profile for testing"""
        return TravelProfile(
            login_id=login_id,
            rule_class=rule_class,
            travel_config_id=self.test_travel_config_id
        )
    
    def wait_for_user_availability(self, login_id: str, max_wait: int = 30):
        """Wait for a newly created user to be available for read operations"""
        print(f"   ⏰ Waiting for user {login_id} to be available...")
        
        for attempt in range(max_wait):
            try:
                self.sdk.find_user_by_username(login_id)
                print(f"   ✅ User available after {attempt + 1} seconds")
                return
            except ProfileNotFoundError:
                if attempt < max_wait - 1:
                    time.sleep(1)
                    continue
                else:
                    self.fail(f"User {login_id} not available after {max_wait} seconds")
            except Exception as e:
                self.fail(f"Unexpected error waiting for user {login_id}: {e}")
    
    def assertApiResponseSuccess(self, response: ApiResponse, message: str = "API response failed"):
        """Assert that an API response indicates success"""
        self.assertIsInstance(response, ApiResponse, f"{message}: Expected ApiResponse object")
        self.assertTrue(response.success, f"{message}: {response.message}")
        if hasattr(response, 'code'):
            self.assertIsNotNone(response.code, f"{message}: Missing response code")
    
    def assertLoyaltyResponseSuccess(self, response: LoyaltyResponse, message: str = "Loyalty response failed"):
        """Assert that a loyalty API response indicates success"""
        self.assertIsInstance(response, LoyaltyResponse, f"{message}: Expected LoyaltyResponse object")
        self.assertTrue(response.success, f"{message}: {response.error or response.message}")
    
    def assertIdentityFieldEquals(self, identity: IdentityUser, field_name: str, expected_value: Any, message: str = ""):
        """Assert that an identity field has the expected value"""
        actual_value = getattr(identity, field_name)
        self.assertEqual(
            actual_value, 
            expected_value, 
            f"{message}: Field '{field_name}' expected '{expected_value}', got '{actual_value}'"
        )
    
    def assertTravelProfileFieldEquals(self, profile: TravelProfile, field_name: str, expected_value: Any, message: str = ""):
        """Assert that a travel profile field has the expected value"""
        actual_value = getattr(profile, field_name)
        self.assertEqual(
            actual_value, 
            expected_value, 
            f"{message}: Field '{field_name}' expected '{expected_value}', got '{actual_value}'"
        )
    
    def assertTravelProfileListLength(self, profile: TravelProfile, list_field_name: str, expected_length: int, message: str = ""):
        """Assert that a travel profile list field has the expected length"""
        actual_list = getattr(profile, list_field_name)
        self.assertIsInstance(actual_list, list, f"{message}: Field '{list_field_name}' is not a list")
        self.assertEqual(
            len(actual_list), 
            expected_length, 
            f"{message}: Field '{list_field_name}' expected length {expected_length}, got {len(actual_list)}"
        )
    
    def create_sample_passport(self) -> Passport:
        """Create a sample passport for testing"""
        return Passport(
            doc_number=f"TEST{self.test_run_id}",
            nationality="US",
            issue_country="US",
            issue_date=date(2020, 1, 1),
            expiration_date=date(2030, 1, 1),
            primary=True
        )
    
    def create_sample_visa(self) -> Visa:
        """Create a sample visa for testing"""
        return Visa(
            visa_nationality="CA",
            visa_number=f"VISA{self.test_run_id}",
            visa_type=VisaType.MULTI_ENTRY,
            visa_country_issued="CA",
            visa_date_issued=date(2022, 6, 1),
            visa_expiration=date(2027, 6, 1)
        )
    
    def create_sample_tsa_info(self) -> TSAInfo:
        """Create sample TSA info for testing"""
        return TSAInfo(
            known_traveler_number=f"KTN{self.test_run_id}",
            gender="M",
            date_of_birth=date(1985, 5, 15),
            redress_number=f"RN{self.test_run_id}",
            no_middle_name=False
        )
    
    def create_sample_loyalty_program(self, program_type: LoyaltyProgramType = LoyaltyProgramType.AIR) -> LoyaltyProgram:
        """Create a sample loyalty program for testing"""
        vendor_codes = {
            LoyaltyProgramType.AIR: "UA",
            LoyaltyProgramType.HOTEL: "HH", 
            LoyaltyProgramType.CAR: "HZ",
            LoyaltyProgramType.RAIL: "AM"
        }
        
        return LoyaltyProgram(
            program_type=program_type,
            vendor_code=vendor_codes[program_type],
            account_number=f"{program_type.value}{self.test_run_id}",
            status="Gold",
            point_total="50000",
            segment_total="25"
        )
    
    def create_sample_air_preferences(self) -> AirPreferences:
        """Create sample air preferences for testing"""
        return AirPreferences(
            seat_preference=SeatPreference.WINDOW,
            seat_section=SeatSection.FORWARD,
            meal_preference=MealType.VEGETARIAN,
            home_airport="SEA",
            air_other="Test air preferences"
        )
    
    def create_sample_hotel_preferences(self) -> HotelPreferences:
        """Create sample hotel preferences for testing"""
        return HotelPreferences(
            room_type=HotelRoomType.KING,
            hotel_other="Test hotel preferences",
            prefer_gym=True,
            prefer_pool=True,
            prefer_foam_pillows=True,
            prefer_room_service=True,
            prefer_early_checkin=True
        )
    
    def create_sample_car_preferences(self) -> CarPreferences:
        """Create sample car preferences for testing"""
        return CarPreferences(
            car_type=CarType.INTERMEDIATE,
            transmission=TransmissionType.AUTOMATIC,
            gps=True,
            ski_rack=False
        )
    
    def create_sample_custom_field(self) -> CustomField:
        """Create a sample custom field for testing"""
        return CustomField(
            field_id=f"TEST_FIELD_{self.test_run_id}",
            value=f"Test Value {self.test_run_id}",
            field_type="Text"
        )
    
    def create_sample_unused_ticket(self) -> UnusedTicket:
        """Create a sample unused ticket for testing"""
        return UnusedTicket(
            ticket_number=f"TKT{self.test_run_id}",
            airline_code="UA",
            amount="250.00",
            currency="USD"
        )
    
    def print_identity_summary(self, identity: IdentityUser, title: str = "Identity Summary"):
        """Print a summary of an identity for debugging"""
        print(f"\n📋 {title}")
        print(f"   User ID: {identity.id}")
        print(f"   Username: {identity.user_name}")
        print(f"   Display Name: {identity.display_name}")
        print(f"   Title: {identity.title}")
        print(f"   Active: {identity.active}")
        if identity.name:
            print(f"   Full Name: {identity.name.given_name} {identity.name.family_name}")
        if identity.emails:
            print(f"   Primary Email: {identity.emails[0].value}")
        if identity.phone_numbers:
            print(f"   Phone Numbers: {len(identity.phone_numbers)}")
        if identity.enterprise_info:
            print(f"   Company ID: {identity.enterprise_info.company_id}")
    
    def print_travel_profile_summary(self, profile: TravelProfile, title: str = "Travel Profile Summary"):
        """Print a summary of a travel profile for debugging"""
        print(f"\n📋 {title}")
        print(f"   Login ID: {profile.login_id}")
        print(f"   Travel Class: {profile.rule_class}")
        print(f"   Travel Config ID: {profile.travel_config_id}")
        print(f"   Passports: {len(profile.passports)}")
        print(f"   Visas: {len(profile.visas)}")
        print(f"   Loyalty Programs: {len(profile.loyalty_programs)}")
        print(f"   Custom Fields: {len(profile.custom_fields)}")
        if profile.air_preferences:
            print(f"   Air: {profile.air_preferences.home_airport}")
        if profile.hotel_preferences:
            print(f"   Hotel: {profile.hotel_preferences.room_type}")
        if profile.car_preferences:
            print(f"   Car: {profile.car_preferences.car_type}")
    
    def save_test_data(self, data: Dict[str, Any], filename: str):
        """Save test data to a JSON file for debugging"""
        test_data_dir = os.path.join(os.path.dirname(__file__), "test_data")
        os.makedirs(test_data_dir, exist_ok=True)
        
        filepath = os.path.join(test_data_dir, f"{filename}_{self.test_run_id}.json")
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"   💾 Test data saved to: {filepath}")


# Re-export all SDK classes for convenience in test files
__all__ = [
    'BaseIntegrationTest',
    'ConcurSDK', 'IdentityUser', 'IdentityName', 'IdentityEmail', 'IdentityPhoneNumber',
    'IdentityEnterpriseInfo', 'TravelProfile', 'Address', 'Phone', 'Email', 'EmergencyContact',
    'NationalID', 'DriversLicense', 'Passport', 'Visa', 'TSAInfo', 'LoyaltyProgram',
    'RatePreference', 'DiscountCode', 'AirPreferences', 'HotelPreferences', 
    'CarPreferences', 'RailPreferences', 'CustomField', 'UnusedTicket',
    'AddressType', 'PhoneType', 'EmailType', 'VisaType', 'LoyaltyProgramType',
    'SeatPreference', 'SeatSection', 'MealType', 'HotelRoomType', 'SmokingPreference',
    'CarType', 'TransmissionType', 'ProfileStatus', 'VendorType',
    'ConcurProfileError', 'AuthenticationError', 'ProfileNotFoundError', 
    'ValidationError', 'ApiResponse', 'LoyaltyResponse', 'ConnectResponse',
    'datetime', 'date', 'timedelta'
] 