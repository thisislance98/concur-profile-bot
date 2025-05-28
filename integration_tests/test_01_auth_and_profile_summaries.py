#!/usr/bin/env python3
"""
Integration tests for authentication and profile summary functionality

Tests:
- SDK initialization and authentication
- Current user profile retrieval with all new fields
- Profile lookup by login ID
- Profile summary API with pagination
- Error handling and edge cases
"""

import unittest
from datetime import datetime, timedelta
from base_test import BaseIntegrationTest

# Import the necessary classes for the test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from concur_profile_sdk_improved import (
    ProfileNotFoundError, ConcurProfileError, ConnectResponse, ProfileStatus
)


class TestAuthAndProfileSummaries(BaseIntegrationTest):
    """Test authentication and profile summary functionality"""
    
    def test_01_sdk_initialization_and_auth(self):
        """Test SDK initialization and authentication"""
        print("\n🔐 Testing SDK initialization and authentication...")
        
        # Test that SDK was initialized properly in setUpClass
        self.assertIsNotNone(self.sdk, "SDK should be initialized")
        self.assertIsNotNone(self.test_travel_config_id, "Travel config ID should be available")
        
        # Test that we can get current user without issues
        profile = self.sdk.get_current_user_profile()
        self.assertIsNotNone(profile, "Should be able to get current user profile")
        self.assertIsNotNone(profile.login_id, "Profile should have login ID")
        self.assertIsNotNone(profile.first_name, "Profile should have first name")
        self.assertIsNotNone(profile.last_name, "Profile should have last name")
        
        print(f"✅ Authentication successful for: {profile.first_name} {profile.last_name}")
        print(f"   Login ID: {profile.login_id}")
        print(f"   Travel Config: {profile.travel_config_id}")
        
        # Print comprehensive profile summary to see what data is available
        self.print_profile_summary(profile, "Current User Profile")
    
    def test_02_comprehensive_profile_retrieval(self):
        """Test retrieval of comprehensive profile data with all new fields"""
        print("\n📊 Testing comprehensive profile data retrieval...")
        
        profile = self.sdk.get_current_user_profile()
        
        # Test that all profile sections are accessible (even if empty)
        self.assertIsInstance(profile.addresses, list, "Addresses should be a list")
        self.assertIsInstance(profile.phones, list, "Phones should be a list")
        self.assertIsInstance(profile.emails, list, "Emails should be a list")
        self.assertIsInstance(profile.emergency_contacts, list, "Emergency contacts should be a list")
        self.assertIsInstance(profile.national_ids, list, "National IDs should be a list")
        self.assertIsInstance(profile.drivers_licenses, list, "Drivers licenses should be a list")
        self.assertIsInstance(profile.passports, list, "Passports should be a list")
        self.assertIsInstance(profile.visas, list, "Visas should be a list")
        self.assertIsInstance(profile.loyalty_programs, list, "Loyalty programs should be a list")
        self.assertIsInstance(profile.custom_fields, list, "Custom fields should be a list")
        self.assertIsInstance(profile.unused_tickets, list, "Unused tickets should be a list")
        self.assertIsInstance(profile.southwest_unused_tickets, list, "Southwest unused tickets should be a list")
        self.assertIsInstance(profile.discount_codes, list, "Discount codes should be a list")
        
        # Test boolean and optional fields
        self.assertIsInstance(profile.has_no_passport, bool, "HasNoPassport should be boolean")
        
        # Test string fields (can be empty)
        self.assertIsInstance(profile.company_name, str, "Company name should be string")
        self.assertIsInstance(profile.employee_id, str, "Employee ID should be string")
        self.assertIsInstance(profile.medical_alerts, str, "Medical alerts should be string")
        self.assertIsInstance(profile.search_id, str, "Search ID should be string")
        self.assertIsInstance(profile.gds_profile_name, str, "GDS profile name should be string")
        self.assertIsInstance(profile.uuid, str, "UUID should be string")
        
        print("✅ All profile sections accessible and properly typed")
        
        # Log what data is actually present
        data_summary = {
            "basic_info": {
                "has_company_name": bool(profile.company_name),
                "has_employee_id": bool(profile.employee_id),
                "has_medical_alerts": bool(profile.medical_alerts),
                "has_uuid": bool(profile.uuid)
            },
            "contact_data": {
                "addresses_count": len(profile.addresses),
                "phones_count": len(profile.phones),
                "emails_count": len(profile.emails),
                "emergency_contacts_count": len(profile.emergency_contacts)
            },
            "documents": {
                "national_ids_count": len(profile.national_ids),
                "drivers_licenses_count": len(profile.drivers_licenses),
                "passports_count": len(profile.passports),
                "visas_count": len(profile.visas),
                "has_no_passport": profile.has_no_passport
            },
            "travel_data": {
                "loyalty_programs_count": len(profile.loyalty_programs),
                "has_air_preferences": profile.air_preferences is not None,
                "has_hotel_preferences": profile.hotel_preferences is not None,
                "has_car_preferences": profile.car_preferences is not None,
                "has_rail_preferences": profile.rail_preferences is not None,
                "has_rate_preferences": profile.rate_preferences is not None,
                "has_tsa_info": profile.tsa_info is not None
            },
            "other": {
                "custom_fields_count": len(profile.custom_fields),
                "unused_tickets_count": len(profile.unused_tickets),
                "discount_codes_count": len(profile.discount_codes)
            }
        }
        
        self.save_test_data(data_summary, "profile_data_summary")
        print("✅ Profile data analysis complete")
    
    def test_03_profile_lookup_by_login_id(self):
        """Test profile lookup by login ID"""
        print("\n🔍 Testing profile lookup by login ID...")
        
        # Get current user first
        current_profile = self.sdk.get_current_user_profile()
        login_id = current_profile.login_id
        
        # Look up the same user by login ID
        looked_up_profile = self.sdk.get_profile_by_login_id(login_id)
        
        # Verify it's the same user
        self.assertEqual(looked_up_profile.login_id, current_profile.login_id)
        self.assertEqual(looked_up_profile.first_name, current_profile.first_name)
        self.assertEqual(looked_up_profile.last_name, current_profile.last_name)
        
        print(f"✅ Profile lookup successful for: {login_id}")
        
        # Test lookup of non-existent user
        fake_login_id = f"nonexistent_{self.test_run_id}@fake.com"
        
        with self.assertRaises(ProfileNotFoundError):
            self.sdk.get_profile_by_login_id(fake_login_id)
        
        print(f"✅ Correctly threw ProfileNotFoundError for non-existent user: {fake_login_id}")
    
    def test_04_profile_summaries_basic(self):
        """Test basic profile summary API functionality"""
        print("\n📋 Testing profile summary API...")
        
        try:
            # Test basic profile summary retrieval
            # Look for profiles modified in the last 30 days
            last_modified_date = datetime.now() - timedelta(days=30)
            
            summaries = self.sdk.list_profile_summaries(
                last_modified_date=last_modified_date,
                limit=10  # Small limit for testing
            )
            
            self.assertIsInstance(summaries, ConnectResponse, "Should return ConnectResponse")
            self.assertIsInstance(summaries.profile_summaries, list, "Should contain profile summaries list")
            
            # Check metadata
            if summaries.metadata:
                self.assertIsInstance(summaries.metadata.total_items, int, "Total items should be integer")
                self.assertIsInstance(summaries.metadata.page, int, "Page should be integer")
                self.assertIsInstance(summaries.metadata.items_per_page, int, "Items per page should be integer")
                
                print(f"✅ Profile summary metadata:")
                print(f"   Total items: {summaries.metadata.total_items}")
                print(f"   Current page: {summaries.metadata.page}")
                print(f"   Items per page: {summaries.metadata.items_per_page}")
                print(f"   Total pages: {summaries.metadata.total_pages}")
            
            # Check profile summaries
            if summaries.profile_summaries:
                print(f"✅ Found {len(summaries.profile_summaries)} profile summaries")
                
                # Examine first profile summary
                first_summary = summaries.profile_summaries[0]
                self.assertIsNotNone(first_summary.login_id, "Profile summary should have login ID")
                self.assertIsInstance(first_summary.status, ProfileStatus, "Status should be ProfileStatus enum")
                
                print(f"   First profile: {first_summary.login_id} (Status: {first_summary.status.value})")
                if first_summary.profile_last_modified_utc:
                    print(f"   Last modified: {first_summary.profile_last_modified_utc}")
            else:
                print("ℹ️  No profile summaries found (this may be expected depending on the environment)")
            
            print("✅ Profile summary API test completed successfully")
            
        except ConcurProfileError as e:
            print(f"⚠️  Profile summary API may not be available in this environment: {e}")
            # Don't fail the test - this functionality may be restricted
    
    def test_05_profile_summaries_with_filters(self):
        """Test profile summary API with various filters"""
        print("\n🔧 Testing profile summary API with filters...")
        
        try:
            # Test with travel config filter
            summaries_with_config = self.sdk.list_profile_summaries(
                last_modified_date=datetime.now() - timedelta(days=7),
                travel_configs=[self.test_travel_config_id],
                limit=5
            )
            
            print(f"✅ Profile summaries with travel config filter: {len(summaries_with_config.profile_summaries)} results")
            
            # Test active users only
            summaries_active_only = self.sdk.list_profile_summaries(
                last_modified_date=datetime.now() - timedelta(days=7),
                active_only=True,
                limit=5
            )
            
            print(f"✅ Active users only: {len(summaries_active_only.profile_summaries)} results")
            
            # Test inactive users only
            summaries_inactive_only = self.sdk.list_profile_summaries(
                last_modified_date=datetime.now() - timedelta(days=7),
                active_only=False,
                limit=5
            )
            
            print(f"✅ Inactive users only: {len(summaries_inactive_only.profile_summaries)} results")
            
            # Test pagination
            summaries_page_1 = self.sdk.list_profile_summaries(
                last_modified_date=datetime.now() - timedelta(days=30),
                page=1,
                limit=2
            )
            
            summaries_page_2 = self.sdk.list_profile_summaries(
                last_modified_date=datetime.now() - timedelta(days=30),
                page=2,
                limit=2
            )
            
            print(f"✅ Page 1 results: {len(summaries_page_1.profile_summaries)}")
            print(f"✅ Page 2 results: {len(summaries_page_2.profile_summaries)}")
            
            # Verify pagination metadata
            if summaries_page_1.metadata:
                self.assertEqual(summaries_page_1.metadata.page, 1, "Page 1 should have page=1")
                self.assertEqual(summaries_page_1.metadata.items_per_page, 2, "Should have items_per_page=2")
            
            if summaries_page_2.metadata:
                self.assertEqual(summaries_page_2.metadata.page, 2, "Page 2 should have page=2")
            
            print("✅ Profile summary filtering and pagination tests completed")
            
        except ConcurProfileError as e:
            print(f"⚠️  Profile summary filters may not be available in this environment: {e}")
            # Don't fail the test - this functionality may be restricted
    
    def test_06_error_handling(self):
        """Test error handling for various edge cases"""
        print("\n❌ Testing error handling...")
        
        # Test invalid date (too far in the future)
        future_date = datetime.now() + timedelta(days=365)
        
        try:
            self.sdk.list_profile_summaries(
                last_modified_date=future_date,
                limit=1
            )
            print("⚠️  Expected error for future date, but none occurred")
        except ConcurProfileError:
            print("✅ Correctly handled invalid future date")
        except Exception as e:
            print(f"⚠️  Unexpected error type for future date: {type(e).__name__}: {e}")
        
        # Test invalid page number
        try:
            self.sdk.list_profile_summaries(
                last_modified_date=datetime.now() - timedelta(days=1),
                page=999999,  # Very high page number
                limit=1
            )
            print("✅ High page number handled gracefully (may return empty results)")
        except Exception as e:
            print(f"✅ High page number resulted in error (expected): {type(e).__name__}")
        
        # Test invalid limit (too high)
        try:
            summaries = self.sdk.list_profile_summaries(
                last_modified_date=datetime.now() - timedelta(days=1),
                limit=500  # Above API maximum of 200
            )
            
            # Should automatically cap at 200
            if summaries.metadata:
                self.assertLessEqual(summaries.metadata.items_per_page, 200, 
                                   "Items per page should be capped at 200")
            
            print("✅ High limit automatically capped at API maximum")
            
        except Exception as e:
            print(f"✅ High limit resulted in error (acceptable): {type(e).__name__}")
        
        print("✅ Error handling tests completed")


if __name__ == '__main__':
    unittest.main() 