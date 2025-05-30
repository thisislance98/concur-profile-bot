#!/usr/bin/env python3
"""
Debug integration tests for travel preferences update functionality

This test file specifically focuses on debugging travel preferences update issues
by testing actual API calls and examining responses in detail.
"""

import unittest
import time
import json
from datetime import datetime
from base_test import BaseIntegrationTest

# Import the necessary classes for the test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from concur_profile_sdk import (
    IdentityUser, IdentityName, IdentityEmail, TravelProfile,
    AirPreferences, HotelPreferences, CarPreferences, RailPreferences, 
    SeatPreference, SeatSection, MealType, HotelRoomType,
    CarType, TransmissionType, ApiResponse, ConcurProfileError,
    ValidationError, ProfileNotFoundError
)


class TestTravelPreferencesDebug(BaseIntegrationTest):
    """Debug travel preferences update functionality with actual API calls"""
    
    def setUp(self):
        """Set up each test with current user context"""
        super().setUp()
        
        # Use current authenticated user
        try:
            self.current_identity = self.sdk.get_current_user_identity()
            self.login_id = self.current_identity.user_name
            print(f"✅ Using authenticated user: {self.login_id}")
            
            # Get current travel profile to understand existing state
            self.current_profile = self.sdk.get_travel_profile(self.login_id)
            print(f"✅ Current travel profile loaded")
            print(f"   Rule Class: {self.current_profile.rule_class}")
            print(f"   Travel Config ID: {self.current_profile.travel_config_id}")
            
        except Exception as e:
            self.fail(f"Failed to set up test user context: {e}")
    
    def test_01_debug_current_travel_profile_state(self):
        """Debug and display current travel profile state in detail"""
        print("\n🔍 Debugging current travel profile state...")
        
        try:
            profile = self.sdk.get_travel_profile(self.login_id)
            
            # Print comprehensive profile state
            print(f"\n📋 Current Travel Profile State:")
            print(f"   Login ID: {profile.login_id}")
            print(f"   Rule Class: {profile.rule_class}")
            print(f"   Travel Config ID: {profile.travel_config_id}")
            
            # Air preferences
            if profile.air_preferences:
                air = profile.air_preferences
                print(f"\n✈️ Current Air Preferences:")
                print(f"   Seat Preference: {air.seat_preference}")
                print(f"   Seat Section: {air.seat_section}")
                print(f"   Meal Preference: {air.meal_preference}")
                print(f"   Home Airport: {air.home_airport}")
                print(f"   Air Other: {air.air_other}")
            else:
                print(f"\n✈️ No current air preferences")
            
            # Hotel preferences
            if profile.hotel_preferences:
                hotel = profile.hotel_preferences
                print(f"\n🏨 Current Hotel Preferences:")
                print(f"   Room Type: {hotel.room_type}")
                print(f"   Hotel Other: {hotel.hotel_other}")
                print(f"   Prefer Gym: {hotel.prefer_gym}")
                print(f"   Prefer Pool: {hotel.prefer_pool}")
                print(f"   Prefer Foam Pillows: {hotel.prefer_foam_pillows}")
            else:
                print(f"\n🏨 No current hotel preferences")
            
            # Car preferences
            if profile.car_preferences:
                car = profile.car_preferences
                print(f"\n🚗 Current Car Preferences:")
                print(f"   Car Type: {car.car_type}")
                print(f"   Transmission: {car.transmission}")
                print(f"   GPS: {car.gps}")
                print(f"   Ski Rack: {car.ski_rack}")
            else:
                print(f"\n🚗 No current car preferences")
            
            # Save current state for comparison
            profile_data = {
                "login_id": profile.login_id,
                "rule_class": profile.rule_class,
                "travel_config_id": profile.travel_config_id,
                "air_preferences": {
                    "seat_preference": str(profile.air_preferences.seat_preference) if profile.air_preferences and profile.air_preferences.seat_preference else None,
                    "seat_section": str(profile.air_preferences.seat_section) if profile.air_preferences and profile.air_preferences.seat_section else None,
                    "meal_preference": str(profile.air_preferences.meal_preference) if profile.air_preferences and profile.air_preferences.meal_preference else None,
                    "home_airport": profile.air_preferences.home_airport if profile.air_preferences else None,
                    "air_other": profile.air_preferences.air_other if profile.air_preferences else None
                } if profile.air_preferences else None,
                "hotel_preferences": {
                    "room_type": str(profile.hotel_preferences.room_type) if profile.hotel_preferences and profile.hotel_preferences.room_type else None,
                    "hotel_other": profile.hotel_preferences.hotel_other if profile.hotel_preferences else None,
                    "prefer_gym": profile.hotel_preferences.prefer_gym if profile.hotel_preferences else None,
                    "prefer_pool": profile.hotel_preferences.prefer_pool if profile.hotel_preferences else None
                } if profile.hotel_preferences else None,
                "car_preferences": {
                    "car_type": str(profile.car_preferences.car_type) if profile.car_preferences and profile.car_preferences.car_type else None,
                    "transmission": str(profile.car_preferences.transmission) if profile.car_preferences and profile.car_preferences.transmission else None,
                    "gps": profile.car_preferences.gps if profile.car_preferences else None
                } if profile.car_preferences else None
            }
            
            self.save_test_data(profile_data, "current_profile_state")
            print(f"✅ Current profile state saved for debugging")
            
        except Exception as e:
            self.fail(f"Failed to debug current travel profile state: {e}")
    
    def test_02_debug_air_preferences_update(self):
        """Debug air preferences update with detailed logging"""
        print("\n✈️ Debugging air preferences update...")
        
        try:
            # Create new air preferences
            new_air_preferences = AirPreferences(
                seat_preference=SeatPreference.WINDOW,
                seat_section=SeatSection.FORWARD,
                meal_preference=MealType.VEGETARIAN,
                home_airport="SEA",
                air_other=f"Test update {self.test_run_id}"
            )
            
            print(f"📝 New air preferences to set:")
            print(f"   Seat Preference: {new_air_preferences.seat_preference}")
            print(f"   Seat Section: {new_air_preferences.seat_section}")
            print(f"   Meal Preference: {new_air_preferences.meal_preference}")
            print(f"   Home Airport: {new_air_preferences.home_airport}")
            print(f"   Air Other: {new_air_preferences.air_other}")
            
            # Create travel profile for update
            update_profile = TravelProfile(
                login_id=self.login_id,
                air_preferences=new_air_preferences
            )
            
            # Generate XML to inspect
            xml_output = update_profile.to_update_xml(fields_to_update=["air_preferences"])
            print(f"\n📄 Generated XML for update:")
            print(f"{xml_output}")
            
            # Save XML for inspection
            self.save_test_data(xml_output, "air_preferences_update_xml")
            
            # Attempt the update
            print(f"\n🚀 Attempting air preferences update...")
            response = self.sdk.update_travel_profile(update_profile, fields_to_update=["air_preferences"])
            
            print(f"✅ Update response received:")
            print(f"   Success: {response.success}")
            print(f"   Message: {response.message}")
            if hasattr(response, 'code'):
                print(f"   Code: {response.code}")
            
            # Verify the update by retrieving the profile again
            print(f"\n🔍 Verifying update by retrieving profile...")
            time.sleep(2)  # Wait for changes to propagate
            
            updated_profile = self.sdk.get_travel_profile(self.login_id)
            
            if updated_profile.air_preferences:
                air = updated_profile.air_preferences
                print(f"✅ Updated air preferences verified:")
                print(f"   Seat Preference: {air.seat_preference}")
                print(f"   Seat Section: {air.seat_section}")
                print(f"   Meal Preference: {air.meal_preference}")
                print(f"   Home Airport: {air.home_airport}")
                print(f"   Air Other: {air.air_other}")
                
                # Check if our update was successful
                self.assertEqual(air.seat_preference, SeatPreference.WINDOW, "Seat preference should be updated")
                self.assertEqual(air.home_airport, "SEA", "Home airport should be updated")
                
            else:
                print(f"⚠️ No air preferences found after update")
            
        except Exception as e:
            print(f"❌ Air preferences update failed: {e}")
            print(f"   Exception type: {type(e).__name__}")
            
            # Save error details for debugging
            error_data = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "test_run_id": self.test_run_id,
                "login_id": self.login_id
            }
            self.save_test_data(error_data, "air_preferences_update_error")
            
            # Re-raise to fail the test
            raise
    
    def test_03_debug_simple_seat_preference_update(self):
        """Debug a very simple seat preference update"""
        print("\n🪑 Debugging simple seat preference update...")
        
        try:
            # Test with minimal air preferences - just seat preference
            simple_air_preferences = AirPreferences(
                seat_preference=SeatPreference.AISLE
            )
            
            print(f"📝 Simple update - changing seat preference to: {simple_air_preferences.seat_preference}")
            
            # Create minimal travel profile
            update_profile = TravelProfile(
                login_id=self.login_id,
                air_preferences=simple_air_preferences
            )
            
            # Generate and inspect XML
            xml_output = update_profile.to_update_xml(fields_to_update=["air_preferences"])
            print(f"\n📄 Simple update XML:")
            print(f"{xml_output}")
            
            # Attempt the update
            print(f"\n🚀 Attempting simple seat preference update...")
            response = self.sdk.update_travel_profile(update_profile, fields_to_update=["air_preferences"])
            
            print(f"✅ Simple update response:")
            print(f"   Success: {response.success}")
            print(f"   Message: {response.message}")
            
            # Verify
            time.sleep(1)
            updated_profile = self.sdk.get_travel_profile(self.login_id)
            
            if updated_profile.air_preferences:
                print(f"✅ Verified seat preference: {updated_profile.air_preferences.seat_preference}")
                self.assertEqual(updated_profile.air_preferences.seat_preference, SeatPreference.AISLE)
            else:
                self.fail("No air preferences found after simple update")
                
        except Exception as e:
            print(f"❌ Simple seat preference update failed: {e}")
            self.save_test_data({"error": str(e)}, "simple_seat_update_error")
            raise
    
    def test_04_debug_hotel_preferences_update(self):
        """Debug hotel preferences update"""
        print("\n🏨 Debugging hotel preferences update...")
        
        try:
            # Create new hotel preferences
            new_hotel_preferences = HotelPreferences(
                room_type=HotelRoomType.KING,
                hotel_other=f"Test hotel update {self.test_run_id}",
                prefer_gym=True,
                prefer_pool=False,
                prefer_foam_pillows=True
            )
            
            print(f"📝 New hotel preferences to set:")
            print(f"   Room Type: {new_hotel_preferences.room_type}")
            print(f"   Hotel Other: {new_hotel_preferences.hotel_other}")
            print(f"   Prefer Gym: {new_hotel_preferences.prefer_gym}")
            print(f"   Prefer Pool: {new_hotel_preferences.prefer_pool}")
            print(f"   Prefer Foam Pillows: {new_hotel_preferences.prefer_foam_pillows}")
            
            # Create travel profile for update
            update_profile = TravelProfile(
                login_id=self.login_id,
                hotel_preferences=new_hotel_preferences
            )
            
            # Generate XML
            xml_output = update_profile.to_update_xml(fields_to_update=["hotel_preferences"])
            print(f"\n📄 Hotel preferences XML:")
            print(f"{xml_output}")
            
            # Attempt the update
            print(f"\n🚀 Attempting hotel preferences update...")
            response = self.sdk.update_travel_profile(update_profile, fields_to_update=["hotel_preferences"])
            
            print(f"✅ Hotel update response:")
            print(f"   Success: {response.success}")
            print(f"   Message: {response.message}")
            
            # Verify
            time.sleep(2)
            updated_profile = self.sdk.get_travel_profile(self.login_id)
            
            if updated_profile.hotel_preferences:
                hotel = updated_profile.hotel_preferences
                print(f"✅ Updated hotel preferences verified:")
                print(f"   Room Type: {hotel.room_type}")
                print(f"   Hotel Other: {hotel.hotel_other}")
                print(f"   Prefer Gym: {hotel.prefer_gym}")
                
                self.assertEqual(hotel.room_type, HotelRoomType.KING)
                
            else:
                print(f"⚠️ No hotel preferences found after update")
                
        except Exception as e:
            print(f"❌ Hotel preferences update failed: {e}")
            self.save_test_data({"error": str(e)}, "hotel_preferences_update_error")
            raise
    
    def test_05_debug_combined_preferences_update(self):
        """Debug updating multiple preference types together"""
        print("\n🌟 Debugging combined preferences update...")
        
        try:
            # Create multiple preference types
            air_prefs = AirPreferences(
                seat_preference=SeatPreference.MIDDLE,
                home_airport="DFW"
            )
            
            hotel_prefs = HotelPreferences(
                room_type=HotelRoomType.DOUBLE,
                prefer_gym=False
            )
            
            car_prefs = CarPreferences(
                car_type=CarType.COMPACT,
                gps=True
            )
            
            print(f"📝 Combined preferences to set:")
            print(f"   Air - Seat: {air_prefs.seat_preference}, Airport: {air_prefs.home_airport}")
            print(f"   Hotel - Room: {hotel_prefs.room_type}, Gym: {hotel_prefs.prefer_gym}")
            print(f"   Car - Type: {car_prefs.car_type}, GPS: {car_prefs.gps}")
            
            # Create comprehensive travel profile
            update_profile = TravelProfile(
                login_id=self.login_id,
                air_preferences=air_prefs,
                hotel_preferences=hotel_prefs,
                car_preferences=car_prefs
            )
            
            # Generate XML
            xml_output = update_profile.to_update_xml(
                fields_to_update=["air_preferences", "hotel_preferences", "car_preferences"]
            )
            print(f"\n📄 Combined preferences XML (first 500 chars):")
            print(f"{xml_output[:500]}...")
            
            # Attempt the update
            print(f"\n🚀 Attempting combined preferences update...")
            response = self.sdk.update_travel_profile(
                update_profile, 
                fields_to_update=["air_preferences", "hotel_preferences", "car_preferences"]
            )
            
            print(f"✅ Combined update response:")
            print(f"   Success: {response.success}")
            print(f"   Message: {response.message}")
            
            # Verify all updates
            time.sleep(2)
            updated_profile = self.sdk.get_travel_profile(self.login_id)
            
            print(f"\n🔍 Verifying combined updates:")
            
            if updated_profile.air_preferences:
                print(f"   ✅ Air seat: {updated_profile.air_preferences.seat_preference}")
                self.assertEqual(updated_profile.air_preferences.seat_preference, SeatPreference.MIDDLE)
                
            if updated_profile.hotel_preferences:
                print(f"   ✅ Hotel room: {updated_profile.hotel_preferences.room_type}")
                self.assertEqual(updated_profile.hotel_preferences.room_type, HotelRoomType.DOUBLE)
                
            if updated_profile.car_preferences:
                print(f"   ✅ Car type: {updated_profile.car_preferences.car_type}")
                self.assertEqual(updated_profile.car_preferences.car_type, CarType.COMPACT)
                
        except Exception as e:
            print(f"❌ Combined preferences update failed: {e}")
            self.save_test_data({"error": str(e)}, "combined_preferences_update_error")
            raise
    
    def test_06_debug_api_endpoint_and_authentication(self):
        """Debug API endpoint configuration and authentication"""
        print("\n🔧 Debugging API endpoint and authentication...")
        
        try:
            # Check SDK configuration
            print(f"📊 SDK Configuration:")
            print(f"   Base URL: {self.sdk.base_url}")
            print(f"   Has access token: {bool(getattr(self.sdk, 'access_token', None))}")
            print(f"   Travel Profile endpoint: {self.sdk.base_url}/api/travelprofile/v2.0/profile")
            
            # Test authentication by getting current user
            current_user = self.sdk.get_current_user_identity()
            print(f"   ✅ Authentication working - User: {current_user.user_name}")
            
            # Test travel profile read access
            current_profile = self.sdk.get_travel_profile(self.login_id)
            print(f"   ✅ Travel profile read access working")
            
            # Create a minimal test update to check endpoint
            test_profile = TravelProfile(
                login_id=self.login_id,
                air_preferences=AirPreferences(home_airport="LAX")
            )
            
            # Generate XML but don't send yet
            xml_data = test_profile.to_update_xml(fields_to_update=["air_preferences"])
            print(f"   📄 Test XML generated successfully ({len(xml_data)} chars)")
            
            # Check if we can make the request (this will be the actual test)
            print(f"   🚀 Testing actual update request...")
            response = self.sdk.update_travel_profile(test_profile, fields_to_update=["air_preferences"])
            
            print(f"   ✅ Update request successful:")
            print(f"      Success: {response.success}")
            print(f"      Message: {response.message}")
            
        except Exception as e:
            print(f"❌ API endpoint/authentication debug failed: {e}")
            
            # Gather detailed error information
            error_details = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "sdk_base_url": getattr(self.sdk, 'base_url', 'unknown'),
                "has_access_token": bool(getattr(self.sdk, 'access_token', None)),
                "login_id": self.login_id
            }
            
            self.save_test_data(error_details, "api_debug_error")
            raise
    
    def test_07_debug_field_validation_patterns(self):
        """Debug specific field validation patterns to identify what works"""
        print("\n🔍 Debugging field validation patterns...")
        
        # Test simple, pattern-compliant values
        test_cases = [
            {
                "name": "minimal_air_prefs",
                "description": "Only seat preference and home airport",
                "air_prefs": AirPreferences(
                    seat_preference=SeatPreference.WINDOW,
                    home_airport="SEA"
                )
            },
            {
                "name": "simple_air_other",
                "description": "Simple air other text",
                "air_prefs": AirPreferences(
                    seat_preference=SeatPreference.AISLE,
                    air_other="Prefer morning flights"
                )
            },
            {
                "name": "no_air_other",
                "description": "All fields except air_other",
                "air_prefs": AirPreferences(
                    seat_preference=SeatPreference.MIDDLE,
                    seat_section=SeatSection.FORWARD,
                    meal_preference=MealType.VEGETARIAN,
                    home_airport="DFW"
                )
            },
            {
                "name": "short_air_other",
                "description": "Very short air other text",
                "air_prefs": AirPreferences(
                    seat_preference=SeatPreference.WINDOW,
                    air_other="Early flights"
                )
            }
        ]
        
        results = {}
        
        for test_case in test_cases:
            case_name = test_case["name"]
            print(f"\n🧪 Testing: {test_case['description']}")
            
            try:
                # Create test profile
                test_profile = TravelProfile(
                    login_id=self.login_id,
                    air_preferences=test_case["air_prefs"]
                )
                
                # Generate and inspect XML
                xml_output = test_profile.to_update_xml(fields_to_update=["air_preferences"])
                print(f"   📄 XML generated ({len(xml_output)} chars)")
                
                # Attempt the update
                print(f"   🚀 Attempting update...")
                response = self.sdk.update_travel_profile(test_profile, fields_to_update=["air_preferences"])
                
                print(f"   ✅ SUCCESS: {response.message}")
                results[case_name] = {
                    "success": True,
                    "message": response.message,
                    "xml_length": len(xml_output)
                }
                
                # Wait briefly between tests
                time.sleep(1)
                
            except Exception as e:
                print(f"   ❌ FAILED: {e}")
                results[case_name] = {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
        
        # Save results for analysis
        self.save_test_data(results, "field_validation_test_results")
        print(f"\n📊 Field validation test results:")
        for case_name, result in results.items():
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {case_name}: {result.get('message', result.get('error', 'Unknown'))}")
    
    def test_08_debug_safe_hotel_preferences(self):
        """Debug hotel preferences with only known-safe fields"""
        print("\n🏨 Debugging safe hotel preferences (avoiding problematic fields)...")
        
        # Based on the guide, avoid smoking_preference and prefer_restaurant
        try:
            safe_hotel_preferences = HotelPreferences(
                room_type=HotelRoomType.KING,
                prefer_gym=True,
                prefer_pool=True,
                prefer_foam_pillows=True,
                prefer_early_checkin=True
                # Explicitly avoiding:
                # - smoking_preference (causes validation errors)
                # - prefer_restaurant (causes validation errors)
                # - hotel_other (might have pattern validation)
            )
            
            print(f"📝 Safe hotel preferences:")
            print(f"   Room Type: {safe_hotel_preferences.room_type}")
            print(f"   Prefer Gym: {safe_hotel_preferences.prefer_gym}")
            print(f"   Prefer Pool: {safe_hotel_preferences.prefer_pool}")
            print(f"   Prefer Foam Pillows: {safe_hotel_preferences.prefer_foam_pillows}")
            print(f"   Prefer Early Checkin: {safe_hotel_preferences.prefer_early_checkin}")
            
            # Create travel profile for update
            update_profile = TravelProfile(
                login_id=self.login_id,
                hotel_preferences=safe_hotel_preferences
            )
            
            # Generate XML
            xml_output = update_profile.to_update_xml(fields_to_update=["hotel_preferences"])
            print(f"\n📄 Safe hotel preferences XML:")
            print(f"{xml_output}")
            
            # Attempt the update
            print(f"\n🚀 Attempting safe hotel preferences update...")
            response = self.sdk.update_travel_profile(update_profile, fields_to_update=["hotel_preferences"])
            
            print(f"✅ Safe hotel update response:")
            print(f"   Success: {response.success}")
            print(f"   Message: {response.message}")
            
            # Verify
            time.sleep(2)
            updated_profile = self.sdk.get_travel_profile(self.login_id)
            
            if updated_profile.hotel_preferences:
                hotel = updated_profile.hotel_preferences
                print(f"✅ Updated safe hotel preferences verified:")
                print(f"   Room Type: {hotel.room_type}")
                print(f"   Prefer Gym: {hotel.prefer_gym}")
                
                self.assertEqual(hotel.room_type, HotelRoomType.KING)
                
            else:
                print(f"⚠️ No hotel preferences found after safe update")
                
        except Exception as e:
            print(f"❌ Safe hotel preferences update failed: {e}")
            self.save_test_data({"error": str(e)}, "safe_hotel_preferences_error")
            raise
    
    def test_09_debug_minimal_working_preferences(self):
        """Test the absolute minimal preferences that should work"""
        print("\n🎯 Testing minimal working preferences...")
        
        try:
            # Test 1: Just seat preference
            print(f"\n📝 Test 1: Just seat preference")
            minimal_air = AirPreferences(seat_preference=SeatPreference.WINDOW)
            air_profile = TravelProfile(login_id=self.login_id, air_preferences=minimal_air)
            response1 = self.sdk.update_travel_profile(air_profile, fields_to_update=["air_preferences"])
            print(f"   ✅ Seat only: {response1.success} - {response1.message}")
            
            time.sleep(1)
            
            # Test 2: Just home airport
            print(f"\n📝 Test 2: Just home airport")
            airport_air = AirPreferences(home_airport="NYC")
            airport_profile = TravelProfile(login_id=self.login_id, air_preferences=airport_air)
            response2 = self.sdk.update_travel_profile(airport_profile, fields_to_update=["air_preferences"])
            print(f"   ✅ Airport only: {response2.success} - {response2.message}")
            
            time.sleep(1)
            
            # Test 3: Just meal preference
            print(f"\n📝 Test 3: Just meal preference")
            meal_air = AirPreferences(meal_preference=MealType.VEGETARIAN)
            meal_profile = TravelProfile(login_id=self.login_id, air_preferences=meal_air)
            response3 = self.sdk.update_travel_profile(meal_profile, fields_to_update=["air_preferences"])
            print(f"   ✅ Meal only: {response3.success} - {response3.message}")
            
            time.sleep(1)
            
            # Test 4: Just hotel room type
            print(f"\n📝 Test 4: Just hotel room type")
            minimal_hotel = HotelPreferences(room_type=HotelRoomType.DOUBLE)
            hotel_profile = TravelProfile(login_id=self.login_id, hotel_preferences=minimal_hotel)
            response4 = self.sdk.update_travel_profile(hotel_profile, fields_to_update=["hotel_preferences"])
            print(f"   ✅ Hotel room only: {response4.success} - {response4.message}")
            
            time.sleep(1)
            
            # Test 5: Just car type
            print(f"\n📝 Test 5: Just car type")
            minimal_car = CarPreferences(car_type=CarType.ECONOMY)
            car_profile = TravelProfile(login_id=self.login_id, car_preferences=minimal_car)
            response5 = self.sdk.update_travel_profile(car_profile, fields_to_update=["car_preferences"])
            print(f"   ✅ Car type only: {response5.success} - {response5.message}")
            
            # Verify final state
            print(f"\n🔍 Verifying final state...")
            final_profile = self.sdk.get_travel_profile(self.login_id)
            
            if final_profile.air_preferences:
                print(f"   ✅ Air preferences exist")
            if final_profile.hotel_preferences:
                print(f"   ✅ Hotel preferences exist")
            if final_profile.car_preferences:
                print(f"   ✅ Car preferences exist")
            
            results = {
                "seat_only": response1.success,
                "airport_only": response2.success,
                "meal_only": response3.success,
                "hotel_room_only": response4.success,
                "car_type_only": response5.success
            }
            
            self.save_test_data(results, "minimal_preferences_test_results")
            print(f"✅ All minimal preference tests completed successfully")
            
        except Exception as e:
            print(f"❌ Minimal preferences test failed: {e}")
            self.save_test_data({"error": str(e)}, "minimal_preferences_error")
            raise


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2) 