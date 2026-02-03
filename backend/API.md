Here is the complete API documentation based on your code.

Here is the complete API documentation for the **User Authentication & Profile** endpoints.

---

### **4. User Authentication & Profile Endpoints**

#### **Register New User**

* **URL:** `/auth/register/`
* **Method:** `POST`
* **Auth:** Public (`AllowAny`)

**Request Body:**

```json
{
    "email": "jane@example.com",
    "password": "securepassword123",
    "first_name": "Jane",
    "last_name": "Doe",
    "role": "USER"  // Optional. Default is "USER". Options: "ADMIN", "USER"
}

```

**Response (201 Created):**

```json
{
    "message": "User registered successfully",
    "user": {
        "email": "jane@example.com",
        "role": "USER"
    }
}

```

---

#### **Login (Get Token)**

* **URL:** `/auth/login/`
* **Method:** `POST`
* **Auth:** Public (`AllowAny`)

**Request Body:**

```json
{
    "email": "jane@example.com",
    "password": "securepassword123"
}

```

**Response (200 OK):**
Returns the JWT tokens along with user information (customized response).

```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
    "user_id": 1,
    "email": "jane@example.com",
    "role": "USER",
    "name": "Jane"
}

```

---

#### **Refresh Access Token**

* **URL:** `/auth/refresh/`
* **Method:** `POST`
* **Auth:** Public (`AllowAny`)
* **Description:** Use this when the `access` token expires to get a new one without logging in again.

**Request Body:**

```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}

```

**Response (200 OK):**

```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}

```

---

#### **Get / Update Current User Profile**

* **URL:** `/auth/me/`
* **Methods:** `GET`, `PUT`, `PATCH`
* **Auth:** Required (Token)

**GET /auth/me/**
Retrieves the logged-in user's details.

* **Response:**
```json
{
    "id": 1,
    "email": "jane@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "full_name": "Jane Doe",
    "role": "USER",
    "eco_points": 0
}

```



**PATCH /auth/me/**
Updates specific fields for the logged-in user. (Note: `email`, `role`, and `eco_points` are read-only).

* **Request Body:**
```json
{
    "first_name": "Janet"
}

```


* **Response:** Returns the updated user object.

### **1. Organization Endpoints**

#### **List / Create Organizations**

* **URL:** `/organizations/`
* **Methods:** `GET`, `POST`

---

**GET /organizations/**
Retrieves a list of all organizations. The response is **deeply nested**, including all Zones belonging to the Organization, and all Cameras belonging to those Zones.

* **Response Body (JSON):**
```json
[
    {
        "id": 1,
        "name": "Tech Corp HQ",
        "org_type": "Corporate",
        "total_capacity": 500,
        "latitude": "34.052200",
        "longitude": "-118.243700",
        "zones": [
            {
                "id": 10,
                "name": "Lobby",
                "zone_type": "Entrance",
                "cameras": [
                    {
                        "id": 101,
                        "name": "Front Desk Cam",
                        "is_active": true
                    }
                ]
            }
        ]
    }
]

```



---

**POST /organizations/**
Creates a new Organization.

* **Request Body (JSON):**
```json
{
    "name": "New Warehouse",
    "org_type": "Logistics",
    "total_capacity": 1000,
    "latitude": 40.7128,
    "longitude": -74.0060
}

```


* **Response Body (JSON):**
*Returns the created object (same structure as GET, but `zones` will be empty initially).*

---

#### **Retrieve / Update / Delete Organization**

* **URL:** `/organizations/<id>/`
* **Methods:** `GET`, `PUT`, `DELETE`

**GET /organizations/<id>/**

* **Response:** Single Organization object with nested zones and cameras.

**PUT /organizations/<id>/**
Updates organization details.

* **Request Body:** (Same as POST, fields are optional for partial updates)
* **Response:** Updated object.

**DELETE /organizations/<id>/**

* **Response:** `204 No Content`

---

### **2. Zone Endpoints**

#### **List / Create Zones**

* **URL:** `/zones/`
* **Methods:** `GET`, `POST`
* **Query Params (GET):** `?org_id=<id>` (Optional: Filter zones by Organization ID)

---

**GET /zones/**
Retrieves a list of zones. Includes the parent **Organization** info and child **Cameras**.

* **Response Body (JSON):**
```json
[
    {
        "id": 10,
        "name": "Lobby",
        "zone_type": "Entrance",
        "capacity": 50,
        "latitude": "34.052200",
        "longitude": "-118.243700",
        "organization": {
            "id": 1,
            "name": "Tech Corp HQ",
            "org_type": "Corporate"
        },
        "cameras": [
            {
                "id": 101,
                "name": "Front Desk Cam",
                "is_active": true
            }
        ]
    }
]

```



---

**POST /zones/**
Creates a new Zone. You must provide the `organization_id` to link it to a parent.

* **Request Body (JSON):**
```json
{
    "name": "Server Room",
    "zone_type": "Restricted",
    "capacity": 5,
    "latitude": 34.0522,
    "longitude": -118.2437,
    "organization_id": 1
}

```


* **Response Body (JSON):**
*Returns the created zone object.*

---

#### **Retrieve / Update / Delete Zone**

* **URL:** `/zones/<id>/`
* **Methods:** `GET`, `PUT`, `DELETE`

**GET /zones/<id>/**

* **Response:** Single Zone object with nested Organization and Cameras.

**PUT /zones/<id>/**

* **Request Body:** (Same as POST, fields optional).
* **Response:** Updated object.

**DELETE /zones/<id>/**

* **Response:** `204 No Content`

---

### **3. Camera Endpoints**

#### **List / Create Cameras**

* **URL:** `/cameras/`
* **Methods:** `GET`, `POST`
* **Query Params (GET):** `?zone_id=<id>` (Optional: Filter cameras by Zone ID)

---

**GET /cameras/**
Retrieves a list of cameras. Includes the parent **Zone**, which includes the grandparent **Organization**.

* **Response Body (JSON):**
```json
[
    {
        "id": 101,
        "name": "Front Desk Cam",
        "is_active": true,
        "created_at": "2024-02-14T12:00:00Z",
        "zone": {
            "id": 10,
            "name": "Lobby",
            "zone_type": "Entrance",
            "organization": {
                "id": 1,
                "name": "Tech Corp HQ",
                "org_type": "Corporate"
            }
        }
    }
]

```



---

**POST /cameras/**
Creates a new Camera. You must provide the `zone_id`.

* **Request Body (JSON):**
```json
{
    "name": "Back Door Cam",
    "is_active": true,
    "zone_id": 10
}

```


* **Response Body (JSON):**
*Returns the created camera object.*

---

#### **Retrieve / Update / Delete Camera**

* **URL:** `/cameras/<id>/`
* **Methods:** `GET`, `PUT`, `DELETE`

**GET /cameras/<id>/**

* **Response:** Single Camera object with nested Zone/Organization.

**PUT /cameras/<id>/**

* **Request Body:** (Same as POST).
* **Response:** Updated object.

**DELETE /cameras/<id>/**

* **Response:** `204 No Content`


Here is the complete API documentation for the **Alerts**, **Notifications**, and **Sensor/Carbon** endpoints.

---

### **1. Alert Endpoints**

#### **List & Create Alerts**

* **URL:** `/alerts/`
* **Methods:** `GET`, `POST`
* **Auth:** Required (Token)

**GET /alerts/**
Retrieves a list of all alerts. You can filter by status using query parameters.

* **Query Params:** `?status=OPEN` or `?status=CLOSED` or `?org_id=organization_id`
* **Response:**
```json
[
    {
        "id": 1,
        "heading": "Overcrowding in Main Hall",
        "sub_heading": "Detected 120/100 people. (Cam: 101)",
        "status": "OPEN",
        "created_at": "2026-02-02T10:30:00Z",
        "updated_at": "2026-02-02T10:30:00Z"
    }
]

```



**POST /alerts/**
Manually create a new alert.

* **Request Body:**
```json
{
    "heading": "Fire Drill",
    "sub_heading": "Scheduled drill at 2 PM.",
    "status": "OPEN"
}

```


* **Response:** Returns the created alert object.

---

#### **Retrieve, Update & Delete Alert**

* **URL:** `/alerts/<id>/`
* **Methods:** `GET`, `PUT`, `DELETE`
* **Auth:** Required (Token)

**GET /alerts/<id>/**

* **Response:** Single Alert object.

**PUT /alerts/<id>/**
Update an alert (e.g., to close it).

* **Request Body:**
```json
{
    "status": "CLOSED"
}

```


* **Response:** Updated Alert object.

**DELETE /alerts/<id>/**

* **Response:** `204 No Content`

---

### **2. Notification Endpoints**

#### **Broadcast & List Notifications**

* **URL:** `/notifications/`
* **Methods:** `GET`, `POST`
* **Auth:** Required (Token)

**GET /notifications/**
Retrieves the list of broadcast messages sent to all users.

* **Response:**
```json
[
    {
        "id": 5,
        "title": "System Maintenance",
        "message": "Servers will restart in 10 mins.",
        "created_at": "2026-02-02T11:00:00Z"
    }
]

```



**POST /notifications/**
Broadcasts a new message to **ALL** users.

* **Request Body:**
```json
{
    "title": "Welcome",
    "message": "Welcome to the EcoFlow system."
}

```


* **Response:** Returns the created notification.

---

#### **Delete Notification**

* **URL:** `/notifications/<id>/`
* **Methods:** `GET`, `DELETE`
* **Auth:** Required (Token)

**DELETE /notifications/<id>/**
Deletes a specific broadcast message.

* **Response:** `204 No Content`

---

### **3. Sensor & Carbon Endpoints**

#### **Sensor Detection (The Main Logic)**

* **URL:** `/sensor/detect/`
* **Method:** `POST`
* **Auth:** Public (`AllowAny`) or Token (depending on settings)
* **Content-Type:** `multipart/form-data`

**Description:**

1. Uploads image to Crowd API to count people (`sahi_count`).
2. If count ≥ 90% of Zone Capacity: Creates an **Alert** and stops.
3. If Safe: Sends image to **Gemini API** to count again, then calculates Carbon Saved using formula: `sahi_count / gemini_count`.

**Request Body (Form Data):**

* `zone_id`: (Integer) ID of the zone.
* `camera_id`: (Integer) ID of the camera.
* `file`: (File) The image file to analyze.

**Response (Scenario A: Normal / Safe)**

```json
{
    "zone": "Lobby",
    "capacity": 100,
    "detected_people": 20,
    "occupancy_percentage": "20.0%",
    "status": "NORMAL",
    "carbon_data": {
        "filename": "capture.jpg",
        "sahi_count": 20,
        "gemini_count": 25,
        "calculation_result": 0.8,
        "formula": "20 / 25 rounded",
        "message": "Prediction successful via Gemini API"
    },
    "alert_created": false
}

```

**Response (Scenario B: Danger / Overcrowded)**

```json
{
    "zone": "Lobby",
    "capacity": 100,
    "detected_people": 95,
    "occupancy_percentage": "95.0%",
    "status": "DANGER",
    "alert_created": true,
    "carbon_message": "Skipped Gemini calculation due to overcrowding."
}

```

---

#### **Get Carbon Statistics**

* **URL:** `/carbon/stats/`
* **Method:** `GET`
* **Auth:** Public (`AllowAny`) or Token

**Description:**
Retrieves the total and average carbon saved. Optional filtering by zone.

**Query Params:**

* `?zone_id=1` (Optional: Get stats for a specific zone only)

**Response:**

```json
{
    "summary": {
        "total_saved_all_time": 150.5,
        "average_per_detection": 0.85
    },
    "recent_history": [
        {
            "zone": "Lobby",
            "saved": 0.8,
            "date": "2026-02-02 12:00"
        },
        {
            "zone": "Main Hall",
            "saved": 1.2,
            "date": "2026-02-02 11:45"
        }
    ]
}

```

---

### **4. System Endpoints**

These are likely located under your `/api/` prefix based on the `include` statement.

#### **System Status**

* **URL:** `/api/status/` (Assumed based on view name `system_status`)
* **Method:** `GET`
* **Auth:** `AllowAny` (No token required)
* **Response Body (JSON):**
```json
{
    "status": "OK",
    "message": "Ecoflow system is operational."
}

```



#### **System Health**

* **URL:** `/api/health/` (Assumed based on view name `system_health`)
* **Method:** `GET`
* **Auth:** `AllowAny`
* **Description:** Checks Database connection and external services.
* **Response Body (Success - 200 OK):**
```json
{
    "overall_status": "OK",
    "database": "OK",
    "external_service": "OK"
}

```


* **Response Body (Failure - 503 Service Unavailable):**
```json
{
    "overall_status": "DEGRADED",
    "database": "DOWN",
    "external_service": "OK"
}

```