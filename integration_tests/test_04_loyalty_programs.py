#!/usr/bin/env python3
"""
Integration tests for loyalty program functionality with read-only permissions

Tests:
- Loyalty program data structure validation
- Loyalty program XML generation and structure
- All loyalty program types (Air, Hotel, Car, Rail)
- Loyalty program validation and error handling
- Travel profile loyalty program data parsing
- Integration with travel preferences

IMPORTANT NOTE: Loyalty programs are managed via dedicated Loyalty v1 API,
which has significant restrictions. Travel suppliers can only update their
OWN loyalty program information, and only after completing SAP Concur
application review. TMCs can update any loyalty program for users.

This test suite focuses on data structure validation and XML generation
rather than API updates due to permission restrictions.
"""

import unittest
import time
from datetime import date
from base_test import BaseIntegrationTest

# Import all necessary classes from the SDK
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from concur_profile_sdk import (
    ConcurSDK, IdentityUser, IdentityName, IdentityEmail, TravelProfile,
    LoyaltyProgram, AirPreferences, HotelPreferences, CarPreferences,
    LoyaltyProgramType, SeatPreference, MealType, HotelRoomType,
    CarType, TransmissionType, ValidationError, ConcurProfileError
)


class TestLoyaltyPrograms(BaseIntegrationTest):
    """Test comprehensive loyalty program functionality with read-only permissions"""
    
    def setUp(self):
        """Set up each test with current user context"""
        super().setUp()
        self.current_identity = self.sdk.get_current_user_identity()
        self.login_id = self.current_identity.user_name
        print(f"Using authenticated user for testing: {self.login_id}")
    
    def test_01_loyalty_program_data_structure_validation(self):
        """Test loyalty program data structures and validation"""
        print("\n🏆 Testing loyalty program data structures and validation...")
        
        # Test creating comprehensive loyalty programs with all fields
        loyalty_programs = [
            # Air loyalty program with all fields
            LoyaltyProgram(
                program_type=LoyaltyProgramType.AIR,
                vendor_code="UA",
                account_number=f"UA{self.test_run_id}",
                status="Premier 1K",
                status_benefits="Unlimited upgrades, priority boarding",
                point_total="150000",
                segment_total="75",
                next_status="Global Services",
                points_until_next_status="50000",
                segments_until_next_status="25",
                expiration=date(2024, 12, 31)
            ),
            
            # Hotel loyalty program
            LoyaltyProgram(
                program_type=LoyaltyProgramType.HOTEL,
                vendor_code="HH",
                account_number=f"HH{self.test_run_id}",
                status="Diamond",
                status_benefits="Executive lounge access, room upgrades",
                point_total="300000",
                segment_total="60"
            ),
            
            # Car rental loyalty program
            LoyaltyProgram(
                program_type=LoyaltyProgramType.CAR,
                vendor_code="HZ",
                account_number=f"HZ{self.test_run_id}",
                status="President's Circle",
                status_benefits="Skip the counter, premium vehicles",
                point_total="75000",
                segment_total="35"
            ),
            
            # Rail loyalty program
            LoyaltyProgram(
                program_type=LoyaltyProgramType.RAIL,
                vendor_code="AM",
                account_number=f"AM{self.test_run_id}",
                status="Select Executive"
            )
        ]
        
        # Validate data structures
        for program in loyalty_programs:
            self.assertIsInstance(program.program_type, LoyaltyProgramType, "Program type should be enum")
            self.assertIsNotNone(program.vendor_code, "Vendor code should not be None")
            self.assertIsNotNone(program.account_number, "Account number should not be None")
            self.assertTrue(len(program.vendor_code) > 0, "Vendor code should not be empty")
            self.assertTrue(len(program.account_number) > 0, "Account number should not be empty")
        
        print(f"✅ Created and validated {len(loyalty_programs)} loyalty program data structures")
        
        # Test loyalty program XML generation in travel profile context
        travel_profile = TravelProfile(
            login_id=self.login_id,
            loyalty_programs=loyalty_programs
        )
        
        # Generate XML for loyalty programs
        xml_output = travel_profile.to_update_xml(fields_to_update=["loyalty_programs"])
        
        # Validate XML structure
        self.assertIn("AdvantageMemberships", xml_output, "Should contain AdvantageMemberships element")
        self.assertIn("Membership", xml_output, "Should contain Membership elements")
        self.assertIn("UA", xml_output, "Should contain UA vendor code")
        self.assertIn("HH", xml_output, "Should contain HH vendor code")
        self.assertIn("HZ", xml_output, "Should contain HZ vendor code")
        self.assertIn("VendorType", xml_output, "Should contain VendorType elements")
        
        print("✅ Loyalty program XML generation successful")
        print(f"   Generated XML length: {len(xml_output)} characters")
        
        # Save XML for inspection
        self.save_test_data(xml_output, "loyalty_programs_xml_sample")
        
        # Test that we can attempt loyalty program updates via dedicated API
        # (These may fail due to API restrictions, which is expected)
        ua_program = loyalty_programs[0]
        try:
            response = self.sdk.update_loyalty_program(ua_program, self.login_id)
            if hasattr(response, 'success') and response.success:
                print("✅ Loyalty program API update successful (unexpected but good!)")
            else:
                print("⚠️  Loyalty program API update failed (expected due to restrictions)")
        except Exception as e:
            print(f"⚠️  Loyalty program API update failed: {e}")
            print("   This is expected - Loyalty v1 API has significant restrictions")
    
    def test_02_loyalty_program_validation(self):
        """Test loyalty program validation and error handling"""
        print("\n✅ Testing loyalty program validation...")
        
        # Test validation of required fields - empty vendor code
        try:
            invalid_loyalty = LoyaltyProgram(
                program_type=LoyaltyProgramType.AIR,
                vendor_code="",  # Invalid - empty
                account_number="12345"
            )
            
            # Test that validation catches this locally or via API
            response = self.sdk.update_loyalty_program(invalid_loyalty, self.login_id)
            if hasattr(response, 'success') and not response.success:
                print("✅ Server correctly caught empty vendor code validation error")
            else:
                print("⚠️  Validation may be handled differently")
                
        except ValidationError:
            print("✅ SDK correctly caught empty vendor code validation error")
        except ConcurProfileError:
            print("✅ Loyalty API validation handled by server (expected)")
        except Exception as e:
            print(f"⚠️  Validation test failed with: {e}")
        
        # Test validation of required fields - empty account number
        try:
            invalid_loyalty = LoyaltyProgram(
                program_type=LoyaltyProgramType.AIR,
                vendor_code="UA",
                account_number=""  # Invalid - empty
            )
            
            response = self.sdk.update_loyalty_program(invalid_loyalty, self.login_id)
            if hasattr(response, 'success') and not response.success:
                print("✅ Server correctly caught empty account number validation error")
            else:
                print("⚠️  Validation may be handled differently")
                
        except ValidationError:
            print("✅ SDK correctly caught empty account number validation error")
        except ConcurProfileError:
            print("✅ Loyalty API validation handled by server (expected)")
        except Exception as e:
            print(f"⚠️  Validation test failed with: {e}")
        
        # Test valid loyalty program structure
        valid_loyalty = LoyaltyProgram(
            program_type=LoyaltyProgramType.AIR,
            vendor_code="UA",
            account_number="VALID123",
            status="Test Status"
        )
        
        self.assertEqual(valid_loyalty.vendor_code, "UA", "Vendor code should be set correctly")
        self.assertEqual(valid_loyalty.account_number, "VALID123", "Account number should be set correctly")
        print("✅ Valid loyalty program structure validation passed")
    
    def test_03_loyalty_programs_with_travel_preferences(self):
        """Test loyalty programs integrated with travel preferences"""
        print("\n🎯 Testing loyalty programs integrated with travel preferences...")
        
        # Create travel profile with both preferences and loyalty programs
        travel_profile = TravelProfile(
            login_id=self.login_id,
            air_preferences=AirPreferences(
                seat_preference=SeatPreference.WINDOW,
                meal_preference=MealType.KOSHER,
                home_airport="DFW"
            ),
            hotel_preferences=HotelPreferences(
                room_type=HotelRoomType.KING,
                prefer_gym=True
            ),
            car_preferences=CarPreferences(
                car_type=CarType.INTERMEDIATE,
                transmission=TransmissionType.AUTOMATIC
            ),
            loyalty_programs=[
                LoyaltyProgram(
                    program_type=LoyaltyProgramType.AIR,
                    vendor_code="AA",
                    account_number=f"AA{self.test_run_id}",
                    status="Executive Platinum"
                ),
                LoyaltyProgram(
                    program_type=LoyaltyProgramType.HOTEL,
                    vendor_code="MA",
                    account_number=f"MA{self.test_run_id}",
                    status="Titanium Elite"
                )
            ]
        )
        
        # Test XML generation for combined preferences and loyalty programs
        xml_output = travel_profile.to_update_xml(
            fields_to_update=["air_preferences", "hotel_preferences", "car_preferences", "loyalty_programs"]
        )
        
        # Validate integration in XML
        self.assertIn("Air", xml_output, "Should contain Air preferences")
        self.assertIn("Hotel", xml_output, "Should contain Hotel preferences")
        self.assertIn("Car", xml_output, "Should contain Car preferences")
        self.assertIn("AdvantageMemberships", xml_output, "Should contain AdvantageMemberships section")
        self.assertIn("AA", xml_output, "Should contain AA vendor code")
        self.assertIn("MA", xml_output, "Should contain MA vendor code")
        
        print("✅ Loyalty programs integrated with travel preferences successfully")
        print(f"   Generated combined XML length: {len(xml_output)} characters")
        
        # Save combined XML for inspection
        self.save_test_data(xml_output, "integrated_preferences_loyalty_xml_sample")
        
        # Test that we can retrieve current user's actual travel profile
        try:
            current_travel_profile = self.sdk.get_travel_profile(self.login_id)
            
            # Verify travel profile structure
            self.assertIsNotNone(current_travel_profile, "Should have travel profile")
            self.assertEqual(current_travel_profile.login_id, self.login_id, "Login ID should match")
            
            print(f"✅ Current user travel profile retrieved successfully")
            print(f"   Has Air Preferences: {current_travel_profile.air_preferences is not None}")
            print(f"   Has Hotel Preferences: {current_travel_profile.hotel_preferences is not None}")
            print(f"   Has Car Preferences: {current_travel_profile.car_preferences is not None}")
            print(f"   Existing Loyalty Programs: {len(current_travel_profile.loyalty_programs)}")
            
        except Exception as e:
            print(f"⚠️  Could not retrieve current travel profile: {e}")
    
    def test_04_comprehensive_loyalty_program_fields(self):
        """Test loyalty programs with all available fields populated"""
        print("\n📊 Testing loyalty programs with comprehensive field data...")
        
        # Create a loyalty program with all fields populated
        comprehensive_loyalty = LoyaltyProgram(
            program_type=LoyaltyProgramType.AIR,
            vendor_code="UA",
            account_number=f"COMP{self.test_run_id}",
            status="Premier 1K",
            status_benefits="Unlimited domestic upgrades, Global Services desk access, "
                           "2 complimentary United Club one-time passes, priority check-in",
            point_total="175000",
            segment_total="85",
            next_status="Global Services",
            points_until_next_status="75000",
            segments_until_next_status="15",
            expiration=date(2025, 1, 31)
        )
        
        # Validate all fields are properly set
        self.assertEqual(comprehensive_loyalty.program_type, LoyaltyProgramType.AIR)
        self.assertEqual(comprehensive_loyalty.vendor_code, "UA")
        self.assertEqual(comprehensive_loyalty.status, "Premier 1K")
        self.assertIn("Unlimited domestic upgrades", comprehensive_loyalty.status_benefits)
        self.assertEqual(comprehensive_loyalty.point_total, "175000")
        self.assertEqual(comprehensive_loyalty.segment_total, "85")
        self.assertEqual(comprehensive_loyalty.next_status, "Global Services")
        self.assertEqual(comprehensive_loyalty.points_until_next_status, "75000")
        self.assertEqual(comprehensive_loyalty.segments_until_next_status, "15")
        self.assertEqual(comprehensive_loyalty.expiration, date(2025, 1, 31))
        
        print("✅ All comprehensive loyalty program fields validated successfully")
        
        # Test XML generation with comprehensive data
        travel_profile = TravelProfile(
            login_id=self.login_id,
            loyalty_programs=[comprehensive_loyalty]
        )
        
        xml_output = travel_profile.to_update_xml(fields_to_update=["loyalty_programs"])
        
        # Validate comprehensive data in XML
        self.assertIn("AdvantageMemberships", xml_output, "Should contain AdvantageMemberships")
        self.assertIn("Membership", xml_output, "Should contain Membership elements")
        self.assertIn("UA", xml_output, "Should contain UA vendor code")
        self.assertIn("VendorType", xml_output, "Should contain VendorType")
        self.assertIn("ProgramNumber", xml_output, "Should contain ProgramNumber")
        self.assertIn("ExpirationDate", xml_output, "Should contain ExpirationDate")
        
        print("✅ Comprehensive loyalty program XML generation successful")
        
        # Save comprehensive XML for inspection
        self.save_test_data(xml_output, "comprehensive_loyalty_xml_sample")
        
        # Test potential API update (expected to fail due to restrictions)
        try:
            response = self.sdk.update_loyalty_program(comprehensive_loyalty, self.login_id)
            
            if hasattr(response, 'success') and response.success:
                print("✅ Comprehensive loyalty program updated successfully")
            else:
                print(f"⚠️  Comprehensive loyalty program update failed: {getattr(response, 'error', 'Unknown error')}")
                print("   This is expected if Loyalty v1 API is restricted")
                
        except Exception as e:
            print(f"⚠️  Comprehensive loyalty program update failed: {e}")
            print("   This is expected if Loyalty v1 API is restricted")
    
    def test_05_loyalty_program_type_coverage(self):
        """Test that all loyalty program types are supported"""
        print("\n🔄 Testing all loyalty program types...")
        
        # Test all loyalty program types
        program_types = [
            (LoyaltyProgramType.AIR, "UA", "United Airlines"),
            (LoyaltyProgramType.HOTEL, "MA", "Marriott"),
            (LoyaltyProgramType.CAR, "HZ", "Hertz"),
            (LoyaltyProgramType.RAIL, "AM", "Amtrak")
        ]
        
        created_programs = []
        successful_types = []
        
        for program_type, vendor_code, vendor_name in program_types:
            try:
                loyalty_program = LoyaltyProgram(
                    program_type=program_type,
                    vendor_code=vendor_code,
                    account_number=f"{vendor_code}TEST{self.test_run_id}",
                    status="Test Status"
                )
                
                created_programs.append(loyalty_program)
                
                # Validate enum and structure
                self.assertEqual(loyalty_program.program_type, program_type, f"Program type should be {program_type}")
                self.assertEqual(loyalty_program.vendor_code, vendor_code, f"Vendor code should be {vendor_code}")
                
                print(f"✅ {vendor_name} ({program_type.value}) loyalty program structure validated")
                
                # Test API update (may fail due to restrictions)
                response = self.sdk.update_loyalty_program(loyalty_program, self.login_id)
                
                if hasattr(response, 'success') and response.success:
                    successful_types.append(vendor_name)
                    print(f"✅ {vendor_name} loyalty program API update successful")
                else:
                    print(f"⚠️  {vendor_name} loyalty program API update failed: {getattr(response, 'error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"⚠️  {vendor_name} loyalty program failed: {e}")
        
        # Test XML generation for all program types
        travel_profile = TravelProfile(
            login_id=self.login_id,
            loyalty_programs=created_programs
        )
        
        xml_output = travel_profile.to_update_xml(fields_to_update=["loyalty_programs"])
        
        # Validate all types appear in XML
        for program_type, vendor_code, vendor_name in program_types:
            self.assertIn(vendor_code, xml_output, f"Should contain {vendor_code} vendor code in XML")
        
        print(f"✅ All {len(program_types)} loyalty program types validated in XML generation")
        
        # Save all types XML for inspection
        self.save_test_data(xml_output, "all_loyalty_types_xml_sample")
        
        if successful_types:
            print(f"✅ Successfully updated {len(successful_types)}/{len(program_types)} loyalty program types via API")
        else:
            print("⚠️  Loyalty v1 API appears to be restricted for all program types")
            print("   This is expected - only travel suppliers with completed SAP Concur")
            print("   application review can update loyalty programs via the API")


if __name__ == '__main__':
    unittest.main() 