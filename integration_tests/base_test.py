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

from concur_profile_sdk_improved import (
    ConcurProfileSDK, UserProfile, Address, Phone, Email, EmergencyContact,
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
    sdk: Optional[ConcurProfileSDK] = None
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
            cls.sdk = ConcurProfileSDK(
                client_id=os.getenv("CONCUR_CLIENT_ID"),
                client_secret=os.getenv("CONCUR_CLIENT_SECRET"),
                username=os.getenv("CONCUR_USERNAME"),
                password=os.getenv("CONCUR_PASSWORD"),
                base_url=os.getenv("CONCUR_BASE_URL", "https://us2.api.concursolutions.com")
            )
            
            # Test authentication by getting current user
            current_user = cls.sdk.get_current_user_profile()
            print(f"✅ SDK initialized successfully")
            print(f"   Authenticated as: {current_user.first_name} {current_user.last_name}")
            print(f"   Login ID: {current_user.login_id}")
            
            # Store travel config ID for test user creation
            cls.test_travel_config_id = os.getenv("CONCUR_TRAVEL_CONFIG_ID")
            if not cls.test_travel_config_id:
                cls.test_travel_config_id = current_user.travel_config_id
            
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
                    cls.sdk.delete_user(login_id)
                    print(f"   ✅ Deleted user: {login_id}")
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
    
    def create_test_user(
        self, 
        login_id: Optional[str] = None,
        first_name: str = "Test",
        last_name: str = "User",
        password: Optional[str] = None
    ) -> UserProfile:
        """Create a test user and track for cleanup"""
        if not login_id:
            login_id = self.generate_unique_login_id()
        
        if not password:
            password = f"TestPass_{self.test_run_id}!"
        
        profile = UserProfile(
            login_id=login_id,
            first_name=first_name,
            last_name=last_name,
            travel_config_id=self.test_travel_config_id,
            job_title="Integration Test User"
        )
        
        response = self.sdk.create_user(profile, password=password)
        self.assertApiResponseSuccess(response, f"Failed to create test user {login_id}")
        
        # Track for cleanup
        self.created_users.append(login_id)
        
        return profile
    
    def wait_for_user_availability(self, login_id: str, max_wait: int = 30):
        """Wait for a newly created user to be available for read operations"""
        print(f"   ⏰ Waiting for user {login_id} to be available...")
        
        for attempt in range(max_wait):
            try:
                self.sdk.get_profile_by_login_id(login_id)
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
    
    def assertProfileFieldEquals(self, profile: UserProfile, field_name: str, expected_value: Any, message: str = ""):
        """Assert that a profile field has the expected value"""
        actual_value = getattr(profile, field_name)
        self.assertEqual(
            actual_value, 
            expected_value, 
            f"{message}: Field '{field_name}' expected '{expected_value}', got '{actual_value}'"
        )
    
    def assertProfileListLength(self, profile: UserProfile, list_field_name: str, expected_length: int, message: str = ""):
        """Assert that a profile list field has the expected length"""
        actual_list = getattr(profile, list_field_name)
        self.assertIsInstance(actual_list, list, f"{message}: Field '{list_field_name}' is not a list")
        self.assertEqual(
            len(actual_list), 
            expected_length, 
            f"{message}: Field '{list_field_name}' expected length {expected_length}, got {len(actual_list)}"
        )
    
    def create_sample_address(self, addr_type: AddressType = AddressType.HOME) -> Address:
        """Create a sample address for testing"""
        return Address(
            type=addr_type,
            street=f"123 Test St {self.test_run_id}",
            city="Test City",
            state_province="TS",
            postal_code="12345",
            country_code="US"
        )
    
    def create_sample_phone(self, phone_type: PhoneType = PhoneType.HOME) -> Phone:
        """Create a sample phone for testing"""
        return Phone(
            type=phone_type,
            phone_number=f"555-{self.test_run_id[-4:]}",
            country_code="1",
            extension="123" if phone_type == PhoneType.WORK else ""
        )
    
    def create_sample_email(self, email_type: EmailType = EmailType.BUSINESS) -> Email:
        """Create a sample email for testing"""
        return Email(
            type=email_type,
            email_address=f"test_{self.test_run_id}@example.com"
        )
    
    def create_sample_emergency_contact(self) -> EmergencyContact:
        """Create a sample emergency contact for testing"""
        # NOTE: Phone and Email fields are excluded during creation due to API validation errors
        # They can be added via separate update operations if the proper scopes are available
        return EmergencyContact(
            name=f"Emergency Contact {self.test_run_id}",
            relationship="Spouse"
            # phone="555-EMERGENCY",  # Excluded during creation
            # mobile_phone="555-MOBILE",  # Excluded during creation  
            # email=f"emergency_{self.test_run_id}@example.com"  # Excluded during creation
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
            smoking_preference=SmokingPreference.NON_SMOKING,
            room_type=HotelRoomType.KING,
            hotel_other="Test hotel preferences",
            prefer_gym=True,
            prefer_pool=True,
            prefer_restaurant=True
        )
    
    def create_sample_car_preferences(self) -> CarPreferences:
        """Create sample car preferences for testing"""
        return CarPreferences(
            car_type=CarType.INTERMEDIATE,
            transmission=TransmissionType.AUTOMATIC,
            smoking_preference=SmokingPreference.NON_SMOKING,
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
    
    def print_profile_summary(self, profile: UserProfile, title: str = "Profile Summary"):
        """Print a summary of a profile for debugging"""
        print(f"\n📋 {title}")
        print(f"   Login ID: {profile.login_id}")
        print(f"   Name: {profile.first_name} {profile.last_name}")
        print(f"   Job Title: {profile.job_title}")
        print(f"   Addresses: {len(profile.addresses)}")
        print(f"   Phones: {len(profile.phones)}")
        print(f"   Emails: {len(profile.emails)}")
        print(f"   Emergency Contacts: {len(profile.emergency_contacts)}")
        print(f"   Passports: {len(profile.passports)}")
        print(f"   Visas: {len(profile.visas)}")
        print(f"   Loyalty Programs: {len(profile.loyalty_programs)}")
        print(f"   Custom Fields: {len(profile.custom_fields)}")
    
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
    'ConcurProfileSDK', 'UserProfile', 'Address', 'Phone', 'Email', 'EmergencyContact',
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