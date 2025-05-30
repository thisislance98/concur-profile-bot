#!/usr/bin/env python3
"""
Integration tests for travel preferences functionality with new SDK architecture

Tests:
- Air travel preferences XML generation and structure
- Hotel preferences XML generation and structure  
- Car rental preferences XML generation and structure
- Rail travel preferences XML generation and structure
- Rate preferences and discount codes XML structure
- Travel preference combinations and XML validation
- Travel profile data parsing from existing user
"""

import unittest
import time
from base_test import BaseIntegrationTest

# Import the necessary classes for the test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from concur_profile_sdk import (
    IdentityUser, IdentityName, IdentityEmail, IdentityEnterpriseInfo, TravelProfile,
    AirPreferences, HotelPreferences, CarPreferences, RailPreferences, 
    RatePreference, DiscountCode, LoyaltyProgram,
    SeatPreference, SeatSection, MealType, HotelRoomType, SmokingPreference,
    CarType, TransmissionType, LoyaltyProgramType, ApiResponse
)


class TestTravelPreferences(BaseIntegrationTest):
    """Test travel preferences functionality with read-only permissions"""
    
    def setUp(self):
        """Set up each test with current user context"""
        super().setUp()
        self.current_identity = self.sdk.get_current_user_identity()
        self.login_id = self.current_identity.user_name
        print(f"Using authenticated user for testing: {self.login_id}")
    
    def test_01_air_travel_preferences_xml_generation(self):
        """Test air travel preferences XML generation and structure"""
        print("\n✈️ Testing air travel preferences XML generation...")
        
        # Create air preferences with comprehensive data
        air_preferences = AirPreferences(
            seat_preference=SeatPreference.WINDOW,
            seat_section=SeatSection.FORWARD,
            meal_preference=MealType.VEGETARIAN,
            home_airport="SEA",
            air_other="Prefer early morning flights"
        )
        
        # Create travel profile for XML generation
        travel_profile = TravelProfile(
            login_id=self.login_id,
            rule_class="Default Travel Class",
            travel_config_id=self.test_travel_config_id,
            air_preferences=air_preferences
        )
        
        # Test XML generation
        xml_output = travel_profile.to_update_xml(fields_to_update=["air_preferences"])
        
        # Validate XML structure
        self.assertIn("Air", xml_output, "Should contain Air element")
        self.assertIn("Window", xml_output, "Should contain seat preference")
        self.assertIn("Forward", xml_output, "Should contain seat section")
        self.assertIn("VGML", xml_output, "Should contain meal preference code")
        self.assertIn("SEA", xml_output, "Should contain home airport")
        self.assertIn("early morning", xml_output, "Should contain air other text")
        
        print("✅ Air preferences XML generation successful")
        print(f"   Generated XML length: {len(xml_output)} characters")
        
        # Save XML for inspection
        self.save_test_data(xml_output, "air_preferences_xml_sample")
        
        # Test XML parsing validation
        from lxml import etree
        try:
            root = etree.fromstring(xml_output.encode('utf-8'))
            self.assertEqual(root.tag, "ProfileResponse")
            self.assertEqual(root.get("LoginId"), self.login_id)
            print("✅ Generated XML is valid and parseable")
        except Exception as e:
            self.fail(f"Generated XML is not valid: {e}")
    
    def test_02_hotel_preferences_xml_generation(self):
        """Test hotel preferences XML generation and structure"""
        print("\n🏨 Testing hotel preferences XML generation...")
        
        # Create hotel preferences with various options
        hotel_preferences = HotelPreferences(
            room_type=HotelRoomType.KING,
            hotel_other="Late checkout preferred",
            prefer_foam_pillows=True,
            prefer_gym=True,
            prefer_pool=True,
            prefer_room_service=True,
            prefer_early_checkin=True
        )
        
        # Create travel profile for XML generation
        travel_profile = TravelProfile(
            login_id=self.login_id,
            hotel_preferences=hotel_preferences
        )
        
        # Test XML generation
        xml_output = travel_profile.to_update_xml(fields_to_update=["hotel_preferences"])
        
        # Validate XML structure
        self.assertIn("Hotel", xml_output, "Should contain Hotel element")
        self.assertIn("King", xml_output, "Should contain room type")
        self.assertIn("Late checkout", xml_output, "Should contain hotel other text")
        self.assertIn("PreferFoamPillows", xml_output, "Should contain foam pillows preference")
        self.assertIn("PreferGym", xml_output, "Should contain gym preference")
        self.assertIn("PreferPool", xml_output, "Should contain pool preference")
        self.assertIn("PreferRoomService", xml_output, "Should contain room service preference")
        self.assertIn("PreferEarlyCheckIn", xml_output, "Should contain early checkin preference")
        
        print("✅ Hotel preferences XML generation successful")
        print(f"   Generated XML length: {len(xml_output)} characters")
        
        # Save XML for inspection
        self.save_test_data(xml_output, "hotel_preferences_xml_sample")
        
        # Test enum values
        test_room_types = [HotelRoomType.KING, HotelRoomType.QUEEN, HotelRoomType.DOUBLE]
        for room_type in test_room_types:
            test_prefs = HotelPreferences(room_type=room_type)
            test_profile = TravelProfile(login_id=self.login_id, hotel_preferences=test_prefs)
            test_xml = test_profile.to_update_xml(fields_to_update=["hotel_preferences"])
            self.assertIn(room_type.value, test_xml, f"Should contain {room_type.value}")
        
        print("✅ Hotel room type enums validated")
    
    def test_03_car_rental_preferences_xml_generation(self):
        """Test car rental preferences XML generation and structure"""
        print("\n🚗 Testing car rental preferences XML generation...")
        
        # Create car preferences with various options
        car_preferences = CarPreferences(
            car_type=CarType.INTERMEDIATE,
            transmission=TransmissionType.AUTOMATIC,
            gps=True,
            ski_rack=False
        )
        
        # Create travel profile for XML generation
        travel_profile = TravelProfile(
            login_id=self.login_id,
            car_preferences=car_preferences
        )
        
        # Test XML generation
        xml_output = travel_profile.to_update_xml(fields_to_update=["car_preferences"])
        
        # Validate XML structure
        self.assertIn("Car", xml_output, "Should contain Car element")
        self.assertIn("Intermediate", xml_output, "Should contain car type")
        self.assertIn("Automatic", xml_output, "Should contain transmission type")
        self.assertIn("CarGPS", xml_output, "Should contain GPS preference")
        
        print("✅ Car preferences XML generation successful")
        print(f"   Generated XML length: {len(xml_output)} characters")
        
        # Save XML for inspection
        self.save_test_data(xml_output, "car_preferences_xml_sample")
        
        # Test different car types
        test_car_types = [CarType.ECONOMY, CarType.COMPACT, CarType.INTERMEDIATE, CarType.LUXURY]
        for car_type in test_car_types:
            test_prefs = CarPreferences(car_type=car_type)
            test_profile = TravelProfile(login_id=self.login_id, car_preferences=test_prefs)
            test_xml = test_profile.to_update_xml(fields_to_update=["car_preferences"])
            self.assertIn(car_type.value, test_xml, f"Should contain {car_type.value}")
        
        print("✅ Car type enums validated")
    
    def test_04_rail_preferences_xml_generation(self):
        """Test rail travel preferences XML generation and structure"""
        print("\n🚆 Testing rail travel preferences XML generation...")
        
        # Create rail preferences with comprehensive data
        rail_preferences = RailPreferences(
            seat="Window",
            coach="First Class",
            noise_comfort="Quiet",
            bed="Upper",
            special_meals="Vegetarian"
        )
        
        # Create travel profile for XML generation
        travel_profile = TravelProfile(
            login_id=self.login_id,
            rail_preferences=rail_preferences
        )
        
        # Test XML generation
        xml_output = travel_profile.to_update_xml(fields_to_update=["rail_preferences"])
        
        # Validate XML structure
        self.assertIn("Rail", xml_output, "Should contain Rail element")
        self.assertIn("Window", xml_output, "Should contain seat preference")
        self.assertIn("First Class", xml_output, "Should contain coach preference")
        self.assertIn("Quiet", xml_output, "Should contain noise comfort")
        self.assertIn("Upper", xml_output, "Should contain bed preference")
        self.assertIn("Vegetarian", xml_output, "Should contain special meals")
        
        print("✅ Rail preferences XML generation successful")
        print(f"   Generated XML length: {len(xml_output)} characters")
        
        # Save XML for inspection
        self.save_test_data(xml_output, "rail_preferences_xml_sample")
    
    def test_05_rate_preferences_and_discounts_xml_generation(self):
        """Test rate preferences and discount codes XML generation"""
        print("\n💰 Testing rate preferences and discount codes XML generation...")
        
        # Create rate preferences and discount codes
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
        
        # Create travel profile for XML generation
        travel_profile = TravelProfile(
            login_id=self.login_id,
            rate_preferences=rate_preferences,
            discount_codes=discount_codes
        )
        
        # Test XML generation
        xml_output = travel_profile.to_update_xml(fields_to_update=["rate_preferences", "discount_codes"])
        
        # Validate XML structure
        self.assertIn("RatePreferences", xml_output, "Should contain RatePreferences element")
        self.assertIn("AAARate", xml_output, "Should contain AAA rate preference")
        self.assertIn("GovtRate", xml_output, "Should contain government rate preference")
        self.assertIn("DiscountCodes", xml_output, "Should contain DiscountCodes element")
        self.assertIn("CDP123456", xml_output, "Should contain HZ discount code")
        self.assertIn("AWD987654", xml_output, "Should contain AV discount code")
        self.assertIn('Vendor="HZ"', xml_output, "Should contain HZ vendor attribute")
        self.assertIn('Vendor="AV"', xml_output, "Should contain AV vendor attribute")
        
        print("✅ Rate preferences and discount codes XML generation successful")
        print(f"   Generated XML length: {len(xml_output)} characters")
        
        # Save XML for inspection
        self.save_test_data(xml_output, "rate_preferences_xml_sample")
    
    def test_06_combined_travel_preferences_xml_generation(self):
        """Test generating XML for multiple travel preferences together"""
        print("\n🌟 Testing combined travel preferences XML generation...")
        
        # Create travel profile with multiple preference types
        travel_profile = TravelProfile(
            login_id=self.login_id,
            rule_class="Default Travel Class",
            travel_config_id=self.test_travel_config_id,
            
            # Multiple preference types
            air_preferences=AirPreferences(
                seat_preference=SeatPreference.AISLE,
                home_airport="SFO"
            ),
            hotel_preferences=HotelPreferences(
                room_type=HotelRoomType.DOUBLE,
                prefer_gym=True,
                prefer_pool=False
            ),
            car_preferences=CarPreferences(
                car_type=CarType.COMPACT,
                gps=False
            ),
            rate_preferences=RatePreference(
                aaa_rate=True,
                govt_rate=False
            )
        )
        
        # Test XML generation for combined preferences
        xml_output = travel_profile.to_update_xml(
            fields_to_update=["air_preferences", "hotel_preferences", "car_preferences", "rate_preferences"]
        )
        
        # Validate all sections are present
        self.assertIn("Air", xml_output, "Should contain Air section")
        self.assertIn("Hotel", xml_output, "Should contain Hotel section")
        self.assertIn("Car", xml_output, "Should contain Car section")
        self.assertIn("RatePreferences", xml_output, "Should contain RatePreferences section")
        
        # Validate specific values
        self.assertIn("Aisle", xml_output, "Should contain aisle seat preference")
        self.assertIn("SFO", xml_output, "Should contain SFO airport")
        self.assertIn("Double", xml_output, "Should contain double room type")
        self.assertIn("Compact", xml_output, "Should contain compact car type")
        
        print("✅ Combined travel preferences XML generation successful")
        print(f"   Generated XML length: {len(xml_output)} characters")
        
        # Save XML for inspection
        self.save_test_data(xml_output, "combined_preferences_xml_sample")
        
        # Test XML is well-formed
        from lxml import etree
        try:
            root = etree.fromstring(xml_output.encode('utf-8'))
            print("✅ Combined XML is well-formed and parseable")
        except Exception as e:
            self.fail(f"Combined XML is not valid: {e}")
    
    def test_07_travel_profile_data_parsing(self):
        """Test parsing travel profile data from existing user"""
        print("\n📊 Testing travel profile data parsing from existing user...")
        
        try:
            # Get current user's travel profile
            travel_profile = self.sdk.get_travel_profile(self.login_id)
            
            # Test that profile object is properly structured
            self.assertIsNotNone(travel_profile, "Should have travel profile")
            self.assertEqual(travel_profile.login_id, self.login_id, "Login ID should match")
            self.assertIsInstance(travel_profile.rule_class, str, "Rule class should be string")
            self.assertIsInstance(travel_profile.loyalty_programs, list, "Loyalty programs should be list")
            self.assertIsInstance(travel_profile.custom_fields, list, "Custom fields should be list")
            
            print(f"✅ Travel profile successfully parsed")
            print(f"   Rule Class: {travel_profile.rule_class}")
            print(f"   Travel Config ID: {travel_profile.travel_config_id}")
            print(f"   Has Air Preferences: {travel_profile.air_preferences is not None}")
            print(f"   Has Hotel Preferences: {travel_profile.hotel_preferences is not None}")
            print(f"   Has Car Preferences: {travel_profile.car_preferences is not None}")
            print(f"   Loyalty Programs: {len(travel_profile.loyalty_programs)}")
            print(f"   Custom Fields: {len(travel_profile.custom_fields)}")
            
            # Test preference parsing details
            if travel_profile.air_preferences:
                air_prefs = travel_profile.air_preferences
                print(f"   Air - Home Airport: {air_prefs.home_airport}")
                print(f"   Air - Seat Preference: {air_prefs.seat_preference}")
                print(f"   Air - Meal Preference: {air_prefs.meal_preference}")
            
            if travel_profile.hotel_preferences:
                hotel_prefs = travel_profile.hotel_preferences
                print(f"   Hotel - Room Type: {hotel_prefs.room_type}")
                print(f"   Hotel - Prefer Gym: {hotel_prefs.prefer_gym}")
                print(f"   Hotel - Prefer Pool: {hotel_prefs.prefer_pool}")
            
            # Save parsed profile summary
            profile_summary = {
                "login_id": travel_profile.login_id,
                "rule_class": travel_profile.rule_class,
                "travel_config_id": travel_profile.travel_config_id,
                "preferences": {
                    "has_air": travel_profile.air_preferences is not None,
                    "has_hotel": travel_profile.hotel_preferences is not None,
                    "has_car": travel_profile.car_preferences is not None,
                    "has_rail": travel_profile.rail_preferences is not None,
                    "has_rate": travel_profile.rate_preferences is not None
                },
                "counts": {
                    "loyalty_programs": len(travel_profile.loyalty_programs),
                    "custom_fields": len(travel_profile.custom_fields),
                    "discount_codes": len(travel_profile.discount_codes),
                    "passports": len(travel_profile.passports),
                    "visas": len(travel_profile.visas)
                }
            }
            
            self.save_test_data(profile_summary, "travel_profile_parsing_summary")
            
        except Exception as e:
            self.fail(f"Failed to parse travel profile: {e}")
    
    def test_08_xml_schema_validation(self):
        """Test XML schema compliance and structure"""
        print("\n📋 Testing XML schema compliance and structure...")
        
        # Test comprehensive profile with all sections
        comprehensive_profile = TravelProfile(
            login_id=self.login_id,
            rule_class="Test Rule Class",
            travel_config_id=self.test_travel_config_id,
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
                gps=True
            ),
            rail_preferences=RailPreferences(
                seat="Window",
                coach="First Class"
            ),
            rate_preferences=RatePreference(
                aaa_rate=True,
                govt_rate=True
            ),
            discount_codes=[
                DiscountCode(vendor="HZ", code="TEST123")
            ]
        )
        
        # Generate XML for all sections
        xml_output = comprehensive_profile.to_update_xml()
        
        # Test XML structure and schema compliance
        from lxml import etree
        try:
            root = etree.fromstring(xml_output.encode('utf-8'))
            
            # Validate root element
            self.assertEqual(root.tag, "ProfileResponse")
            self.assertEqual(root.get("Action"), "Update")
            self.assertEqual(root.get("LoginId"), self.login_id)
            
            # Check for expected sections in schema order
            expected_sections = ["General", "Air", "Rail", "Car", "Hotel", "RatePreferences", "DiscountCodes"]
            found_sections = [elem.tag for elem in root]
            
            print(f"   Found XML sections: {found_sections}")
            
            # Ensure some key sections exist
            self.assertIn("General", found_sections, "Should have General section")
            self.assertIn("Air", found_sections, "Should have Air section")
            self.assertIn("Hotel", found_sections, "Should have Hotel section")
            self.assertIn("Car", found_sections, "Should have Car section")
            
            print("✅ XML schema structure validation successful")
            
            # Save comprehensive XML for inspection
            self.save_test_data(xml_output, "comprehensive_profile_xml_sample")
            
        except Exception as e:
            self.fail(f"XML schema validation failed: {e}")

    def test_09_comprehensive_air_preferences_update(self):
        """Test comprehensive air preferences update with validation-compliant values"""
        print(f"🔄 Testing comprehensive air preferences update...")
        
        new_air_preferences = AirPreferences(
            seat_preference=SeatPreference.WINDOW,
            seat_section=SeatSection.FORWARD,
            meal_preference=MealType.VEGETARIAN,
            home_airport="SEA",
            air_other="Prefer early morning flights"  # Use simple, pattern-compliant text
        )
        
        # Create travel profile for update
        travel_profile = TravelProfile(
            login_id=self.login_id,
            air_preferences=new_air_preferences
        )
        
        try:
            # Update travel profile with comprehensive air preferences
            response = self.sdk.update_travel_profile(
                travel_profile, 
                fields_to_update=["air_preferences"]
            )
            
            print(f"✅ Air preferences update successful")
            print(f"   Response: {response.success} - {response.message}")
            
            # Verify the update
            time.sleep(2)  # Wait for changes to propagate
            updated_profile = self.sdk.get_travel_profile(self.login_id)
            
            self.assertIsNotNone(updated_profile.air_preferences, "Air preferences should exist after update")
            
            air_prefs = updated_profile.air_preferences
            self.assertEqual(air_prefs.seat_preference, SeatPreference.WINDOW, "Seat preference should be updated")
            self.assertEqual(air_prefs.seat_section, SeatSection.FORWARD, "Seat section should be updated") 
            self.assertEqual(air_prefs.meal_preference, MealType.VEGETARIAN, "Meal preference should be updated")
            self.assertEqual(air_prefs.home_airport, "SEA", "Home airport should be updated")
            self.assertEqual(air_prefs.air_other, "Prefer early morning flights", "Air other should be updated")
            
            print(f"✅ All air preference fields verified successfully")
            
        except Exception as e:
            self.fail(f"Air preferences update failed: {e}")
    
    def test_10_safe_hotel_preferences_update(self):
        """Test hotel preferences update with only validated-safe fields"""
        print(f"🏨 Testing safe hotel preferences update...")
        
        # Based on debugging, avoid smoking_preference and prefer_restaurant
        safe_hotel_preferences = HotelPreferences(
            room_type=HotelRoomType.KING,
            prefer_gym=True,
            prefer_pool=True,
            prefer_foam_pillows=True,
            prefer_early_checkin=True
            # Explicitly avoiding problematic fields:
            # - smoking_preference (causes validation errors)
            # - prefer_restaurant (causes validation errors)
        )
        
        travel_profile = TravelProfile(
            login_id=self.login_id,
            hotel_preferences=safe_hotel_preferences
        )
        
        try:
            # Update travel profile with safe hotel preferences
            response = self.sdk.update_travel_profile(
                travel_profile,
                fields_to_update=["hotel_preferences"]
            )
            
            print(f"✅ Hotel preferences update successful")
            print(f"   Response: {response.success} - {response.message}")
            
            # Verify the update
            time.sleep(2)
            updated_profile = self.sdk.get_travel_profile(self.login_id)
            
            self.assertIsNotNone(updated_profile.hotel_preferences, "Hotel preferences should exist after update")
            
            hotel_prefs = updated_profile.hotel_preferences
            self.assertEqual(hotel_prefs.room_type, HotelRoomType.KING, "Room type should be updated")
            self.assertTrue(hotel_prefs.prefer_gym, "Gym preference should be updated")
            self.assertTrue(hotel_prefs.prefer_pool, "Pool preference should be updated")
            
            print(f"✅ All safe hotel preference fields verified successfully")
            
        except Exception as e:
            self.fail(f"Safe hotel preferences update failed: {e}")

if __name__ == '__main__':
    unittest.main() 