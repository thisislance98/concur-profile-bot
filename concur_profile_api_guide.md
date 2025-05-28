# Concur Profile API Guide

A comprehensive guide to the SAP Concur Travel Profile APIs with working curl examples, corrections to the official documentation, and common pitfalls to avoid.

## Table of Contents
1. [Authentication](#authentication)
2. [Profile v2.0 API](#profile-v20-api)
3. [Error Handling](#error-handling)
4. [Common Pitfalls](#common-pitfalls)
5. [Working Examples](#working-examples)

## Authentication

### OAuth 2.0 Password Grant Flow

**Endpoint:** `POST {base_url}/oauth2/v0/token`

**Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Request Body:**
```
client_id={your_client_id}
client_secret={your_client_secret}
grant_type=password
username={concur_username}
password={concur_password}
```

**Example:**
```bash
curl -X POST https://us.api.concursolutions.com/oauth2/v0/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=26d1290b-c37a-4192-8ef0-0c228642140e" \
  -d "client_secret=b029b1a7-3d99-4fc0-978f-688f985fe125" \
  -d "grant_type=password" \
  -d "username=wsadmin@platformds-connect.com" \
  -d "password=PlatformDS2"
```

**Successful Response:**
```json
{
  "expires_in": 3600,
  "scope": "openid expense.report.read ...",
  "token_type": "Bearer",
  "access_token": "eyJraWQiOiIxNDU1NjE0MDIyIi...",
  "refresh_token": "pdnn8iw3l9m5m5jgn8ekxcgbxfj",
  "refresh_expires_in": 1763496892,
  "geolocation": "https://us2.api.concursolutions.com",
  "id_token": "eyJraWQiOiIxNDU1NjE0MDIyIi..."
}
```

**Store the Token:**
```bash
export ACCESS_TOKEN=$(curl -s -X POST https://us.api.concursolutions.com/oauth2/v0/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=your_client_id" \
  -d "client_secret=your_client_secret" \
  -d "grant_type=password" \
  -d "username=your_username" \
  -d "password=your_password" | jq -r '.access_token')
```

## Profile v2.0 API

### Base Information
- **Base URL:** `https://us.api.concursolutions.com` (for US instance)
- **Endpoint:** `/api/travelprofile/v2.0/profile`
- **Content-Type:** `application/xml` (for POST requests)
- **Accept:** `application/xml`
- **Authorization:** `Bearer {access_token}`

### Get Current User Profile

```bash
curl -X GET "https://us.api.concursolutions.com/api/travelprofile/v2.0/profile" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Accept: application/xml"
```

### Get Specific User Profile by Login ID

```bash
curl -X GET "https://us.api.concursolutions.com/api/travelprofile/v2.0/profile?userid_type=login&userid_value=user@example.com" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Accept: application/xml"
```

### Create New User

**Minimum Required Fields:**
- `FirstName`
- `LastName`
- `TravelConfigID`
- `LoginId` (in the root element attribute)
- `RuleClass` (optional, uses default if not provided)
- `Password` (optional, random strong password assigned if not provided)

```bash
curl -X POST "https://us.api.concursolutions.com/api/travelprofile/v2.0/profile" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0" encoding="utf-8"?>
<ProfileResponse xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Action="Create" LoginId="newuser@example.com">
  <General>
    <FirstName>John</FirstName>
    <LastName>Doe</LastName>
    <RuleClass>Default Travel Class</RuleClass>
    <TravelConfigID>250027436</TravelConfigID>
  </General>
  <Password>SecurePassword123!</Password>
</ProfileResponse>'
```

**Successful Response:**
```xml
<TravelProfileResponseMessage>
  <Code>S001</Code>
  <Message>Success, no errors or warnings reported</Message>
  <UUID>94374f9b-3b54-424a-bf3a-28c9ffceab04</UUID>
</TravelProfileResponseMessage>
```

### Update Existing User

```bash
curl -X POST "https://us.api.concursolutions.com/api/travelprofile/v2.0/profile" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0" encoding="utf-8"?>
<ProfileResponse xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Action="Update" LoginId="user@example.com">
  <General>
    <FirstName>UpdatedFirstName</FirstName>
  </General>
</ProfileResponse>'
```

## Profile Response Structure

A successful profile retrieval returns XML with the following main sections:

```xml
<ProfileResponse Status="Active" LoginId="user@example.com">
  <General>
    <FirstName>John</FirstName>
    <LastName>Doe</LastName>
    <MiddleName>M</MiddleName>
    <JobTitle>Software Engineer</JobTitle>
    <CompanyEmployeeID>12345</CompanyEmployeeID>
    <PreferredLanguage>en</PreferredLanguage>
    <CountryCode>US</CountryCode>
    <CompanyName>Company Name</CompanyName>
    <RuleClass>Default Travel Class</RuleClass>
    <TravelConfigID>250027436</TravelConfigID>
    <UUID>uuid-here</UUID>
  </General>
  
  <Addresses>
    <Address Type="Home">
      <Street>123 Main St</Street>
      <City>City</City>
      <StateProvince>ST</StateProvince>
      <PostalCode>12345</PostalCode>
      <CountryCode>US</CountryCode>
    </Address>
  </Addresses>
  
  <Telephones>
    <Telephone Type="Home">
      <CountryCode>1</CountryCode>
      <PhoneNumber>555-123-4567</PhoneNumber>
      <Extension />
    </Telephone>
  </Telephones>
  
  <Visas>
    <Visa>
      <VisaNationality>US</VisaNationality>
      <VisaNumber>VISA123</VisaNumber>
      <VisaType>Unknown</VisaType>
    </Visa>
  </Visas>
  
  <EmailAddresses>
    <EmailAddress Type="Business">user@company.com</EmailAddress>
  </EmailAddresses>
  
  <RatePreferences>
    <AAARate>false</AAARate>
    <AARPRate>false</AARPRate>
    <GovtRate>false</GovtRate>
    <MilitaryRate>false</MilitaryRate>
  </RatePreferences>
  
  <Air>
    <AirMemberships />
    <Seat>
      <InterRowPositionCode>Aisle</InterRowPositionCode>
      <SectionPositionCode>DontCare</SectionPositionCode>
    </Seat>
  </Air>
  
  <Rail>
    <Seat>DontCare</Seat>
    <RailMemberships />
  </Rail>
  
  <Car>
    <CarType>DontCare</CarType>
    <CarMemberships />
  </Car>
  
  <Hotel>
    <HotelSmokingCode>NonSmoking</HotelSmokingCode>
    <RoomType>King</RoomType>
    <HotelMemberships />
  </Hotel>
  
  <TSAInfo>
    <NoMiddleName>false</NoMiddleName>
  </TSAInfo>
</ProfileResponse>
```

## Error Handling

### Authentication Errors

**Invalid Token:**
```xml
<Error>
  <Message>IDX10708: 'System.IdentityModel.Tokens.JwtSecurityTokenHandler' cannot read this string: 'invalid_token'...</Message>
  <Server-Time>2025-05-22T16:17:57</Server-Time>
  <Id>1B172328-3574-4E2C-912F-3243AD82DF3F</Id>
</Error>
```

### User Not Found Error

```xml
<Error>
  <Message>Invalid User (EC1): nonexistent@example.com</Message>
  <Server-Time>2025-05-22T16:16:41</Server-Time>
  <Id>52836E02-AC0C-42C4-8100-5B4279C10070</Id>
</Error>
```

### XML Format Error

```xml
<Error>
  <Message>There is an error in XML document (1, 489).</Message>
  <Server-Time>2025-05-22T16:17:35</Server-Time>
  <Id>1D7F5915-8ADF-4B81-B970-C3EAC219F90F</Id>
</Error>
```

## Loyalty Program API

⚠️ **Important Note:** The separate Loyalty Program v1.0 endpoint (`/api/travelprofile/v1.0/loyalty`) returns "Not Found" in current testing. Loyalty program information appears to be integrated into the main Profile v2.0 API response under sections like:
- `<Air><AirMemberships />`
- `<Hotel><HotelMemberships />`
- `<Car><CarMemberships />`
- `<Rail><RailMemberships />`

## Common Pitfalls

### 1. Base URL Issues
- **Documentation shows:** `{InstanceURI}/api/travelprofile/v2.0/profile`
- **Actual working URL:** `https://us.api.concursolutions.com/api/travelprofile/v2.0/profile`
- The geolocation URL from the auth response can be different from the base URL used for auth

### 2. XML Formatting
- Use proper XML declaration: `<?xml version="1.0" encoding="utf-8"?>`
- Include required namespace: `xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"`
- Ensure proper Action attribute: `Action="Create"` or `Action="Update"`

### 3. Required Fields for User Creation
- `TravelConfigID` is mandatory and must be valid for your organization
- `LoginId` must be unique across the system
- Complex updates with multiple sections may fail - start with simple field updates

### 4. Authentication
- Tokens expire after 3600 seconds (1 hour)
- Always check token expiration before making requests
- Store and reuse tokens rather than authenticating for each request

## Working Examples

### Complete User Creation and Update Flow

```bash
# 1. Authenticate and store token
export ACCESS_TOKEN=$(curl -s -X POST https://us.api.concursolutions.com/oauth2/v0/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=your_client_id" \
  -d "client_secret=your_client_secret" \
  -d "grant_type=password" \
  -d "username=your_username" \
  -d "password=your_password" | jq -r '.access_token')

# 2. Create a new user
UNIQUE_ID=$(date +%s)
curl -X POST "https://us.api.concursolutions.com/api/travelprofile/v2.0/profile" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"utf-8\"?><ProfileResponse xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" Action=\"Create\" LoginId=\"testuser_${UNIQUE_ID}@example.com\"><General><FirstName>John</FirstName><LastName>TestUser</LastName><RuleClass>Default Travel Class</RuleClass><TravelConfigID>250027436</TravelConfigID></General><Password>TestPassword123!</Password></ProfileResponse>"

# 3. Verify user creation
curl -X GET "https://us.api.concursolutions.com/api/travelprofile/v2.0/profile?userid_type=login&userid_value=testuser_${UNIQUE_ID}@example.com" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Accept: application/xml"

# 4. Update the user
curl -X POST "https://us.api.concursolutions.com/api/travelprofile/v2.0/profile" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"utf-8\"?><ProfileResponse xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" Action=\"Update\" LoginId=\"testuser_${UNIQUE_ID}@example.com\"><General><FirstName>Johnny</FirstName></General></ProfileResponse>"

# 5. Verify the update
curl -X GET "https://us.api.concursolutions.com/api/travelprofile/v2.0/profile?userid_type=login&userid_value=testuser_${UNIQUE_ID}@example.com" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Accept: application/xml"
```

## Corrections to Official Documentation

1. **Base URL:** The documentation uses `{InstanceURI}` which is unclear. Use `https://us.api.concursolutions.com` for US instances.

2. **Loyalty Program API:** The `/api/travelprofile/v1.0/loyalty` endpoint appears to be unavailable or deprecated. Loyalty data is included in the main profile response.

3. **Required Fields:** The documentation doesn't clearly specify that `TravelConfigID` is mandatory for user creation.

4. **Error Format:** All errors return XML format even when requesting JSON, not just "standard error codes" as mentioned.

5. **Update Complexity:** Complex multi-section updates may fail with XML format errors. Start with simple single-field updates.

This guide provides working, tested examples that can be used immediately for integrating with the Concur Profile APIs. 