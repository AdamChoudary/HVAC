"""
Scott Valley HVAC Business Data Configuration.
Contains static data for service areas, pricing, and staff.
"""
from typing import List, Dict, TypedDict

# --- Service Area Configuration ---

# Primary service area: 20-25 mile radius from 3353 Belvedere St NW, Salem, OR 97304
# Plus specific cities northward.
SERVICE_AREA_CONFIG = {
    "primary_zip_codes": [
        # Salem
        "97301", "97302", "97303", "97304", "97305", "97306", "97317",
        # Keizer
        "97303", "97307",
        # West: Independence, Monmouth, Dallas, Rickreall, Willamina, Sheridan
        "97351", "97361", "97338", "97371", "97396", "97378",
        # South: Jefferson, Millersburg
        "97352", "97321",
        # East: Turner, Aumsville, Sublimity, Stayton, Silverton
        "97392", "97325", "97385", "97383", "97381",
        # North: McMinnville, Amity, Dayton, Lafayette, Newberg, Brooks, Gervais, Woodburn, Hubbard
        "97128", "97101", "97114", "97127", "97132", "97305", "97026", "97071", "97032",
        # Portland & Surrounding (Extended Area)
        "97201", "97202", "97203", "97204", "97205", "97206", "97209", "97210", 
        "97211", "97212", "97213", "97214", "97215", "97216", "97217", "97218", 
        "97219", "97220", "97221", "97222", "97223", "97224", "97225", "97227", 
        "97229", "97230", "97231", "97232", "97233", "97236", "97239", "97266", 
        "97267", "97005", "97006", "97007", "97008", "97015", "97027", "97030", 
        "97034", "97035", "97045", "97060", "97062", "97068", "97080", "97086", 
        "97089", "97267",
        # Albany, Corvallis, Eugene (Extended South)
        "97321", "97322", "97330", "97331", "97333", "97401", "97402", "97403", 
        "97404", "97405", "97408"
    ],
    "extended_cities": [
        "Portland", "Albany", "Eugene", "Corvallis", "Salem", "Keizer", 
        "Independence", "Monmouth", "Dallas", "Rickreall", "Willamina", "Sheridan",
        "Jefferson", "Millersburg", "Turner", "Aumsville", "Sublimity", "Stayton", "Silverton",
        "McMinnville", "Amity", "Dayton", "Lafayette", "Newberg", "Brooks", "Gervais", "Woodburn", "Hubbard"
    ]
}

# --- Pricing Configuration ---

PRICING_CONFIG = {
    "diagnostics": {
        "residential": 190,
        "commercial": 240,
    },
    "fees": {
        "weekend_surcharge": 50,
        "emergency_surcharge": 55,
        "commute_hazard": 40, # Example from docs
    },
    "discounts": {
        "standard_tier": 0.10, # 10% for Senior, Veteran, Educator, First Responder
        "stacked_tier_2": 0.14, # ~14% for 2 qualifiers
        "stacked_tier_3": 0.16, # Max 16% ceiling
    }
}

# --- Staff Directory ---

class StaffMember(TypedDict):
    name: str
    role: str
    phone: str
    email: str
    can_transfer: bool

STAFF_DIRECTORY: Dict[str, StaffMember] = {
    "scott": {
        "name": "Scott",
        "role": "CEO/President",
        "phone": "+15034772696", # Forwarded from 971-712-6763
        "email": "vvhvac.nw@gmail.com",
        "can_transfer": True
    },
    "austin": {
        "name": "Austin",
        "role": "COO/Site Manager",
        "phone": "+15034374134",
        "email": "austin.vvhvac@gmail.com",
        "can_transfer": True
    },
    "david": {
        "name": "David",
        "role": "Technician",
        "phone": "", # No published number yet, placeholder
        "email": "david.vvhvac@gmail.com",
        "can_transfer": False # Cannot transfer to him yet
    }
}
