Concur Docs

SAP Concur Identity APIs and Authentication Guide
Overview
SAP Concur provides a comprehensive OAuth2 authentication framework and Identity APIs for managing user profiles and authentication. This guide covers everything you need to know about authenticating with SAP Concur services and using the Identity v4 and v4.1 APIs.
Table of Contents

Authentication Overview
Getting Started with OAuth2
Grant Types and Flows
Token Management
Identity v4 API
Identity v4.1 API
Schemas and Data Structures
Best Practices
Error Handling
Examples and Code Samples


Authentication Overview
SAP Concur uses OAuth2 for authentication and authorization. The system supports multiple grant types for different use cases:

Authorization Grant: 3-legged OAuth2 for user consent
Password Grant: For trusted applications with user credentials
Client Credentials Grant: For application-level access
One-Time Password Grant: Email/SMS-based authentication
Refresh Grant: For token renewal

Key Components

Client ID: UUID4 identifier for your application
Client Secret: Application password
Geolocation: Base URI for API calls
Access Token: Short-lived token for API calls (1 hour)
Refresh Token: Long-lived token for obtaining new access tokens (6 months)


Getting Started with OAuth2
Step 1: Register Your Application
Before using the APIs, you must register your application with SAP Concur:

Contact your Partner Enablement Manager or Partner Account Manager
Receive your clientId, clientSecret, and geolocation
The geolocation serves as your default base URI

Step 2: Choose Your Grant Type
Select the appropriate grant type based on your application's needs:

Authorization Grant: For third-party applications requiring user consent
Password Grant: For partner applications with stored user credentials
Client Credentials: For application-level operations
One-Time Password: For passwordless authentication

Step 3: Base URIs and Geolocations
SAP Concur operates in multiple data centers. Common base URIs include:

US: https://us.api.concursolutions.com
EMEA: https://emea.api.concursolutions.com
Client-side calls use www- prefix: https://www-us.api.concursolutions.com


Grant Types and Flows
Authorization Grant (3-Legged OAuth2)
When to use: Third-party applications requiring explicit user authorization
Flow:

Redirect user to authorization endpoint
User authenticates and grants permission
Receive authorization code
Exchange code for access token

Authorization Request:
GET /oauth2/v0/authorize?
    client_id={clientId}&
    redirect_uri={redirectUri}&
    scope={scopes}&
    response_type=code&
    state={state}
Token Exchange:
POST /oauth2/v0/token
Content-Type: application/x-www-form-urlencoded

client_id={clientId}&
client_secret={clientSecret}&
redirect_uri={redirectUri}&
code={authorizationCode}&
grant_type=authorization_code
Password Grant
When to use: Trusted applications with user credentials or App Center integrations
Two credential types:

password: Direct username/password
authtoken: For App Center connections (24-hour temporary tokens)

Request:
POST /oauth2/v0/token
Content-Type: application/x-www-form-urlencoded

client_id={clientId}&
client_secret={clientSecret}&
grant_type=password&
username={username}&
password={password}&
credtype={password|authtoken}
Client Credentials Grant
When to use: Application-level authentication without user context
Request:
POST /oauth2/v0/token
Content-Type: application/x-www-form-urlencoded

client_id={clientId}&
client_secret={clientSecret}&
grant_type=client_credentials
One-Time Password Grant
When to use: Passwordless authentication via email/SMS
Step 1 - Request OTP:
POST /oauth2/v0/otp
Content-Type: application/x-www-form-urlencoded

client_id={clientId}&
client_secret={clientSecret}&
channel_handle={email}&
channel_type=email&
name={userName}&
company={companyName}&
link={callbackUrl}
Step 2 - Exchange OTP for Token:
POST /oauth2/v0/token
Content-Type: application/x-www-form-urlencoded

client_id={clientId}&
client_secret={clientSecret}&
channel_handle={email}&
channel_type=email&
scope={scopes}&
grant_type=otp&
otp={otpToken}

Token Management
Access Tokens

Lifetime: 1 hour
Usage: Include in Authorization header as Bearer {token}
Format: JWT (JSON Web Token)

Refresh Tokens

Lifetime: 6 months
Purpose: Obtain new access tokens
Storage: Store securely with user metadata

Token Refresh
POST /oauth2/v0/token
Content-Type: application/x-www-form-urlencoded

client_id={clientId}&
client_secret={clientSecret}&
grant_type=refresh_token&
refresh_token={refreshToken}
Important: Always use the geolocation from the token response for subsequent API calls.
Token Response Format
json{
  "expires_in": "3600",
  "scope": "app-scopes",
  "token_type": "Bearer",
  "access_token": "eyJ0eXAiOiJKV1Q...",
  "refresh_token": "e013335d-b4ce-4c43...",
  "id_token": "eyJhbGciOiJSUzI1NiI...",
  "geolocation": "https://us.api.concursolutions.com"
}
Token Revocation
To revoke all refresh tokens for a user:
DELETE /app-mgmt/v0/connections
Authorization: Bearer {accessToken}

Identity v4 API
The Identity v4 API provides core user identity management capabilities.
Base URL
https://{datacenterURI}/profile/identity/v4/
Required Scopes

identity.user.ids.read: Read user ID data
identity.user.core.read: Read user core data
identity.user.coresensitive.read: Read core sensitive data
identity.user.enterprise.read: Read enterprise data
identity.user.coreenterprise.writeonly: Write core/enterprise data
identity.user.externalID.writeonly: Write external ID
identity.user.emails.verified.writeonly: Write verified email status
identity.user.sap.read: Read SAP Global ID
identity.user.sap.writeonly: Write SAP Global ID
identity.user.delete: Delete users (not recommended)

Core Operations
Retrieve Users
Get all users:
GET /profile/identity/v4/Users
Authorization: Bearer {token}
Filter users:
GET /profile/identity/v4/Users?filter=employeeNumber eq "123456789"
GET /profile/identity/v4/Users?filter=userName eq "user@domain.com"
Pagination:
GET /profile/identity/v4/Users?startIndex=1&count=50
Retrieve Single User
GET /profile/identity/v4/Users/{userId}
Authorization: Bearer {token}
Create User
POST /profile/identity/v4/Users
Authorization: Bearer {token}
Content-Type: application/json

{
  "schemas": [
    "urn:ietf:params:scim:schemas:core:2.0:User"
  ],
  "userName": "john.doe@company.com",
  "active": true,
  "name": {
    "familyName": "Doe",
    "givenName": "John"
  },
  "emails": [
    {
      "value": "john.doe@company.com",
      "type": "work",
      "verified": true
    }
  ],
  "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User": {
    "employeeNumber": "12345",
    "companyId": "aa076ada-80a9-4f57-8e98-9300b1c3171d"
  }
}
Update User (PATCH)
PATCH /profile/identity/v4/Users/{userId}
Authorization: Bearer {token}
Content-Type: application/json

{
  "schemas": [
    "urn:ietf:params:scim:api:messages:2.0:PatchOp"
  ],
  "Operations": [
    {
      "op": "replace",
      "path": "name.givenName",
      "value": "Jane"
    }
  ]
}
Replace User (PUT)
PUT /profile/identity/v4/Users/{userId}
Authorization: Bearer {token}
Content-Type: application/json

{
  "schemas": [
    "urn:ietf:params:scim:schemas:core:2.0:User"
  ],
  "userName": "jane.doe@company.com",
  "active": true,
  "name": {
    "familyName": "Doe",
    "givenName": "Jane"
  },
  "emails": [
    {
      "value": "jane.doe@company.com",
      "type": "work"
    }
  ]
}

Identity v4.1 API
The Identity v4.1 API includes enhanced search capabilities and improved performance.
Base URL
https://{datacenterURI}/profile/identity/v4.1/
New Features

Advanced search functionality
Cursor-based pagination
Enhanced filtering capabilities
Improved performance

Enhanced Search
The v4.1 API introduces a dedicated search endpoint with powerful filtering:
POST /profile/identity/v4.1/Users/.search
Authorization: Bearer {token}
Content-Type: application/json

{
  "schemas": [
    "urn:ietf:params:scim:api:messages:concur:2.0:SearchRequest"
  ],
  "filter": "active eq true and emails.type eq \"work\"",
  "attributes": ["id", "userName", "active", "emails"],
  "count": 100
}
Supported Filter Operations

eq (equals)
ne (not equals)
gt (greater than)
ge (greater than or equal)
lt (less than)
le (less than or equal)
co (contains)
sw (starts with)
ew (ends with)
pr (present)

Complex Filter Examples
# Multiple conditions
filter: active eq true and name.familyName co "Smith"

# Date comparisons
filter: urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:startDate gt "2023-01-01"

# Array operations
filter: emails[type eq "work"].value co "@company.com"

Schemas and Data Structures
Core User Schema
The User schema contains core identity attributes:
Required Fields:

userName: Unique login identifier
active: Boolean status
name.familyName: Last name
name.givenName: First name
emails: Array of email objects

Optional Fields:

displayName: Display name
nickName: Preferred name
title: Job title
phoneNumbers: Array of phone objects
addresses: Array of address objects
dateOfBirth: Date of birth
timezone: User timezone
preferredLanguage: Language preference

Enterprise Extension
Enterprise-specific attributes:

companyId: SAP Concur company ID (required, immutable)
employeeNumber: Employee number (unique within company)
manager: Manager information
department: Department name
division: Division name
costCenter: Cost center code
startDate: Employment start date
terminationDate: Employment end date
leavesOfAbsence: Leave information

SAP Extension
SAP-specific attributes:

userUuid: SAP Global ID for cross-SAP integration

Email Object Structure
json{
  "value": "user@company.com",
  "type": "work|home|work2|other|other2",
  "notifications": true,
  "verified": false
}
Phone Number Object Structure
json{
  "value": "+1-425-123-4567",
  "type": "work|home|mobile|fax|pager|other",
  "display": "425-123-4567",
  "primary": true,
  "notifications": true
}
Address Object Structure
json{
  "type": "work|home|other|billing|bank|shipping",
  "streetAddress": "123 Main St",
  "locality": "Seattle",
  "region": "WA",
  "postalCode": "98101",
  "country": "US"
}

Best Practices
Security

Store credentials securely: Never expose client secrets in client-side code
Use HTTPS: Always use encrypted connections
Token storage: Store refresh tokens securely with user data
Geolocation: Always use the geolocation from token responses
Token refresh: Implement automatic token refresh logic

Performance

Pagination: Use appropriate page sizes (max 1000 for v4.1, 100 default)
Filtering: Use filters to reduce response sizes
Attribute selection: Request only needed attributes
Caching: Cache user data appropriately with proper invalidation

API Usage

Correlation IDs: Include correlation IDs for troubleshooting
Rate limiting: Implement appropriate rate limiting
Error handling: Handle all HTTP status codes properly
Retry logic: Implement exponential backoff for retries

Data Management

Username uniqueness: Ensure usernames are unique across all SAP Concur products
Employee number uniqueness: Ensure employee numbers are unique within companies
Data validation: Validate all user data before submission
Locale support: Handle localization properly


Error Handling
HTTP Status Codes

200 OK: Successful request
400 Bad Request: Invalid request syntax or parameters
401 Unauthorized: Invalid or missing authentication
403 Forbidden: Insufficient permissions
404 Not Found: Resource not found
500 Internal Server Error: Server error
503 Service Unavailable: Service temporarily unavailable

Common Error Codes
Authentication Errors:

Code 5: invalid_grant - Incorrect credentials
Code 10-14: Account disabled/locked
Code 16: invalid_request - User lives elsewhere
Code 61: invalid_client - Client not found
Code 64: invalid_client - Incorrect credentials

Request Errors:

Code 51-52: Missing username/password
Code 53: invalid_client - Company not enabled
Code 54: invalid_scope - Requested scope exceeds granted
Code 55: invalid_request - Email not found
Code 108: invalid_grant - Bad or expired refresh token

Error Response Format
json{
  "error": "invalid_grant",
  "error_description": "Incorrect Credentials. Please Retry",
  "code": 5
}
SCIM Error Format
json{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
  "scimType": "invalidValue",
  "detail": "The specified filter syntax is invalid",
  "status": "400"
}

Examples and Code Samples
Complete Authentication Flow (Node.js)
javascriptconst axios = require('axios');

class ConcurAuth {
  constructor(clientId, clientSecret, geolocation) {
    this.clientId = clientId;
    this.clientSecret = clientSecret;
    this.geolocation = geolocation;
    this.accessToken = null;
    this.refreshToken = null;
  }

  async authenticatePassword(username, password) {
    try {
      const response = await axios.post(
        `${this.geolocation}/oauth2/v0/token`,
        new URLSearchParams({
          client_id: this.clientId,
          client_secret: this.clientSecret,
          grant_type: 'password',
          username: username,
          password: password
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'concur-correlationid': 'my-app-correlation-id'
          }
        }
      );

      this.accessToken = response.data.access_token;
      this.refreshToken = response.data.refresh_token;
      this.geolocation = response.data.geolocation;

      return response.data;
    } catch (error) {
      console.error('Authentication failed:', error.response?.data);
      throw error;
    }
  }

  async refreshAccessToken() {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await axios.post(
        `${this.geolocation}/oauth2/v0/token`,
        new URLSearchParams({
          client_id: this.clientId,
          client_secret: this.clientSecret,
          grant_type: 'refresh_token',
          refresh_token: this.refreshToken
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );

      this.accessToken = response.data.access_token;
      this.refreshToken = response.data.refresh_token;
      this.geolocation = response.data.geolocation;

      return response.data;
    } catch (error) {
      console.error('Token refresh failed:', error.response?.data);
      throw error;
    }
  }

  getAuthHeaders() {
    return {
      Authorization: `Bearer ${this.accessToken}`,
      'Content-Type': 'application/json'
    };
  }
}
Identity API Usage
javascriptclass ConcurIdentity {
  constructor(authClient) {
    this.auth = authClient;
  }

  async getUsers(filter = null, count = 100) {
    const params = new URLSearchParams();
    if (filter) params.append('filter', filter);
    params.append('count', count.toString());

    const response = await axios.get(
      `${this.auth.geolocation}/profile/identity/v4/Users?${params}`,
      { headers: this.auth.getAuthHeaders() }
    );

    return response.data;
  }

  async getUser(userId) {
    const response = await axios.get(
      `${this.auth.geolocation}/profile/identity/v4/Users/${userId}`,
      { headers: this.auth.getAuthHeaders() }
    );

    return response.data;
  }

  async createUser(userData) {
    const response = await axios.post(
      `${this.auth.geolocation}/profile/identity/v4/Users`,
      userData,
      { headers: this.auth.getAuthHeaders() }
    );

    return response.data;
  }

  async updateUser(userId, updates) {
    const patchData = {
      schemas: ['urn:ietf:params:scim:api:messages:2.0:PatchOp'],
      Operations: updates
    };

    const response = await axios.patch(
      `${this.auth.geolocation}/profile/identity/v4/Users/${userId}`,
      patchData,
      { headers: this.auth.getAuthHeaders() }
    );

    return response.data;
  }

  async searchUsers(filter, attributes = null, count = 100) {
    const searchData = {
      schemas: ['urn:ietf:params:scim:api:messages:concur:2.0:SearchRequest'],
      filter: filter,
      count: count
    };

    if (attributes) {
      searchData.attributes = attributes;
    }

    const response = await axios.post(
      `${this.auth.geolocation}/profile/identity/v4.1/Users/.search`,
      searchData,
      { headers: this.auth.getAuthHeaders() }
    );

    return response.data;
  }
}
Usage Example
javascriptasync function main() {
  // Initialize authentication
  const auth = new ConcurAuth(
    'your-client-id',
    'your-client-secret',
    'https://us.api.concursolutions.com'
  );

  // Authenticate
  await auth.authenticatePassword('username', 'password');

  // Initialize Identity API
  const identity = new ConcurIdentity(auth);

  // Get all active users
  const users = await identity.getUsers('active eq true');
  console.log(`Found ${users.totalResults} active users`);

  // Search for specific users
  const searchResults = await identity.searchUsers(
    'emails[type eq "work"].value co "@company.com"',
    ['id', 'userName', 'emails']
  );
  console.log('Company users:', searchResults.Resources);

  // Create a new user
  const newUser = {
    schemas: ['urn:ietf:params:scim:schemas:core:2.0:User'],
    userName: 'new.user@company.com',
    active: true,
    name: {
      familyName: 'User',
      givenName: 'New'
    },
    emails: [{
      value: 'new.user@company.com',
      type: 'work'
    }],
    'urn:ietf:params:scim:schemas:extension:enterprise:2.0:User': {
      employeeNumber: '54321',
      companyId: 'your-company-id'
    }
  };

  const createdUser = await identity.createUser(newUser);
  console.log('Created user:', createdUser.id);

  // Update user
  const updates = [{
    op: 'replace',
    path: 'title',
    value: 'Senior Developer'
  }];

  await identity.updateUser(createdUser.id, updates);
  console.log('User updated successfully');
}

main().catch(console.error);
Company-Level Authentication
javascriptasync function authenticateAsCompany(auth, requestToken, companyId) {
  const response = await axios.post(
    `${auth.geolocation}/oauth2/v0/token`,
    new URLSearchParams({
      client_id: auth.clientId,
      client_secret: auth.clientSecret,
      grant_type: 'password',
      username: companyId,
      password: requestToken,
      credtype: 'authtoken'
    }),
    {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    }
  );

  return response.data;
}
cURL Examples
Get Access Token:
bashcurl -X POST 'https://us.api.concursolutions.com/oauth2/v0/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'concur-correlationid: my-app' \
  --data-urlencode 'client_id=your-client-id' \
  --data-urlencode 'client_secret=your-client-secret' \
  --data-urlencode 'grant_type=password' \
  --data-urlencode 'username=user@domain.com' \
  --data-urlencode 'password=password123'
Get User Profile:
bashcurl -X GET 'https://us.api.concursolutions.com/profile/identity/v4/Users/user-id' \
  -H 'Authorization: Bearer your-access-token' \
  -H 'Accept: application/json'
Search Users:
bashcurl -X POST 'https://us.api.concursolutions.com/profile/identity/v4.1/Users/.search' \
  -H 'Authorization: Bearer your-access-token' \
  -H 'Content-Type: application/json' \
  -d '{
    "schemas": ["urn:ietf:params:scim:api:messages:concur:2.0:SearchRequest"],
    "filter": "active eq true",
    "attributes": ["id", "userName", "active"]
  }'

This comprehensive guide covers all aspects of SAP Concur authentication and Identity API usage. For additional support, always include correlation IDs in your requests and consult the official SAP Concur documentation for the latest updates and changes.RetryLthe examples should be in curl and pythonEditPlotted curl and Python API authentication examples.1sThe user wants me to replace the Node.js examples with curl and Python examples. I should provide practical, working examples for both curl commands and Python code that demonstrate how to authenticate and use the Concur Identity APIs.SAP Concur Identity APIs and Authentication Guide
Overview
SAP Concur provides a comprehensive OAuth2 authentication framework and Identity APIs for managing user profiles and authentication. This guide covers everything you need to know about authenticating with SAP Concur services and using the Identity v4 and v4.1 APIs.
Table of Contents

Authentication Overview
Getting Started with OAuth2
Grant Types and Flows
Token Management
Identity v4 API
Identity v4.1 API
Schemas and Data Structures
Best Practices
Error Handling
Examples and Code Samples


Authentication Overview
SAP Concur uses OAuth2 for authentication and authorization. The system supports multiple grant types for different use cases:

Authorization Grant: 3-legged OAuth2 for user consent
Password Grant: For trusted applications with user credentials
Client Credentials Grant: For application-level access
One-Time Password Grant: Email/SMS-based authentication
Refresh Grant: For token renewal

Key Components

Client ID: UUID4 identifier for your application
Client Secret: Application password
Geolocation: Base URI for API calls
Access Token: Short-lived token for API calls (1 hour)
Refresh Token: Long-lived token for obtaining new access tokens (6 months)


Getting Started with OAuth2
Step 1: Register Your Application
Before using the APIs, you must register your application with SAP Concur:

Contact your Partner Enablement Manager or Partner Account Manager
Receive your clientId, clientSecret, and geolocation
The geolocation serves as your default base URI

Step 2: Choose Your Grant Type
Select the appropriate grant type based on your application's needs:

Authorization Grant: For third-party applications requiring user consent
Password Grant: For partner applications with stored user credentials
Client Credentials: For application-level operations
One-Time Password: For passwordless authentication

Step 3: Base URIs and Geolocations
SAP Concur operates in multiple data centers. Common base URIs include:

US: https://us.api.concursolutions.com
EMEA: https://emea.api.concursolutions.com
Client-side calls use www- prefix: https://www-us.api.concursolutions.com


Grant Types and Flows
Authorization Grant (3-Legged OAuth2)
When to use: Third-party applications requiring explicit user authorization
Flow:

Redirect user to authorization endpoint
User authenticates and grants permission
Receive authorization code
Exchange code for access token

Authorization Request:
GET /oauth2/v0/authorize?
    client_id={clientId}&
    redirect_uri={redirectUri}&
    scope={scopes}&
    response_type=code&
    state={state}
Token Exchange:
POST /oauth2/v0/token
Content-Type: application/x-www-form-urlencoded

client_id={clientId}&
client_secret={clientSecret}&
redirect_uri={redirectUri}&
code={authorizationCode}&
grant_type=authorization_code
Password Grant
When to use: Trusted applications with user credentials or App Center integrations
Two credential types:

password: Direct username/password
authtoken: For App Center connections (24-hour temporary tokens)

Request:
POST /oauth2/v0/token
Content-Type: application/x-www-form-urlencoded

client_id={clientId}&
client_secret={clientSecret}&
grant_type=password&
username={username}&
password={password}&
credtype={password|authtoken}
Client Credentials Grant
When to use: Application-level authentication without user context
Request:
POST /oauth2/v0/token
Content-Type: application/x-www-form-urlencoded

client_id={clientId}&
client_secret={clientSecret}&
grant_type=client_credentials
One-Time Password Grant
When to use: Passwordless authentication via email/SMS
Step 1 - Request OTP:
POST /oauth2/v0/otp
Content-Type: application/x-www-form-urlencoded

client_id={clientId}&
client_secret={clientSecret}&
channel_handle={email}&
channel_type=email&
name={userName}&
company={companyName}&
link={callbackUrl}
Step 2 - Exchange OTP for Token:
POST /oauth2/v0/token
Content-Type: application/x-www-form-urlencoded

client_id={clientId}&
client_secret={clientSecret}&
channel_handle={email}&
channel_type=email&
scope={scopes}&
grant_type=otp&
otp={otpToken}

Token Management
Access Tokens

Lifetime: 1 hour
Usage: Include in Authorization header as Bearer {token}
Format: JWT (JSON Web Token)

Refresh Tokens

Lifetime: 6 months
Purpose: Obtain new access tokens
Storage: Store securely with user metadata

Token Refresh
POST /oauth2/v0/token
Content-Type: application/x-www-form-urlencoded

client_id={clientId}&
client_secret={clientSecret}&
grant_type=refresh_token&
refresh_token={refreshToken}
Important: Always use the geolocation from the token response for subsequent API calls.
Token Response Format
json{
  "expires_in": "3600",
  "scope": "app-scopes",
  "token_type": "Bearer",
  "access_token": "eyJ0eXAiOiJKV1Q...",
  "refresh_token": "e013335d-b4ce-4c43...",
  "id_token": "eyJhbGciOiJSUzI1NiI...",
  "geolocation": "https://us.api.concursolutions.com"
}
Token Revocation
To revoke all refresh tokens for a user:
DELETE /app-mgmt/v0/connections
Authorization: Bearer {accessToken}

Identity v4 API
The Identity v4 API provides core user identity management capabilities.
Base URL
https://{datacenterURI}/profile/identity/v4/
Required Scopes

identity.user.ids.read: Read user ID data
identity.user.core.read: Read user core data
identity.user.coresensitive.read: Read core sensitive data
identity.user.enterprise.read: Read enterprise data
identity.user.coreenterprise.writeonly: Write core/enterprise data
identity.user.externalID.writeonly: Write external ID
identity.user.emails.verified.writeonly: Write verified email status
identity.user.sap.read: Read SAP Global ID
identity.user.sap.writeonly: Write SAP Global ID
identity.user.delete: Delete users (not recommended)

Core Operations
Retrieve Users
Get all users:
GET /profile/identity/v4/Users
Authorization: Bearer {token}
Filter users:
GET /profile/identity/v4/Users?filter=employeeNumber eq "123456789"
GET /profile/identity/v4/Users?filter=userName eq "user@domain.com"
Pagination:
GET /profile/identity/v4/Users?startIndex=1&count=50
Retrieve Single User
GET /profile/identity/v4/Users/{userId}
Authorization: Bearer {token}
Create User
POST /profile/identity/v4/Users
Authorization: Bearer {token}
Content-Type: application/json

{
  "schemas": [
    "urn:ietf:params:scim:schemas:core:2.0:User"
  ],
  "userName": "john.doe@company.com",
  "active": true,
  "name": {
    "familyName": "Doe",
    "givenName": "John"
  },
  "emails": [
    {
      "value": "john.doe@company.com",
      "type": "work",
      "verified": true
    }
  ],
  "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User": {
    "employeeNumber": "12345",
    "companyId": "aa076ada-80a9-4f57-8e98-9300b1c3171d"
  }
}
Update User (PATCH)
PATCH /profile/identity/v4/Users/{userId}
Authorization: Bearer {token}
Content-Type: application/json

{
  "schemas": [
    "urn:ietf:params:scim:api:messages:2.0:PatchOp"
  ],
  "Operations": [
    {
      "op": "replace",
      "path": "name.givenName",
      "value": "Jane"
    }
  ]
}
Replace User (PUT)
PUT /profile/identity/v4/Users/{userId}
Authorization: Bearer {token}
Content-Type: application/json

{
  "schemas": [
    "urn:ietf:params:scim:schemas:core:2.0:User"
  ],
  "userName": "jane.doe@company.com",
  "active": true,
  "name": {
    "familyName": "Doe",
    "givenName": "Jane"
  },
  "emails": [
    {
      "value": "jane.doe@company.com",
      "type": "work"
    }
  ]
}

Identity v4.1 API
The Identity v4.1 API includes enhanced search capabilities and improved performance.
Base URL
https://{datacenterURI}/profile/identity/v4.1/
New Features

Advanced search functionality
Cursor-based pagination
Enhanced filtering capabilities
Improved performance

Enhanced Search
The v4.1 API introduces a dedicated search endpoint with powerful filtering:
POST /profile/identity/v4.1/Users/.search
Authorization: Bearer {token}
Content-Type: application/json

{
  "schemas": [
    "urn:ietf:params:scim:api:messages:concur:2.0:SearchRequest"
  ],
  "filter": "active eq true and emails.type eq \"work\"",
  "attributes": ["id", "userName", "active", "emails"],
  "count": 100
}
Supported Filter Operations

eq (equals)
ne (not equals)
gt (greater than)
ge (greater than or equal)
lt (less than)
le (less than or equal)
co (contains)
sw (starts with)
ew (ends with)
pr (present)

Complex Filter Examples
# Multiple conditions
filter: active eq true and name.familyName co "Smith"

# Date comparisons
filter: urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:startDate gt "2023-01-01"

# Array operations
filter: emails[type eq "work"].value co "@company.com"

Schemas and Data Structures
Core User Schema
The User schema contains core identity attributes:
Required Fields:

userName: Unique login identifier
active: Boolean status
name.familyName: Last name
name.givenName: First name
emails: Array of email objects

Optional Fields:

displayName: Display name
nickName: Preferred name
title: Job title
phoneNumbers: Array of phone objects
addresses: Array of address objects
dateOfBirth: Date of birth
timezone: User timezone
preferredLanguage: Language preference

Enterprise Extension
Enterprise-specific attributes:

companyId: SAP Concur company ID (required, immutable)
employeeNumber: Employee number (unique within company)
manager: Manager information
department: Department name
division: Division name
costCenter: Cost center code
startDate: Employment start date
terminationDate: Employment end date
leavesOfAbsence: Leave information

SAP Extension
SAP-specific attributes:

userUuid: SAP Global ID for cross-SAP integration

Email Object Structure
json{
  "value": "user@company.com",
  "type": "work|home|work2|other|other2",
  "notifications": true,
  "verified": false
}
Phone Number Object Structure
json{
  "value": "+1-425-123-4567",
  "type": "work|home|mobile|fax|pager|other",
  "display": "425-123-4567",
  "primary": true,
  "notifications": true
}
Address Object Structure
json{
  "type": "work|home|other|billing|bank|shipping",
  "streetAddress": "123 Main St",
  "locality": "Seattle",
  "region": "WA",
  "postalCode": "98101",
  "country": "US"
}

Best Practices
Security

Store credentials securely: Never expose client secrets in client-side code
Use HTTPS: Always use encrypted connections
Token storage: Store refresh tokens securely with user data
Geolocation: Always use the geolocation from token responses
Token refresh: Implement automatic token refresh logic

Performance

Pagination: Use appropriate page sizes (max 1000 for v4.1, 100 default)
Filtering: Use filters to reduce response sizes
Attribute selection: Request only needed attributes
Caching: Cache user data appropriately with proper invalidation

API Usage

Correlation IDs: Include correlation IDs for troubleshooting
Rate limiting: Implement appropriate rate limiting
Error handling: Handle all HTTP status codes properly
Retry logic: Implement exponential backoff for retries

Data Management

Username uniqueness: Ensure usernames are unique across all SAP Concur products
Employee number uniqueness: Ensure employee numbers are unique within companies
Data validation: Validate all user data before submission
Locale support: Handle localization properly


Error Handling
HTTP Status Codes

200 OK: Successful request
400 Bad Request: Invalid request syntax or parameters
401 Unauthorized: Invalid or missing authentication
403 Forbidden: Insufficient permissions
404 Not Found: Resource not found
500 Internal Server Error: Server error
503 Service Unavailable: Service temporarily unavailable

Common Error Codes
Authentication Errors:

Code 5: invalid_grant - Incorrect credentials
Code 10-14: Account disabled/locked
Code 16: invalid_request - User lives elsewhere
Code 61: invalid_client - Client not found
Code 64: invalid_client - Incorrect credentials

Request Errors:

Code 51-52: Missing username/password
Code 53: invalid_client - Company not enabled
Code 54: invalid_scope - Requested scope exceeds granted
Code 55: invalid_request - Email not found
Code 108: invalid_grant - Bad or expired refresh token

Error Response Format
json{
  "error": "invalid_grant",
  "error_description": "Incorrect Credentials. Please Retry",
  "code": 5
}
SCIM Error Format
json{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
  "scimType": "invalidValue",
  "detail": "The specified filter syntax is invalid",
  "status": "400"
}

Examples and Code Samples
cURL Examples
Authentication Examples
Password Grant Authentication:
bashcurl -X POST 'https://us.api.concursolutions.com/oauth2/v0/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -H 'concur-correlationid: my-app-correlation-id' \
  --data-urlencode 'client_id=e01f725d-b4ce-4ce3-a664-b670cb5876cb0' \
  --data-urlencode 'client_secret=35c3bd92-fcb8-405e-a886-47ff3fba5664' \
  --data-urlencode 'grant_type=password' \
  --data-urlencode 'username=john.doe@company.com' \
  --data-urlencode 'password=mypassword123'
Client Credentials Grant:
bashcurl -X POST 'https://us.api.concursolutions.com/oauth2/v0/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'client_id=e01f725d-b4ce-4ce3-a664-b670cb5876cb0' \
  --data-urlencode 'client_secret=35c3bd92-fcb8-405e-a886-47ff3fba5664' \
  --data-urlencode 'grant_type=client_credentials'
Refresh Token:
bashcurl -X POST 'https://us.api.concursolutions.com/oauth2/v0/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'client_id=e01f725d-b4ce-4ce3-a664-b670cb5876cb0' \
  --data-urlencode 'client_secret=35c3bd92-fcb8-405e-a886-47ff3fba5664' \
  --data-urlencode 'grant_type=refresh_token' \
  --data-urlencode 'refresh_token=2d725xipty0z7ha3vlpy8b2c3hqxmw'
Company-Level Authentication:
bashcurl -X POST 'https://us.api.concursolutions.com/oauth2/v0/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'client_id=e01f725d-b4ce-4ce3-a664-b670cb5876cb0' \
  --data-urlencode 'client_secret=35c3bd92-fcb8-405e-a886-47ff3fba5664' \
  --data-urlencode 'grant_type=password' \
  --data-urlencode 'username=08BCCA1E-0D4F-4261-9F1B-F778D96617D6' \
  --data-urlencode 'password=5l85ae5a-426f-4d6f-8af4-08648c4b696b' \
  --data-urlencode 'credtype=authtoken'
One-Time Password Request:
bashcurl -X POST 'https://us.api.concursolutions.com/oauth2/v0/otp' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'client_id=e01f725d-b4ce-4ce3-a664-b670cb5876cb0' \
  --data-urlencode 'client_secret=35c3bd92-fcb8-405e-a886-47ff3fba5664' \
  --data-urlencode 'channel_handle=user@company.com' \
  --data-urlencode 'channel_type=email' \
  --data-urlencode 'name=John Doe' \
  --data-urlencode 'company=My Company' \
  --data-urlencode 'link=https://myapp.com/callback'
Exchange OTP for Token:
bashcurl -X POST 'https://us.api.concursolutions.com/oauth2/v0/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'client_id=e01f725d-b4ce-4ce3-a664-b670cb5876cb0' \
  --data-urlencode 'client_secret=35c3bd92-fcb8-405e-a886-47ff3fba5664' \
  --data-urlencode 'channel_handle=user@company.com' \
  --data-urlencode 'channel_type=email' \
  --data-urlencode 'scope=identity.user.core.read' \
  --data-urlencode 'grant_type=otp' \
  --data-urlencode 'otp=123456'
Identity API Examples
Get All Users:
bashcurl -X GET 'https://us.api.concursolutions.com/profile/identity/v4/Users' \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1Q...' \
  -H 'Accept: application/json'
Get Users with Filter:
bashcurl -X GET 'https://us.api.concursolutions.com/profile/identity/v4/Users?filter=active%20eq%20true&count=50' \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1Q...' \
  -H 'Accept: application/json'
Get Single User:
bashcurl -X GET 'https://us.api.concursolutions.com/profile/identity/v4/Users/3df11695-e8bb-40ff-8e98-c85913ab2789' \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1Q...' \
  -H 'Accept: application/json'
Create User:
bashcurl -X POST 'https://us.api.concursolutions.com/profile/identity/v4/Users' \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1Q...' \
  -H 'Content-Type: application/json' \
  -d '{
    "schemas": [
      "urn:ietf:params:scim:schemas:core:2.0:User"
    ],
    "userName": "john.doe@company.com",
    "active": true,
    "name": {
      "familyName": "Doe",
      "givenName": "John"
    },
    "emails": [
      {
        "value": "john.doe@company.com",
        "type": "work",
        "verified": true
      }
    ],
    "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User": {
      "employeeNumber": "12345",
      "companyId": "aa076ada-80a9-4f57-8e98-9300b1c3171d"
    }
  }'
Update User (PATCH):
bashcurl -X PATCH 'https://us.api.concursolutions.com/profile/identity/v4/Users/3df11695-e8bb-40ff-8e98-c85913ab2789' \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1Q...' \
  -H 'Content-Type: application/json' \
  -d '{
    "schemas": [
      "urn:ietf:params:scim:api:messages:2.0:PatchOp"
    ],
    "Operations": [
      {
        "op": "replace",
        "path": "title",
        "value": "Senior Developer"
      },
      {
        "op": "add",
        "path": "nickName",
        "value": "Johnny"
      }
    ]
  }'
Search Users (v4.1):
bashcurl -X POST 'https://us.api.concursolutions.com/profile/identity/v4.1/Users/.search' \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1Q...' \
  -H 'Content-Type: application/json' \
  -d '{
    "schemas": [
      "urn:ietf:params:scim:api:messages:concur:2.0:SearchRequest"
    ],
    "filter": "active eq true and emails[type eq \"work\"].value co \"@company.com\"",
    "attributes": ["id", "userName", "active", "emails"],
    "count": 100
  }'
Get Profile Information:
bashcurl -X GET 'https://us.api.concursolutions.com/profile/v1/me' \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1Q...' \
  -H 'Accept: application/json'
Revoke Token:
bashcurl -X DELETE 'https://us.api.concursolutions.com/app-mgmt/v0/connections' \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1Q...'
Python Examples
Complete Authentication and Identity Management Class
pythonimport requests
import json
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta

class ConcurAuth:
    """SAP Concur OAuth2 Authentication Handler"""
    
    def __init__(self, client_id: str, client_secret: str, geolocation: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.geolocation = geolocation
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
    def authenticate_password(self, username: str, password: str, credtype: str = "password") -> Dict[str, Any]:
        """
        Authenticate using password grant
        
        Args:
            username: Username or Company UUID
            password: Password or request token
            credtype: "password" or "authtoken"
        """
        url = f"{self.geolocation}/oauth2/v0/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'password',
            'username': username,
            'password': password,
            'credtype': credtype
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'concur-correlationid': 'python-client'
        }
        
        try:
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            self._store_tokens(token_data)
            
            return token_data
            
        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def authenticate_client_credentials(self) -> Dict[str, Any]:
        """Authenticate using client credentials grant"""
        url = f"{self.geolocation}/oauth2/v0/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            self._store_tokens(token_data)
            
            return token_data
            
        except requests.exceptions.RequestException as e:
            print(f"Client credentials authentication failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            raise ValueError("No refresh token available")
            
        url = f"{self.geolocation}/oauth2/v0/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            self._store_tokens(token_data)
            
            return token_data
            
        except requests.exceptions.RequestException as e:
            print(f"Token refresh failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def request_otp(self, email: str, name: str = None, company: str = None, callback_url: str = None) -> Dict[str, Any]:
        """Request one-time password via email"""
        url = f"{self.geolocation}/oauth2/v0/otp"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'channel_handle': email,
            'channel_type': 'email'
        }
        
        if name:
            data['name'] = name
        if company:
            data['company'] = company
        if callback_url:
            data['link'] = callback_url
            
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"OTP request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def authenticate_otp(self, email: str, otp: str, scope: str = None) -> Dict[str, Any]:
        """Exchange OTP for access token"""
        url = f"{self.geolocation}/oauth2/v0/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'channel_handle': email,
            'channel_type': 'email',
            'grant_type': 'otp',
            'otp': otp
        }
        
        if scope:
            data['scope'] = scope
            
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(url, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            self._store_tokens(token_data)
            
            return token_data
            
        except requests.exceptions.RequestException as e:
            print(f"OTP authentication failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def _store_tokens(self, token_data: Dict[str, Any]):
        """Store token data internally"""
        self.access_token = token_data.get('access_token')
        self.refresh_token = token_data.get('refresh_token')
        
        # Update geolocation if provided
        if 'geolocation' in token_data:
            self.geolocation = token_data['geolocation']
            
        # Calculate expiration time
        expires_in = int(token_data.get('expires_in', 3600))
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
    
    def is_token_expired(self) -> bool:
        """Check if access token is expired"""
        if not self.token_expires_at:
            return True
        return datetime.now() >= self.token_expires_at
    
    def ensure_valid_token(self):
        """Ensure we have a valid access token, refresh if needed"""
        if self.is_token_expired() and self.refresh_token:
            self.refresh_access_token()
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API calls"""
        self.ensure_valid_token()
        
        if not self.access_token:
            raise ValueError("No access token available")
            
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }


class ConcurIdentity:
    """SAP Concur Identity API Client"""
    
    def __init__(self, auth_client: ConcurAuth):
        self.auth = auth_client
    
    def get_users(self, filter_expr: str = None, count: int = 100, start_index: int = 1, 
                  attributes: List[str] = None, excluded_attributes: List[str] = None) -> Dict[str, Any]:
        """Get users with optional filtering and pagination"""
        url = f"{self.auth.geolocation}/profile/identity/v4/Users"
        
        params = {
            'count': count,
            'startIndex': start_index
        }
        
        if filter_expr:
            params['filter'] = filter_expr
        if attributes:
            params['attributes'] = ','.join(attributes)
        if excluded_attributes:
            params['excludedAttributes'] = ','.join(excluded_attributes)
            
        try:
            response = requests.get(url, params=params, headers=self.auth.get_auth_headers())
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Get users failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get a single user by ID"""
        url = f"{self.auth.geolocation}/profile/identity/v4/Users/{user_id}"
        
        try:
            response = requests.get(url, headers=self.auth.get_auth_headers())
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Get user failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        url = f"{self.auth.geolocation}/profile/identity/v4/Users"
        
        try:
            response = requests.post(url, json=user_data, headers=self.auth.get_auth_headers())
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Create user failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def update_user(self, user_id: str, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update user using PATCH operations"""
        url = f"{self.auth.geolocation}/profile/identity/v4/Users/{user_id}"
        
        patch_data = {
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
            "Operations": operations
        }
        
        try:
            response = requests.patch(url, json=patch_data, headers=self.auth.get_auth_headers())
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Update user failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def replace_user(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Replace user data using PUT"""
        url = f"{self.auth.geolocation}/profile/identity/v4/Users/{user_id}"
        
        try:
            response = requests.put(url, json=user_data, headers=self.auth.get_auth_headers())
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Replace user failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def search_users(self, filter_expr: str, attributes: List[str] = None, count: int = 100, 
                     cursor: str = None) -> Dict[str, Any]:
        """Search users using Identity v4.1 enhanced search"""
        url = f"{self.auth.geolocation}/profile/identity/v4.1/Users/.search"
        
        search_data = {
            "schemas": ["urn:ietf:params:scim:api:messages:concur:2.0:SearchRequest"],
            "filter": filter_expr,
            "count": count
        }
        
        if attributes:
            search_data["attributes"] = attributes
        if cursor:
            search_data["cursor"] = cursor
            
        try:
            response = requests.post(url, json=search_data, headers=self.auth.get_auth_headers())
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Search users failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def get_schemas(self) -> Dict[str, Any]:
        """Get all supported schemas"""
        url = f"{self.auth.geolocation}/profile/identity/v4/Schemas/"
        
        try:
            response = requests.get(url, headers=self.auth.get_auth_headers())
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Get schemas failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    def get_resource_types(self) -> Dict[str, Any]:
        """Get resource types"""
        url = f"{self.auth.geolocation}/profile/identity/v4/ResourceTypes/"
        
        try:
            response = requests.get(url, headers=self.auth.get_auth_headers())
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Get resource types failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise


# Example usage and demonstrations
def main():
    """Demonstrate usage of the Concur authentication and Identity APIs"""
    
    # Initialize authentication client
    auth = ConcurAuth(
        client_id="e01f725d-b4ce-4ce3-a664-b670cb5876cb0",
        client_secret="35c3bd92-fcb8-405e-a886-47ff3fba5664",
        geolocation="https://us.api.concursolutions.com"
    )
    
    try:
        # Authenticate using password grant
        print("Authenticating with password grant...")
        token_data = auth.authenticate_password("john.doe@company.com", "password123")
        print(f"Authentication successful. Token expires in {token_data['expires_in']} seconds")
        
        # Initialize Identity API client
        identity = ConcurIdentity(auth)
        
        # Get all active users
        print("\nGetting active users...")
        users_response = identity.get_users(filter_expr="active eq true", count=10)
        print(f"Found {users_response['totalResults']} active users")
        
        # Search for users with specific email domain
        print("\nSearching for company users...")
        search_results = identity.search_users(
            filter_expr='emails[type eq "work"].value co "@company.com"',
            attributes=["id", "userName", "emails", "active"]
        )
        print(f"Found {len(search_results['Resources'])} company users")
        
        # Create a new user
        print("\nCreating new user...")
        new_user_data = {
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:User"
            ],
            "userName": "jane.smith@company.com",
            "active": True,
            "name": {
                "familyName": "Smith",
                "givenName": "Jane"
            },
            "emails": [
                {
                    "value": "jane.smith@company.com",
                    "type": "work",
                    "verified": True
                }
            ],
            "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User": {
                "employeeNumber": "54321",
                "companyId": "aa076ada-80a9-4f57-8e98-9300b1c3171d"
            }
        }
        
        created_user = identity.create_user(new_user_data)
        print(f"Created user with ID: {created_user['id']}")
        
        # Update the user
        print("\nUpdating user...")
        update_operations = [
            {
                "op": "replace",
                "path": "title",
                "value": "Senior Developer"
            },
            {
                "op": "add",
                "path": "nickName",
                "value": "Janie"
            }
        ]
        
        updated_user = identity.update_user(created_user['id'], update_operations)
        print(f"Updated user: {updated_user['displayName']}")
        
        # Get specific user details
        print("\nGetting user details...")
        user_details = identity.get_user(created_user['id'])
        print(f"User details: {user_details['userName']} - {user_details.get('title', 'No title')}")
        
        # Demonstrate token refresh
        print("\nRefreshing access token...")
        refreshed_token = auth.refresh_access_token()
        print("Token refreshed successfully")
        
        # Get schemas information
        print("\nGetting API schemas...")
        schemas = identity.get_schemas()
        print(f"Available schemas: {len(schemas['Resources'])}")
        
    except Exception as e:
        print(f"Error occurred: {e}")


def company_authentication_example():
    """Example of company-level authentication"""
    
    auth = ConcurAuth(
        client_id="your-client-id",
        client_secret="your-client-secret",
        geolocation="https://us.api.concursolutions.com"
    )
    
    try:
        # Authenticate as company using request token
        print("Authenticating as company...")
        token_data = auth.authenticate_password(
            username="08BCCA1E-0D4F-4261-9F1B-F778D96617D6",  # Company UUID
            password="5l85ae5a-426f-4d6f-8af4-08648c4b696b",   # Request token
            credtype="authtoken"
        )
        print("Company authentication successful")
        
        # Use company-level access for Identity API
        identity = ConcurIdentity(auth)
        users = identity.get_users(count=50)
        print(f"Company has {users['totalResults']} users")
        
    except Exception as e:
        print(f"Company authentication failed: {e}")


def otp_authentication_example():
    """Example of one-time password authentication"""
    
    auth = ConcurAuth(
        client_id="your-client-id",
        client_secret="your-client-secret",
        geolocation="https://us.api.concursolutions.com"
    )
    
    try:
        # Request OTP
        print("Requesting OTP...")
        otp_response = auth.request_otp(
            email="user@company.com",
            name="John Doe",
            company="My Company",
            callback_url="https://myapp.com/callback"
        )
        print("OTP sent to email")
        
        # In real application, user would receive OTP via email
        # For demo purposes, assume we have the OTP
        otp_code = input("Enter OTP received via email: ")
        
        # Authenticate with OTP
        print("Authenticating with OTP...")
        token_data = auth.authenticate_otp(
            email="user@company.com",
            otp=otp_code,
            scope="identity.user.core.read"
        )
        print("OTP authentication successful")
        
    except Exception as e:
        print(f"OTP authentication failed: {e}")


if __name__ == "__main__":
    # Run the main demonstration
    main()
    
    # Uncomment to run other examples
    # company_authentication_example()
    # otp_authentication_example()
Simple Usage Examples
Basic Authentication and User Retrieval:
pythonimport requests

# Configuration
CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-client-secret"
GEOLOCATION = "https://us.api.concursolutions.com"
USERNAME = "user@company.com"
PASSWORD = "password123"

# Step 1: Authenticate
auth_url = f"{GEOLOCATION}/oauth2/v0/token"
auth_data = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'password',
    'username': USERNAME,
    'password': PASSWORD
}

auth_response = requests.post(auth_url, data=auth_data)
auth_response.raise_for_status()
token_info = auth_response.json()

access_token = token_info['access_token']
actual_geolocation = token_info['geolocation']

# Step 2: Get users
users_url = f"{actual_geolocation}/profile/identity/v4/Users"
headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json'
}

users_response = requests.get(users_url, headers=headers)
users_response.raise_for_status()
users_data = users_response.json()

print(f"Total users: {users_data['totalResults']}")
for user in users_data['Resources'][:5]:  # Show first 5 users
    print(f"- {user['userName']} (ID: {user['id']})")
Filter and Search Users:
pythonimport requests

def search_users_by_department(access_token, geolocation, department):
    """Search for users in a specific department"""
    
    search_url = f"{geolocation}/profile/identity/v4.1/Users/.search"
    
    search_payload = {
        "schemas": ["urn:ietf:params:scim:api:messages:concur:2.0:SearchRequest"],
        "filter": f'urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:department eq "{department}"',
        "attributes": ["id", "userName", "name", "emails"],
        "count": 50
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(search_url, json=search_payload, headers=headers)
    response.raise_for_status()
    
    return response.json()

# Usage
results = search_users_by_department(access_token, actual_geolocation, "Engineering")
print(f"Found {len(results['Resources'])} users in Engineering department")
Create and Update User:
pythonimport requests

def create_user_example(access_token, geolocation):
    """Create a new user"""
    
    create_url = f"{geolocation}/profile/identity/v4/Users"
    
    user_data = {
        "schemas": [
            "urn:ietf:params:scim:schemas:core:2.0:User"
        ],
        "userName": "newuser@company.com",
        "active": True,
        "name": {
            "familyName": "Johnson",
            "givenName": "Alex"
        },
        "emails": [
            {
                "value": "newuser@company.com",
                "type": "work"
            }
        ],
        "phoneNumbers": [
            {
                "value": "+1-555-123-4567",
                "type": "work"
            }
        ],
        "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User": {
            "employeeNumber": "EMP12345",
            "companyId": "your-company-id",
            "department": "Engineering"
        }
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(create_url, json=user_data, headers=headers)
    response.raise_for_status()
    
    return response.json()

def update_user_example(access_token, geolocation, user_id):
    """Update an existing user"""
    
    update_url = f"{geolocation}/profile/identity/v4/Users/{user_id}"
    
    update_data = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
        "Operations": [
            {
                "op": "replace",
                "path": "title",
                "value": "Senior Software Engineer"
            },
            {
                "op": "add",
                "path": "phoneNumbers",
                "value": [
                    {
                        "value": "+1-555-987-6543",
                        "type": "mobile",
                        "primary": True
                    }
                ]
            }
        ]
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.patch(update_url, json=update_data, headers=headers)
    response.raise_for_status()
    
    return response.json()

# Usage
new_user = create_user_example(access_token, actual_geolocation)
print(f"Created user: {new_user['id']}")

updated_user = update_user_example(access_token, actual_geolocation, new_user['id'])
print(f"Updated user: {updated_user['userName']}")
Error Handling Example:
pythonimport requests
from requests.exceptions import HTTPError, RequestException

def robust_api_call(access_token, geolocation, endpoint, method='GET', data=None):
    """Make API call with proper error handling"""
    
    url = f"{geolocation}{endpoint}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'PATCH':
            response = requests.patch(url, json=data, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json() if response.content else {}
        
    except HTTPError as e:
        print(f"HTTP Error {e.response.status_code}: {e.response.reason}")
        
        # Try to parse error response
        try:
            error_data = e.response.json()
            if 'error' in error_data:
                print(f"Error: {error_data['error']}")
                print(f"Description: {error_data.get('error_description', 'No description')}")
                print(f"Code: {error_data.get('code', 'No code')}")
            else:
                print(f"Error response: {error_data}")
        except:
            print(f"Raw error response: {e.response.text}")
            
        raise
        
    except RequestException as e:
        print(f"Request failed: {e}")
        raise
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

# Usage with error handling
try:
    users = robust_api_call(access_token, actual_geolocation, "/profile/identity/v4/Users?count=10")
    print(f"Successfully retrieved {len(users['Resources'])} users")
except Exception as e:
    print(f"Failed to retrieve users: {e}")

This comprehensive guide provides everything you need to authenticate with SAP Concur's OAuth2 system and use the Identity APIs effectively. The examples demonstrate real-world usage patterns with both curl commands and Python code, including proper error handling and best practices.