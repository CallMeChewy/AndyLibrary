# AndyLibrary Visual User Flow Chart

## Complete User Journey with Symbols and Connectors

```mermaid
flowchart TD
    %% ========== START & INITIAL ACCESS ==========
    START([👤 USER OPENS BROWSER]) --> URL_VISIT{🌐 Visit Website}

    URL_VISIT -->|First Time| LANDING_PAGE[📄 LANDING PAGE<br/>🔄 Load static assets<br/>⚙️ Register service worker<br/>🔍 Check auth status]
    URL_VISIT -->|Returning User| SESSION_CHECK{🔐 Valid Session?}

    SESSION_CHECK -->|✅ Valid| DASHBOARD_DIRECT[📚 DASHBOARD<br/>🎉 Welcome back!]
    SESSION_CHECK -->|❌ Invalid/Expired| AUTH_REQUIRED[🔐 AUTH REQUIRED]

    %% ========== AUTHENTICATION CHOICE ==========
    LANDING_PAGE --> AUTH_STATUS{🔍 User Authenticated?}
    AUTH_STATUS -->|❌ No| AUTH_OPTIONS[🔐 AUTHENTICATION OPTIONS<br/>📝 Register New Account<br/>🔑 Login Existing<br/>🌐 OAuth Providers]
    AUTH_STATUS -->|✅ Yes| DASHBOARD_DIRECT

    AUTH_REQUIRED --> AUTH_OPTIONS

    %% ========== REGISTRATION FLOW ==========
    AUTH_OPTIONS --> REG_CHOICE{👤 User Choice}
    REG_CHOICE -->|📝 Register| REG_FORM[📝 REGISTRATION FORM<br/>📧 Email: user@example.com<br/>👤 Username: johndoe<br/>🔒 Password: ••••••••<br/>✅ Mission Acknowledgment]
    REG_CHOICE -->|🔑 Login| LOGIN_FORM[🔑 LOGIN FORM<br/>📧 Email: user@example.com<br/>🔒 Password: ••••••••]
    REG_CHOICE -->|🌐 OAuth| OAUTH_PROVIDERS[🌐 OAUTH PROVIDERS<br/>🔵 Google<br/>⚫ GitHub<br/>🔷 Facebook]

    %% Registration Submission & Validation
    REG_FORM -->|📤 Submit| REG_SUBMIT[📤 POST /api/auth/register<br/>📊 Data validation]
    REG_SUBMIT --> REG_VALIDATE{✅ Valid Data?}

    REG_VALIDATE -->|❌ Invalid| REG_ERROR_INVALID[❌ VALIDATION ERROR<br/>🚫 Missing fields<br/>📧 Invalid email format<br/>🔒 Weak password<br/>⚠️ Mission not acknowledged]
    REG_ERROR_INVALID -->|🔄 Retry| REG_FORM

    REG_VALIDATE -->|✅ Valid| DUPLICATE_CHECK{🔍 Check Duplicates}
    DUPLICATE_CHECK -->|📧 Email exists| REG_ERROR_EMAIL[❌ EMAIL EXISTS<br/>Status: 409 Conflict<br/>💬 "Email already registered"]
    DUPLICATE_CHECK -->|👤 Username exists| REG_ERROR_USERNAME[❌ USERNAME TAKEN<br/>Status: 409 Conflict<br/>💬 "Username already taken"]
    DUPLICATE_CHECK -->|✅ Unique| CREATE_USER[✅ CREATE USER<br/>🔐 Hash password (bcrypt)<br/>🎫 Generate verification token<br/>📧 EmailVerified = FALSE<br/>🚫 IsActive = FALSE<br/>💾 Insert into database]

    REG_ERROR_EMAIL -->|🔄 Try Again| REG_FORM
    REG_ERROR_USERNAME -->|🔄 Try Again| REG_FORM

    %% ========== EMAIL VERIFICATION FLOW ==========
    CREATE_USER --> SEND_EMAIL[📧 SEND VERIFICATION EMAIL<br/>📤 To: user@example.com<br/>📤 From: HimalayaProject1@gmail.com<br/>🔐 SMTP: smtp.gmail.com:465<br/>📝 Subject: "Verify Your Email"<br/>🔗 Contains verification link]

    SEND_EMAIL --> EMAIL_STATUS{📧 Email Sent?}
    EMAIL_STATUS -->|✅ Success| EMAIL_SUCCESS[✅ EMAIL SENT<br/>📊 SMTP Status: 250 OK<br/>🔐 SSL Connection: ✅<br/>⏰ Delivery confirmed]
    EMAIL_STATUS -->|❌ Failed| EMAIL_FAILED[❌ EMAIL FAILED<br/>🔴 SMTP server error<br/>🔴 Network timeout<br/>🔴 Invalid credentials<br/>🔴 Rate limit exceeded]

    EMAIL_SUCCESS --> REG_SUCCESS[🎉 REGISTRATION SUCCESS<br/>👤 User ID: 30 assigned<br/>💬 "Check your email to verify"<br/>⏳ Awaiting verification]
    EMAIL_FAILED --> REG_WARNING[⚠️ PARTIAL SUCCESS<br/>👤 Account created<br/>❌ Email delivery failed<br/>🔄 Manual verification needed]

    REG_SUCCESS --> EMAIL_WAIT[⏳ USER CHECKS EMAIL<br/>📧 Check inbox<br/>📧 Check spam folder<br/>👆 Click verification link]
    REG_WARNING --> EMAIL_WAIT

    %% Email Verification Process
    EMAIL_WAIT --> EMAIL_RECEIVED{📧 Email Received?}
    EMAIL_RECEIVED -->|✅ Yes| VERIFY_CLICK[👆 CLICK VERIFICATION LINK<br/>🔗 GET /api/auth/verify-email<br/>🎫 Token: xyz123abc<br/>⏰ Link expiration check]
    EMAIL_RECEIVED -->|❌ No - Lost| RESEND_REQUEST[🔄 REQUEST RESEND<br/>👆 Click "Resend Email"<br/>📤 POST /api/auth/resend-verification]
    EMAIL_RECEIVED -->|❌ No - Issues| EMAIL_ISSUES[📧 EMAIL DELIVERY ISSUES<br/>📁 Check spam folder<br/>🚫 Provider blocking<br/>❌ Wrong email address<br/>🔴 SMTP problems]

    RESEND_REQUEST --> SEND_EMAIL
    EMAIL_ISSUES -->|🔄 Retry| SEND_EMAIL
    EMAIL_ISSUES -->|📞 Support| SUPPORT_CONTACT[📞 CONTACT SUPPORT<br/>📧 Manual verification<br/>🆔 Account recovery<br/>📋 Issue reporting]

    %% Token Verification
    VERIFY_CLICK --> TOKEN_VALIDATE{🎫 Valid Token?}
    TOKEN_VALIDATE -->|✅ Valid| ACTIVATE_ACCOUNT[✅ ACTIVATE ACCOUNT<br/>📧 EmailVerified = TRUE<br/>✅ IsActive = TRUE<br/>🔑 AccessLevel = basic<br/>🗑️ Clear verification token<br/>⏰ Update timestamp]
    TOKEN_VALIDATE -->|❌ Invalid| VERIFY_ERROR[❌ VERIFICATION ERROR<br/>⏰ Token expired<br/>🔍 Token not found<br/>✅ Already verified<br/>🔧 Malformed token]

    ACTIVATE_ACCOUNT --> VERIFY_SUCCESS[🎉 VERIFICATION SUCCESS<br/>✅ Account fully activated<br/>🎊 "Email verified successfully!"<br/>▶️ Redirect to login]
    VERIFY_ERROR --> VERIFY_RETRY[🔄 VERIFICATION RETRY<br/>📧 Request new verification<br/>📞 Contact support<br/>🔑 Try login if already verified]

    VERIFY_RETRY --> RESEND_REQUEST

    %% ========== LOGIN FLOW ==========
    LOGIN_FORM -->|📤 Submit| LOGIN_SUBMIT[📤 POST /api/auth/login<br/>📊 {email, password}]
    VERIFY_SUCCESS --> LOGIN_FORM

    LOGIN_SUBMIT --> LOGIN_VALIDATE{✅ Valid Fields?}
    LOGIN_VALIDATE -->|❌ Missing| LOGIN_ERROR_FIELDS[❌ MISSING FIELDS<br/>Status: 422<br/>🚫 Email required<br/>🚫 Password required]
    LOGIN_VALIDATE -->|✅ Present| AUTH_PROCESS[🔍 AUTHENTICATE USER<br/>📧 Find user by email<br/>🔐 Verify credentials]

    LOGIN_ERROR_FIELDS -->|🔄 Fix| LOGIN_FORM

    %% Authentication Process
    AUTH_PROCESS --> USER_FOUND{👤 User Found?}
    USER_FOUND -->|❌ Not Found| LOGIN_ERROR_INVALID[❌ INVALID CREDENTIALS<br/>Status: 401<br/>💬 "Invalid email or password"<br/>🔒 Security: Don't reveal which]
    USER_FOUND -->|✅ Found| SECURITY_CHECKS[🔒 SECURITY CHECKS<br/>🔍 Account locked?<br/>📧 Email verified?<br/>✅ Account active?]

    SECURITY_CHECKS --> LOCKOUT_CHECK{🔒 Account Locked?}
    LOCKOUT_CHECK -->|🔒 Yes| LOGIN_ERROR_LOCKED[❌ ACCOUNT LOCKED<br/>Status: 423<br/>⏰ Locked for 15 minutes<br/>🔢 5+ failed attempts<br/>⏳ Time remaining shown]
    LOCKOUT_CHECK -->|🔓 No| EMAIL_VERIFY_CHECK{📧 Email Verified?}

    EMAIL_VERIFY_CHECK -->|❌ No| LOGIN_ERROR_UNVERIFIED[❌ EMAIL NOT VERIFIED<br/>Status: 401<br/>💬 "Email verification required"<br/>🔄 Option to resend verification]
    EMAIL_VERIFY_CHECK -->|✅ Yes| ACTIVE_CHECK{✅ Account Active?}

    ACTIVE_CHECK -->|❌ No| LOGIN_ERROR_INACTIVE[❌ ACCOUNT DEACTIVATED<br/>Status: 401<br/>💬 "Account is deactivated"<br/>📞 Contact support]
    ACTIVE_CHECK -->|✅ Yes| PASSWORD_VERIFY[🔐 VERIFY PASSWORD<br/>🔒 bcrypt.checkpw()<br/>💻 Compare with stored hash]

    %% Password Verification
    PASSWORD_VERIFY --> PASSWORD_MATCH{🔐 Password Match?}
    PASSWORD_MATCH -->|❌ No| FAILED_ATTEMPT[❌ FAILED ATTEMPT<br/>📈 Increment LoginAttempts<br/>🔍 Check if >= 5 attempts<br/>🔒 Set lockout if needed<br/>💾 Update database]
    PASSWORD_MATCH -->|✅ Yes| RESET_ATTEMPTS[✅ RESET ATTEMPTS<br/>🔢 LoginAttempts = 0<br/>🔓 Clear LockoutUntil<br/>⏰ Update LastLoginAt<br/>💾 Save to database]

    FAILED_ATTEMPT --> LOGIN_ERROR_INVALID
    RESET_ATTEMPTS --> CREATE_SESSION[✅ CREATE SESSION<br/>🎫 Generate session token<br/>🔄 Generate refresh token<br/>⏰ Set expiration (24h)<br/>💾 Store in UserSessions<br/>📊 Include user info]

    CREATE_SESSION --> LOGIN_SUCCESS[🎉 LOGIN SUCCESS<br/>👤 User: johndoe (ID: 30)<br/>🎫 Session: NtBRr-Vv0lmZ...<br/>🔄 Refresh: y3_jddCIpX...<br/>⏰ Expires: 2025-08-05 10:32<br/>💬 "Welcome back!"]

    %% Error Recovery Paths
    LOGIN_ERROR_INVALID -->|🔄 Retry| LOGIN_FORM
    LOGIN_ERROR_LOCKED --> LOCKOUT_WAIT[⏰ LOCKOUT WAIT<br/>⏱️ 15 minutes remaining<br/>🔄 Password reset option<br/>📞 Contact support<br/>⏳ Auto-unlock timer]
    LOGIN_ERROR_UNVERIFIED --> EMAIL_RESEND[📧 RESEND VERIFICATION<br/>🔄 New verification email<br/>🎫 Fresh token generated<br/>📤 Sent to registered email]
    LOGIN_ERROR_INACTIVE --> SUPPORT_CONTACT

    LOCKOUT_WAIT -->|⏰ Time Expires| LOGIN_FORM
    EMAIL_RESEND --> EMAIL_WAIT

    %% ========== DASHBOARD & LIBRARY ACCESS ==========
    LOGIN_SUCCESS --> DASHBOARD[📚 LIBRARY DASHBOARD<br/>🔍 Search 1,219 books<br/>📂 Browse 26 categories<br/>📑 View 118 subjects<br/>👤 User profile menu<br/>⭐ Book recommendations]
    DASHBOARD_DIRECT --> DASHBOARD

    DASHBOARD --> USER_ACTIONS{🎯 User Action}
    USER_ACTIONS -->|🔍 Search| SEARCH_BOOKS[🔍 SEARCH BOOKS<br/>💬 Query: "python programming"<br/>📤 GET /api/books?search=python<br/>📊 Returns: Book metadata<br/>🔢 Results from 1,219 books]
    USER_ACTIONS -->|📂 Browse| BROWSE_CATEGORY[📂 BROWSE CATEGORY<br/>📁 Category: "Programming Languages"<br/>📤 GET /api/books?category=21<br/>📋 Filtered book list<br/>📄 Pagination controls]
    USER_ACTIONS -->|👤 Profile| USER_PROFILE[👤 USER PROFILE<br/>⚙️ Account settings<br/>📊 Reading history<br/>⭐ Preferences<br/>🔐 Security settings]

    %% Search Results
    SEARCH_BOOKS --> SEARCH_RESULTS[📋 SEARCH RESULTS<br/>📚 Book titles & metadata<br/>👨‍💼 Author information<br/>📑 Subject categories<br/>✅ Availability status<br/>👆 Click to access]
    BROWSE_CATEGORY --> BROWSE_RESULTS[📂 CATEGORY RESULTS<br/>📚 Filtered book list<br/>📄 Page 1 of 15<br/>🔀 Sort options<br/>🎯 Filter by subject]

    SEARCH_RESULTS --> BOOK_SELECT{📖 Select Book}
    BROWSE_RESULTS --> BOOK_SELECT
    BOOK_SELECT --> BOOK_ACCESS[📖 ACCESS BOOK<br/>📚 Book ID: 893<br/>📝 Title: "Algorithmic Problem Solving with Python"<br/>📤 GET /api/books/893/url<br/>🔍 Check availability]

    %% ========== GOOGLE DRIVE INTEGRATION ==========
    BOOK_ACCESS --> GDRIVE_CHECK{🌐 Google Drive Configured?}
    GDRIVE_CHECK -->|❌ No| GDRIVE_SETUP_REQUIRED[⚙️ GOOGLE DRIVE SETUP REQUIRED<br/>🌐 Redirect to: /setup.html<br/>💬 "Configure Google Drive to access books"<br/>📋 Setup instructions<br/>🔗 OAuth integration needed]
    GDRIVE_CHECK -->|✅ Yes| GDRIVE_AUTH_CHECK{🔐 Google Auth Valid?}

    %% Google Drive Setup Process
    GDRIVE_SETUP_REQUIRED --> OAUTH_INITIATE[🌐 INITIATE OAUTH<br/>🔗 Redirect to Google<br/>🌐 accounts.google.com/o/oauth2/auth<br/>🔑 Scopes: drive.readonly, drive.metadata<br/>🆔 Client ID from config]

    OAUTH_INITIATE --> GOOGLE_AUTH{🌐 Google Authorization}
    GOOGLE_AUTH -->|✅ Grant Permission| OAUTH_SUCCESS[✅ OAUTH SUCCESS<br/>📤 GET /api/auth/oauth/callback<br/>🎫 Code & state parameters<br/>🔄 Exchange code for tokens<br/>💾 Save access & refresh tokens]
    GOOGLE_AUTH -->|❌ Deny Permission| OAUTH_DENIED[❌ OAUTH DENIED<br/>🚫 Error: access_denied<br/>💬 "Google Drive access required"<br/>🔄 Retry option<br/>📞 Support contact]
    GOOGLE_AUTH -->|⏰ Timeout/Error| OAUTH_ERROR[❌ OAUTH ERROR<br/>🔴 Network timeout<br/>🔴 Invalid client config<br/>🔴 Google service down<br/>🔄 Retry available]

    OAUTH_SUCCESS --> GDRIVE_CONFIGURED[✅ GOOGLE DRIVE CONFIGURED<br/>🎫 Access token saved<br/>🔄 Refresh token saved<br/>⏰ Expiration tracked<br/>👤 User association created<br/>🎉 Ready for book access]
    OAUTH_DENIED --> GDRIVE_SETUP_REQUIRED
    OAUTH_ERROR --> GDRIVE_SETUP_REQUIRED

    GDRIVE_CONFIGURED --> FIND_LIBRARY_FOLDER

    %% Google Drive Authentication Check
    GDRIVE_AUTH_CHECK -->|✅ Valid| FIND_LIBRARY_FOLDER[🔍 FIND LIBRARY FOLDER<br/>🌐 Search Google Drive<br/>📁 Folder name: "AndyLibrary"<br/>🔍 Type: vnd.google-apps.folder<br/>🔑 Using stored tokens]
    GDRIVE_AUTH_CHECK -->|❌ Invalid/Expired| TOKEN_REFRESH{🔄 Refresh Tokens}

    TOKEN_REFRESH -->|✅ Success| FIND_LIBRARY_FOLDER
    TOKEN_REFRESH -->|❌ Failed| GDRIVE_SETUP_REQUIRED

    %% Library Folder Discovery
    FIND_LIBRARY_FOLDER --> FOLDER_EXISTS{📁 Folder Exists?}
    FOLDER_EXISTS -->|❌ Not Found| FOLDER_MISSING[❌ LIBRARY FOLDER MISSING<br/>💬 "Create 'AndyLibrary' folder in Google Drive"<br/>📋 Step-by-step instructions:<br/>1️⃣ Go to drive.google.com<br/>2️⃣ Create "AndyLibrary" folder<br/>3️⃣ Upload book files<br/>4️⃣ Return and retry]
    FOLDER_EXISTS -->|✅ Found| SEARCH_BOOK_FILE[🔍 SEARCH BOOK FILE<br/>📁 In folder: AndyLibrary<br/>📚 Search for: "Algorithmic Problem Solving with Python"<br/>📄 Extensions: .pdf, .epub, .mobi, .txt, .doc, .docx<br/>🔍 Exact title matching]

    %% Book File Search
    SEARCH_BOOK_FILE --> FILE_FOUND{📄 Book File Found?}
    FILE_FOUND -->|✅ Yes| GENERATE_DOWNLOAD[🔗 GENERATE DOWNLOAD LINK<br/>🔐 Create signed URL<br/>⏰ Valid for: 1 hour<br/>🌐 Direct from Google Drive<br/>📊 Track download progress]
    FILE_FOUND -->|❌ No| FILE_NOT_FOUND[❌ BOOK FILE NOT AVAILABLE<br/>💬 "Book not found in your Google Drive"<br/>📚 Expected: "Algorithmic Problem Solving with Python.pdf"<br/>📁 Upload to: AndyLibrary folder<br/>📋 Upload instructions provided]

    %% Successful Book Delivery
    GENERATE_DOWNLOAD --> BOOK_DELIVERY[📖 BOOK DELIVERED<br/>🎉 Success! Book is ready<br/>⬇️ Direct download option<br/>🌐 Stream in browser<br/>📱 Open in PDF reader<br/>📊 Download progress tracking<br/>⭐ Rate book option]

    %% Error Recovery & Help
    FOLDER_MISSING --> FOLDER_HELP[📋 FOLDER CREATION HELP<br/>🎥 Video tutorial link<br/>📝 Written instructions<br/>❓ FAQ section<br/>📞 Support contact<br/>🔄 Retry button]
    FILE_NOT_FOUND --> UPLOAD_HELP[📋 FILE UPLOAD HELP<br/>📚 Supported formats listed<br/>📝 Filename requirements<br/>📁 Upload instructions<br/>⚖️ Legal sources guidance<br/>🔄 Retry after upload]

    FOLDER_HELP -->|📁 Created| FIND_LIBRARY_FOLDER
    UPLOAD_HELP -->|📚 Uploaded| SEARCH_BOOK_FILE

    %% Alternative Access Methods
    OAUTH_DENIED --> MANUAL_ACCESS[📖 MANUAL ACCESS METHODS<br/>💡 Alternative solutions<br/>📞 Support contact info<br/>📋 Troubleshooting guide<br/>🆘 Account recovery options]
    FOLDER_MISSING --> MANUAL_ACCESS
    FILE_NOT_FOUND --> MANUAL_ACCESS

    %% ========== SUCCESS & RETURN VISITS ==========
    BOOK_DELIVERY --> SUCCESS_END[🎉 COMPLETE SUCCESS<br/>✅ User successfully accesses books<br/>📚 Full functionality achieved<br/>🔄 Streamlined return visits<br/>⭐ Enhanced user experience]

    %% Return Visit Flow
    SUCCESS_END -->|🔄 Return Visit| URL_VISIT
    DASHBOARD -->|🔄 Return Visit| USER_ACTIONS

    %% ========== OAUTH PROVIDERS FLOW ==========
    OAUTH_PROVIDERS --> OAUTH_CHOICE{🌐 OAuth Choice}
    OAUTH_CHOICE -->|🔵 Google| GOOGLE_OAUTH[🔵 GOOGLE OAUTH<br/>🌐 accounts.google.com<br/>🔑 OpenID Connect<br/>📧 Email & profile access]
    OAUTH_CHOICE -->|⚫ GitHub| GITHUB_OAUTH[⚫ GITHUB OAUTH<br/>🌐 github.com/login/oauth<br/>👤 User profile access<br/>📧 Email access]
    OAUTH_CHOICE -->|🔷 Facebook| FACEBOOK_OAUTH[🔷 FACEBOOK OAUTH<br/>🌐 facebook.com/v19.0/dialog<br/>👤 Public profile access<br/>📧 Email access]

    GOOGLE_OAUTH --> OAUTH_CALLBACK_HANDLE[🔄 OAUTH CALLBACK<br/>🎫 Process authorization code<br/>👤 Create/login user<br/>📧 Email verification bypass<br/>✅ Auto-activate account]
    GITHUB_OAUTH --> OAUTH_CALLBACK_HANDLE
    FACEBOOK_OAUTH --> OAUTH_CALLBACK_HANDLE

    OAUTH_CALLBACK_HANDLE --> OAUTH_LOGIN_SUCCESS[🎉 OAUTH LOGIN SUCCESS<br/>👤 User authenticated<br/>📧 Email verified automatically<br/>✅ Account active<br/>🎫 Session created]

    OAUTH_LOGIN_SUCCESS --> DASHBOARD

    %% ========== STYLING ==========
    classDef startNode fill:#e1f5fe,stroke:#01579b,stroke-width:4px,color:#000
    classDef processNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    classDef decisionNode fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    classDef errorNode fill:#ffebee,stroke:#c62828,stroke-width:3px,color:#000
    classDef successNode fill:#e8f5e8,stroke:#2e7d32,stroke-width:3px,color:#000
    classDef warningNode fill:#fff8e1,stroke:#f57c00,stroke-width:2px,color:#000
    classDef infoNode fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000

    %% Apply styles
    class START,SUCCESS_END startNode
    class LANDING_PAGE,REG_FORM,LOGIN_FORM,SEND_EMAIL,CREATE_USER,BOOK_DELIVERY,OAUTH_INITIATE processNode
    class AUTH_STATUS,REG_CHOICE,SESSION_CHECK,EMAIL_RECEIVED,USER_FOUND,GDRIVE_CHECK decisionNode
    class REG_ERROR_INVALID,LOGIN_ERROR_INVALID,FOLDER_MISSING,FILE_NOT_FOUND,OAUTH_DENIED,EMAIL_FAILED errorNode
    class LOGIN_SUCCESS,REG_SUCCESS,BOOK_DELIVERY,VERIFY_SUCCESS,OAUTH_SUCCESS,GDRIVE_CONFIGURED successNode
    class REG_WARNING,EMAIL_ISSUES,VERIFY_ERROR,LOGIN_ERROR_UNVERIFIED warningNode
    class DASHBOARD,SEARCH_RESULTS,BROWSE_RESULTS,USER_PROFILE infoNode
```

## 🎯 **Symbol Legend:**

| Symbol | Meaning          | Example                        |
| ------ | ---------------- | ------------------------------ |
| 👤     | User/Person      | User actions, profile          |
| 📧     | Email            | Email address, verification    |
| 🔐     | Security/Auth    | Passwords, tokens, locks       |
| 📚     | Books/Library    | Book access, library content   |
| 🌐     | Web/Network      | URLs, OAuth, web requests      |
| ✅      | Success          | Successful operations          |
| ❌      | Error            | Failed operations              |
| ⚠️     | Warning          | Partial success, warnings      |
| 🔄     | Process/Loop     | Retry, refresh, process        |
| 📤     | Send/Submit      | Form submissions, API calls    |
| 📥     | Receive          | Responses, data retrieval      |
| 🎯     | Action/Choice    | User decisions, selections     |
| ⏰      | Time             | Timestamps, expiration, delays |
| 🔍     | Search/Find      | Search operations, lookups     |
| 💾     | Database         | Data storage, persistence      |
| 🎫     | Token            | Session tokens, verification   |
| 📁     | Folder/Directory | File system, organization      |
| 🔗     | Link/URL         | Web links, API endpoints       |

## 🔥 **Critical Decision Points:**

1. **🔐 Authentication Choice** - Register vs Login vs OAuth
2. **📧 Email Verification** - Success vs Failure vs Recovery
3. **🌐 Google Drive Setup** - Accept vs Deny vs Error
4. **📁 Library Folder** - Exists vs Missing vs Creation
5. **📚 Book File** - Found vs Not Found vs Upload

## ⚡ **High-Risk Failure Paths:**

- **Red Nodes**: Complete blockers requiring user action
- **Orange Nodes**: Warnings that allow partial functionality  
- **Blue Nodes**: Information flows that continue normally
- **Green Nodes**: Success states that enable full functionality

This visual chart makes it easy to trace any user path and identify where interventions might be needed to improve the user experience.