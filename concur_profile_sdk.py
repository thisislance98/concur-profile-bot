#!/usr/bin/env python3
"""
Complete Concur SDK using Identity v4 + Travel Profile v2

A comprehensive SDK for interacting with SAP Concur's APIs:
- Identity v4 for user management (SCIM 2.0) - replaces Profile v1
- Travel Profile v2 for travel preferences, loyalty programs, and travel-specific data
"""

import requests
from lxml import etree
from typing import Dict, List, Optional, Union, TypedDict, Literal, Any
from datetime import datetime, timedelta, date
from enum import Enum
import logging
from dataclasses import dataclass, field, asdict
import json
import re
import base64
import urllib.parse
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Identity v4 Types and Enums
class SCIMSchemas(str, Enum):
    """SCIM schema URNs"""
    CORE_USER = "urn:ietf:params:scim:schemas:core:2.0:User"
    ENTERPRISE_USER = "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User"
    CONCUR_USER = "urn:ietf:params:scim:schemas:extension:concur:2.0:User"
    PATCH_OP = "urn:ietf:params:scim:api:messages:2.0:PatchOp"


class IdentityResourceType(str, Enum):
    """Identity resource types"""
    USER = "User"
    GROUP = "Group"


# Travel Profile v2 Enums (keeping these for travel preferences)
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


# Identity v4 Data Classes
@dataclass
class IdentityEmail:
    """Identity v4 email structure"""
    value: str
    type: str = "work"
    primary: bool = True
    verified: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "type": self.type,
            "primary": self.primary,
            "verified": self.verified
        }


@dataclass
class IdentityPhoneNumber:
    """Identity v4 phone number structure"""
    value: str
    type: str = "work"
    primary: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "type": self.type,
            "primary": self.primary
        }


@dataclass
class IdentityName:
    """Identity v4 name structure"""
    given_name: str = ""
    family_name: str = ""
    middle_name: str = ""
    formatted: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.given_name:
            result["givenName"] = self.given_name
        if self.family_name:
            result["familyName"] = self.family_name
        if self.middle_name:
            result["middleName"] = self.middle_name
        if self.formatted:
            result["formatted"] = self.formatted
        return result


@dataclass
class IdentityEnterpriseInfo:
    """Identity v4 enterprise extension"""
    company_id: str = ""
    employee_number: str = ""
    start_date: Optional[date] = None
    department: str = ""
    cost_center: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        if self.company_id:
            result["companyId"] = self.company_id
        if self.employee_number:
            result["employeeNumber"] = self.employee_number
        if self.start_date:
            result["startDate"] = self.start_date.isoformat()
        if self.department:
            result["department"] = self.department
        if self.cost_center:
            result["costCenter"] = self.cost_center
        return result


@dataclass
class IdentityUser:
    """Complete Identity v4 user object"""
    user_name: str
    
    # Core user attributes
    display_name: str = ""
    active: bool = True
    title: str = ""
    nick_name: str = ""
    preferred_language: str = "en-US"
    timezone: str = "America/New_York"
    
    # Complex attributes
    name: Optional[IdentityName] = None
    emails: List[IdentityEmail] = field(default_factory=list)
    phone_numbers: List[IdentityPhoneNumber] = field(default_factory=list)
    
    # Enterprise attributes
    enterprise_info: Optional[IdentityEnterpriseInfo] = None
    
    # System attributes (read-only)
    id: str = ""
    external_id: str = ""
    
    def to_create_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for user creation"""
        user_data = {
            "schemas": [
                SCIMSchemas.CORE_USER.value,
                SCIMSchemas.ENTERPRISE_USER.value
            ],
            "userName": self.user_name,
            "active": self.active
        }
        
        # Add optional core fields
        if self.display_name:
            user_data["displayName"] = self.display_name
        if self.title:
            user_data["title"] = self.title
        if self.nick_name:
            user_data["nickName"] = self.nick_name
        if self.preferred_language:
            user_data["preferredLanguage"] = self.preferred_language
        if self.timezone:
            user_data["timezone"] = self.timezone
        if self.external_id:
            user_data["externalId"] = self.external_id
        
        # Add name
        if self.name:
            name_dict = self.name.to_dict()
            if name_dict:
                user_data["name"] = name_dict
        
        # Add emails
        if self.emails:
            user_data["emails"] = [email.to_dict() for email in self.emails]
        
        # Add phone numbers
        if self.phone_numbers:
            user_data["phoneNumbers"] = [phone.to_dict() for phone in self.phone_numbers]
        
        # Add enterprise extension
        if self.enterprise_info:
            enterprise_dict = self.enterprise_info.to_dict()
            if enterprise_dict:
                user_data[SCIMSchemas.ENTERPRISE_USER.value] = enterprise_dict
        
        return user_data
    
    @classmethod
    def from_identity_response(cls, data: Dict[str, Any]) -> 'IdentityUser':
        """Create IdentityUser from Identity v4 API response"""
        user = cls(
            user_name=data.get("userName", ""),
            id=data.get("id", ""),
            display_name=data.get("displayName", ""),
            active=data.get("active", True),
            title=data.get("title", ""),
            nick_name=data.get("nickName", ""),
            preferred_language=data.get("preferredLanguage", "en-US"),
            timezone=data.get("timezone", "America/New_York"),
            external_id=data.get("externalId", "")
        )
        
        # Parse name
        if "name" in data:
            name_data = data["name"]
            user.name = IdentityName(
                given_name=name_data.get("givenName", ""),
                family_name=name_data.get("familyName", ""),
                middle_name=name_data.get("middleName", ""),
                formatted=name_data.get("formatted", "")
            )
        
        # Parse emails
        if "emails" in data:
            user.emails = [
                IdentityEmail(
                    value=email.get("value", ""),
                    type=email.get("type", "work"),
                    primary=email.get("primary", False),
                    verified=email.get("verified", False)
                )
                for email in data["emails"]
            ]
        
        # Parse phone numbers
        if "phoneNumbers" in data:
            user.phone_numbers = [
                IdentityPhoneNumber(
                    value=phone.get("value", ""),
                    type=phone.get("type", "work"),
                    primary=phone.get("primary", False)
                )
                for phone in data["phoneNumbers"]
            ]
        
        # Parse enterprise info
        enterprise_key = SCIMSchemas.ENTERPRISE_USER.value
        if enterprise_key in data:
            enterprise_data = data[enterprise_key]
            start_date = None
            if enterprise_data.get("startDate"):
                try:
                    start_date = datetime.fromisoformat(enterprise_data["startDate"]).date()
                except:
                    pass
            
            user.enterprise_info = IdentityEnterpriseInfo(
                company_id=enterprise_data.get("companyId", ""),
                employee_number=enterprise_data.get("employeeNumber", ""),
                start_date=start_date,
                department=enterprise_data.get("department", ""),
                cost_center=enterprise_data.get("costCenter", "")
            )
        
        return user


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
        
        # IMPORTANT: Based on API testing, the <Seat> element seems to be required 
        # even when only other air preferences (like home_airport) are set.
        # Always include the Seat element if we have any air preferences.
        
        # Check if we need to create a Seat element
        has_seat_prefs = self.seat_preference or self.seat_section
        has_other_air_prefs = self.home_airport or self.air_other or self.meal_preference
        
        # Always create Seat element if we have any air preferences to avoid validation errors
        if has_seat_prefs or has_other_air_prefs:
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
        
        # NOTE: PreferRestaraunt is documented but not actually supported by the API
        if self.prefer_room_service:
            etree.SubElement(hotel_elem, "PreferRoomService").text = "true"
        
        if self.prefer_early_checkin:
            etree.SubElement(hotel_elem, "PreferEarlyCheckIn").text = "true"
        
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
class TravelProfile:
    """Travel Profile v2 data - contains only travel-specific information"""
    login_id: str
    
    # Travel configuration
    rule_class: str = "Default Travel Class"
    travel_config_id: str = ""
    
    # Travel documents and identity
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
    
    def to_update_xml(self, fields_to_update: Optional[List[str]] = None) -> str:
        """Convert to XML for travel profile update using lxml"""
        # Create root element with proper namespace and schema location
        root = etree.Element("ProfileResponse", 
                           nsmap={'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
        root.set("Action", ProfileAction.UPDATE.value)
        root.set("LoginId", self.login_id)
        
        # If no specific fields, update all non-empty fields
        if fields_to_update is None:
            fields_to_update = self._get_non_empty_fields()
        
        # Add sections based on fields_to_update
        self._add_sections_to_xml(root, fields_to_update)
        
        # Return properly formatted XML
        return etree.tostring(root, 
                             pretty_print=True, 
                             xml_declaration=True, 
                             encoding='utf-8').decode('utf-8')
    
    def _get_non_empty_fields(self) -> List[str]:
        """Get list of non-empty field names for update"""
        fields = []
        if self.rule_class: fields.append("rule_class")
        if self.travel_config_id: fields.append("travel_config_id")
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
        """Add travel profile sections to XML in schema order"""
        
        # General section for travel config
        general_fields = ["rule_class", "travel_config_id"]
        if any(f in fields_to_update for f in general_fields):
            general = etree.SubElement(root, "General")
            
            if "rule_class" in fields_to_update and self.rule_class:
                etree.SubElement(general, "RuleClass").text = self.rule_class
            if "travel_config_id" in fields_to_update and self.travel_config_id:
                etree.SubElement(general, "TravelConfigID").text = self.travel_config_id
        
        # Travel documents in schema order
        if not fields_to_update or "national_ids" in fields_to_update:
            if self.national_ids:
                ids_elem = etree.SubElement(root, "NationalIDs")
                for national_id in self.national_ids:
                    national_id.to_xml_element(ids_elem)
        
        if not fields_to_update or "drivers_licenses" in fields_to_update:
            if self.drivers_licenses:
                licenses_elem = etree.SubElement(root, "DriversLicenses")
                for license in self.drivers_licenses:
                    license.to_xml_element(licenses_elem)
        
        if not fields_to_update or "has_no_passport" in fields_to_update:
            if self.has_no_passport:
                etree.SubElement(root, "HasNoPassport").text = "true"
        
        if not fields_to_update or "passports" in fields_to_update:
            if self.passports:
                passports_elem = etree.SubElement(root, "Passports")
                for passport in self.passports:
                    passport.to_xml_element(passports_elem)
        
        if not fields_to_update or "visas" in fields_to_update:
            if self.visas:
                visas_elem = etree.SubElement(root, "Visas")
                for visa in self.visas:
                    visa.to_xml_element(visas_elem)
        
        # Rate preferences and discount codes
        if not fields_to_update or "rate_preferences" in fields_to_update:
            if self.rate_preferences:
                self.rate_preferences.to_xml_element(root)
        
        if not fields_to_update or "discount_codes" in fields_to_update:
            if self.discount_codes:
                codes_elem = etree.SubElement(root, "DiscountCodes")
                for code in self.discount_codes:
                    code.to_xml_element(codes_elem)
        
        # Travel preferences
        if not fields_to_update or "air_preferences" in fields_to_update:
            if self.air_preferences:
                self.air_preferences.to_xml_element(root)
        
        if not fields_to_update or "rail_preferences" in fields_to_update:
            if self.rail_preferences:
                self.rail_preferences.to_xml_element(root)
        
        if not fields_to_update or "car_preferences" in fields_to_update:
            if self.car_preferences:
                car_elem = self.car_preferences.to_xml_element(root)
        
        if not fields_to_update or "hotel_preferences" in fields_to_update:
            if self.hotel_preferences:
                hotel_elem = self.hotel_preferences.to_xml_element(root)
        
        # Custom fields
        if not fields_to_update or "custom_fields" in fields_to_update:
            if self.custom_fields:
                fields_elem = etree.SubElement(root, "CustomFields")
                for field in self.custom_fields:
                    field.to_xml_element(fields_elem)
        
        # TSA info
        if not fields_to_update or "tsa_info" in fields_to_update:
            if self.tsa_info:
                self.tsa_info.to_xml_element(root)
        
        # Unused tickets
        if not fields_to_update or "unused_tickets" in fields_to_update:
            if self.unused_tickets:
                tickets_elem = etree.SubElement(root, "UnusedTickets")
                for ticket in self.unused_tickets:
                    ticket.to_xml_element(tickets_elem)
        
        if not fields_to_update or "southwest_unused_tickets" in fields_to_update:
            if self.southwest_unused_tickets:
                sw_tickets_elem = etree.SubElement(root, "SouthwestUnusedTickets")
                for ticket in self.southwest_unused_tickets:
                    ticket.to_xml_element(sw_tickets_elem)
        
        # Loyalty programs
        if not fields_to_update or "loyalty_programs" in fields_to_update:
            if self.loyalty_programs:
                memberships_elem = etree.SubElement(root, "AdvantageMemberships")
                for loyalty_program in self.loyalty_programs:
                    loyalty_program.to_xml_element(memberships_elem, "Membership")


@dataclass
class IdentityPatchOperation:
    """SCIM 2.0 PATCH operation for Identity v4"""
    op: str  # "add", "remove", "replace"
    path: str
    value: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "op": self.op,
            "path": self.path
        }
        if self.value is not None:
            result["value"] = self.value
        return result


@dataclass
class IdentityPatchRequest:
    """SCIM 2.0 PATCH request for Identity v4"""
    operations: List[IdentityPatchOperation]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "schemas": [SCIMSchemas.PATCH_OP.value],
            "Operations": [op.to_dict() for op in self.operations]
        }


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
class ApiResponse:
    """Represents a response from the Concur API"""
    success: bool
    message: str = ""
    profile_id: str = ""
    
    @classmethod
    def from_xml(cls, xml_str: str) -> 'ApiResponse':
        """Parse an API response from XML"""
        try:
            root = etree.fromstring(xml_str.encode('utf-8'))
            
            # Check for error response
            if root.tag == "Errors":
                error_text = root.findtext("Error/Text", "Unknown error")
                return cls(success=False, message=error_text)
            
            # Check for success response
            status = root.get("Status", "")
            if status == "Success":
                profile_id = root.get("ProfileID", "")
                return cls(success=True, message="Operation completed successfully", profile_id=profile_id)
            elif status == "ERROR":
                error_desc = root.findtext("ErrorDescription", "Unknown error")
                return cls(success=False, message=error_desc)
            else:
                return cls(success=True, message="Operation completed")
                
        except Exception as e:
            return cls(success=False, message=f"Failed to parse response: {str(e)}")


@dataclass
class ApiError:
    """Represents an error from the Concur API"""
    message: str
    code: str = ""
    
    @classmethod
    def from_xml(cls, xml_str: str) -> 'ApiError':
        """Parse an API error from XML"""
        try:
            root = etree.fromstring(xml_str.encode('utf-8'))
            
            # Try different error formats
            if root.tag == "Errors":
                error_text = root.findtext("Error/Text", "Unknown error")
                error_code = root.findtext("Error/Code", "")
                return cls(message=error_text, code=error_code)
            elif root.tag == "Error":
                error_text = root.findtext("Text", root.text or "Unknown error")
                error_code = root.findtext("Code", "")
                return cls(message=error_text, code=error_code)
            else:
                error_desc = root.findtext("ErrorDescription", "Unknown error")
                return cls(message=error_desc)
                
        except Exception as e:
            return cls(message=f"Failed to parse error: {str(e)}")


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


class ConcurSDK:
    """
    Complete SDK for interacting with Concur APIs using Identity v4 + Travel Profile v2
    
    This SDK provides comprehensive access to Concur functionality:
    - Identity v4 for user management (SCIM 2.0) - replaces Profile v1
    - Travel Profile v2 for travel preferences, loyalty programs, and travel-specific data
    
    Key Features:
    - Full CRUD operations on user identities via Identity v4
    - Complete travel profile management via Travel Profile v2
    - Loyalty program management
    - Travel preferences (Air, Hotel, Car, Rail)
    - Advanced features like TSA info, custom fields, etc.
    
    Args:
        client_id: Your Concur OAuth client ID
        client_secret: Your Concur OAuth client secret
        username: Concur username for authentication
        password: Concur password for authentication
        base_url: Base URL for Concur API (defaults to US instance)
    
    Example:
        sdk = ConcurSDK(
            client_id="your-client-id",
            client_secret="your-client-secret", 
            username="user@example.com",
            password="password123"
        )
        
        # Get current user identity
        identity = sdk.get_current_user_identity()
        print(f"Hello {identity.display_name}!")
        
        # Get current user's travel profile
        travel_profile = sdk.get_current_user_travel_profile()
        
        # Create a new user
        new_user = IdentityUser(
            user_name="newuser@example.com",
            name=IdentityName(given_name="John", family_name="Doe"),
            emails=[IdentityEmail(value="newuser@example.com")]
        )
        result = sdk.create_user_identity(new_user)
        
        # Update travel preferences
        travel_profile = TravelProfile(
            login_id="user@example.com",
            air_preferences=AirPreferences(
                home_airport="SEA",
                seat_preference=SeatPreference.WINDOW
            )
        )
        sdk.update_travel_profile(travel_profile)
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        refresh_token: Optional[str] = None,
        base_url: str = "https://us2.api.concursolutions.com",
        company_id: Optional[str] = None
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.refresh_token = refresh_token
        self.base_url = base_url.rstrip("/")
        
        # Set company ID from parameter or environment variable
        self.company_id = company_id or os.getenv('CONCUR_COMPANY_UUID')
        
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self._geolocation: Optional[str] = None
        
        # Validate authentication parameters - allow client credentials (no username/password or refresh_token)
        if not (client_id and client_secret):
            raise ValidationError("client_id and client_secret are required")
        
        # API endpoints
        self.auth_url = f"{self.base_url}/oauth2/v0/token"
        self.travel_profile_url = f"{self.base_url}/api/travelprofile/v2.0/profile"
        self.travel_summary_url = f"{self.base_url}/api/travelprofile/v2.0/summary"
        self.loyalty_url = f"{self.base_url}/api/travelprofile/v1.0/loyalty"
        # Identity v4 endpoint will be constructed using geolocation after auth
        self._identity_base_url: Optional[str] = None
    
    def _ensure_authenticated(self) -> None:
        """Ensure we have a valid access token"""
        if not self._access_token or (self._token_expiry and datetime.now() >= self._token_expiry):
            self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Concur API and store access token and geolocation"""
        logger.info("Authenticating with Concur API...")
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "concur-correlationid": "python-concur-sdk"
        }
        
        # Choose authentication method based on available parameters
        if self.refresh_token:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            }
        elif self.username and self.password:
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "password",
                "username": self.username,
                "password": self.password
            }
        else:
            # Use client credentials grant as fallback
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials"
            }
        
        try:
            response = requests.post(self.auth_url, headers=headers, data=data)
            response.raise_for_status()
            
            auth_data: AuthResponse = response.json()
            self._access_token = auth_data["access_token"]
            self._geolocation = auth_data["geolocation"]
            
            # Set up Identity v4 endpoint using geolocation
            self._identity_base_url = f"{self._geolocation}/profile/identity/v4"
            
            # Calculate token expiry (subtract 60 seconds for safety)
            expires_in = auth_data["expires_in"] - 60
            self._token_expiry = datetime.now().replace(microsecond=0) + timedelta(seconds=expires_in)
            
            logger.info(f"Authentication successful! Geolocation: {self._geolocation}")
            
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")
    
    def _make_identity_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """Make an authenticated request to the Identity v4 API"""
        self._ensure_authenticated()
        
        if not self._identity_base_url:
            raise AuthenticationError("Identity base URL not available - authentication may have failed")
        
        url = f"{self._identity_base_url}/{endpoint.lstrip('/')}"
        
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        json_data = json.dumps(data) if data else None
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=json_data,
                params=params
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
                    data=json_data,
                    params=params
                )
            
            return response
            
        except requests.exceptions.RequestException as e:
            raise ConcurProfileError(f"Identity API request failed: {str(e)}")
    
    def _make_travel_profile_request(
        self,
        method: str,
        url: str,
        data: Optional[str] = None,
        params: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """Make an authenticated request to the Travel Profile v2 API"""
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
                data=data,
                params=params
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
                    data=data,
                    params=params
                )
            
            return response
            
        except requests.exceptions.RequestException as e:
            raise ConcurProfileError(f"Travel Profile API request failed: {str(e)}")
    
    # ========================================
    # Identity v4 API Methods (User Management)
    # ========================================
    
    def _decode_jwt_payload(self, jwt_token: str) -> Dict[str, Any]:
        """Decode JWT payload without verification (for extracting user info)"""
        try:
            # JWT tokens have 3 parts separated by dots: header.payload.signature
            parts = jwt_token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid JWT token format")
            
            # Decode the payload (middle part)
            payload = parts[1]
            
            # Add padding if needed for base64 decoding
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            
            # Decode base64 and parse JSON
            decoded_bytes = base64.urlsafe_b64decode(payload)
            payload_data = json.loads(decoded_bytes.decode('utf-8'))
            
            return payload_data
        except Exception as e:
            logger.warning(f"Failed to decode JWT token: {e}")
            return {}
    
    def get_current_user_identity(self) -> IdentityUser:
        """
        Get the identity of the currently authenticated user
            
        Returns:
            IdentityUser object containing user identity information
            
        Raises:
            ConcurProfileError: If the request fails
            ValidationError: If the response cannot be parsed
            AuthenticationError: If token lacks user access permissions
        """
        logger.info("Getting identity for current user")
        
        # Try the /me endpoint first
        try:
            response = self._make_identity_request("GET", "me")
        
            if response.status_code == 200:
                user_data = response.json()
                logger.debug(f"Current user data from /me endpoint: {user_data}")
        
                # Check if this is a User resource or Company resource
                resource_type = user_data.get('meta', {}).get('resourceType', '')
        
                if resource_type == 'User':
                    # This is a user identity, parse it directly
                    return IdentityUser.from_identity_response(user_data)
                elif resource_type == 'Company':
                    # This is company info, we need to extract user ID from JWT
                    logger.info("Got Company resource from /me, extracting user ID from JWT token")
                    
                    if self._access_token:
                        jwt_payload = self._decode_jwt_payload(self._access_token)
                        user_id = jwt_payload.get('sub')
                        
                        if user_id:
                            logger.info(f"Attempting to get user by ID from JWT: {user_id}")
                            try:
                                return self.get_user_identity_by_id(user_id)
                            except ProfileNotFoundError:
                                # The ID from JWT is likely a company ID, not user ID
                                logger.info("JWT 'sub' field contains company ID, not user ID")
                                raise AuthenticationError(
                                    "Company-scoped token detected. "
                                    "This token does not provide access to user identity information. "
                                    "Please use a user-scoped refresh token or username/password authentication."
                                )
                        else:
                            raise AuthenticationError("Could not extract user ID from JWT token")
                    else:
                        raise AuthenticationError("No access token available")
                else:
                    # Unknown resource type
                    raise ValidationError(f"Unknown resource type from /me endpoint: {resource_type}")
            
            else:
                # Non-200 response
                error_msg = f"Failed to get current user identity: HTTP {response.status_code}"
                if response.text:
                    error_msg += f" - {response.text}"
                raise ConcurProfileError(error_msg)
                
        except AuthenticationError:
            # Re-raise authentication errors as-is
            raise
        except ConcurProfileError:
            # Re-raise SDK errors as-is
            raise
        except Exception as e:
            # Wrap other exceptions
            raise ConcurProfileError(f"Unexpected error getting current user identity: {str(e)}")
    
    def get_user_identity_by_id(self, user_id: str) -> IdentityUser:
        """
        Get a user identity by ID
        
        Args:
            user_id: The unique ID of the user
            
        Returns:
            IdentityUser object containing user identity information
            
        Raises:
            ProfileNotFoundError: If the user is not found
            ConcurProfileError: If the request fails
        """
        logger.info(f"Getting user identity by ID: {user_id}")
        
        try:
            response = self._make_identity_request("GET", f"Users/{user_id}")
            
            if response.status_code == 200:
                user_data = response.json()
                return IdentityUser.from_identity_response(user_data)
            elif response.status_code == 404:
                raise ProfileNotFoundError(f"User not found: {user_id}")
            else:
                error_msg = f"Failed to get user {user_id}: HTTP {response.status_code}"
                if response.text:
                    error_msg += f" - {response.text}"
                raise ConcurProfileError(error_msg)
                
        except ProfileNotFoundError:
            raise
        except Exception as e:
            raise ConcurProfileError(f"Error getting user by ID {user_id}: {str(e)}")
    
    def find_user_by_username(self, username: str) -> Optional[IdentityUser]:
        """
        Find a user by username
        
        Args:
            username: The username to search for
            
        Returns:
            IdentityUser object containing user identity information, or None if not found
            
        Raises:
            ConcurProfileError: If the request fails
        """
        logger.info(f"Finding user by username: {username}")
        
        try:
            # Use SCIM filter to search by userName
            params = {
                "filter": f'userName eq "{username}"'
            }
            response = self._make_identity_request("GET", "Users", params=params)
            
            if response.status_code == 200:
                search_results = response.json()
                resources = search_results.get('Resources', [])
                
                if len(resources) == 0:
                    return None  # Return None instead of raising exception
                elif len(resources) == 1:
                    return IdentityUser.from_identity_response(resources[0])
                else:
                    # Multiple results - return the first one
                    logger.warning(f"Multiple users found for username {username}, returning first result")
                    return IdentityUser.from_identity_response(resources[0])
            else:
                error_msg = f"Failed to search for user {username}: HTTP {response.status_code}"
                if response.text:
                    error_msg += f" - {response.text}"
                raise ConcurProfileError(error_msg)
                
        except ConcurProfileError:
            raise
        except Exception as e:
            raise ConcurProfileError(f"Error finding user by username {username}: {str(e)}")
    
    def create_user_identity(self, user: IdentityUser) -> IdentityUser:
        """
        Create a new user identity
        
        Args:
            user: IdentityUser object containing the user data to create
            
        Returns:
            IdentityUser object containing the created user information
            
        Raises:
            ValidationError: If the user data is invalid
            ConcurProfileError: If the request fails
        """
        logger.info(f"Creating user identity: {user.user_name}")
        
        try:
            # Ensure the user has enterprise info with company ID
            if not user.enterprise_info:
                user.enterprise_info = IdentityEnterpriseInfo()
            
            # Ensure company ID is set from SDK configuration if not already provided
            if not user.enterprise_info.company_id and self.company_id:
                user.enterprise_info.company_id = self.company_id
            
            # Validate that we have a company ID
            if not user.enterprise_info.company_id:
                raise ValidationError(
                    "Company ID is required for user creation. "
                    "Set the CONCUR_COMPANY_UUID environment variable or provide company_id parameter."
                )
            
            user_data = user.to_create_dict()
            response = self._make_identity_request("POST", "Users", data=user_data)
            
            if response.status_code == 201:
                created_user_data = response.json()
                return IdentityUser.from_identity_response(created_user_data)
            else:
                error_msg = f"Failed to create user {user.user_name}: HTTP {response.status_code}"
                if response.text:
                    error_msg += f" - {response.text}"
                raise ConcurProfileError(error_msg)
                
        except Exception as e:
            raise ConcurProfileError(f"Error creating user {user.user_name}: {str(e)}")
    
    # ========================================
    # Travel Profile v2 API Methods
    # ========================================
    
    def get_current_user_travel_profile(self) -> TravelProfile:
        """
        Get the travel profile of the currently authenticated user
        
        Returns:
            TravelProfile object containing travel profile information
            
        Raises:
            ConcurProfileError: If the request fails
            AuthenticationError: If not authenticated or no user context
        """
        logger.info("Getting current user's travel profile")
        
        # For client credentials flow, we can't get "current user" travel profile
        # because there's no user context. This will need a specific user login ID.
        raise AuthenticationError(
            "Cannot get current user travel profile with client credentials authentication. "
            "Client credentials provides company-level access without user context. "
            "Use get_travel_profile(login_id) instead with a specific user login ID."
        )
    
    def get_travel_profile(self, login_id: str) -> TravelProfile:
        """
        Get travel profile for a specific user by login ID
        
        Args:
            login_id: The login ID of the user
             
        Returns:
            TravelProfile object containing travel profile information
            
        Raises:
            ProfileNotFoundError: If the travel profile is not found
            ConcurProfileError: If the request fails
        """
        logger.info(f"Getting travel profile for user: {login_id}")
        
        try:
            # URL encode the login ID for the API request
            encoded_login_id = urllib.parse.quote(login_id, safe='')
            
            # Make the API request
            url = f"{self.travel_profile_url}?userid={encoded_login_id}"
            response = self._make_travel_profile_request("GET", url)
            
            if response.status_code == 200:
                xml_content = response.text
                logger.debug(f"Travel profile XML response: {xml_content[:500]}...")
                
                # Parse the XML response into a TravelProfile object
                return self._parse_travel_profile_xml(xml_content, login_id)
                
            elif response.status_code == 404:
                raise ProfileNotFoundError(f"Travel profile not found for user: {login_id}")
            else:
                error_msg = f"Failed to get travel profile for {login_id}: HTTP {response.status_code}"
                if response.text:
                    error_msg += f" - {response.text}"
                raise ConcurProfileError(error_msg)
                
        except ProfileNotFoundError:
            raise
        except Exception as e:
            raise ConcurProfileError(f"Error getting travel profile for {login_id}: {str(e)}")
    
    def _parse_travel_profile_xml(self, xml_content: str, login_id: str) -> TravelProfile:
        """Parse travel profile XML response into TravelProfile object"""
        try:
            # Parse the XML
            root = etree.fromstring(xml_content.encode('utf-8'))
            
            # Create the base travel profile object
            profile = TravelProfile(login_id=login_id)
            
            # Parse General section
            general_elem = root.find("General")
            if general_elem is not None:
                profile.rule_class = general_elem.findtext("RuleClass", "")
                profile.travel_config_id = general_elem.findtext("TravelConfigID", "")
            
            # Parse HasNoPassport flag
            has_no_passport = root.findtext("HasNoPassport", "false")
            profile.has_no_passport = has_no_passport.lower() == "true"
            
            # Parse National IDs
            national_ids_elem = root.find("NationalIDs")
            if national_ids_elem is not None:
                for id_elem in national_ids_elem.findall("NationalID"):
                    national_id = NationalID(
                        id_number=id_elem.findtext("NationalIDNumber", ""),
                        country_code=id_elem.findtext("IssuingCountry", "")
                    )
                    profile.national_ids.append(national_id)
            
            # Parse Driver's Licenses
            licenses_elem = root.find("DriversLicenses")
            if licenses_elem is not None:
                for license_elem in licenses_elem.findall("DriversLicense"):
                    license = DriversLicense(
                        license_number=license_elem.findtext("DriversLicenseNumber", ""),
                        country_code=license_elem.findtext("IssuingCountry", ""),
                        state_province=license_elem.findtext("IssuingState", "")
                    )
                    profile.drivers_licenses.append(license)
            
            # Parse Passports
            passports_elem = root.find("Passports")
            if passports_elem is not None:
                for passport_elem in passports_elem.findall("Passport"):
                    issue_date = None
                    expiration_date = None
                    
                    issue_date_str = passport_elem.findtext("PassportDateIssued")
                    if issue_date_str:
                        try:
                            issue_date = datetime.strptime(issue_date_str, "%Y-%m-%d").date()
                        except:
                            pass
                    
                    expiration_date_str = passport_elem.findtext("PassportExpiration")
                    if expiration_date_str:
                        try:
                            expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d").date()
                        except:
                            pass
                    
                    passport = Passport(
                        doc_number=passport_elem.findtext("PassportNumber", ""),
                        nationality=passport_elem.findtext("PassportNationality", ""),
                        issue_country=passport_elem.findtext("PassportCountryIssued", ""),
                        issue_date=issue_date,
                        expiration_date=expiration_date
                    )
                    profile.passports.append(passport)
            
            # Parse Visas
            visas_elem = root.find("Visas")
            if visas_elem is not None:
                for visa_elem in visas_elem.findall("Visa"):
                    visa_date_issued = None
                    visa_expiration = None
                    
                    date_issued_str = visa_elem.findtext("VisaDateIssued")
                    if date_issued_str:
                        try:
                            visa_date_issued = datetime.strptime(date_issued_str, "%Y-%m-%d").date()
                        except:
                            pass
                    
                    expiration_str = visa_elem.findtext("VisaExpiration")
                    if expiration_str:
                        try:
                            visa_expiration = datetime.strptime(expiration_str, "%Y-%m-%d").date()
                        except:
                            pass
                    
                    visa_type_str = visa_elem.findtext("VisaType", "Unknown")
                    try:
                        visa_type = VisaType(visa_type_str)
                    except ValueError:
                        visa_type = VisaType.UNKNOWN
                    
                    visa = Visa(
                        visa_nationality=visa_elem.findtext("VisaNationality", ""),
                        visa_number=visa_elem.findtext("VisaNumber", ""),
                        visa_type=visa_type,
                        visa_country_issued=visa_elem.findtext("VisaCountryIssued", ""),
                        visa_date_issued=visa_date_issued,
                        visa_expiration=visa_expiration
                    )
                    profile.visas.append(visa)
            
            # Parse TSA Info
            tsa_elem = root.find("TSAInfo")
            if tsa_elem is not None:
                dob = None
                dob_str = tsa_elem.findtext("DateOfBirth")
                if dob_str:
                    try:
                        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
                    except:
                        pass
                
                no_middle_name = tsa_elem.findtext("NoMiddleName", "false").lower() == "true"
                
                profile.tsa_info = TSAInfo(
                    known_traveler_number=tsa_elem.findtext("PreCheckNumber", ""),
                    gender=tsa_elem.findtext("Gender", ""),
                    date_of_birth=dob,
                    redress_number=tsa_elem.findtext("RedressNumber", ""),
                    no_middle_name=no_middle_name
                )
            
            # Parse Rate Preferences
            rate_prefs_elem = root.find("RatePreferences")
            if rate_prefs_elem is not None:
                profile.rate_preferences = RatePreference(
                    aaa_rate=rate_prefs_elem.findtext("AAARate", "false").lower() == "true",
                    aarp_rate=rate_prefs_elem.findtext("AARPRate", "false").lower() == "true",
                    govt_rate=rate_prefs_elem.findtext("GovtRate", "false").lower() == "true",
                    military_rate=rate_prefs_elem.findtext("MilitaryRate", "false").lower() == "true"
                )
            
            # Parse Discount Codes
            discount_codes_elem = root.find("DiscountCodes")
            if discount_codes_elem is not None:
                for code_elem in discount_codes_elem.findall("DiscountCode"):
                    vendor = code_elem.get("Vendor", "")
                    code = code_elem.text or ""
                    if vendor and code:
                        profile.discount_codes.append(DiscountCode(vendor=vendor, code=code))
            
            # Parse Air Preferences
            air_elem = root.find("Air")
            if air_elem is not None:
                air_prefs = AirPreferences()
                
                # Parse seat preferences
                seat_elem = air_elem.find("Seat")
                if seat_elem is not None:
                    inter_row = seat_elem.findtext("InterRowPositionCode", "")
                    section = seat_elem.findtext("SectionPositionCode", "")
                    
                    if inter_row:
                        try:
                            air_prefs.seat_preference = SeatPreference(inter_row)
                        except ValueError:
                            pass
                    
                    if section:
                        try:
                            air_prefs.seat_section = SeatSection(section)
                        except ValueError:
                            pass
                
                # Parse meal preference
                meal_code = air_elem.findtext("MealCode", "")
                if meal_code:
                    try:
                        air_prefs.meal_preference = MealType(meal_code)
                    except ValueError:
                        pass
                
                air_prefs.home_airport = air_elem.findtext("HomeAirport", "")
                air_prefs.air_other = air_elem.findtext("AirOther", "")
                
                profile.air_preferences = air_prefs
            
            # Parse Hotel Preferences
            hotel_elem = root.find("Hotel")
            if hotel_elem is not None:
                hotel_prefs = HotelPreferences()
                
                room_type = hotel_elem.findtext("RoomType", "")
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
                hotel_prefs.prefer_room_service = hotel_elem.findtext("PreferRoomService", "false") == "true"
                hotel_prefs.prefer_early_checkin = hotel_elem.findtext("PreferEarlyCheckIn", "false") == "true"
                
                profile.hotel_preferences = hotel_prefs
            
            # Parse Car Preferences
            car_elem = root.find("Car")
            if car_elem is not None:
                car_prefs = CarPreferences()
                
                car_type = car_elem.findtext("CarType", "")
                if car_type:
                    try:
                        car_prefs.car_type = CarType(car_type)
                    except ValueError:
                        pass
                
                transmission = car_elem.findtext("CarTransmission", "")
                if transmission:
                    try:
                        car_prefs.transmission = TransmissionType(transmission)
                    except ValueError:
                        pass
                
                smoking_code = car_elem.findtext("CarSmokingCode", "")
                if smoking_code:
                    try:
                        car_prefs.smoking_preference = SmokingPreference(smoking_code)
                    except ValueError:
                        pass
                
                car_prefs.gps = car_elem.findtext("CarGPS", "false") == "true"
                car_prefs.ski_rack = car_elem.findtext("CarSkiRack", "false") == "true"
                
                profile.car_preferences = car_prefs
            
            # Parse Rail Preferences
            rail_elem = root.find("Rail")
            if rail_elem is not None:
                rail_prefs = RailPreferences(
                    seat=rail_elem.findtext("Seat", ""),
                    coach=rail_elem.findtext("Coach", ""),
                    noise_comfort=rail_elem.findtext("NoiseComfort", ""),
                    bed=rail_elem.findtext("Bed", ""),
                    bed_category=rail_elem.findtext("BedCategory", ""),
                    berth=rail_elem.findtext("Berth", ""),
                    deck=rail_elem.findtext("Deck", ""),
                    space_type=rail_elem.findtext("SpaceType", ""),
                    fare_space_comfort=rail_elem.findtext("FareSpaceComfort", ""),
                    special_meals=rail_elem.findtext("SpecialMeals", ""),
                    contingencies=rail_elem.findtext("Contingencies", "")
                )
                profile.rail_preferences = rail_prefs
            
            # Parse Custom Fields
            custom_fields_elem = root.find("CustomFields")
            if custom_fields_elem is not None:
                for field_elem in custom_fields_elem.findall("CustomField"):
                    field_name = field_elem.get("Name", "")
                    field_value = field_elem.text or ""
                    if field_name:
                        profile.custom_fields.append(CustomField(field_id=field_name, value=field_value))
            
            # Parse Unused Tickets
            unused_tickets_elem = root.find("UnusedTickets")
            if unused_tickets_elem is not None:
                for ticket_elem in unused_tickets_elem.findall("UnusedTicket"):
                    ticket = UnusedTicket(
                        ticket_number=ticket_elem.findtext("TicketNumber", ""),
                        airline_code=ticket_elem.findtext("AirlineCode", ""),
                        amount=ticket_elem.findtext("Amount", ""),
                        currency=ticket_elem.findtext("Currency", "USD")
                    )
                    profile.unused_tickets.append(ticket)
            
            # Parse Southwest Unused Tickets
            sw_unused_tickets_elem = root.find("SouthwestUnusedTickets")
            if sw_unused_tickets_elem is not None:
                for ticket_elem in sw_unused_tickets_elem.findall("UnusedTicket"):
                    ticket = UnusedTicket(
                        ticket_number=ticket_elem.findtext("TicketNumber", ""),
                        airline_code=ticket_elem.findtext("AirlineCode", ""),
                        amount=ticket_elem.findtext("Amount", ""),
                        currency=ticket_elem.findtext("Currency", "USD")
                    )
                    profile.southwest_unused_tickets.append(ticket)
            
            # Parse Advantage Memberships (Loyalty Programs)
            memberships_elem = root.find("AdvantageMemberships")
            if memberships_elem is not None:
                for membership_elem in memberships_elem.findall("Membership"):
                    vendor_code = membership_elem.findtext("VendorCode", "")
                    vendor_type = membership_elem.findtext("VendorType", "")
                    program_number = membership_elem.findtext("ProgramNumber", "")
                    
                    if vendor_code and vendor_type and program_number:
                        # Map vendor type to loyalty program type
                        program_type_map = {
                            "Air": LoyaltyProgramType.AIR,
                            "Hotel": LoyaltyProgramType.HOTEL,
                            "Car": LoyaltyProgramType.CAR,
                            "Rail": LoyaltyProgramType.RAIL
                        }
                        
                        program_type = program_type_map.get(vendor_type, LoyaltyProgramType.AIR)
                        
                        expiration = None
                        exp_date_str = membership_elem.findtext("ExpirationDate")
                        if exp_date_str:
                            try:
                                expiration = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
                            except:
                                pass
                        
                        loyalty_program = LoyaltyProgram(
                            program_type=program_type,
                            vendor_code=vendor_code,
                            account_number=program_number,
                            expiration=expiration
                        )
                        profile.loyalty_programs.append(loyalty_program)
            
            logger.info(f"Successfully parsed travel profile for {login_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to parse travel profile XML: {e}")
            raise ConcurProfileError(f"Failed to parse travel profile XML response: {str(e)}")

    def update_travel_profile(
        self,
        profile: TravelProfile,
        fields_to_update: Optional[List[str]] = None
    ) -> 'ApiResponse':
        """
        Update an existing travel profile with comprehensive data
        
        Args:
            profile: TravelProfile object with login_id and fields to update
            fields_to_update: Optional list of field names to update.
                            If not provided, all non-empty fields will be updated.
                            Valid field names include:
                            - "air_preferences", "hotel_preferences", "car_preferences", "rail_preferences"
                            - "tsa_info", "passports", "visas", "national_ids", "drivers_licenses"
                            - "loyalty_programs", "custom_fields", "emergency_contacts"
            
        Returns:
            ApiResponse with success code
            
        Raises:
            ValidationError: If login_id is missing
            ProfileNotFoundError: If the user is not found
            ConcurProfileError: If the update fails
        """
        if not profile.login_id:
            raise ValidationError("login_id is required for update")
        
        logger.info(f"Updating travel profile for user: {profile.login_id}")
        
        xml_data = profile.to_update_xml(fields_to_update)
        logger.debug(f"Generated update XML:\n{xml_data}")
        
        response = self._make_travel_profile_request("POST", self.travel_profile_url, data=xml_data)
        
        if response.status_code == 404 or "Invalid User" in response.text:
            raise ProfileNotFoundError(f"User not found: {profile.login_id}")
        
        if response.status_code != 200:
            logger.error(f"Update failed. Status: {response.status_code}")
            logger.error(f"Response text: {response.text}")
            try:
                error = ApiError.from_xml(response.text)
                raise ConcurProfileError(f"Failed to update travel profile: {error.message}")
            except:
                raise ConcurProfileError(f"Failed to update travel profile: HTTP {response.status_code}")
        
        return ApiResponse.from_xml(response.text)
