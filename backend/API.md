Here is the complete API documentation based on your code.

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