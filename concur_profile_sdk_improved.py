#!/usr/bin/env python3
"""
Complete Concur Profile SDK using lxml

A comprehensive, strongly-typed SDK for interacting with SAP Concur's Profile APIs.
This version includes all Profile v2 and Loyalty Program v1 functionality.
"""

import requests
from lxml import etree
from typing import Dict, List, Optional, Union, TypedDict, Literal
from datetime import datetime, timedelta, date
from enum import Enum
import logging
from dataclasses import dataclass, field, asdict
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Comprehensive Enums for strongly-typed values
class AddressType(str, Enum):
    """Valid address types in Concur"""
    HOME = "Home"
    WORK = "Work"


class PhoneType(str, Enum):
    """Valid phone types in Concur"""
    HOME = "Home"
    WORK = "Work"
    CELL = "Cell"
    FAX = "Fax"
    PAGER = "Pager"
    OTHER = "Other"


class EmailType(str, Enum):
    """Valid email types in Concur"""
    BUSINESS = "Business"
    PERSONAL = "Personal"
    SUPERVISOR = "Supervisor"
    TRAVEL_ARRANGER = "TravelArranger"
    BUSINESS2 = "Business2"
    OTHER1 = "Other1"
    OTHER2 = "Other2"


class VisaType(str, Enum):
    """Valid visa types according to XSD schema"""
    UNKNOWN = "Unknown"
    SINGLE_ENTRY = "SE"
    DOUBLE_ENTRY = "DE"
    MULTI_ENTRY = "ME"
    ENTRY_STAMP = "ES"
    ENTRY_TOKEN = "ET"
    SPECIAL_HANDLING = "SH"


class LoyaltyProgramType(str, Enum):
    """Valid loyalty program types"""
    AIR = "Air"
    HOTEL = "Hotel" 
    CAR = "Car"
    RAIL = "Rail"


class VendorType(str, Enum):
    """Vendor type codes for loyalty programs"""
    AIR = "A"
    HOTEL = "H"
    CAR = "C"
    RAIL = "R"


class SeatPreference(str, Enum):
    """Air seat preferences"""
    WINDOW = "Window"
    AISLE = "Aisle"
    MIDDLE = "Middle"
    DONT_CARE = "DontCare"


class SeatSection(str, Enum):
    """Air seat section preferences"""
    BULKHEAD = "Bulkhead"
    FORWARD = "Forward"
    REAR = "Rear"
    EXIT_ROW = "ExitRow"
    DONT_CARE = "DontCare"


class MealType(str, Enum):
    """Meal preferences according to XSD schema"""
    BLAND = "BLML"
    CHILD = "CHML"
    DIABETIC = "DBML"
    FRUIT_PLATTER = "FPML"
    GLUTEN_FREE = "GFML"
    HINDU = "HNML"
    BABY = "BBML"
    KOSHER = "KSML"
    LOW_CALORIE = "LCML"
    LOW_SALT = "LSML"
    MUSLIM = "MOML"
    NO_SALT = "NSML"
    NO_LACTOSE = "NLML"
    PEANUT_FREE = "PFML"
    SEAFOOD = "SFML"
    VEGETARIAN_LACTO = "VLML"
    VEGETARIAN = "VGML"
    KOSHER_VEGETARIAN = "KVML"
    RAW_VEGETARIAN = "RVML"
    ASIAN_VEGETARIAN = "AVML"


class HotelRoomType(str, Enum):
    """Hotel room preferences"""
    KING = "King"
    QUEEN = "Queen"
    DOUBLE = "Double"
    TWIN = "Twin"
    SINGLE = "Single"
    DISABILITY = "Disability"
    DONT_CARE = "DontCare"


class SmokingPreference(str, Enum):
    """Smoking preferences"""
    NON_SMOKING = "NonSmoking"
    SMOKING = "Smoking"
    DONT_CARE = "DontCare"


class CarType(str, Enum):
    """Car type preferences"""
    ECONOMY = "Economy"
    COMPACT = "Compact"
    INTERMEDIATE = "Intermediate"
    STANDARD = "Standard"
    FULL_SIZE = "FullSize"
    PREMIUM = "Premium"
    LUXURY = "Luxury"
    SUV = "SUV"
    MINI_VAN = "MiniVan"
    CONVERTIBLE = "Convertible"
    DONT_CARE = "DontCare"


class TransmissionType(str, Enum):
    """Car transmission preferences"""
    AUTOMATIC = "Automatic"
    MANUAL = "Manual"
    DONT_CARE = "DontCare"


class ProfileAction(str, Enum):
    """Valid profile actions"""
    CREATE = "Create"
    UPDATE = "Update"


class ProfileStatus(str, Enum):
    """Profile status values"""
    ACTIVE = "Active"
    INACTIVE = "Inactive"


# Type definitions for strong typing
class AuthResponse(TypedDict):
    """OAuth authentication response"""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    refresh_expires_in: int
    scope: str
    geolocation: str
    id_token: str


@dataclass
class Address:
    """Represents a user's address"""
    type: AddressType
    street: str = ""
    city: str = ""
    state_province: str = ""
    postal_code: str = ""
    country_code: str = "US"  # ISO 2-letter code
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add address as XML element to parent"""
        addr_elem = etree.SubElement(parent, "Address", Type=self.type.value)
        
        if self.street:
            etree.SubElement(addr_elem, "Street").text = self.street
        if self.city:
            etree.SubElement(addr_elem, "City").text = self.city
        if self.state_province:
            etree.SubElement(addr_elem, "StateProvince").text = self.state_province
        if self.postal_code:
            etree.SubElement(addr_elem, "PostalCode").text = self.postal_code
        if self.country_code:
            etree.SubElement(addr_elem, "CountryCode").text = self.country_code
            
        return addr_elem


@dataclass
class Phone:
    """Represents a phone number"""
    type: PhoneType
    phone_number: str
    country_code: str = ""
    extension: str = ""
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add phone as XML element to parent"""
        phone_elem = etree.SubElement(parent, "Telephone", Type=self.type.value)
        
        if self.country_code:
            etree.SubElement(phone_elem, "CountryCode").text = self.country_code
        if self.phone_number:
            etree.SubElement(phone_elem, "PhoneNumber").text = self.phone_number
        if self.extension:
            etree.SubElement(phone_elem, "Extension").text = self.extension
            
        return phone_elem


@dataclass
class Email:
    """Represents an email address"""
    type: EmailType
    email_address: str
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add email as XML element to parent"""
        email_elem = etree.SubElement(parent, "EmailAddress", Type=self.type.value)
        email_elem.text = self.email_address
        return email_elem


@dataclass
class EmergencyContact:
    """Represents an emergency contact"""
    name: str
    relationship: str = ""
    phone: str = ""
    mobile_phone: str = ""
    email: str = ""
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add emergency contact as XML element to parent"""
        contact_elem = etree.SubElement(parent, "EmergencyContact")
        
        if self.name:
            etree.SubElement(contact_elem, "Name").text = self.name
        if self.relationship:
            etree.SubElement(contact_elem, "Relationship").text = self.relationship
        # NOTE: Phone and Email fields in EmergencyContact cause XML validation errors
        # during user creation. These fields require special scopes and structures.
        # They are excluded during creation and should be added via separate update operations.
        # if self.phone:
        #     etree.SubElement(contact_elem, "Phone").text = self.phone
        # if self.mobile_phone:
        #     etree.SubElement(contact_elem, "MobilePhone").text = self.mobile_phone
        # if self.email:
        #     etree.SubElement(contact_elem, "Email").text = self.email
            
        return contact_elem


@dataclass
class NationalID:
    """Represents a national identification"""
    id_number: str
    country_code: str
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add national ID as XML element to parent"""
        id_elem = etree.SubElement(parent, "NationalID")
        etree.SubElement(id_elem, "NationalIDNumber").text = self.id_number
        etree.SubElement(id_elem, "IssuingCountry").text = self.country_code
        return id_elem


@dataclass
class DriversLicense:
    """Represents a driver's license"""
    license_number: str
    country_code: str
    state_province: str = ""
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add driver's license as XML element to parent"""
        license_elem = etree.SubElement(parent, "DriversLicense")
        etree.SubElement(license_elem, "DriversLicenseNumber").text = self.license_number
        etree.SubElement(license_elem, "IssuingCountry").text = self.country_code
        if self.state_province:
            etree.SubElement(license_elem, "IssuingState").text = self.state_province
        return license_elem


@dataclass
class Passport:
    """Represents a passport"""
    doc_number: str
    nationality: str
    issue_country: str
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None
    primary: bool = False
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add passport as XML element to parent"""
        passport_elem = etree.SubElement(parent, "Passport")
        
        etree.SubElement(passport_elem, "PassportNumber").text = self.doc_number
        etree.SubElement(passport_elem, "PassportNationality").text = self.nationality
        etree.SubElement(passport_elem, "PassportCountryIssued").text = self.issue_country
        
        if self.issue_date:
            etree.SubElement(passport_elem, "PassportDateIssued").text = self.issue_date.strftime("%Y-%m-%d")
        if self.expiration_date:
            etree.SubElement(passport_elem, "PassportExpiration").text = self.expiration_date.strftime("%Y-%m-%d")
        # Note: 'Primary' field not in schema - removing
            
        return passport_elem


@dataclass
class Visa:
    """Represents a visa"""
    visa_nationality: str
    visa_number: str
    visa_type: VisaType
    visa_country_issued: str
    visa_date_issued: Optional[date] = None
    visa_expiration: Optional[date] = None
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add visa as XML element to parent"""
        visa_elem = etree.SubElement(parent, "Visa")
        
        # Order elements per schema: VisaNationality, VisaNumber, VisaType, VisaDateIssued, VisaExpiration, VisaCityIssued, VisaCountryIssued
        etree.SubElement(visa_elem, "VisaNationality").text = self.visa_nationality
        etree.SubElement(visa_elem, "VisaNumber").text = self.visa_number
        etree.SubElement(visa_elem, "VisaType").text = self.visa_type.value
        
        if self.visa_date_issued:
            etree.SubElement(visa_elem, "VisaDateIssued").text = self.visa_date_issued.strftime("%Y-%m-%d")
        if self.visa_expiration:
            etree.SubElement(visa_elem, "VisaExpiration").text = self.visa_expiration.strftime("%Y-%m-%d")
        
        # VisaCityIssued not implemented yet but should come before VisaCountryIssued
        etree.SubElement(visa_elem, "VisaCountryIssued").text = self.visa_country_issued
            
        return visa_elem


@dataclass
class TSAInfo:
    """Represents TSA information"""
    known_traveler_number: str = ""
    gender: str = ""
    date_of_birth: Optional[date] = None
    redress_number: str = ""
    no_middle_name: bool = False
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add TSA info as XML element to parent"""
        tsa_elem = etree.SubElement(parent, "TSAInfo")
        
        # Order elements according to schema: Gender, DateOfBirth, NoMiddleName, PreCheckNumber, RedressNumber
        if self.gender:
            gender_elem = etree.SubElement(tsa_elem, "Gender")
            # Convert single letter gender codes to schema-compliant values
            if self.gender.upper() == 'M':
                gender_elem.text = "Male"
            elif self.gender.upper() == 'F':
                gender_elem.text = "Female"
            elif self.gender in ["Male", "Female", "Undisclosed", "Unknown", "Unspecified"]:
                gender_elem.text = self.gender
            else:
                gender_elem.text = "Unknown"
        if self.date_of_birth:
            etree.SubElement(tsa_elem, "DateOfBirth").text = self.date_of_birth.strftime("%Y-%m-%d")
        etree.SubElement(tsa_elem, "NoMiddleName").text = "true" if self.no_middle_name else "false"
        if self.known_traveler_number:
            etree.SubElement(tsa_elem, "PreCheckNumber").text = self.known_traveler_number
        if self.redress_number:
            etree.SubElement(tsa_elem, "RedressNumber").text = self.redress_number
            
        return tsa_elem


@dataclass
class LoyaltyProgram:
    """Represents a loyalty program membership"""
    program_type: LoyaltyProgramType
    vendor_code: str
    account_number: str
    status: str = ""
    status_benefits: str = ""
    point_total: str = ""
    segment_total: str = ""
    next_status: str = ""
    points_until_next_status: str = ""
    segments_until_next_status: str = ""
    expiration: Optional[date] = None
    
    def to_xml_element(self, parent: etree.Element, membership_type: str = "Membership") -> etree.Element:
        """Add loyalty program as XML element to parent"""
        membership_elem = etree.SubElement(parent, membership_type)
        
        # For Profile v2 AdvantageMemberships, use the correct schema fields
        if membership_type == "Membership":
            # Profile v2 AdvantageMemberships schema (required fields)
            etree.SubElement(membership_elem, "VendorCode").text = self.vendor_code
            
            # Map program type to VendorType string
            vendor_type_map = {
                LoyaltyProgramType.AIR: "Air",
                LoyaltyProgramType.HOTEL: "Hotel", 
                LoyaltyProgramType.CAR: "Car",
                LoyaltyProgramType.RAIL: "Rail"
            }
            etree.SubElement(membership_elem, "VendorType").text = vendor_type_map[self.program_type]
            
            # ProgramNumber is the account number in Profile v2
            etree.SubElement(membership_elem, "ProgramNumber").text = self.account_number
            
            # ProgramCode is required - use vendor code as program code for simplicity
            etree.SubElement(membership_elem, "ProgramCode").text = self.vendor_code
            
            # Optional fields for Profile v2
            if self.expiration:
                etree.SubElement(membership_elem, "ExpirationDate").text = self.expiration.strftime("%Y-%m-%d")
        else:
            # For Loyalty v1 API, use the full schema with all fields
            etree.SubElement(membership_elem, "VendorCode").text = self.vendor_code
            etree.SubElement(membership_elem, "AccountNo").text = self.account_number
            
            if self.status:
                etree.SubElement(membership_elem, "Status").text = self.status
            if self.status_benefits:
                etree.SubElement(membership_elem, "StatusBenefits").text = self.status_benefits
            if self.point_total:
                etree.SubElement(membership_elem, "PointTotal").text = self.point_total
            if self.segment_total:
                etree.SubElement(membership_elem, "SegmentTotal").text = self.segment_total
            if self.next_status:
                etree.SubElement(membership_elem, "NextStatus").text = self.next_status
            if self.points_until_next_status:
                etree.SubElement(membership_elem, "PointsUntilNextStatus").text = self.points_until_next_status
            if self.segments_until_next_status:
                etree.SubElement(membership_elem, "SegmentsUntilNextStatus").text = self.segments_until_next_status
            if self.expiration:
                etree.SubElement(membership_elem, "Expiration").text = self.expiration.strftime("%Y-%m-%d")
            
        return membership_elem


@dataclass
class RatePreference:
    """Represents rate preferences"""
    aaa_rate: bool = False
    aarp_rate: bool = False
    govt_rate: bool = False
    military_rate: bool = False
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add rate preferences as XML element to parent"""
        rate_elem = etree.SubElement(parent, "RatePreferences")
        
        etree.SubElement(rate_elem, "AAARate").text = "true" if self.aaa_rate else "false"
        etree.SubElement(rate_elem, "AARPRate").text = "true" if self.aarp_rate else "false"
        etree.SubElement(rate_elem, "GovtRate").text = "true" if self.govt_rate else "false"
        etree.SubElement(rate_elem, "MilitaryRate").text = "true" if self.military_rate else "false"
            
        return rate_elem


@dataclass
class DiscountCode:
    """Represents a discount code"""
    vendor: str
    code: str
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add discount code as XML element to parent"""
        discount_elem = etree.SubElement(parent, "DiscountCode", Vendor=self.vendor)
        discount_elem.text = self.code
        return discount_elem


@dataclass
class AirPreferences:
    """Represents air travel preferences"""
    seat_preference: Optional[SeatPreference] = None
    seat_section: Optional[SeatSection] = None
    meal_preference: Optional[MealType] = None
    home_airport: str = ""
    air_other: str = ""
    memberships: List[LoyaltyProgram] = field(default_factory=list)
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add air preferences as XML element to parent"""
        air_elem = etree.SubElement(parent, "Air")
        
        # Seat preferences
        if self.seat_preference or self.seat_section:
            seat_elem = etree.SubElement(air_elem, "Seat")
            if self.seat_preference:
                etree.SubElement(seat_elem, "InterRowPositionCode").text = self.seat_preference.value
            if self.seat_section:
                etree.SubElement(seat_elem, "SectionPositionCode").text = self.seat_section.value
        
        # Meal preferences
        if self.meal_preference:
            etree.SubElement(air_elem, "MealCode").text = self.meal_preference.value
        
        # Other preferences
        if self.home_airport:
            etree.SubElement(air_elem, "HomeAirport").text = self.home_airport
        if self.air_other:
            etree.SubElement(air_elem, "AirOther").text = self.air_other
        
        # NOTE: Memberships are excluded from travel preference updates
        # They should be managed via the dedicated Loyalty API
        # if self.memberships:
        #     memberships_elem = etree.SubElement(air_elem, "AirMemberships")
        #     for membership in self.memberships:
        #         if membership.program_type == LoyaltyProgramType.AIR:
        #             membership.to_xml_element(memberships_elem, "AirMembership")
            
        return air_elem


@dataclass
class HotelPreferences:
    """Represents hotel travel preferences"""
    smoking_preference: Optional[SmokingPreference] = None
    room_type: Optional[HotelRoomType] = None
    hotel_other: str = ""
    prefer_foam_pillows: bool = False
    prefer_crib: bool = False
    prefer_rollaway_bed: bool = False
    prefer_gym: bool = False
    prefer_pool: bool = False
    prefer_restaurant: bool = False
    prefer_room_service: bool = False
    prefer_early_checkin: bool = False
    memberships: List[LoyaltyProgram] = field(default_factory=list)
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add hotel preferences as XML element to parent"""
        # Check if we have any actual preferences to set
        has_preferences = (
            self.smoking_preference or 
            self.room_type or 
            self.hotel_other or
            self.prefer_foam_pillows or
            self.prefer_crib or
            self.prefer_rollaway_bed or
            self.prefer_gym or
            self.prefer_pool or
            self.prefer_restaurant or
            self.prefer_room_service or
            self.prefer_early_checkin
        )
        
        # Don't create empty hotel elements - this might cause validation issues
        if not has_preferences:
            return None
            
        hotel_elem = etree.SubElement(parent, "Hotel")
        
        # IMPORTANT: Based on API testing, some documented fields are NOT actually supported!
        # Working order: HotelMemberships, RoomType, HotelOther, PreferFoamPillows, PreferCrib, 
        # PreferRollawayBed, PreferGym, PreferPool, PreferRoomService, PreferEarlyCheckIn
        # BROKEN FIELDS (don't use): SmokingCode, PreferRestaraunt
        
        # NOTE: SmokingCode is documented but NOT supported by the API - causes XML validation error
        # if self.smoking_preference:
        #     etree.SubElement(hotel_elem, "SmokingCode").text = self.smoking_preference.value
        
        # HotelMemberships - include empty element to maintain schema order
        # Per documentation: only appears for travel suppliers or TMCs, but required for schema validation
        etree.SubElement(hotel_elem, "HotelMemberships")
        
        if self.room_type:
            etree.SubElement(hotel_elem, "RoomType").text = self.room_type.value
        
        if self.hotel_other:
            etree.SubElement(hotel_elem, "HotelOther").text = self.hotel_other
        
        # Boolean preferences in documented order - only include if explicitly set to true
        if self.prefer_foam_pillows:
            etree.SubElement(hotel_elem, "PreferFoamPillows").text = "true"
        
        if self.prefer_crib:
            etree.SubElement(hotel_elem, "PreferCrib").text = "true"
        
        if self.prefer_rollaway_bed:
            etree.SubElement(hotel_elem, "PreferRollawayBed").text = "true"
        
        if self.prefer_gym:
            etree.SubElement(hotel_elem, "PreferGym").text = "true"
        
        if self.prefer_pool:
            etree.SubElement(hotel_elem, "PreferPool").text = "true"
        
        # NOTE: PreferRestaraunt is documented but NOT supported by the API - causes XML validation error
        # if self.prefer_restaurant:
        #     etree.SubElement(hotel_elem, "PreferRestaraunt").text = "true"
        
        # PreferWheelchairAccess and PreferAccessForBlind would go here but we don't have those fields
        
        if self.prefer_room_service:
            etree.SubElement(hotel_elem, "PreferRoomService").text = "true"
        
        if self.prefer_early_checkin:
            etree.SubElement(hotel_elem, "PreferEarlyCheckIn").text = "true"
        
        # NOTE: Memberships are excluded from travel preference updates
        # They should be managed via the dedicated Loyalty API
            
        return hotel_elem


@dataclass
class CarPreferences:
    """Represents car rental preferences"""
    car_type: Optional[CarType] = None
    transmission: Optional[TransmissionType] = None
    smoking_preference: Optional[SmokingPreference] = None
    gps: bool = False
    ski_rack: bool = False
    memberships: List[LoyaltyProgram] = field(default_factory=list)
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add car preferences as XML element to parent"""
        # Check if we have any actual preferences to set
        has_preferences = (
            self.car_type or
            self.transmission or
            self.smoking_preference or 
            self.gps or 
            self.ski_rack
        )
        
        # Don't create empty car elements - this might cause validation issues
        if not has_preferences:
            return None
            
        car_elem = etree.SubElement(parent, "Car")
        
        # IMPORTANT: Based on API testing, CarType and CarTransmission ARE supported
        # but they might need to be set together or in proper order
        # WORKING FIELDS: CarType, CarTransmission, CarSmokingCode, CarGPS, CarSkiRack
        
        # Set car type and transmission (they default to "DontCare" if not specified)
        if self.car_type:
            etree.SubElement(car_elem, "CarType").text = self.car_type.value
        if self.transmission:
            etree.SubElement(car_elem, "CarTransmission").text = self.transmission.value
        
        if self.smoking_preference:
            etree.SubElement(car_elem, "CarSmokingCode").text = self.smoking_preference.value
        
        # Only include boolean fields if they're explicitly set to true
        if self.gps:
            etree.SubElement(car_elem, "CarGPS").text = "true"
        if self.ski_rack:
            etree.SubElement(car_elem, "CarSkiRack").text = "true"
        
        # NOTE: Memberships are excluded from travel preference updates
        # They should be managed via the dedicated Loyalty API
        # if self.memberships:
        #     memberships_elem = etree.SubElement(car_elem, "CarMemberships")
        #     for membership in self.memberships:
        #         if membership.program_type == LoyaltyProgramType.CAR:
        #             membership.to_xml_element(memberships_elem, "CarMembership")
            
        return car_elem


@dataclass
class RailPreferences:
    """Represents rail travel preferences"""
    seat: str = ""
    coach: str = ""
    noise_comfort: str = ""
    bed: str = ""
    bed_category: str = ""
    berth: str = ""
    deck: str = ""
    space_type: str = ""
    fare_space_comfort: str = ""
    special_meals: str = ""
    contingencies: str = ""
    memberships: List[LoyaltyProgram] = field(default_factory=list)
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add rail preferences as XML element to parent"""
        rail_elem = etree.SubElement(parent, "Rail")
        
        if self.seat:
            etree.SubElement(rail_elem, "Seat").text = self.seat
        if self.coach:
            etree.SubElement(rail_elem, "Coach").text = self.coach
        if self.noise_comfort:
            etree.SubElement(rail_elem, "NoiseComfort").text = self.noise_comfort
        if self.bed:
            etree.SubElement(rail_elem, "Bed").text = self.bed
        if self.bed_category:
            etree.SubElement(rail_elem, "BedCategory").text = self.bed_category
        if self.berth:
            etree.SubElement(rail_elem, "Berth").text = self.berth
        if self.deck:
            etree.SubElement(rail_elem, "Deck").text = self.deck
        if self.space_type:
            etree.SubElement(rail_elem, "SpaceType").text = self.space_type
        if self.fare_space_comfort:
            etree.SubElement(rail_elem, "FareSpaceComfort").text = self.fare_space_comfort
        if self.special_meals:
            etree.SubElement(rail_elem, "SpecialMeals").text = self.special_meals
        if self.contingencies:
            etree.SubElement(rail_elem, "Contingencies").text = self.contingencies
        
        # NOTE: Memberships are excluded from travel preference updates
        # They should be managed via the dedicated Loyalty API
        # if self.memberships:
        #     memberships_elem = etree.SubElement(rail_elem, "RailMemberships")
        #     for membership in self.memberships:
        #         if membership.program_type == LoyaltyProgramType.RAIL:
        #             membership.to_xml_element(memberships_elem, "RailMembership")
            
        return rail_elem


@dataclass
class CustomField:
    """Represents a custom field"""
    field_id: str
    value: str
    field_type: str = "Text"
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add custom field as XML element to parent"""
        field_elem = etree.SubElement(parent, "CustomField", Name=self.field_id)
        field_elem.text = self.value
        return field_elem


@dataclass
class UnusedTicket:
    """Represents an unused ticket"""
    ticket_number: str
    airline_code: str
    amount: str = ""
    currency: str = "USD"
    
    def to_xml_element(self, parent: etree.Element) -> etree.Element:
        """Add unused ticket as XML element to parent"""
        ticket_elem = etree.SubElement(parent, "UnusedTicket")
        
        etree.SubElement(ticket_elem, "TicketNumber").text = self.ticket_number
        etree.SubElement(ticket_elem, "AirlineCode").text = self.airline_code
        if self.amount:
            etree.SubElement(ticket_elem, "Amount").text = self.amount
        if self.currency:
            etree.SubElement(ticket_elem, "Currency").text = self.currency
            
        return ticket_elem


@dataclass
class UserProfile:
    """Complete user profile with all available fields"""
    login_id: str
    
    # General information
    first_name: str = ""
    last_name: str = ""
    middle_name: str = ""
    job_title: str = ""
    preferred_name: str = ""
    preferred_language: str = "en-US"
    country_code: str = "US"
    rule_class: str = "Default Travel Class"
    travel_config_id: str = ""
    company_name: str = ""
    employee_id: str = ""
    medical_alerts: str = ""
    search_id: str = ""
    gds_profile_name: str = ""
    sabre_profile_id: str = ""
    uuid: str = ""
    agency_number: str = ""
    password: Optional[str] = None  # Only used for creation
    
    # Contact information
    addresses: List[Address] = field(default_factory=list)
    phones: List[Phone] = field(default_factory=list)
    emails: List[Email] = field(default_factory=list)
    emergency_contacts: List[EmergencyContact] = field(default_factory=list)
    
    # Identity documents
    national_ids: List[NationalID] = field(default_factory=list)
    drivers_licenses: List[DriversLicense] = field(default_factory=list)
    has_no_passport: bool = False
    passports: List[Passport] = field(default_factory=list)
    visas: List[Visa] = field(default_factory=list)
    
    # TSA and security
    tsa_info: Optional[TSAInfo] = None
    
    # Rate preferences and discounts
    rate_preferences: Optional[RatePreference] = None
    discount_codes: List[DiscountCode] = field(default_factory=list)
    
    # Travel preferences
    air_preferences: Optional[AirPreferences] = None
    hotel_preferences: Optional[HotelPreferences] = None
    car_preferences: Optional[CarPreferences] = None
    rail_preferences: Optional[RailPreferences] = None
    
    # Custom fields and tickets
    custom_fields: List[CustomField] = field(default_factory=list)
    unused_tickets: List[UnusedTicket] = field(default_factory=list)
    southwest_unused_tickets: List[UnusedTicket] = field(default_factory=list)
    
    # Loyalty programs (consolidated)
    loyalty_programs: List[LoyaltyProgram] = field(default_factory=list)
    
    def to_create_xml(self) -> str:
        """Convert to XML for profile creation using lxml - MINIMAL fields only!"""
        # Create root element with proper namespace
        root = etree.Element("ProfileResponse", 
                           nsmap={'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
        root.set("Action", ProfileAction.CREATE.value)
        root.set("LoginId", self.login_id)
        
        # General section - ONLY essential fields for creation!
        # Based on curl testing, complex fields cause XML validation errors during creation
        general = etree.SubElement(root, "General")
        
        # Only include the absolutely required fields for creation
        if self.first_name:
            etree.SubElement(general, "FirstName").text = self.first_name
        if self.last_name:
            etree.SubElement(general, "LastName").text = self.last_name
        if self.rule_class:
            etree.SubElement(general, "RuleClass").text = self.rule_class
        if self.travel_config_id:
            etree.SubElement(general, "TravelConfigID").text = self.travel_config_id
        
        # NOTE: JobTitle, CompanyName, CompanyEmployeeID cause validation errors during creation
        # These fields should be added via update_user() after successful creation
        
        # EARLY SCHEMA ELEMENTS ONLY - Based on successful curl tests:
        # Only include elements that are early in the schema order and work during creation
        
        # EmergencyContact works during creation (early in schema)
        if self.emergency_contacts:
            for contact in self.emergency_contacts:
                contact.to_xml_element(root)
        
        # Telephones work during creation  
        if self.phones:
            phones_elem = etree.SubElement(root, "Telephones")
            for phone in self.phones:
                phone.to_xml_element(phones_elem)
        
        # Addresses work during creation
        if self.addresses:
            addresses_elem = etree.SubElement(root, "Addresses")
            for addr in self.addresses:
                addr.to_xml_element(addresses_elem)
        
        # NOTE: EmailAddresses should come much later in schema order (after Visas)
        # For creation, keeping it simple and only including basic contact info
        # EmailAddresses will be added via update operation to maintain proper schema order
        
        # NOTE: More complex elements (NationalIDs, Passports, TSAInfo, CustomFields, etc.)
        # cause XML validation errors during creation and should only be added via UPDATE
        
        # NOTE: AdvantageMemberships are NOT supported during user creation
        # They must be added via update operations after the user is created
        # Attempting to include them during creation causes XML validation errors
        
        # Password for creation (comes last)
        if self.password:
            etree.SubElement(root, "Password").text = self.password
        
        # Return properly formatted XML with declaration
        return etree.tostring(root, 
                             pretty_print=True,
                             xml_declaration=True, 
                             encoding='utf-8').decode('utf-8')
    
    def to_update_xml(self, fields_to_update: Optional[List[str]] = None) -> str:
        """Convert to XML for profile update using lxml"""
        # Create root element with proper namespace and schema location
        root = etree.Element("ProfileResponse", 
                           nsmap={'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
        root.set("Action", ProfileAction.UPDATE.value)
        root.set("LoginId", self.login_id)
        # Add schema location if needed for validation
        # root.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "...")
        
        # If no specific fields, update all non-empty fields
        if fields_to_update is None:
            fields_to_update = self._get_non_empty_fields()
        
        # General section - elements MUST be in correct XSD schema order!
        general_fields = ["first_name", "last_name", "middle_name", "job_title", "company_name", "employee_id", "medical_alerts"]
        if any(f in fields_to_update for f in general_fields):
            general = etree.SubElement(root, "General")
            
            # Required fields first (in schema order)
            if "first_name" in fields_to_update and self.first_name:
                etree.SubElement(general, "FirstName").text = self.first_name
            if "last_name" in fields_to_update and self.last_name:
                etree.SubElement(general, "LastName").text = self.last_name
            
            # MiddleName comes before RuleClass/TravelConfigID
            if "middle_name" in fields_to_update and self.middle_name:
                etree.SubElement(general, "MiddleName").text = self.middle_name
            
            # JobTitle, CompanyName, CompanyEmployeeID come after required fields
            if "job_title" in fields_to_update and self.job_title:
                etree.SubElement(general, "JobTitle").text = self.job_title
            if "company_name" in fields_to_update and self.company_name:
                etree.SubElement(general, "CompanyName").text = self.company_name
            if "employee_id" in fields_to_update and self.employee_id:
                etree.SubElement(general, "CompanyEmployeeID").text = self.employee_id
            if "medical_alerts" in fields_to_update and self.medical_alerts:
                etree.SubElement(general, "MedicalAlerts").text = self.medical_alerts
        
        # Add other sections based on fields_to_update
        self._add_sections_to_xml(root, fields_to_update)
        
        # Return properly formatted XML
        return etree.tostring(root, 
                             pretty_print=True, 
                             xml_declaration=True, 
                             encoding='utf-8').decode('utf-8')
    
    def _get_non_empty_fields(self) -> List[str]:
        """Get list of non-empty field names for update"""
        fields = []
        if self.first_name: fields.append("first_name")
        if self.last_name: fields.append("last_name")
        if self.middle_name: fields.append("middle_name")
        if self.job_title: fields.append("job_title")
        if self.company_name: fields.append("company_name")
        if self.employee_id: fields.append("employee_id")
        if self.medical_alerts: fields.append("medical_alerts")
        if self.phones: fields.append("phones")
        if self.addresses: fields.append("addresses")
        if self.emails: fields.append("emails")
        if self.emergency_contacts: fields.append("emergency_contacts")
        if self.national_ids: fields.append("national_ids")
        if self.drivers_licenses: fields.append("drivers_licenses")
        if self.passports: fields.append("passports")
        if self.visas: fields.append("visas")
        if self.tsa_info: fields.append("tsa_info")
        if self.rate_preferences: fields.append("rate_preferences")
        if self.discount_codes: fields.append("discount_codes")
        if self.air_preferences: fields.append("air_preferences")
        if self.hotel_preferences: fields.append("hotel_preferences")
        if self.car_preferences: fields.append("car_preferences")
        if self.rail_preferences: fields.append("rail_preferences")
        if self.custom_fields: fields.append("custom_fields")
        if self.unused_tickets: fields.append("unused_tickets")
        if self.southwest_unused_tickets: fields.append("southwest_unused_tickets")
        if self.loyalty_programs: fields.append("loyalty_programs")
        return fields
    
    def _add_sections_to_xml(self, root: etree.Element, fields_to_update: Optional[List[str]] = None):
        """Add all profile sections to XML in EXACT schema order from Concur documentation"""
        
        # CRITICAL: Elements MUST appear in this exact order per Concur XSD schema:
        # General, EmergencyContact, Telephones, Addresses, NationalIDs, DriversLicenses, 
        # HasNoPassport, Passports, Visas, EmailAddresses, RatePreferences, DiscountCodes, 
        # Air, Rail, Car, Hotel, CustomFields, Roles, Sponsors, TSAInfo, UnusedTickets, SouthwestUnusedTickets, AdvantageMemberships
        
        # 1. EmergencyContact (comes right after General)
        if not fields_to_update or "emergency_contacts" in fields_to_update:
            if self.emergency_contacts:
                for contact in self.emergency_contacts:
                    contact.to_xml_element(root)
        
        # 2. Telephones 
        if not fields_to_update or "phones" in fields_to_update:
            if self.phones:
                phones_elem = etree.SubElement(root, "Telephones")
                for phone in self.phones:
                    phone.to_xml_element(phones_elem)
        
        # 3. Addresses (comes after Telephones)
        if not fields_to_update or "addresses" in fields_to_update:
            if self.addresses:
                addresses_elem = etree.SubElement(root, "Addresses")
                for addr in self.addresses:
                    addr.to_xml_element(addresses_elem)
        
        # 4. NationalIDs (comes before drivers licenses)
        if not fields_to_update or "national_ids" in fields_to_update:
            if self.national_ids:
                ids_elem = etree.SubElement(root, "NationalIDs")
                for national_id in self.national_ids:
                    national_id.to_xml_element(ids_elem)
        
        # 5. DriversLicenses
        if not fields_to_update or "drivers_licenses" in fields_to_update:
            if self.drivers_licenses:
                licenses_elem = etree.SubElement(root, "DriversLicenses")
                for license in self.drivers_licenses:
                    license.to_xml_element(licenses_elem)
        
        # 6. HasNoPassport flag (comes before Passports)
        if not fields_to_update or "has_no_passport" in fields_to_update:
            if self.has_no_passport:
                etree.SubElement(root, "HasNoPassport").text = "true"
        
        # 7. Passports
        if not fields_to_update or "passports" in fields_to_update:
            if self.passports:
                passports_elem = etree.SubElement(root, "Passports")
                for passport in self.passports:
                    passport.to_xml_element(passports_elem)
        
        # 8. Visas
        if not fields_to_update or "visas" in fields_to_update:
            if self.visas:
                visas_elem = etree.SubElement(root, "Visas")
                for visa in self.visas:
                    visa.to_xml_element(visas_elem)
        
        # 9. EmailAddresses (IMPORTANT: comes AFTER visas, not after addresses!)
        if not fields_to_update or "emails" in fields_to_update:
            if self.emails:
                emails_elem = etree.SubElement(root, "EmailAddresses")
                for email in self.emails:
                    email.to_xml_element(emails_elem)
        
        # 10. RatePreferences
        if not fields_to_update or "rate_preferences" in fields_to_update:
            if self.rate_preferences:
                self.rate_preferences.to_xml_element(root)
        
        # 11. DiscountCodes
        if not fields_to_update or "discount_codes" in fields_to_update:
            if self.discount_codes:
                codes_elem = etree.SubElement(root, "DiscountCodes")
                for code in self.discount_codes:
                    code.to_xml_element(codes_elem)
        
        # 12. Air preferences
        if not fields_to_update or "air_preferences" in fields_to_update:
            if self.air_preferences:
                self.air_preferences.to_xml_element(root)
        
        # 13. Rail preferences  
        if not fields_to_update or "rail_preferences" in fields_to_update:
            if self.rail_preferences:
                self.rail_preferences.to_xml_element(root)
        
        # 14. Car preferences
        if not fields_to_update or "car_preferences" in fields_to_update:
            if self.car_preferences:
                car_elem = self.car_preferences.to_xml_element(root)
                # car_elem might be None if no preferences are actually set
        
        # 15. Hotel preferences
        if not fields_to_update or "hotel_preferences" in fields_to_update:
            if self.hotel_preferences:
                hotel_elem = self.hotel_preferences.to_xml_element(root)
                # hotel_elem might be None if no preferences are actually set
        
        # 16. CustomFields (comes before TSAInfo!)
        if not fields_to_update or "custom_fields" in fields_to_update:
            if self.custom_fields:
                fields_elem = etree.SubElement(root, "CustomFields")
                for field in self.custom_fields:
                    field.to_xml_element(fields_elem)
        
        # 17. TSAInfo (comes near the end)
        if not fields_to_update or "tsa_info" in fields_to_update:
            if self.tsa_info:
                self.tsa_info.to_xml_element(root)
        
        # 18. UnusedTickets
        if not fields_to_update or "unused_tickets" in fields_to_update:
            if self.unused_tickets:
                tickets_elem = etree.SubElement(root, "UnusedTickets")
                for ticket in self.unused_tickets:
                    ticket.to_xml_element(tickets_elem)
        
        # 19. SouthwestUnusedTickets
        if not fields_to_update or "southwest_unused_tickets" in fields_to_update:
            if self.southwest_unused_tickets:
                sw_tickets_elem = etree.SubElement(root, "SouthwestUnusedTickets")
                for ticket in self.southwest_unused_tickets:
                    ticket.to_xml_element(sw_tickets_elem)
        
        # 20. AdvantageMemberships (comes last - standalone loyalty programs)
        if not fields_to_update or "loyalty_programs" in fields_to_update:
            if self.loyalty_programs:
                memberships_elem = etree.SubElement(root, "AdvantageMemberships")
                for loyalty_program in self.loyalty_programs:
                    loyalty_program.to_xml_element(memberships_elem, "Membership")


@dataclass
class ProfileSummary:
    """Represents a profile summary from the summary API"""
    status: ProfileStatus
    login_id: str
    xml_profile_sync_id: str = ""
    profile_last_modified_utc: Optional[datetime] = None


@dataclass 
class PagingInfo:
    """Represents paging information"""
    total_pages: int = 0
    total_items: int = 0
    page: int = 1
    items_per_page: int = 200
    previous_page_url: str = ""
    next_page_url: str = ""


@dataclass
class ConnectResponse:
    """Represents a Connect API response for profile summaries"""
    metadata: Optional[PagingInfo] = None
    profile_summaries: List[ProfileSummary] = field(default_factory=list)


@dataclass
class ApiError:
    """Represents an API error response"""
    message: str
    server_time: str
    error_id: str
    code: str = ""
    
    @classmethod
    def from_xml(cls, xml_str: str) -> 'ApiError':
        """Parse error from XML response using lxml"""
        try:
            root = etree.fromstring(xml_str.encode('utf-8'))
            return cls(
                message=root.findtext("Message", "Unknown error"),
                server_time=root.findtext("Server-Time", ""),
                error_id=root.findtext("Id", ""),
                code=root.findtext("Code", "")
            )
        except Exception as e:
            return cls(
                message=f"Failed to parse error: {xml_str}",
                server_time="",
                error_id="",
                code=""
            )


@dataclass
class ApiResponse:
    """Represents a successful API response"""
    code: str
    message: str
    uuid: Optional[str] = None
    success: bool = True
    
    @classmethod
    def from_xml(cls, xml_str: str) -> 'ApiResponse':
        """Parse response from XML using lxml"""
        root = etree.fromstring(xml_str.encode('utf-8'))
        return cls(
            code=root.findtext("Code", ""),
            message=root.findtext("Message", ""),
            uuid=root.findtext("UUID"),
            success=True
        )


@dataclass
class LoyaltyResponse:
    """Represents a loyalty program API response"""
    success: bool
    message: str = ""
    error: Optional[str] = None
    
    @classmethod
    def from_xml(cls, xml_str: str) -> 'LoyaltyResponse':
        """Parse loyalty response from XML"""
        try:
            root = etree.fromstring(xml_str.encode('utf-8'))
            status = root.findtext("Status", "")
            
            if status == "ERROR":
                error_desc = root.findtext("ErrorDescription", "Unknown error")
                return cls(success=False, error=error_desc)
            else:
                return cls(success=True, message="Loyalty program updated successfully")
        except Exception as e:
            return cls(success=False, error=f"Failed to parse response: {str(e)}")


# Exception classes
class ConcurProfileError(Exception):
    """Base exception for Concur Profile SDK errors"""
    pass


class AuthenticationError(ConcurProfileError):
    """Authentication-related errors"""
    pass


class ProfileNotFoundError(ConcurProfileError):
    """Profile not found error"""
    pass


class ValidationError(ConcurProfileError):
    """Data validation error"""
    pass


class ConcurProfileSDK:
    """
    Complete SDK for interacting with Concur Profile APIs using lxml
    
    Supports all Profile v2 and Loyalty Program v1 functionality including:
    - Full CRUD operations on user profiles
    - Complete profile schema with all fields
    - Travel preferences (Air, Hotel, Car, Rail)
    - Loyalty program management
    - Profile summary listing with pagination
    - Advanced features like TSA info, custom fields, etc.
    
    Args:
        client_id: Your Concur OAuth client ID
        client_secret: Your Concur OAuth client secret
        username: Concur username for authentication
        password: Concur password for authentication
        base_url: Base URL for Concur API (defaults to US instance)
    
    Example:
        sdk = ConcurProfileSDK(
            client_id="your-client-id",
            client_secret="your-client-secret",
            username="user@example.com",
            password="password123"
        )
        
        # Get current user profile with all data
        profile = sdk.get_current_user_profile()
        print(f"Hello {profile.first_name} {profile.last_name}!")
        
        # List recent profile summaries
        summaries = sdk.list_profile_summaries(
            last_modified_date=datetime.now() - timedelta(days=30),
            limit=50
        )
        
        # Update loyalty program
        loyalty = LoyaltyProgram(
            program_type=LoyaltyProgramType.AIR,
            vendor_code="UA",
            account_number="123456789",
            status="Premier Gold"
        )
        response = sdk.update_loyalty_program(loyalty)
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
        base_url: str = "https://us2.api.concursolutions.com"
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip("/")
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        
        # API endpoints
        self.auth_url = f"{self.base_url}/oauth2/v0/token"
        self.profile_url = f"{self.base_url}/api/travelprofile/v2.0/profile"
        self.summary_url = f"{self.base_url}/api/travelprofile/v2.0/summary"
        self.loyalty_url = f"{self.base_url}/api/travelprofile/v1.0/loyalty"
    
    def _ensure_authenticated(self) -> None:
        """Ensure we have a valid access token"""
        if not self._access_token or (self._token_expiry and datetime.now() >= self._token_expiry):
            self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Concur API and store access token"""
        logger.info("Authenticating with Concur API...")
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "password",
            "username": self.username,
            "password": self.password
        }
        
        try:
            response = requests.post(self.auth_url, headers=headers, data=data)
            response.raise_for_status()
            
            auth_data: AuthResponse = response.json()
            self._access_token = auth_data["access_token"]
            
            # Calculate token expiry (subtract 60 seconds for safety)
            expires_in = auth_data["expires_in"] - 60
            self._token_expiry = datetime.now().replace(microsecond=0) + timedelta(seconds=expires_in)
            
            logger.info("Authentication successful")
            
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")
    
    def _make_request(
        self,
        method: str,
        url: str,
        data: Optional[str] = None
    ) -> requests.Response:
        """Make an authenticated request to the API"""
        self._ensure_authenticated()
        
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/xml"
        }
        
        if method == "POST" and data:
            headers["Content-Type"] = "application/xml"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=data
            )
            
            # Check for authentication errors
            if response.status_code == 401:
                # Try to re-authenticate once
                self._authenticate()
                headers["Authorization"] = f"Bearer {self._access_token}"
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data
                )
            
            return response
            
        except requests.exceptions.RequestException as e:
            raise ConcurProfileError(f"Request failed: {str(e)}")
    
    def _wait_for_user_availability(self, login_id: str, max_wait: int = 30):
        """Wait for a newly created user to be available for read/update operations"""
        import time
        
        logger.info(f"Waiting for user {login_id} to be available...")
        
        for attempt in range(max_wait):
            try:
                self.get_profile_by_login_id(login_id)
                logger.info(f"User available after {attempt + 1} seconds")
                return
            except ProfileNotFoundError:
                if attempt < max_wait - 1:
                    time.sleep(1)
                    continue
                else:
                    raise ProfileNotFoundError(f"User {login_id} not available after {max_wait} seconds")
            except Exception as e:
                # Other errors (like authentication) should be raised immediately
                raise e
    
    def _update_car_preferences_individually(self, login_id: str, car_prefs: CarPreferences):
        """
        Update car preferences one field at a time with delays
        
        Based on API testing, car preferences must be updated individually:
        - CarType and CarTransmission work individually but fail when combined
        - Each field needs time to propagate before setting the next one
        """
        import time
        
        logger.info("Updating car preferences individually...")
        
        # Update fields in order, one at a time
        if car_prefs.car_type:
            try:
                logger.info(f"Setting CarType to {car_prefs.car_type.value}")
                profile = UserProfile(
                    login_id=login_id,
                    car_preferences=CarPreferences(car_type=car_prefs.car_type)
                )
                self.update_user(profile, fields_to_update=["car_preferences"])
                time.sleep(3)  # Wait for propagation
            except Exception as e:
                logger.warning(f"Failed to set CarType: {e}")
        
        if car_prefs.transmission:
            try:
                logger.info(f"Setting CarTransmission to {car_prefs.transmission.value}")
                profile = UserProfile(
                    login_id=login_id,
                    car_preferences=CarPreferences(transmission=car_prefs.transmission)
                )
                self.update_user(profile, fields_to_update=["car_preferences"])
                time.sleep(3)  # Wait for propagation
            except Exception as e:
                logger.warning(f"Failed to set CarTransmission: {e}")
        
        if car_prefs.smoking_preference:
            try:
                logger.info(f"Setting CarSmokingCode to {car_prefs.smoking_preference.value}")
                profile = UserProfile(
                    login_id=login_id,
                    car_preferences=CarPreferences(smoking_preference=car_prefs.smoking_preference)
                )
                self.update_user(profile, fields_to_update=["car_preferences"])
                time.sleep(3)  # Wait for propagation
            except Exception as e:
                logger.warning(f"Failed to set CarSmokingCode: {e}")
        
        if car_prefs.gps:
            try:
                logger.info(f"Setting CarGPS to {car_prefs.gps}")
                profile = UserProfile(
                    login_id=login_id,
                    car_preferences=CarPreferences(gps=car_prefs.gps)
                )
                self.update_user(profile, fields_to_update=["car_preferences"])
                time.sleep(3)  # Wait for propagation
            except Exception as e:
                logger.warning(f"Failed to set CarGPS: {e}")
        
        if car_prefs.ski_rack:
            try:
                logger.info(f"Setting CarSkiRack to {car_prefs.ski_rack}")
                profile = UserProfile(
                    login_id=login_id,
                    car_preferences=CarPreferences(ski_rack=car_prefs.ski_rack)
                )
                self.update_user(profile, fields_to_update=["car_preferences"])
                time.sleep(3)  # Wait for propagation
            except Exception as e:
                logger.warning(f"Failed to set CarSkiRack: {e}")
        
        logger.info("Car preferences individual updates completed")
    
    def _update_loyalty_programs_individually(self, login_id: str, loyalty_programs: List[LoyaltyProgram]):
        """
        Update loyalty programs one at a time using the dedicated Loyalty v1 API
        
        Based on API testing and documentation, loyalty programs should be managed
        via the dedicated Loyalty v1 API, not through Profile v2 AdvantageMemberships.
        """
        import time
        
        logger.info(f"Updating {len(loyalty_programs)} loyalty programs individually via Loyalty v1 API...")
        
        for i, loyalty_program in enumerate(loyalty_programs, 1):
            try:
                logger.info(f"Setting loyalty program {i}/{len(loyalty_programs)}: {loyalty_program.program_type.value} {loyalty_program.vendor_code}")
                
                # Use the dedicated Loyalty v1 API instead of Profile v2
                response = self.update_loyalty_program(loyalty_program, login_id)
                
                if response.success:
                    logger.info(f"✅ Successfully set loyalty program {i}: {loyalty_program.vendor_code}")
                else:
                    logger.warning(f"❌ Failed to set loyalty program {i} ({loyalty_program.vendor_code}): {response.error}")
                
                time.sleep(3)  # Wait for propagation
            except Exception as e:
                logger.warning(f"❌ Failed to set loyalty program {i} ({loyalty_program.vendor_code}): {e}")
                # Continue with next loyalty program
        
        logger.info("Loyalty programs individual updates completed")
    
    def _parse_profile_response(self, xml_str: str) -> UserProfile:
        """Parse complete profile XML response into UserProfile object using lxml"""
        root = etree.fromstring(xml_str.encode('utf-8'))
        
        # Get basic attributes
        login_id = root.get("LoginId", "")
        
        # Parse General section
        general = root.find("General")
        if general is None:
            raise ValidationError("Invalid profile response: missing General section")
        
        profile = UserProfile(
            login_id=login_id,
            first_name=general.findtext("FirstName", ""),
            last_name=general.findtext("LastName", ""),
            middle_name=general.findtext("MiddleName", ""),
            job_title=general.findtext("JobTitle", ""),
            preferred_name=general.findtext("PreferredName", ""),
            preferred_language=general.findtext("PreferredLanguage", "en-US"),
            country_code=general.findtext("CountryCode", "US"),
            rule_class=general.findtext("RuleClass", "Default Travel Class"),
            travel_config_id=general.findtext("TravelConfigID", ""),
            company_name=general.findtext("CompanyName", ""),
            employee_id=general.findtext("CompanyEmployeeID", ""),
            medical_alerts=general.findtext("MedicalAlerts", ""),
            search_id=general.findtext("SearchID", ""),
            gds_profile_name=general.findtext("GDSProfileName", ""),
            sabre_profile_id=general.findtext("SabreProfileId", ""),
            uuid=general.findtext("UUID", ""),
            agency_number=general.findtext("AgencyNumber", "")
        )
        
        # Parse Emergency Contacts
        for contact_elem in root.findall("EmergencyContact"):
            profile.emergency_contacts.append(EmergencyContact(
                name=contact_elem.findtext("Name", ""),
                relationship=contact_elem.findtext("Relationship", ""),
                phone=contact_elem.findtext("Phone", ""),
                mobile_phone=contact_elem.findtext("MobilePhone", ""),
                email=contact_elem.findtext("Email", "")
            ))
        
        # Parse Addresses
        addresses_elem = root.find("Addresses")
        if addresses_elem is not None:
            for addr_elem in addresses_elem.findall("Address"):
                addr_type = addr_elem.get("Type", "Home")
                try:
                    addr_type_enum = AddressType(addr_type)
                except ValueError:
                    continue  # Skip unknown address types
                
                profile.addresses.append(Address(
                    type=addr_type_enum,
                    street=addr_elem.findtext("Street", ""),
                    city=addr_elem.findtext("City", ""),
                    state_province=addr_elem.findtext("StateProvince", ""),
                    postal_code=addr_elem.findtext("PostalCode", ""),
                    country_code=addr_elem.findtext("CountryCode", "US")
                ))
        
        # Parse Phones
        phones_elem = root.find("Telephones")
        if phones_elem is not None:
            for phone_elem in phones_elem.findall("Telephone"):
                phone_type = phone_elem.get("Type", "Home")
                try:
                    phone_type_enum = PhoneType(phone_type)
                except ValueError:
                    continue  # Skip unknown phone types
                
                profile.phones.append(Phone(
                    type=phone_type_enum,
                    country_code=phone_elem.findtext("CountryCode", ""),
                    phone_number=phone_elem.findtext("PhoneNumber", ""),
                    extension=phone_elem.findtext("Extension", "")
                ))
        
        # Parse Emails
        emails_elem = root.find("EmailAddresses")
        if emails_elem is not None:
            for email_elem in emails_elem.findall("EmailAddress"):
                email_type = email_elem.get("Type", "Business")
                try:
                    email_type_enum = EmailType(email_type)
                except ValueError:
                    continue  # Skip unknown email types
                
                profile.emails.append(Email(
                    type=email_type_enum,
                    email_address=email_elem.text or ""
                ))
        
        # Parse National IDs
        ids_elem = root.find("NationalIDs")
        if ids_elem is not None:
            for id_elem in ids_elem.findall("NationalID"):
                profile.national_ids.append(NationalID(
                    id_number=id_elem.findtext("NationalIDNumber", ""),
                    country_code=id_elem.findtext("IssuingCountry", "")
                ))
        
        # Parse Drivers Licenses
        licenses_elem = root.find("DriversLicenses")
        if licenses_elem is not None:
            for license_elem in licenses_elem.findall("DriversLicense"):
                profile.drivers_licenses.append(DriversLicense(
                    license_number=license_elem.findtext("DriversLicenseNumber", ""),
                    country_code=license_elem.findtext("IssuingCountry", ""),
                    state_province=license_elem.findtext("IssuingState", "")
                ))
        
        # Parse HasNoPassport flag
        has_no_passport_elem = root.find("HasNoPassport")
        if has_no_passport_elem is not None:
            profile.has_no_passport = has_no_passport_elem.text == "true"
        
        # Parse Passports
        passports_elem = root.find("Passports")
        if passports_elem is not None:
            for passport_elem in passports_elem.findall("Passport"):
                issue_date = None
                exp_date = None
                
                if passport_elem.findtext("IssDate"):
                    try:
                        issue_date = datetime.strptime(passport_elem.findtext("IssDate"), "%Y-%m-%d").date()
                    except:
                        pass
                
                if passport_elem.findtext("ExpDate"):
                    try:
                        exp_date = datetime.strptime(passport_elem.findtext("ExpDate"), "%Y-%m-%d").date()
                    except:
                        pass
                
                profile.passports.append(Passport(
                    doc_number=passport_elem.findtext("DocNumber", ""),
                    nationality=passport_elem.findtext("Nat", ""),
                    issue_country=passport_elem.findtext("IssCountry", ""),
                    issue_date=issue_date,
                    expiration_date=exp_date,
                    primary=passport_elem.findtext("Primary", "false") == "true"
                ))
        
        # Parse Visas
        visas_elem = root.find("Visas")
        if visas_elem is not None:
            for visa_elem in visas_elem.findall("Visa"):
                visa_date_issued = None
                visa_expiration = None
                
                if visa_elem.findtext("VisaDateIssued"):
                    try:
                        visa_date_issued = datetime.strptime(visa_elem.findtext("VisaDateIssued"), "%Y-%m-%d").date()
                    except:
                        pass
                
                if visa_elem.findtext("VisaExpiration"):
                    try:
                        visa_expiration = datetime.strptime(visa_elem.findtext("VisaExpiration"), "%Y-%m-%d").date()
                    except:
                        pass
                
                visa_type_str = visa_elem.findtext("VisaType", "SingleEntry")
                try:
                    visa_type_enum = VisaType(visa_type_str)
                except ValueError:
                    visa_type_enum = VisaType.SINGLE_ENTRY
                
                profile.visas.append(Visa(
                    visa_nationality=visa_elem.findtext("VisaNationality", ""),
                    visa_number=visa_elem.findtext("VisaNumber", ""),
                    visa_type=visa_type_enum,
                    visa_country_issued=visa_elem.findtext("VisaCountryIssued", ""),
                    visa_date_issued=visa_date_issued,
                    visa_expiration=visa_expiration
                ))
        
        # Parse TSA Info
        tsa_elem = root.find("TSAInfo")
        if tsa_elem is not None:
            dob = None
            if tsa_elem.findtext("DateOfBirth"):
                try:
                    dob = datetime.strptime(tsa_elem.findtext("DateOfBirth"), "%Y-%m-%d").date()
                except:
                    pass
            
            profile.tsa_info = TSAInfo(
                known_traveler_number=tsa_elem.findtext("KnownTravelerNumber", ""),
                gender=tsa_elem.findtext("Gender", ""),
                date_of_birth=dob,
                redress_number=tsa_elem.findtext("RedressNumber", ""),
                no_middle_name=tsa_elem.findtext("NoMiddleName", "false") == "true"
            )
        
        # Parse Rate Preferences
        rate_prefs_elem = root.find("RatePreferences")
        if rate_prefs_elem is not None:
            profile.rate_preferences = RatePreference(
                aaa_rate=rate_prefs_elem.findtext("AAARate", "false") == "true",
                aarp_rate=rate_prefs_elem.findtext("AARPRate", "false") == "true",
                govt_rate=rate_prefs_elem.findtext("GovtRate", "false") == "true",
                military_rate=rate_prefs_elem.findtext("MilitaryRate", "false") == "true"
            )
        
        # Parse Discount Codes
        codes_elem = root.find("DiscountCodes")
        if codes_elem is not None:
            for code_elem in codes_elem.findall("DiscountCode"):
                profile.discount_codes.append(DiscountCode(
                    vendor=code_elem.get("Vendor", ""),
                    code=code_elem.text or ""
                ))
        
        # Parse Travel Preferences
        self._parse_travel_preferences(root, profile)
        
        # Parse Custom Fields
        fields_elem = root.find("CustomFields")
        if fields_elem is not None:
            for field_elem in fields_elem.findall("CustomField"):
                profile.custom_fields.append(CustomField(
                    field_id=field_elem.get("ID", ""),
                    value=field_elem.text or "",
                    field_type=field_elem.get("Type", "Text")
                ))
        
        # Parse Unused Tickets
        tickets_elem = root.find("UnusedTickets")
        if tickets_elem is not None:
            for ticket_elem in tickets_elem.findall("UnusedTicket"):
                profile.unused_tickets.append(UnusedTicket(
                    ticket_number=ticket_elem.findtext("TicketNumber", ""),
                    airline_code=ticket_elem.findtext("AirlineCode", ""),
                    amount=ticket_elem.findtext("Amount", ""),
                    currency=ticket_elem.findtext("Currency", "USD")
                ))
        
        # Parse Southwest Unused Tickets
        sw_tickets_elem = root.find("SouthwestUnusedTickets")
        if sw_tickets_elem is not None:
            for ticket_elem in sw_tickets_elem.findall("UnusedTicket"):
                profile.southwest_unused_tickets.append(UnusedTicket(
                    ticket_number=ticket_elem.findtext("TicketNumber", ""),
                    airline_code=ticket_elem.findtext("AirlineCode", ""),
                    amount=ticket_elem.findtext("Amount", ""),
                    currency=ticket_elem.findtext("Currency", "USD")
                ))
        
        return profile
    
    def _parse_travel_preferences(self, root: etree.Element, profile: UserProfile):
        """Parse travel preferences from XML"""
        # Parse Air preferences
        air_elem = root.find("Air")
        if air_elem is not None:
            air_prefs = AirPreferences()
            
            # Seat preferences
            seat_elem = air_elem.find("Seat")
            if seat_elem is not None:
                seat_pref = seat_elem.findtext("InterRowPositionCode")
                if seat_pref:
                    try:
                        air_prefs.seat_preference = SeatPreference(seat_pref)
                    except ValueError:
                        pass
                
                seat_section = seat_elem.findtext("SectionPositionCode")
                if seat_section:
                    try:
                        air_prefs.seat_section = SeatSection(seat_section)
                    except ValueError:
                        pass
            
            # Meal preferences - check both structures
            meal_code = air_elem.findtext("MealCode")  # Direct structure
            if not meal_code:
                # Try nested structure
                meals_elem = air_elem.find("Meals")
                if meals_elem is not None:
                    meal_code = meals_elem.findtext("MealCode")
            
            if meal_code:
                try:
                    air_prefs.meal_preference = MealType(meal_code)
                except ValueError:
                    pass
            
            air_prefs.home_airport = air_elem.findtext("HomeAirport", "")
            air_prefs.air_other = air_elem.findtext("AirOther", "")
            
            # Air memberships
            memberships_elem = air_elem.find("AirMemberships")
            if memberships_elem is not None:
                for membership_elem in memberships_elem.findall("AirMembership"):
                    membership = self._parse_loyalty_membership(membership_elem, LoyaltyProgramType.AIR)
                    if membership:
                        air_prefs.memberships.append(membership)
                        profile.loyalty_programs.append(membership)
            
            profile.air_preferences = air_prefs
        
        # Parse Hotel preferences
        hotel_elem = root.find("Hotel")
        if hotel_elem is not None:
            hotel_prefs = HotelPreferences()
            
            # NOTE: SmokingCode is documented but not actually supported by the API
            # Check smoking code field name per documentation (but it won't be present)
            smoking_code = hotel_elem.findtext("SmokingCode")  # Per API documentation
            
            if smoking_code:
                try:
                    hotel_prefs.smoking_preference = SmokingPreference(smoking_code)
                except ValueError:
                    pass
            
            room_type = hotel_elem.findtext("RoomType")
            if room_type:
                try:
                    hotel_prefs.room_type = HotelRoomType(room_type)
                except ValueError:
                    pass
            
            hotel_prefs.hotel_other = hotel_elem.findtext("HotelOther", "")
            hotel_prefs.prefer_foam_pillows = hotel_elem.findtext("PreferFoamPillows", "false") == "true"
            hotel_prefs.prefer_crib = hotel_elem.findtext("PreferCrib", "false") == "true"
            hotel_prefs.prefer_rollaway_bed = hotel_elem.findtext("PreferRollawayBed", "false") == "true"
            hotel_prefs.prefer_gym = hotel_elem.findtext("PreferGym", "false") == "true"
            hotel_prefs.prefer_pool = hotel_elem.findtext("PreferPool", "false") == "true"
            # NOTE: PreferRestaraunt is documented but not actually supported by the API
            # Parse additional preference fields from documentation (note the typo in "PreferRestaraunt")
            # hotel_prefs.prefer_restaurant = hotel_elem.findtext("PreferRestaraunt", "false") == "true"
            hotel_prefs.prefer_room_service = hotel_elem.findtext("PreferRoomService", "false") == "true"
            hotel_prefs.prefer_early_checkin = hotel_elem.findtext("PreferEarlyCheckIn", "false") == "true"
            
            # Hotel memberships
            memberships_elem = hotel_elem.find("HotelMemberships")
            if memberships_elem is not None:
                for membership_elem in memberships_elem.findall("HotelMembership"):
                    membership = self._parse_loyalty_membership(membership_elem, LoyaltyProgramType.HOTEL)
                    if membership:
                        hotel_prefs.memberships.append(membership)
                        profile.loyalty_programs.append(membership)
            
            profile.hotel_preferences = hotel_prefs
        
        # Parse Car preferences
        car_elem = root.find("Car")
        if car_elem is not None:
            car_prefs = CarPreferences()
            
            # NOTE: CarType and CarTransmission are documented but not actually supported by the API
            car_type = car_elem.findtext("CarType")
            if car_type:
                try:
                    car_prefs.car_type = CarType(car_type)
                except ValueError:
                    pass
            
            transmission = car_elem.findtext("CarTransmission")
            if transmission:
                try:
                    car_prefs.transmission = TransmissionType(transmission)
                except ValueError:
                    pass
            
            smoking_code = car_elem.findtext("CarSmokingCode")
            if smoking_code:
                try:
                    car_prefs.smoking_preference = SmokingPreference(smoking_code)
                except ValueError:
                    pass
            
            car_prefs.gps = car_elem.findtext("CarGPS", "false") == "true"
            car_prefs.ski_rack = car_elem.findtext("CarSkiRack", "false") == "true"
            
            # Car memberships
            memberships_elem = car_elem.find("CarMemberships")
            if memberships_elem is not None:
                for membership_elem in memberships_elem.findall("CarMembership"):
                    membership = self._parse_loyalty_membership(membership_elem, LoyaltyProgramType.CAR)
                    if membership:
                        car_prefs.memberships.append(membership)
                        profile.loyalty_programs.append(membership)
            
            profile.car_preferences = car_prefs
        
        # Parse Rail preferences
        rail_elem = root.find("Rail")
        if rail_elem is not None:
            rail_prefs = RailPreferences()
            
            rail_prefs.seat = rail_elem.findtext("Seat", "")
            rail_prefs.coach = rail_elem.findtext("Coach", "")
            rail_prefs.noise_comfort = rail_elem.findtext("NoiseComfort", "")
            rail_prefs.bed = rail_elem.findtext("Bed", "")
            rail_prefs.bed_category = rail_elem.findtext("BedCategory", "")
            rail_prefs.berth = rail_elem.findtext("Berth", "")
            rail_prefs.deck = rail_elem.findtext("Deck", "")
            rail_prefs.space_type = rail_elem.findtext("SpaceType", "")
            rail_prefs.fare_space_comfort = rail_elem.findtext("FareSpaceComfort", "")
            rail_prefs.special_meals = rail_elem.findtext("SpecialMeals", "")
            rail_prefs.contingencies = rail_elem.findtext("Contingencies", "")
            
            # Rail memberships
            memberships_elem = rail_elem.find("RailMemberships")
            if memberships_elem is not None:
                for membership_elem in memberships_elem.findall("RailMembership"):
                    membership = self._parse_loyalty_membership(membership_elem, LoyaltyProgramType.RAIL)
                    if membership:
                        rail_prefs.memberships.append(membership)
                        profile.loyalty_programs.append(membership)
            
            profile.rail_preferences = rail_prefs
    
    def _parse_loyalty_membership(self, elem: etree.Element, program_type: LoyaltyProgramType) -> Optional[LoyaltyProgram]:
        """Parse a loyalty membership element"""
        vendor_code = elem.findtext("VendorCode", "")
        account_no = elem.findtext("AccountNo", "")
        
        if not vendor_code or not account_no:
            return None
        
        expiration = None
        if elem.findtext("Expiration"):
            try:
                expiration = datetime.strptime(elem.findtext("Expiration"), "%Y-%m-%d").date()
            except:
                pass
        
        return LoyaltyProgram(
            program_type=program_type,
            vendor_code=vendor_code,
            account_number=account_no,
            status=elem.findtext("Status", ""),
            status_benefits=elem.findtext("StatusBenefits", ""),
            point_total=elem.findtext("PointTotal", ""),
            segment_total=elem.findtext("SegmentTotal", ""),
            next_status=elem.findtext("NextStatus", ""),
            points_until_next_status=elem.findtext("PointsUntilNextStatus", ""),
            segments_until_next_status=elem.findtext("SegmentsUntilNextStatus", ""),
            expiration=expiration
        )
    
    def _parse_summary_response(self, xml_str: str) -> ConnectResponse:
        """Parse profile summary response from XML"""
        root = etree.fromstring(xml_str.encode('utf-8'))
        
        response = ConnectResponse()
        
        # Parse metadata/paging
        metadata_elem = root.find("Metadata")
        if metadata_elem is not None:
            paging_elem = metadata_elem.find("Paging")
            if paging_elem is not None:
                response.metadata = PagingInfo(
                    total_pages=int(paging_elem.findtext("TotalPages", "0")),
                    total_items=int(paging_elem.findtext("TotalItems", "0")),
                    page=int(paging_elem.findtext("Page", "1")),
                    items_per_page=int(paging_elem.findtext("ItemsPerPage", "200")),
                    previous_page_url=paging_elem.findtext("PreviousPageURL", ""),
                    next_page_url=paging_elem.findtext("NextPageURL", "")
                )
        
        # Parse profile summaries
        data_elem = root.find("Data")
        if data_elem is not None:
            for summary_elem in data_elem.findall("ProfileSummary"):
                status_str = summary_elem.findtext("Status", "Active")
                try:
                    status = ProfileStatus(status_str)
                except ValueError:
                    status = ProfileStatus.ACTIVE
                
                last_modified = None
                if summary_elem.findtext("ProfileLastModifiedUTC"):
                    try:
                        last_modified = datetime.strptime(
                            summary_elem.findtext("ProfileLastModifiedUTC"), 
                            "%Y-%m-%dT%H:%M:%S"
                        )
                    except:
                        pass
                
                response.profile_summaries.append(ProfileSummary(
                    status=status,
                    login_id=summary_elem.findtext("LoginID", ""),
                    xml_profile_sync_id=summary_elem.findtext("XmlProfileSyncID", ""),
                    profile_last_modified_utc=last_modified
                ))
        
        return response
    
    def get_current_user_profile(self) -> UserProfile:
        """
        Get the complete profile of the currently authenticated user
        
        Returns:
            UserProfile object containing all available profile information
            
        Raises:
            ConcurProfileError: If the request fails
            ValidationError: If the response cannot be parsed
        """
        logger.info("Getting profile for current user")
        
        response = self._make_request("GET", self.profile_url)
        
        if response.status_code != 200:
            error = ApiError.from_xml(response.text)
            raise ConcurProfileError(f"Failed to get profile: {error.message}")
        
        return self._parse_profile_response(response.text)
    
    def get_profile_by_login_id(self, login_id: str) -> UserProfile:
        """
        Get a complete user profile by login ID
        
        Args:
            login_id: The login ID (email) of the user
            
        Returns:
            UserProfile object containing all available profile information
            
        Raises:
            ProfileNotFoundError: If the user is not found
            ConcurProfileError: If the request fails
            ValidationError: If the response cannot be parsed
        """
        logger.info(f"Getting profile for user: {login_id}")
        
        url = f"{self.profile_url}?userid_type=login&userid_value={login_id}"
        response = self._make_request("GET", url)
        
        if response.status_code == 404 or "Invalid User" in response.text:
            raise ProfileNotFoundError(f"User not found: {login_id}")
        
        if response.status_code != 200:
            error = ApiError.from_xml(response.text)
            raise ConcurProfileError(f"Failed to get profile: {error.message}")
        
        return self._parse_profile_response(response.text)
    
    def list_profile_summaries(
        self,
        last_modified_date: datetime,
        page: int = 1,
        limit: int = 200,
        travel_configs: Optional[List[str]] = None,
        active_only: Optional[bool] = None
    ) -> ConnectResponse:
        """
        Get a list of profile summaries that have been updated since the specified date
        
        Args:
            last_modified_date: Only return profiles updated after this date (UTC)
            page: Page number to retrieve (default: 1)
            limit: Number of profiles per page (max: 200, default: 200)
            travel_configs: List of travel config IDs to filter by
            active_only: If True, only return active users; if False, only inactive; if None, return all
            
        Returns:
            ConnectResponse with paging info and list of ProfileSummary objects
            
        Raises:
            ConcurProfileError: If the request fails
            ValidationError: If the response cannot be parsed
        """
        logger.info(f"Listing profile summaries since {last_modified_date}")
        
        # Build query parameters
        params = {
            "LastModifiedDate": last_modified_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "Page": str(page),
            "ItemsPerPage": str(min(limit, 200))  # API max is 200
        }
        
        if travel_configs:
            params["travelConfigs"] = ",".join(travel_configs)
        
        if active_only is not None:
            params["Active"] = "1" if active_only else "0"
        
        # Build URL with query parameters
        url = f"{self.summary_url}?" + "&".join(f"{k}={v}" for k, v in params.items())
        
        response = self._make_request("GET", url)
        
        if response.status_code != 200:
            error = ApiError.from_xml(response.text)
            raise ConcurProfileError(f"Failed to get profile summaries: {error.message}")
        
        return self._parse_summary_response(response.text)
    
    def create_user(
        self,
        profile: UserProfile,
        password: Optional[str] = None
    ) -> ApiResponse:
        """
        Create a new user profile with comprehensive data
        
        This method uses a two-step process:
        1. Create user with essential fields only (FirstName, LastName, RuleClass, TravelConfigID)
        2. Update user with additional fields if provided (JobTitle, CompanyName, etc.)
        
        Args:
            profile: UserProfile object with required fields:
                     - login_id: unique email address
                     - first_name: user's first name
                     - last_name: user's last name
                     - travel_config_id: your organization's travel config ID
            password: Optional password (random one will be generated if not provided)
            
        Returns:
            ApiResponse with success code and UUID of created user
            
        Raises:
            ValidationError: If required fields are missing
            ConcurProfileError: If the creation fails
        """
        # Validate required fields
        if not profile.login_id:
            raise ValidationError("login_id is required")
        if not profile.first_name:
            raise ValidationError("first_name is required")
        if not profile.last_name:
            raise ValidationError("last_name is required")
        if not profile.travel_config_id:
            raise ValidationError("travel_config_id is required")
        
        # Set password if provided
        if password:
            profile.password = password
        
        logger.info(f"Creating user: {profile.login_id}")
        
        # Step 1: Create user with essential fields only
        xml_data = profile.to_create_xml()
        logger.debug(f"Generated creation XML:\n{xml_data}")
        
        response = self._make_request("POST", self.profile_url, data=xml_data)
        
        if response.status_code != 200:
            error = ApiError.from_xml(response.text)
            raise ConcurProfileError(f"Failed to create user: {error.message}")
        
        create_response = ApiResponse.from_xml(response.text)
        
        # Step 2: Check if we need to update with additional fields
        # Start with the most reliable fields first
        additional_fields = []
        if profile.job_title:
            additional_fields.append("job_title")
        if profile.company_name:
            additional_fields.append("company_name")
        if profile.employee_id:
            additional_fields.append("employee_id")
        # Note: middle_name and medical_alerts can be problematic, handle separately
        if profile.medical_alerts:
            additional_fields.append("medical_alerts")
        
        # Add non-general fields that were provided
        if profile.addresses:
            additional_fields.append("addresses")
        if profile.phones:
            additional_fields.append("phones")
        if profile.emails:
            additional_fields.append("emails")
        if profile.emergency_contacts:
            additional_fields.append("emergency_contacts")
        if profile.national_ids:
            additional_fields.append("national_ids")
        if profile.drivers_licenses:
            additional_fields.append("drivers_licenses")
        if profile.passports:
            additional_fields.append("passports")
        if profile.visas:
            additional_fields.append("visas")
        if profile.tsa_info:
            additional_fields.append("tsa_info")
        if profile.custom_fields:
            additional_fields.append("custom_fields")
        
        # Add travel preferences - these are often sensitive and should be updated individually
        travel_preference_fields = []
        if profile.air_preferences:
            travel_preference_fields.append("air_preferences")
        if profile.hotel_preferences:
            travel_preference_fields.append("hotel_preferences")
        if profile.car_preferences:
            travel_preference_fields.append("car_preferences")
        if profile.rail_preferences:
            travel_preference_fields.append("rail_preferences")
        if profile.rate_preferences:
            travel_preference_fields.append("rate_preferences")
        if profile.discount_codes:
            travel_preference_fields.append("discount_codes")
        
        # Add loyalty programs - these must be updated after creation
        if profile.loyalty_programs:
            travel_preference_fields.append("loyalty_programs")
        
        # If we have additional fields, update the user
        if additional_fields or travel_preference_fields:
            logger.info(f"Updating user with additional fields: {additional_fields + travel_preference_fields}")
            try:
                # Wait for user to be available for updates
                import time
                self._wait_for_user_availability(profile.login_id, max_wait=30)
                
                # Update each field individually to avoid XML validation issues
                # This is more reliable than multi-field updates
                for field in additional_fields:
                    try:
                        logger.info(f"Updating field: {field}")
                        update_response = self.update_user(profile, fields_to_update=[field])
                        logger.info(f"Successfully updated {field}")
                    except Exception as e:
                        logger.warning(f"Failed to update {field}: {e}")
                
                # Handle travel preferences separately - these are particularly sensitive
                # Update each travel preference field individually with delays
                for travel_field in travel_preference_fields:
                    try:
                        logger.info(f"Updating travel preference: {travel_field}")
                        
                        # Special handling for car preferences - they need to be set one field at a time
                        if travel_field == "car_preferences" and profile.car_preferences:
                            self._update_car_preferences_individually(profile.login_id, profile.car_preferences)
                        # Special handling for loyalty programs - they need to be set one at a time
                        elif travel_field == "loyalty_programs" and profile.loyalty_programs:
                            self._update_loyalty_programs_individually(profile.login_id, profile.loyalty_programs)
                        else:
                            update_response = self.update_user(profile, fields_to_update=[travel_field])
                            logger.info(f"Successfully updated {travel_field}")
                        
                        # Wait between travel preference updates to allow processing
                        time.sleep(2)
                        
                    except Exception as e:
                        logger.warning(f"Failed to update {travel_field}: {e}")
                        # Continue with other fields even if one fails
                
                # Handle middle_name separately if provided
                if profile.middle_name:
                    try:
                        logger.info("Updating middle name...")
                        middle_name_response = self.update_user(profile, fields_to_update=["middle_name"])
                        logger.info("Middle name updated successfully")
                    except Exception as e:
                        logger.warning(f"Failed to update middle name: {e}")
                
                logger.info("User created and updated successfully with additional fields")
                
            except Exception as e:
                logger.warning(f"User created but failed to update with additional fields: {e}")
                # Don't fail the whole operation, user was created successfully
        
        return create_response
    
    def update_user(
        self,
        profile: UserProfile,
        fields_to_update: Optional[List[str]] = None
    ) -> ApiResponse:
        """
        Update an existing user profile with comprehensive data
        
        Args:
            profile: UserProfile object with login_id and fields to update
            fields_to_update: Optional list of field names to update.
                            If not provided, all non-empty fields will be updated.
                            Valid field names include all UserProfile fields:
                            - General: "first_name", "last_name", "middle_name", "job_title", etc.
                            - Contact: "addresses", "phones", "emails", "emergency_contacts"
                            - Documents: "national_ids", "drivers_licenses", "passports", "visas"
                            - Travel: "air_preferences", "hotel_preferences", "car_preferences", "rail_preferences"
                            - Other: "tsa_info", "custom_fields", "unused_tickets", etc.
            
        Returns:
            ApiResponse with success code
            
        Raises:
            ValidationError: If login_id is missing
            ProfileNotFoundError: If the user is not found
            ConcurProfileError: If the update fails
        """
        if not profile.login_id:
            raise ValidationError("login_id is required for update")
        
        logger.info(f"Updating user: {profile.login_id}")
        
        xml_data = profile.to_update_xml(fields_to_update)
        
        # Debug: Log the XML being sent for hotel preferences
        if fields_to_update and "hotel_preferences" in fields_to_update:
            logger.info(f"Hotel preferences XML being sent:\n{xml_data}")
        else:
            logger.debug(f"Generated XML:\n{xml_data}")
        
        response = self._make_request("POST", self.profile_url, data=xml_data)
        
        if response.status_code == 404 or "Invalid User" in response.text:
            raise ProfileNotFoundError(f"User not found: {profile.login_id}")
        
        if response.status_code != 200:
            # Debug: Log the full response for hotel preferences errors
            if fields_to_update and "hotel_preferences" in fields_to_update:
                logger.info(f"Hotel preferences update failed. Status: {response.status_code}")
                logger.info(f"Response text: {response.text}")
            error = ApiError.from_xml(response.text)
            raise ConcurProfileError(f"Failed to update user: {error.message}")
        
        return ApiResponse.from_xml(response.text)
    
    def update_loyalty_program(
        self,
        loyalty_program: LoyaltyProgram,
        login_id: Optional[str] = None
    ) -> LoyaltyResponse:
        """
        Update a user's loyalty program information using the dedicated Loyalty v1 API
        
        Note: This functionality has significant restrictions per Concur documentation:
        - Only available to travel suppliers who have completed SAP Concur application review
        - Travel suppliers can only update their OWN loyalty program information
        - TMCs can update any loyalty program for users
        
        Args:
            loyalty_program: LoyaltyProgram object with required fields:
                           - program_type: Air, Hotel, Car, or Rail
                           - vendor_code: 2-letter vendor code
                           - account_number: User's membership number
                           - status: Optional status level
            login_id: Optional login ID (uses authenticated user if not provided)
            
        Returns:
            LoyaltyResponse indicating success or failure
            
        Raises:
            ValidationError: If required fields are missing
            ConcurProfileError: If the request fails
        """
        # Validate required fields
        if not loyalty_program.vendor_code:
            raise ValidationError("vendor_code is required")
        if not loyalty_program.account_number:
            raise ValidationError("account_number is required")
        
        logger.info(f"Updating {loyalty_program.program_type.value} loyalty program: {loyalty_program.vendor_code}")
        
        # Map program type to vendor type code
        vendor_type_map = {
            LoyaltyProgramType.AIR: VendorType.AIR.value,
            LoyaltyProgramType.HOTEL: VendorType.HOTEL.value,
            LoyaltyProgramType.CAR: VendorType.CAR.value,
            LoyaltyProgramType.RAIL: VendorType.RAIL.value
        }
        
        vendor_type = vendor_type_map[loyalty_program.program_type]
        
        # Build XML for loyalty update
        root = etree.Element("LoyaltyMembershipUpdate")
        membership = etree.SubElement(
            root, 
            "Membership", 
            UniqueID=f"{loyalty_program.program_type.value} Program"
        )
        
        etree.SubElement(membership, "VendorCode").text = loyalty_program.vendor_code
        etree.SubElement(membership, "VendorType").text = vendor_type
        etree.SubElement(membership, "AccountNo").text = loyalty_program.account_number
        
        if loyalty_program.status:
            etree.SubElement(membership, "Status").text = loyalty_program.status
        
        xml_data = etree.tostring(root, pretty_print=True, encoding='utf-8').decode('utf-8')
        logger.debug(f"Generated loyalty XML:\n{xml_data}")
        
        response = self._make_request("POST", self.loyalty_url, data=xml_data)
        
        if response.status_code != 200:
            error = ApiError.from_xml(response.text)
            return LoyaltyResponse(
                success=False, 
                error=f"Failed to update loyalty program: {error.message}"
            )
        
        return LoyaltyResponse.from_xml(response.text)
    
    def delete_user(self, login_id: str) -> ApiResponse:
        """
        Delete/deactivate a user profile
        
        Note: Concur typically doesn't support true deletion, but rather deactivation.
        This method is provided for completeness but may not be supported by all Concur instances.
        
        Args:
            login_id: The login ID of the user to delete/deactivate
            
        Returns:
            ApiResponse with result
            
        Raises:
            ProfileNotFoundError: If the user is not found
            ConcurProfileError: If the request fails
        """
        logger.warning(f"Attempting to delete user: {login_id} (may not be supported)")
        
        # Most Concur implementations don't support DELETE method
        # This would need to be implemented as a status update to "Inactive"
        # For now, we'll attempt the operation but expect it may fail
        
        url = f"{self.profile_url}?userid_type=login&userid_value={login_id}"
        response = self._make_request("DELETE", url)
        
        if response.status_code == 404:
            raise ProfileNotFoundError(f"User not found: {login_id}")
        
        if response.status_code not in [200, 204]:
            error = ApiError.from_xml(response.text)
            raise ConcurProfileError(f"Failed to delete user: {error.message}")
        
        return ApiResponse(
            code="S001",
            message="User deleted/deactivated successfully",
            success=True
        ) 