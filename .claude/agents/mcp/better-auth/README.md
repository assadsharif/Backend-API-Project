# Better-Auth MCP Server

**Type**: Design-Time Intelligence
**Version**: 1.0.0
**Purpose**: OAuth integration, session management, and authentication design guidance for progressive signup flows

---

## Overview

The Better-Auth MCP Server provides design-time intelligence for authentication and authorization patterns in educational platforms. It guides the implementation of:

- **OAuth Integration** (Google, GitHub, Microsoft)
- **Email Verification** (magic links, verification codes)
- **Session Management** (JWT access/refresh tokens, cookie security)
- **Progressive Tier Upgrades** (anonymous → lightweight → full → premium)
- **Privacy Compliance** (GDPR, CCPA, FERPA, COPPA)

**Design Philosophy**: Privacy-first, zero-friction authentication with progressive enhancement.

---

## Capabilities

### 1. OAuth Provider Integration

**Supported Providers**:
- **Google** (OAuth 2.0, OpenID Connect)
- **GitHub** (OAuth 2.0)
- **Microsoft** (OAuth 2.0, Azure AD)

**Design Guidance**:
- OAuth flow diagrams (authorization code flow)
- State parameter validation (CSRF protection)
- Token exchange (authorization code → access token)
- User profile mapping (email, name, avatar)

**Example Flow**:
```
1. User clicks "Sign in with Google"
2. Redirect to Google OAuth consent screen
3. User approves → redirected to /api/v1/auth/oauth/callback?code=AUTH_CODE
4. Backend exchanges code for access token
5. Fetch user profile (email, name)
6. Create or update user record
7. Issue JWT session token
8. Redirect to app with session cookie
```

---

### 2. Email Verification

**Supported Methods**:
- **Magic Links** (passwordless, email-only login)
- **Verification Codes** (6-digit codes sent via email)
- **Email + Password** (traditional signup with verification)

**Design Guidance**:
- Email template design (welcome emails, verification links)
- Token expiration (magic links: 15 min, verification codes: 5 min)
- Rate limiting (max 3 emails per hour per user)

**Example Flow**:
```
1. User enters email → clicks "Sign Up"
2. Backend generates verification token (UUID + HMAC)
3. Send email with link: /api/v1/auth/verify?token=TOKEN
4. User clicks link → backend validates token
5. Mark email as verified
6. Issue JWT session token
7. Redirect to app
```

---

### 3. Session Management

**Token Types**:
- **Access Token** (JWT, 15-minute TTL, HttpOnly cookie)
- **Refresh Token** (JWT, 7-day TTL, HttpOnly cookie)

**Security Features**:
- **HttpOnly** cookies (prevent XSS)
- **Secure** flag (HTTPS only)
- **SameSite=Strict** (prevent CSRF)
- **Token rotation** (refresh token rotated on every use)

**Design Guidance**:
- JWT payload structure (user_id, tier, email, exp)
- Token refresh flow (access token expired → use refresh token)
- Session invalidation (logout, password change)

**Example JWT Payload**:
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "tier": "full",
  "iat": 1672531200,
  "exp": 1672532100
}
```

---

### 4. Progressive Tier Upgrades

**Tier Definitions**:
- **Tier 0 (Anonymous)**: Browser-local only, no account
- **Tier 1 (Lightweight)**: Email verification, basic features
- **Tier 2 (Full)**: OAuth login, personalized learning
- **Tier 3 (Premium)**: Analytics, advanced features

**Upgrade Flows**:
1. **Tier 0 → Tier 1**: User clicks "Save Progress" → email signup → session merge (browser-local → server)
2. **Tier 1 → Tier 2**: User clicks "Connect Google/GitHub" → OAuth login → profile enrichment
3. **Tier 2 → Tier 3**: User subscribes to premium → payment verification → feature unlock

**Design Guidance**:
- Session merge algorithm (preserve conversation history)
- Tier badge display (Anonymous / Member / Premium)
- Feature gating (check user.tier before rendering features)

---

### 5. Privacy Compliance

**GDPR (EU)**:
- **Consent Management**: Explicit opt-in before Tier 1+ signup
- **Data Export**: Download all user data (JSON/CSV)
- **Data Deletion**: One-click account deletion (30-day retention for anonymous)
- **Right to Access**: View all stored data

**CCPA (California)**:
- **"Do Not Sell My Data"**: Opt-out link in footer
- **Third-Party Sharing**: Disclosure of data sharing practices

**FERPA (Education)**:
- **Age Gate**: Minimum age 13 for account creation
- **Parental Consent**: Required for users <18
- **Educational Records**: Encrypt progress, quiz scores (AES-256)

**COPPA (<13 years)**:
- **Age Verification**: Date of birth required
- **Parental Consent**: Email verification sent to parent
- **Disabled Features**: No social sharing, public profiles, third-party analytics for <13

---

## Integration Points

### Skills
- `.claude/skills/signup-personalization/` (Progressive Enhancement Signup Pattern)
- `.claude/skills/chatkit-widget/` (Session Continuity Pattern)

### Agents
- None (design-time only, no runtime orchestration)

### MCP Servers
- `.claude/mcp/chatkit/` (ChatKit Widget uses Better-Auth for Tier upgrades)

---

## Event Schemas

### signup_initiated Event

**Description**: User clicks signup button (Tier 0 → Tier 1)

**Payload**:
```json
{
  "event": "signup_initiated",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "flow": {
    "type": "progressive_signup",
    "current_tier": "anonymous",
    "target_tier": "lightweight",
    "trigger": "save_progress_button"
  }
}
```

---

### authentication_completed Event

**Description**: User completes email verification or OAuth login

**Payload**:
```json
{
  "event": "authentication_completed",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "auth": {
    "method": "oauth_google",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "tier": "full",
    "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2025-12-27T11:30:00.000Z"
  }
}
```

---

### session_tier_upgraded Event

**Description**: User upgrades from one tier to another (e.g., Tier 1 → Tier 2)

**Payload**:
```json
{
  "event": "session_tier_upgraded",
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "upgrade": {
    "previous_tier": "lightweight",
    "new_tier": "full",
    "method": "oauth_github",
    "timestamp": "2025-12-27T10:45:00.000Z"
  }
}
```

---

## API Endpoints (Phase 7+ Implementation)

### OAuth Flow

**POST /api/v1/auth/oauth/:provider**
- **Purpose**: Initiate OAuth flow (redirect to provider)
- **Providers**: `google`, `github`, `microsoft`
- **Response**: 302 Redirect to OAuth provider

**GET /api/v1/auth/oauth/callback**
- **Purpose**: OAuth callback (exchange code for token)
- **Query Params**: `code` (authorization code), `state` (CSRF token)
- **Response**: 302 Redirect to app with session cookie

---

### Email Verification

**POST /api/v1/auth/signup**
- **Purpose**: Email signup (send verification email)
- **Request Body**: `{ "email": "user@example.com" }`
- **Response**: `{ "message": "Verification email sent" }`

**GET /api/v1/auth/verify**
- **Purpose**: Verify email (magic link)
- **Query Params**: `token` (verification token)
- **Response**: 302 Redirect to app with session cookie

---

### Session Management

**POST /api/v1/auth/refresh**
- **Purpose**: Refresh access token using refresh token
- **Request**: Refresh token in HttpOnly cookie
- **Response**: New access token in HttpOnly cookie

**POST /api/v1/auth/logout**
- **Purpose**: Invalidate session (clear cookies)
- **Response**: `{ "message": "Logged out" }`

---

### Session Merge (Tier 0 → Tier 1)

**POST /api/v1/session/merge**
- **Purpose**: Merge anonymous session with authenticated user
- **Request Body**:
  ```json
  {
    "anonymous_session_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "data": {
      "conversation_history": [
        { "role": "user", "content": "What is embodied intelligence?" },
        { "role": "assistant", "content": "Embodied intelligence..." }
      ]
    }
  }
  ```
- **Response**: `{ "success": true, "merged_session_id": "123e4567-e89b-12d3-a456-426614174000" }`

---

## Security Best Practices

### 1. OAuth Security

**CSRF Protection**:
- Generate random `state` parameter before redirect
- Validate `state` parameter in callback
- Reject mismatched `state` values

**PKCE (Proof Key for Code Exchange)**:
- Generate `code_verifier` (random string)
- Hash to create `code_challenge`
- Include `code_challenge` in authorization request
- Send `code_verifier` in token exchange

---

### 2. Session Security

**Token Storage**:
- ✅ Store access token in HttpOnly cookie (prevent XSS)
- ❌ Never store token in localStorage (vulnerable to XSS)

**Token Rotation**:
- Rotate refresh token on every use
- Invalidate old refresh token after rotation

**Session Fixation Prevention**:
- Regenerate session ID after login
- Clear old session data

---

### 3. Rate Limiting

**Signup Endpoints**:
- Max 3 signup attempts per IP per hour
- Max 5 verification emails per user per day

**OAuth Endpoints**:
- Max 10 OAuth attempts per IP per hour

**Session Endpoints**:
- Max 100 refresh token requests per user per hour

---

## Compliance Rules

### GDPR

```json
{
  "gdpr": {
    "consent_required": true,
    "data_export": true,
    "data_deletion": true,
    "retention_policy": "30_days_inactive"
  }
}
```

**Implementation**:
- Cookie consent banner before Tier 1+ signup
- "Export My Data" button in user settings
- "Delete My Account" button (soft delete with 30-day retention)

---

### CCPA

```json
{
  "ccpa": {
    "do_not_sell_opt_out": true,
    "third_party_sharing": false
  }
}
```

**Implementation**:
- "Do Not Sell My Personal Information" link in footer
- Privacy policy disclosure (no data selling)

---

### FERPA

```json
{
  "ferpa": {
    "age_gate": 13,
    "parental_consent_under": 18,
    "educational_records_encryption": "AES-256"
  }
}
```

**Implementation**:
- Age verification during signup (date of birth)
- Parental consent email for users <18
- Encrypt educational records (progress, quiz scores)

---

### COPPA

```json
{
  "coppa": {
    "minimum_age": 13,
    "parental_consent_required": true,
    "under_13_features_disabled": ["social_sharing", "public_profiles", "third_party_analytics"]
  }
}
```

**Implementation**:
- Age gate (block signup if age <13 without parental consent)
- Parental consent flow (send email to parent with verification link)
- Feature gating (disable social features for <13)

---

## Cross-Domain Applicability

| Domain | Use Cases | Applicability |
|--------|-----------|---------------|
| **Educational Platforms** | Course platforms, MOOCs, LMS | ✅ Very High (FERPA compliance) |
| **SaaS Applications** | Freemium products, productivity tools | ✅ Very High (progressive signup) |
| **Documentation Sites** | API docs, developer portals | ✅ High (OAuth for GitHub) |
| **E-Commerce** | Online stores, marketplaces | ✅ Medium (OAuth for checkout) |
| **Healthcare** | Patient portals, telehealth | ✅ Medium (HIPAA compliance) |

---

## Design Validation Checklist

- [x] OAuth flows documented (Google, GitHub, Microsoft)
- [x] Email verification flows documented (magic links, codes)
- [x] Session management rules documented (JWT, cookies)
- [x] Progressive tier upgrade flows documented (Tier 0 → 1 → 2 → 3)
- [x] Privacy compliance rules documented (GDPR, CCPA, FERPA, COPPA)
- [x] Security best practices documented (CSRF, PKCE, rate limiting)
- [x] API endpoints specified (OAuth, email, session, merge)
- [x] Event schemas defined (signup_initiated, authentication_completed, session_tier_upgraded)
- [x] Cross-domain applicability assessed (5 domains)

---

## Future Enhancements (Phase 7+)

### Multi-Factor Authentication (MFA)
- SMS verification codes
- Authenticator apps (TOTP)
- Email 2FA

### Passwordless Authentication
- WebAuthn (biometric, hardware keys)
- Magic links only (no passwords)

### Social Login Expansion
- LinkedIn, Twitter/X, Apple
- Academic institution SSO (SAML)

---

## References

- **OAuth 2.0 RFC**: https://tools.ietf.org/html/rfc6749
- **OpenID Connect**: https://openid.net/connect/
- **JWT Best Practices**: https://tools.ietf.org/html/rfc7519
- **GDPR Compliance**: https://gdpr.eu/
- **CCPA Compliance**: https://oag.ca.gov/privacy/ccpa
- **FERPA Guidelines**: https://www2.ed.gov/policy/gen/guid/fpco/ferpa/index.html
- **COPPA Compliance**: https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa

---

**Status**: Design-Complete ✅
**Lines**: 500+
**Purpose**: Design-time intelligence for authentication and authorization (Phase 7+ implementation reference)
