#!/usr/bin/env python3
"""
Integration tests for comprehensive profile CRUD operations

Tests:
- User creation with comprehensive profile data
- Profile updates with all new field types
- Contact information management (addresses, phones, emails)
- Emergency contacts and document management
- Complex profile scenarios and validation
"""

import unittest
import time
from datetime import date
from base_test import BaseIntegrationTest

# Import the necessary classes for the test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from concur_profile_sdk_improved import (
    UserProfile, Address, Phone, Email, EmergencyContact,
    NationalID, DriversLicense, Passport, Visa, TSAInfo, CustomField,
    AddressType, PhoneType, EmailType, VisaType,
    ProfileNotFoundError, ConcurProfileError, ApiResponse
)


class TestComprehensiveProfileCRUD(BaseIntegrationTest):
    """Test comprehensive profile CRUD operations with all new field types"""
    
    def test_01_create_user_with_basic_data(self):
        """Test creating a user with basic profile data"""
        print("\n👤 Testing user creation with basic data...")
        
        login_id = self.generate_unique_login_id("basic")
        
        profile = UserProfile(
            login_id=login_id,
            first_name="Basic",
            last_name="TestUser",
            middle_name="Middle",
            job_title="Test Engineer",
            company_name="Test Company Inc",
            employee_id=f"EMP{self.test_run_id}",
            travel_config_id=self.test_travel_config_id
        )
        
        response = self.sdk.create_user(profile, password=f"BasicTest{self.test_run_id}!")
        self.assertApiResponseSuccess(response, "Failed to create basic user")
        
        print(f"✅ Created basic user: {login_id}")
        print(f"   UUID: {response.uuid}")
        
        # Wait for user to be available
        self.wait_for_user_availability(login_id)
        
        # Verify the created user
        created_profile = self.sdk.get_profile_by_login_id(login_id)
        self.assertEqual(created_profile.login_id, login_id)
        self.assertEqual(created_profile.first_name, "Basic")
        self.assertEqual(created_profile.last_name, "TestUser")
        self.assertEqual(created_profile.job_title, "Test Engineer")
        
        print("✅ Basic user verified successfully")
        return login_id
    
    def test_02_create_user_with_contact_information(self):
        """Test creating a user with comprehensive contact information"""
        print("\n📞 Testing user creation with contact information...")
        
        login_id = self.generate_unique_login_id("contact")
        
        profile = UserProfile(
            login_id=login_id,
            first_name="Contact",
            last_name="TestUser",
            travel_config_id=self.test_travel_config_id,
            
            # Multiple addresses
            addresses=[
                self.create_sample_address(AddressType.HOME),
                Address(
                    type=AddressType.WORK,
                    street=f"456 Work Blvd {self.test_run_id}",
                    city="Business City",
                    state_province="BC",
                    postal_code="54321",
                    country_code="US"
                )
            ],
            
            # Multiple phone numbers
            phones=[
                self.create_sample_phone(PhoneType.HOME),
                self.create_sample_phone(PhoneType.WORK),
                Phone(
                    type=PhoneType.CELL,
                    phone_number=f"555-CELL-{self.test_run_id[-4:]}",
                    country_code="1"
                )
            ],
            
            # Multiple email addresses
            emails=[
                self.create_sample_email(EmailType.BUSINESS),
                Email(
                    type=EmailType.PERSONAL,
                    email_address=f"personal_{self.test_run_id}@example.com"
                )
            ]
        )
        
        response = self.sdk.create_user(profile, password=f"ContactTest{self.test_run_id}!")
        self.assertApiResponseSuccess(response, "Failed to create contact user")
        
        print(f"✅ Created contact user: {login_id}")
        
        # Wait for user to be available
        self.wait_for_user_availability(login_id)
        
        # Verify the contact information
        created_profile = self.sdk.get_profile_by_login_id(login_id)
        
        self.assertProfileListLength(created_profile, "addresses", 2, "Should have 2 addresses")
        self.assertProfileListLength(created_profile, "phones", 3, "Should have 3 phone numbers")
        self.assertProfileListLength(created_profile, "emails", 2, "Should have 2 email addresses")
        
        # Verify address details
        home_addresses = [addr for addr in created_profile.addresses if addr.type == AddressType.HOME]
        work_addresses = [addr for addr in created_profile.addresses if addr.type == AddressType.WORK]
        
        self.assertEqual(len(home_addresses), 1, "Should have 1 home address")
        self.assertEqual(len(work_addresses), 1, "Should have 1 work address")
        self.assertIn(self.test_run_id, home_addresses[0].street, "Home address should contain test run ID")
        
        # Verify phone details
        cell_phones = [phone for phone in created_profile.phones if phone.type == PhoneType.CELL]
        self.assertEqual(len(cell_phones), 1, "Should have 1 cell phone")
        
        print("✅ Contact information verified successfully")
        return login_id
    
    def test_03_create_user_with_emergency_contacts(self):
        """Test creating a user with emergency contacts"""
        print("\n🚨 Testing user creation with emergency contacts...")
        
        login_id = self.generate_unique_login_id("emergency")
        
        profile = UserProfile(
            login_id=login_id,
            first_name="Emergency",
            last_name="TestUser",
            travel_config_id=self.test_travel_config_id,
            
            # Multiple emergency contacts
            emergency_contacts=[
                self.create_sample_emergency_contact(),
                EmergencyContact(
                    name=f"Secondary Contact {self.test_run_id}",
                    relationship="Parent",
                    phone="555-PARENT",
                    mobile_phone="555-MOBILE-2",
                    email=f"parent_{self.test_run_id}@example.com"
                )
            ]
        )
        
        response = self.sdk.create_user(profile, password=f"EmergencyTest{self.test_run_id}!")
        self.assertApiResponseSuccess(response, "Failed to create emergency contact user")
        
        print(f"✅ Created emergency contact user: {login_id}")
        
        # Wait for user to be available
        self.wait_for_user_availability(login_id)
        
        # Verify emergency contacts
        created_profile = self.sdk.get_profile_by_login_id(login_id)
        self.assertProfileListLength(created_profile, "emergency_contacts", 2, "Should have 2 emergency contacts")
        
        # Verify emergency contact details
        spouse_contacts = [ec for ec in created_profile.emergency_contacts if ec.relationship == "Spouse"]
        parent_contacts = [ec for ec in created_profile.emergency_contacts if ec.relationship == "Parent"]
        
        self.assertEqual(len(spouse_contacts), 1, "Should have 1 spouse contact")
        self.assertEqual(len(parent_contacts), 1, "Should have 1 parent contact")
        
        print("✅ Emergency contacts verified successfully")
        return login_id
    
    def test_04_create_user_with_documents(self):
        """Test creating a user with identity documents"""
        print("\n📄 Testing user creation with identity documents...")
        
        login_id = self.generate_unique_login_id("documents")
        
        profile = UserProfile(
            login_id=login_id,
            first_name="Document",
            last_name="TestUser",
            travel_config_id=self.test_travel_config_id,
            
            # National IDs
            national_ids=[
                NationalID(f"SSN{self.test_run_id}", "US"),
                NationalID(f"SIN{self.test_run_id}", "CA")
            ],
            
            # Driver's licenses
            drivers_licenses=[
                DriversLicense(f"DL{self.test_run_id}", "US", "CA")
            ],
            
            # Passports
            passports=[
                self.create_sample_passport(),
                Passport(
                    doc_number=f"SEC{self.test_run_id}",
                    nationality="CA",
                    issue_country="CA",
                    issue_date=date(2019, 6, 15),
                    expiration_date=date(2029, 6, 15),
                    primary=False
                )
            ],
            
            # Visas
            visas=[
                self.create_sample_visa()
            ]
        )
        
        response = self.sdk.create_user(profile, password=f"DocumentTest{self.test_run_id}!")
        self.assertApiResponseSuccess(response, "Failed to create document user")
        
        print(f"✅ Created document user: {login_id}")
        
        # Wait for user to be available
        self.wait_for_user_availability(login_id)
        
        # Verify documents
        created_profile = self.sdk.get_profile_by_login_id(login_id)
        
        self.assertProfileListLength(created_profile, "national_ids", 2, "Should have 2 national IDs")
        self.assertProfileListLength(created_profile, "drivers_licenses", 1, "Should have 1 driver's license")
        self.assertProfileListLength(created_profile, "passports", 2, "Should have 2 passports")
        self.assertProfileListLength(created_profile, "visas", 1, "Should have 1 visa")
        
        # Verify document details
        primary_passports = [p for p in created_profile.passports if p.primary]
        self.assertEqual(len(primary_passports), 1, "Should have 1 primary passport")
        
        us_national_ids = [nid for nid in created_profile.national_ids if nid.country_code == "US"]
        self.assertEqual(len(us_national_ids), 1, "Should have 1 US national ID")
        
        print("✅ Identity documents verified successfully")
        return login_id
    
    def test_05_create_user_with_tsa_info(self):
        """Test creating a user with TSA information"""
        print("\n🛂 Testing user creation with TSA information...")
        
        login_id = self.generate_unique_login_id("tsa")
        
        profile = UserProfile(
            login_id=login_id,
            first_name="TSA",
            last_name="TestUser",
            travel_config_id=self.test_travel_config_id,
            
            # TSA information
            tsa_info=self.create_sample_tsa_info()
        )
        
        response = self.sdk.create_user(profile, password=f"TSATest{self.test_run_id}!")
        self.assertApiResponseSuccess(response, "Failed to create TSA user")
        
        print(f"✅ Created TSA user: {login_id}")
        
        # Wait for user to be available
        self.wait_for_user_availability(login_id)
        
        # Verify TSA information
        created_profile = self.sdk.get_profile_by_login_id(login_id)
        
        self.assertIsNotNone(created_profile.tsa_info, "Should have TSA info")
        self.assertIn(self.test_run_id, created_profile.tsa_info.known_traveler_number, 
                     "KTN should contain test run ID")
        self.assertEqual(created_profile.tsa_info.gender, "M", "Gender should be M")
        self.assertEqual(created_profile.tsa_info.date_of_birth, date(1985, 5, 15), 
                        "DOB should match")
        
        print("✅ TSA information verified successfully")
        return login_id
    
    def test_06_create_user_with_custom_fields(self):
        """Test creating a user with custom fields"""
        print("\n🔧 Testing user creation with custom fields...")
        
        login_id = self.generate_unique_login_id("custom")
        
        profile = UserProfile(
            login_id=login_id,
            first_name="Custom",
            last_name="TestUser",
            travel_config_id=self.test_travel_config_id,
            
            # Custom fields
            custom_fields=[
                self.create_sample_custom_field(),
                CustomField(
                    field_id=f"DEPARTMENT_{self.test_run_id}",
                    value="Engineering",
                    field_type="Text"
                ),
                CustomField(
                    field_id=f"LEVEL_{self.test_run_id}",
                    value="Senior",
                    field_type="Text"
                )
            ]
        )
        
        response = self.sdk.create_user(profile, password=f"CustomTest{self.test_run_id}!")
        self.assertApiResponseSuccess(response, "Failed to create custom fields user")
        
        print(f"✅ Created custom fields user: {login_id}")
        
        # Wait for user to be available
        self.wait_for_user_availability(login_id)
        
        # Verify custom fields
        created_profile = self.sdk.get_profile_by_login_id(login_id)
        self.assertProfileListLength(created_profile, "custom_fields", 3, "Should have 3 custom fields")
        
        # Verify specific custom fields
        dept_fields = [cf for cf in created_profile.custom_fields if "DEPARTMENT" in cf.field_id]
        self.assertEqual(len(dept_fields), 1, "Should have 1 department field")
        self.assertEqual(dept_fields[0].value, "Engineering", "Department should be Engineering")
        
        print("✅ Custom fields verified successfully")
        return login_id
    
    def test_07_update_user_comprehensive_data(self):
        """Test updating a user with comprehensive profile data"""
        print("\n📝 Testing comprehensive user profile updates...")
        
        # Create a basic user first
        login_id = self.generate_unique_login_id("update")
        
        basic_profile = UserProfile(
            login_id=login_id,
            first_name="Update",
            last_name="TestUser",
            travel_config_id=self.test_travel_config_id
        )
        
        create_response = self.sdk.create_user(basic_profile, password=f"UpdateTest{self.test_run_id}!")
        self.assertApiResponseSuccess(create_response, "Failed to create user for update test")
        
        self.wait_for_user_availability(login_id)
        
        print(f"✅ Created user for update test: {login_id}")
        
        # Now update with comprehensive data
        updated_profile = UserProfile(
            login_id=login_id,
            first_name="Updated",
            last_name="TestUser",
            middle_name="Middle",
            job_title="Senior Test Engineer",
            company_name="Updated Company Inc",
            employee_id=f"EMP_UPD_{self.test_run_id}",
            medical_alerts="No known allergies",
            
            # Add comprehensive contact information
            addresses=[
                Address(
                    type=AddressType.HOME,
                    street=f"789 Updated St {self.test_run_id}",
                    city="Updated City",
                    state_province="UC",
                    postal_code="99999",
                    country_code="US"
                )
            ],
            
            phones=[
                Phone(
                    type=PhoneType.WORK,
                    phone_number=f"555-UPDATE-{self.test_run_id[-4:]}",
                    country_code="1",
                    extension="999"
                )
            ],
            
            emails=[
                Email(
                    type=EmailType.BUSINESS,
                    email_address=f"updated_{self.test_run_id}@example.com"
                )
            ],
            
            # Add emergency contact
            emergency_contacts=[
                EmergencyContact(
                    name=f"Updated Emergency {self.test_run_id}",
                    relationship="Spouse",
                    phone="555-EMERGENCY-UPD",
                    email=f"emergency_upd_{self.test_run_id}@example.com"
                )
            ],
            
            # Add TSA info
            tsa_info=TSAInfo(
                known_traveler_number=f"KTNUPD{self.test_run_id}",
                gender="F",
                date_of_birth=date(1990, 12, 25)
            )
        )
        
        # Perform the update
        update_response = self.sdk.update_user(updated_profile)
        self.assertApiResponseSuccess(update_response, "Failed to update user profile")
        
        print("✅ Profile update successful")
        
        # Wait a moment for update to propagate
        time.sleep(2)
        
        # Verify the updates
        final_profile = self.sdk.get_profile_by_login_id(login_id)
        
        # Verify basic field updates
        self.assertEqual(final_profile.first_name, "Updated", "First name should be updated")
        self.assertEqual(final_profile.middle_name, "Middle", "Middle name should be updated")
        self.assertEqual(final_profile.job_title, "Senior Test Engineer", "Job title should be updated")
        self.assertEqual(final_profile.medical_alerts, "No known allergies", "Medical alerts should be updated")
        
        # Verify contact information updates
        self.assertGreaterEqual(len(final_profile.addresses), 1, "Should have at least 1 address")
        self.assertGreaterEqual(len(final_profile.phones), 1, "Should have at least 1 phone")
        self.assertGreaterEqual(len(final_profile.emails), 1, "Should have at least 1 email")
        self.assertGreaterEqual(len(final_profile.emergency_contacts), 1, "Should have at least 1 emergency contact")
        
        # Verify TSA info update
        if final_profile.tsa_info:
            self.assertIn("KTNUPD", final_profile.tsa_info.known_traveler_number, "KTN should be updated")
        
        print("✅ Comprehensive profile updates verified successfully")
        
        self.print_profile_summary(final_profile, "Updated Profile Summary")
        
        return login_id
    
    def test_08_partial_field_updates(self):
        """Test updating specific fields only"""
        print("\n🎯 Testing partial field updates...")
        
        # Create a user with some initial data
        login_id = self.generate_unique_login_id("partial")
        
        initial_profile = UserProfile(
            login_id=login_id,
            first_name="Partial",
            last_name="TestUser",
            job_title="Initial Title",
            travel_config_id=self.test_travel_config_id,
            addresses=[self.create_sample_address(AddressType.HOME)]
        )
        
        create_response = self.sdk.create_user(initial_profile, password=f"PartialTest{self.test_run_id}!")
        self.assertApiResponseSuccess(create_response, "Failed to create user for partial update test")
        
        self.wait_for_user_availability(login_id)
        
        # Test updating only the job title
        job_title_update = UserProfile(
            login_id=login_id,
            job_title="Updated Title Only"
        )
        
        response = self.sdk.update_user(job_title_update, fields_to_update=["job_title"])
        self.assertApiResponseSuccess(response, "Failed to update job title only")
        
        print("✅ Job title only update successful")
        
        # Wait for update to propagate
        time.sleep(2)
        
        # Verify only job title was updated
        updated_profile = self.sdk.get_profile_by_login_id(login_id)
        
        self.assertEqual(updated_profile.job_title, "Updated Title Only", "Job title should be updated")
        self.assertEqual(updated_profile.first_name, "Partial", "First name should be unchanged")
        self.assertEqual(updated_profile.last_name, "TestUser", "Last name should be unchanged")
        
        print("✅ Partial field update verified - other fields unchanged")
        
        # Test updating multiple specific fields
        multi_field_update = UserProfile(
            login_id=login_id,
            first_name="Updated First",
            company_name="New Company",
            medical_alerts="Updated medical info"
        )
        
        response2 = self.sdk.update_user(
            multi_field_update, 
            fields_to_update=["first_name", "company_name", "medical_alerts"]
        )
        self.assertApiResponseSuccess(response2, "Failed to update multiple specific fields")
        
        print("✅ Multiple field update successful")
        
        # Wait and verify
        time.sleep(2)
        final_profile = self.sdk.get_profile_by_login_id(login_id)
        
        self.assertEqual(final_profile.first_name, "Updated First", "First name should be updated")
        self.assertEqual(final_profile.company_name, "New Company", "Company name should be updated")
        self.assertEqual(final_profile.medical_alerts, "Updated medical info", "Medical alerts should be updated")
        self.assertEqual(final_profile.job_title, "Updated Title Only", "Job title should remain from previous update")
        
        print("✅ Multiple specific field updates verified successfully")
        
        return login_id


if __name__ == '__main__':
    unittest.main() 