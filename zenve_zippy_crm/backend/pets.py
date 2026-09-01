import fastapi
import fastapi.middleware.cors
import sqlalchemy.engine
import pydantic
import sqlalchemy
import sqlalchemy.orm
from typing import Optional
from datetime import datetime,date,time
from zoneinfo import ZoneInfo

DATABASE_URL = sqlalchemy.engine.URL.create(
    drivername="mysql+pymysql",
    username="root",
    password="root",
    host="localhost",
    port=3306,
    database="pet_management",
)
engine = sqlalchemy.create_engine( DATABASE_URL,echo=True,pool_pre_ping=True)
SessionLocal = sqlalchemy.orm.sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = sqlalchemy.orm.declarative_base()
app = fastapi.FastAPI(title= "Pet Management API",version= "1.0.0")

app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins= ["http://localhost:5173", 
        "http://127.0.0.1:5173", 
        "http://localhost:3000",
        "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def yes_no_to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value = value.strip().lower()
        if value == "yes":
            return True
        if value == "no":
            return False
    raise fastapi.HTTPException(status_code=422,detail="Value must be Yes or No")
def model_response(obj):
    data = {
        key: value
        for key, value in obj.__dict__.items()
        if key != "_sa_instance_state"
    }
    if "is_active" in data:
        data["is_active"] = "Yes" if data["is_active"] else "No"
    return data
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
class PetParent(Base):
    __tablename__ = "pet_parents"
    id = sqlalchemy.Column(sqlalchemy.Integer , primary_key= True , index = True)
    full_name = sqlalchemy.Column(sqlalchemy.String(150), nullable = False)
    email = sqlalchemy.Column(sqlalchemy.String(100) , unique = True, nullable =False)
    phone = sqlalchemy.Column(sqlalchemy.String(30))
    city = sqlalchemy.Column(sqlalchemy.String(150))
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class Pet(Base):
    __tablename__ = "pets"
    id = sqlalchemy.Column(sqlalchemy.Integer,primary_key= True , index=True)
    parent_id = sqlalchemy.Column(sqlalchemy.Integer,sqlalchemy.ForeignKey("pet_parents.id"),nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String(100),nullable = False)
    species = sqlalchemy.Column(sqlalchemy.String(100))
    breed = sqlalchemy.Column(sqlalchemy.String(100))
    gender = sqlalchemy.Column(sqlalchemy.String(20))
    weight_kg = sqlalchemy.Column(sqlalchemy.Float)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean,default = True)
class MedicalRecord(Base):
    __tablename__ = "medical_records"
    id = sqlalchemy.Column(sqlalchemy.Integer , primary_key = True , index=True)
    pet_id = sqlalchemy.Column(sqlalchemy.Integer,sqlalchemy.ForeignKey("pets.id"),nullable=False)
    record_type = sqlalchemy.Column(sqlalchemy.String(100))
    title = sqlalchemy.Column(sqlalchemy.String(200))
    diagnosis = sqlalchemy.Column(sqlalchemy.String(500))
    record_date = sqlalchemy.Column(sqlalchemy.Date)
class Vaccination(Base):
    __tablename__ = "vaccinations"
    id=sqlalchemy.Column(sqlalchemy.Integer,primary_key=True , index=True)
    pet_id = sqlalchemy.Column(sqlalchemy.Integer,sqlalchemy.ForeignKey("pets.id"),nullable=False)
    vaccine_name = sqlalchemy.Column(sqlalchemy.String(200))
    administered_on = sqlalchemy.Column(sqlalchemy.Date)
    next_due_on = sqlalchemy.Column(sqlalchemy.Date)
    batch_number =sqlalchemy.Column(sqlalchemy.String(100))
class Address(Base):
    __tablename__ = "addresses"
    id = sqlalchemy.Column(sqlalchemy.Integer,primary_key=True , index=True)
    parent_id = sqlalchemy.Column(sqlalchemy.Integer,sqlalchemy.ForeignKey("pet_parents.id"),nullable=False)
    label = sqlalchemy.Column(sqlalchemy.String(100))
    contact_name = sqlalchemy.Column(sqlalchemy.String(150))
    line1 = sqlalchemy.Column(sqlalchemy.String(300))
    city = sqlalchemy.Column(sqlalchemy.String(100))
    pincode = sqlalchemy.Column(sqlalchemy.String(20))
    is_default =sqlalchemy.Column(sqlalchemy.Boolean,default=True)
class UserRole(Base):
    __tablename__ = "user_roles"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    role = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class Doctor(Base):
    __tablename__ = "doctors"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String(150), nullable=False)
    qualification = sqlalchemy.Column(sqlalchemy.String(300))
    specializations = sqlalchemy.Column(sqlalchemy.String(500))
    pincode = sqlalchemy.Column(sqlalchemy.String(20))
    experience_years = sqlalchemy.Column(sqlalchemy.Integer)
    consultation_fee = sqlalchemy.Column(sqlalchemy.Float)
    rating = sqlalchemy.Column(sqlalchemy.Float)
    verification_status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
class ClinicHospital(Base):
    __tablename__ = "clinics_hospitals"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)
    facility_type = sqlalchemy.Column(sqlalchemy.String(100))
    phone = sqlalchemy.Column(sqlalchemy.String(30))
    emergency_available = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    open_24x7 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    verification_status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
    rating = sqlalchemy.Column(sqlalchemy.Float)
class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    doctor_id = sqlalchemy.Column(sqlalchemy.Integer,sqlalchemy.ForeignKey("doctors.id"),nullable=False)
    day_of_week = sqlalchemy.Column(sqlalchemy.String(20), nullable=False)
    start_time = sqlalchemy.Column(sqlalchemy.Time, nullable=False)
    end_time = sqlalchemy.Column(sqlalchemy.Time, nullable=False)
    consultation_type = sqlalchemy.Column(sqlalchemy.String(100))
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
class DoctorDocument(Base):
    __tablename__ = "doctor_documents"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    doctor_id = sqlalchemy.Column(sqlalchemy.Integer,sqlalchemy.ForeignKey("doctors.id"),nullable=False)
    document_type = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class Appointment(Base):
    __tablename__ = "appointments"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    pet_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("pets.id"), nullable=False)
    doctor_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("doctors.id"), nullable=False)
    appointment_date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    appointment_time = sqlalchemy.Column(sqlalchemy.Time, nullable=False)
    appointment_type = sqlalchemy.Column(sqlalchemy.String(100))
    status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
    payment_status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
    consultation_fee = sqlalchemy.Column(sqlalchemy.Float, default=0)
class Consultation(Base):
    __tablename__ = "consultations"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    appointment_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("appointments.id"), nullable=False)
    consultation_mode = sqlalchemy.Column(sqlalchemy.String(100))
    diagnosis = sqlalchemy.Column(sqlalchemy.String(500))
    follow_up_date = sqlalchemy.Column(sqlalchemy.Date)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class Prescription(Base):
    __tablename__ = "prescriptions"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    doctor_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("doctors.id"), nullable=False)
    pet_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("pets.id"), nullable=False)
    valid_until = sqlalchemy.Column(sqlalchemy.Date)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class ServiceProvider(Base):
    __tablename__ = "service_providers"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String(150), nullable=False)
    provider_type = sqlalchemy.Column(sqlalchemy.String(100))
    phone = sqlalchemy.Column(sqlalchemy.String(30))
    verification_status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
    rating = sqlalchemy.Column(sqlalchemy.Float)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
class Service(Base):
    __tablename__ = "services"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    title = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)
    service_type = sqlalchemy.Column(sqlalchemy.String(100))
    price = sqlalchemy.Column(sqlalchemy.Float, default=0)
    duration_minutes = sqlalchemy.Column(sqlalchemy.Integer)
    home_service = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
class ServiceBooking(Base):
    __tablename__ = "service_bookings"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    service_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("services.id"), nullable=False)
    provider_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("service_providers.id"), nullable=False)
    pet_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("pets.id"), nullable=False)
    booking_date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    booking_time = sqlalchemy.Column(sqlalchemy.Time, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Float, default=0)
    status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
    payment_status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
class Product(Base):
    __tablename__ = "products"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Float, default=0)
    mrp = sqlalchemy.Column(sqlalchemy.Float, default=0)
    discount_percent = sqlalchemy.Column(sqlalchemy.Float, default=0)
    pincode = sqlalchemy.Column(sqlalchemy.String(20))
    stock_quantity = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    is_prescription_required = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    rating = sqlalchemy.Column(sqlalchemy.Float)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
class Inventory(Base):
    __tablename__ = "inventory"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    product_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("products.id"), nullable=False)
    seller_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("seller_stores.id"), nullable=False)
    pincode = sqlalchemy.Column(sqlalchemy.String(20))
    inventory_source = sqlalchemy.Column(sqlalchemy.String(100))
    available_quantity = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    reserved_quantity = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    reorder_level = sqlalchemy.Column(sqlalchemy.Integer, default=0)
class Category(Base):
    __tablename__ = "categories"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String(150), nullable=False)
    slug = sqlalchemy.Column(sqlalchemy.String(200), unique=True)
    sort_order = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
class Brand(Base):
    __tablename__ = "brands"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String(150), nullable=False)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class SellerStore(Base):
    __tablename__ = "seller_stores"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    business_name = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)
    seller_type = sqlalchemy.Column(sqlalchemy.String(100))
    phone = sqlalchemy.Column(sqlalchemy.String(30))
    commission_rate = sqlalchemy.Column(sqlalchemy.Float, default=0)
    verification_status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
    rating = sqlalchemy.Column(sqlalchemy.Float)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
class Warehouse(Base):
    __tablename__ = "warehouses"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)
    seller_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("seller_stores.id"), nullable=False)
    is_zenve_owned = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    contact_phone = sqlalchemy.Column(sqlalchemy.String(30))
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
class Cart(Base):
    __tablename__ = "carts"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
    updated_at =sqlalchemy.Column(sqlalchemy.DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None),
    onupdate=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class CartItem(Base):
    __tablename__ = "cart_items"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    cart_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("carts.id"), nullable=False)
    product_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("products.id"), nullable=False)
    quantity = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    price = sqlalchemy.Column(sqlalchemy.Float, default=0)
    saved_for_later = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
class Order(Base):
    __tablename__ = "orders"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    order_number = sqlalchemy.Column(sqlalchemy.String(100), unique=True, nullable=False)
    total_amount = sqlalchemy.Column(sqlalchemy.Float, default=0)
    status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
    payment_status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
    placed_at = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.utcnow)
class OrderItem(Base):
    __tablename__ = "order_items"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("orders.id"), nullable=False)
    product_name = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)
    quantity = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    unit_price = sqlalchemy.Column(sqlalchemy.Float, default=0)
    total_price = sqlalchemy.Column(sqlalchemy.Float, default=0)
    status = sqlalchemy.Column(sqlalchemy.String(50), default="CONFIRMED")
class Delivery(Base):
    __tablename__ = "deliveries"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("orders.id"), nullable=False)
    tracking_number = sqlalchemy.Column(sqlalchemy.String(150))
    status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
    estimated_delivery = sqlalchemy.Column(sqlalchemy.Date)
    delivered_at = sqlalchemy.Column(sqlalchemy.DateTime)
class Payment(Base):
    __tablename__ = "payments"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("orders.id"), nullable=False)
    amount = sqlalchemy.Column(sqlalchemy.Float, default=0)
    gateway = sqlalchemy.Column(sqlalchemy.String(100))
    status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
    webhook_verified = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class Refund(Base):
    __tablename__ = "refunds"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    payment_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("payments.id"), nullable=False)
    amount = sqlalchemy.Column(sqlalchemy.Float, default=0)
    reason = sqlalchemy.Column(sqlalchemy.String(500))
    status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class Payout(Base):
    __tablename__ = "payouts"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    payee_type = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    payee_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    amount = sqlalchemy.Column(sqlalchemy.Float, default=0)
    commission_amount = sqlalchemy.Column(sqlalchemy.Float, default=0)
    status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
class CommissionRule(Base):
    __tablename__ = "commission_rules"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    scope = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    percentage = sqlalchemy.Column(sqlalchemy.Float, default=0)
    fixed_fee = sqlalchemy.Column(sqlalchemy.Float, default=0)
    effective_from = sqlalchemy.Column(sqlalchemy.Date)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
class GPSLocation(Base):
    __tablename__ = "gps_locations"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    entity_type = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    city = sqlalchemy.Column(sqlalchemy.String(150))
    address = sqlalchemy.Column(sqlalchemy.String(300))
    latitude = sqlalchemy.Column(sqlalchemy.Float)
    longitude = sqlalchemy.Column(sqlalchemy.Float)
    service_radius_km = sqlalchemy.Column(sqlalchemy.Float, default=0)
    is_primary = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
class Review(Base):
    __tablename__ = "reviews"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    target_type = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    rating = sqlalchemy.Column(sqlalchemy.Float)
    review_text = sqlalchemy.Column(sqlalchemy.String(1000))
    status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class Notification(Base):
    __tablename__ = "notifications"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    event_type = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)
    channel = sqlalchemy.Column(sqlalchemy.String(100))
    is_read = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class MembershipPlan(Base):
    __tablename__ = "membership_plans"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String(150), nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Float, default=0)
    duration_days = sqlalchemy.Column(sqlalchemy.Integer)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
class PlanBenefit(Base):
    __tablename__ = "plan_benefits"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    plan_id = sqlalchemy.Column(sqlalchemy.Integer,sqlalchemy.ForeignKey("membership_plans.id"),nullable=False)
    benefit = sqlalchemy.Column(sqlalchemy.String(300), nullable=False)
    value = sqlalchemy.Column(sqlalchemy.String(300))
class Membership(Base):
    __tablename__ = "memberships"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    plan_id = sqlalchemy.Column(sqlalchemy.Integer,sqlalchemy.ForeignKey("membership_plans.id"),nullable=False)
    started_on = sqlalchemy.Column(sqlalchemy.Date)
    expires_on = sqlalchemy.Column(sqlalchemy.Date)
    status = sqlalchemy.Column(sqlalchemy.String(50), default="active")
class SupportTicket(Base):
    __tablename__ = "support_tickets"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    subject = sqlalchemy.Column(sqlalchemy.String(300), nullable=False)
    category = sqlalchemy.Column(sqlalchemy.String(100))
    status = sqlalchemy.Column(sqlalchemy.String(50), default="open")
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class GeocodingCache(Base):
    __tablename__ = "geocoding_cache"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    query = sqlalchemy.Column(sqlalchemy.String(500), nullable=False)
    latitude = sqlalchemy.Column(sqlalchemy.Float)
    longitude = sqlalchemy.Column(sqlalchemy.Float)
    formatted_address = sqlalchemy.Column(sqlalchemy.String(500))
class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    action = sqlalchemy.Column(sqlalchemy.String(100), nullable=False)
    entity_type = sqlalchemy.Column(sqlalchemy.String(100))
    entity_id = sqlalchemy.Column(sqlalchemy.Integer)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class SalesExecutive(Base):
    __tablename__ = "sales_executives"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String(150), nullable=False)
    code = sqlalchemy.Column(sqlalchemy.String(100), unique=True, nullable=False)
    phone = sqlalchemy.Column(sqlalchemy.String(30))
    email = sqlalchemy.Column(sqlalchemy.String(100))
    region = sqlalchemy.Column(sqlalchemy.String(150))
    city = sqlalchemy.Column(sqlalchemy.String(150))
    monthly_target = sqlalchemy.Column(sqlalchemy.Float, default=0)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
class PincodeCoverage(Base):
    __tablename__ = "pincode_coverages"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    executive_id = sqlalchemy.Column(sqlalchemy.Integer,sqlalchemy.ForeignKey("sales_executives.id"),nullable=False)
    pincode = sqlalchemy.Column(sqlalchemy.String(20), nullable=False)
    city = sqlalchemy.Column(sqlalchemy.String(150))
    state = sqlalchemy.Column(sqlalchemy.String(150))
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
class ExecutiveTask(Base):
    __tablename__ = "executive_tasks"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    title = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)
    task_type = sqlalchemy.Column(sqlalchemy.String(100))
    entity_type = sqlalchemy.Column(sqlalchemy.String(100))
    pincode = sqlalchemy.Column(sqlalchemy.String(20))
    priority = sqlalchemy.Column(sqlalchemy.String(50))
    status = sqlalchemy.Column(sqlalchemy.String(50), default="pending")
    due_date = sqlalchemy.Column(sqlalchemy.Date)
class ExecutiveAlert(Base):
    __tablename__ = "executive_alerts"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    title = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)
    severity = sqlalchemy.Column(sqlalchemy.String(50))
    entity_type = sqlalchemy.Column(sqlalchemy.String(100))
    pincode = sqlalchemy.Column(sqlalchemy.String(20))
    is_read = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime,default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None))
Base.metadata.create_all(bind=engine)
class PetParentCreate(pydantic.BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    city: Optional[str] = None
class PetParentResponse(PetParentCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
class PetCreate(pydantic.BaseModel):
    parent_id: int
    name :str
    species: Optional[str] = None
    breed :Optional[str]=None
    gender: Optional[str] = None
    weight_kg: Optional[float] = None
    is_active: str = "Yes"
class PetResponse(pydantic.BaseModel):
    id:int
    class Config:
        from_attributes = True
class MedicalRecordCreate(pydantic.BaseModel):
    pet_id: int
    record_type: Optional[str] = None
    title: Optional[str] = None
    diagnosis: Optional[str] = None
    record_date: Optional[date] = None
class VaccinationCreate(pydantic.BaseModel):
    pet_id: int
    vaccine_name: str
    administered_on: Optional[date] = None
    next_due_on: Optional[date] = None
    batch_number: Optional[str] = None
class AddressCreate(pydantic.BaseModel):
    parent_id: int
    label: Optional[str] = None
    contact_name: Optional[str] = None
    line1: Optional[str] = None
    city: Optional[str] = None
    pincode: Optional[str] = None
    is_default: bool = False
class UserRoleCreate(pydantic.BaseModel):
    user_id: int
    role: str
class DoctorCreate(pydantic.BaseModel):
    name: str
    qualification: Optional[str] = None
    specializations: Optional[str] = None
    pincode: Optional[str] = None
    experience_years: Optional[int] = None
    consultation_fee: Optional[float] = None
    rating: Optional[float] = None
    verification_status: str = "pending"
    is_active: str = "Yes"
class ClinicHospitalCreate(pydantic.BaseModel):
    name: str
    facility_type: Optional[str] = None
    phone: Optional[str] = None
    emergency_available: bool = False
    open_24x7: bool = False
    verification_status: str = "pending"
    rating: Optional[float] = None
class AvailabilitySlotCreate(pydantic.BaseModel):
    doctor_id: int
    day_of_week: str
    start_time: time
    end_time: time
    consultation_type: Optional[str] = None
    is_active: str = "Yes"
class DoctorDocumentCreate(pydantic.BaseModel):
    doctor_id: int
    document_type: str
    status: str = "pending"
class AppointmentCreate(pydantic.BaseModel):
    pet_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    appointment_type: Optional[str] = None
    status: str = "pending"
    payment_status: str = "pending"
    consultation_fee: Optional[float] = 0
class ConsultationCreate(pydantic.BaseModel):
    appointment_id: int
    consultation_mode: Optional[str] = None
    diagnosis: Optional[str] = None
    follow_up_date: Optional[date] = None
class PrescriptionCreate(pydantic.BaseModel):
    doctor_id: int
    pet_id: int
    valid_until: Optional[date] = None
class ServiceProviderCreate(pydantic.BaseModel):
    name: str
    provider_type: Optional[str] = None
    phone: Optional[str] = None
    verification_status: str = "pending"
    rating: Optional[float] = None
    is_active: str = "Yes"
class ServiceCreate(pydantic.BaseModel):
    title: str
    service_type: Optional[str] = None
    price: Optional[float] = 0
    duration_minutes: Optional[int] = None
    home_service: bool = False
    is_active: str = "Yes"
class ServiceBookingCreate(pydantic.BaseModel):
    service_id: int
    provider_id: int
    pet_id: int
    booking_date: date
    booking_time: time
    price: Optional[float] = 0
    status: str = "pending"
    payment_status: str = "pending"
class ProductCreate(pydantic.BaseModel):
    name: str
    price: Optional[float] = 0
    mrp: Optional[float] = 0
    discount_percent: Optional[float] = 0
    pincode: Optional[str] = None
    stock_quantity: Optional[int] = 0
    is_prescription_required: bool = False
    rating: Optional[float] = None
    is_active: str = "Yes"
class InventoryCreate(pydantic.BaseModel):
    product_id: int
    seller_id: int
    pincode: Optional[str] = None
    inventory_source: Optional[str] = None
    available_quantity: Optional[int] = 0
    reserved_quantity: Optional[int] = 0
    reorder_level: Optional[int] = 0
class CategoryCreate(pydantic.BaseModel):
    name: str
    slug: Optional[str] = None
    sort_order: Optional[int] = 0
    is_active: str = "Yes"
class BrandCreate(pydantic.BaseModel):
    name: str
    is_active: str = "Yes"
class SellerStoreCreate(pydantic.BaseModel):
    business_name: str
    seller_type: Optional[str] = None
    phone: Optional[str] = None
    commission_rate: Optional[float] = 0
    verification_status: str = "pending"
    rating: Optional[float] = None
    is_active: str = "Yes"
class WarehouseCreate(pydantic.BaseModel):
    name: str
    seller_id: int
    is_zenve_owned: bool = False
    contact_phone: Optional[str] = None
    is_active: str = "Yes"
class CartCreate(pydantic.BaseModel):
    user_id: int
class CartItemCreate(pydantic.BaseModel):
    cart_id: int
    product_id: int
    quantity: int = 1
    price: Optional[float] = 0
    saved_for_later: bool = False
class OrderCreate(pydantic.BaseModel):
    order_number: str
    total_amount: Optional[float] = 0
    status: str = "pending"
    payment_status: str = "pending"
class OrderItemCreate(pydantic.BaseModel):
    order_id: int
    product_name: str
    quantity: int = 1
    unit_price: Optional[float] = 0
    total_price: Optional[float] = 0
    status: str = "CONFIRMED"
class DeliveryCreate(pydantic.BaseModel):
    order_id: int
    tracking_number: Optional[str] = None
    status: str = "pending"
    estimated_delivery: Optional[date] = None
    delivered_at: Optional[datetime] = None
class PaymentCreate(pydantic.BaseModel):
    order_id: int
    amount: Optional[float] = 0
    gateway: Optional[str] = None
    status: str = "pending"
    webhook_verified: bool = False
class RefundCreate(pydantic.BaseModel):
    payment_id: int
    amount: Optional[float] = 0
    reason: Optional[str] = None
    status: str = "pending"
class PayoutCreate(pydantic.BaseModel):
    payee_type: str
    payee_id: int
    amount: Optional[float] = 0
    commission_amount: Optional[float] = 0
    status: str = "pending"
class CommissionRuleCreate(pydantic.BaseModel):
    scope: str
    percentage: Optional[float] = 0
    fixed_fee: Optional[float] = 0
    effective_from: Optional[date] = None
    is_active: str = "Yes"
class GPSLocationCreate(pydantic.BaseModel):
    entity_type: str
    city: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    service_radius_km: Optional[float] = 0
    is_primary: bool = False
class ReviewCreate(pydantic.BaseModel):
    target_type: str
    rating: Optional[float] = None
    review_text: Optional[str] = None
    status: str = "pending"
class NotificationCreate(pydantic.BaseModel):
    event_type: str
    title: str
    channel: Optional[str] = None
    is_read: bool = False
class MembershipPlanCreate(pydantic.BaseModel):
    name: str
    price: Optional[float] = 0
    duration_days: Optional[int] = None
    is_active: str = "Yes"
class PlanBenefitCreate(pydantic.BaseModel):
    plan_id: int
    benefit: str
    value: Optional[str] = None
class MembershipCreate(pydantic.BaseModel):
    user_id: int
    plan_id: int
    started_on: Optional[date] = None
    expires_on: Optional[date] = None
    status: str = "active"
class SupportTicketCreate(pydantic.BaseModel):
    subject: str
    category: Optional[str] = None
    status: str = "open"
class GeocodingCacheCreate(pydantic.BaseModel):
    query: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    formatted_address: Optional[str] = None
class AuditLogCreate(pydantic.BaseModel):
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
class SalesExecutiveCreate(pydantic.BaseModel):
    name: str
    code: str
    phone: Optional[str] = None
    email: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    monthly_target: Optional[float] = 0
    is_active: str = "Yes"
class PincodeCoverageCreate(pydantic.BaseModel):
    executive_id: int
    pincode: str
    city: Optional[str] = None
    state: Optional[str] = None
class ExecutiveTaskCreate(pydantic.BaseModel):
    title: str
    task_type: Optional[str] = None
    entity_type: Optional[str] = None
    pincode: Optional[str] = None
    priority: Optional[str] = None
    status: str = "pending"
    due_date: Optional[date] = None
class ExecutiveAlertCreate(pydantic.BaseModel):
    title: str
    severity: Optional[str] = None
    entity_type: Optional[str] = None
    pincode: Optional[str] = None
    is_read: bool = False
@app.get("/")
def home():
    return{"message":"Pet Management API is Running"}
@app.post("/pet-parents")
def create_pet_parent(
    data: PetParentCreate,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    parent = PetParent(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        city=data.city
    )
    db.add(parent)
    db.commit()
    db.refresh(parent)
    return parent
@app.get("/pet-parents")
def get_pet_parent(db:sqlalchemy.orm.Session=fastapi.Depends(get_db)):
    return db.query(PetParent).all()
@app.get("/pet-parents/{parent_id}")
def get_pet_parent(
    parent_id: int,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    parent = db.query(PetParent).filter(PetParent.id == parent_id).first()
    if not parent:
        raise fastapi.HTTPException(status_code=404,detail="Pet parent not found")
    return parent
@app.put("/pet-parents/{parent_id}")
def update_petparent(parent_id: int,data: PetParentCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(PetParent).filter(PetParent.id == parent_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="PetParent not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/pet-parents/{parent_id}")
def delete_petparent(parent_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(PetParent).filter(PetParent.id == parent_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="PetParent not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "PetParent deleted successfully",
            "id": parent_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/pets")
def create_pet(data: PetCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    parent = db.query(PetParent).filter(
        PetParent.id == data.parent_id).first()
    if not parent:
        raise fastapi.HTTPException(status_code=404,detail="Pet parent not found")
    pet = Pet(
        parent_id=data.parent_id,
        name=data.name,
        species=data.species,
        breed=data.breed,
        gender=data.gender,
        weight_kg=data.weight_kg,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return model_response(pet)
@app.get("/pets")
def get_pets(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return [model_response(item) for item in db.query(Pet).all()]
@app.get("/pets/{pet_id}")
def get_pet(pet_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    pet = db.query(Pet).filter(
        Pet.id == pet_id).first()
    if not pet:
        raise fastapi.HTTPException(
            status_code=404,
            detail="Pet not found")
    return model_response(pet)
@app.put("/pets/{pet_id}")
def update_pet(pet_id: int,data: PetCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Pet).filter(Pet.id == pet_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Pet not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/pets/{pet_id}")
def delete_pet(pet_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Pet).filter(Pet.id == pet_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Pet not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Pet deleted successfully",
            "id": pet_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/medical-records")
def create_medical_record(data: MedicalRecordCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    pet = db.query(Pet).filter(
        Pet.id == data.pet_id).first()
    if not pet:
        raise fastapi.HTTPException(status_code=404,detail="Pet not found")
    record = MedicalRecord(
        pet_id=data.pet_id,
        record_type=data.record_type,
        title=data.title,
        diagnosis=data.diagnosis,
        record_date=data.record_date)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
@app.get("/medical-records")
def get_medical_records(
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(MedicalRecord).all()
@app.get("/medical-records/{medical_record_id}")
def get_medical_record_id(medical_record_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == medical_record_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Medical record not found")
    return record
@app.put("/medical-records/{record_id}")
def update_medicalrecord(record_id: int,data: MedicalRecordCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="MedicalRecord not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/medical-records/{record_id}")
def delete_medicalrecord(
    record_id: int,
    db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="MedicalRecord not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "MedicalRecord deleted successfully",
            "id": record_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/vaccinations")
def create_vaccination(data:VaccinationCreate,db: sqlalchemy.orm.Session =fastapi.Depends(get_db)):
    pet = db.query(Pet).filter(
        Pet.id ==data.pet_id).first()
    if not pet:
        raise fastapi.HTTPException(
            status_code=404,detail="Pet Not Found")
    vaccination = Vaccination(
        pet_id=data.pet_id,
        vaccine_name=data.vaccine_name,
        administered_on=data.administered_on,
        next_due_on=data.next_due_on,
        batch_number=data.batch_number
    )
    db.add(vaccination)
    db.commit()
    db.refresh(vaccination)
    return vaccination
@app.get("/vaccinations")
def get_vaccinations(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(Vaccination).all()
@app.get("/vaccinations/{vaccination_id}")
def get_vaccination_id(vaccination_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Vaccination).filter(
        Vaccination.id == vaccination_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Vaccination not found")
    return record
@app.put("/vaccinations/{vaccination_id}")
def update_vaccination(vaccination_id: int,data: VaccinationCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Vaccination).filter(Vaccination.id == vaccination_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Vaccination not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/vaccinations/{vaccination_id}")
def delete_vaccination(vaccination_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Vaccination).filter(Vaccination.id == vaccination_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Vaccination not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Vaccination deleted successfully",
            "id": vaccination_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/addresses")
def create_address(data: AddressCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    parent = db.query(PetParent).filter(
        PetParent.id == data.parent_id).first()
    if not parent:
        raise fastapi.HTTPException(
            status_code=404,detail="Pet parent not found")
    address = Address(
        parent_id=data.parent_id,
        label=data.label,
        contact_name=data.contact_name,
        line1=data.line1,
        city=data.city,
        pincode=data.pincode,
        is_default=data.is_default
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    return address
@app.get("/addresses")
def get_addresses(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(Address).all()
@app.get("/addresses/{address_id}")
def get_address_id(address_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Address).filter(Address.id == address_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Address not found")
    return record
@app.put("/addresses/{address_id}")
def update_address(address_id: int,data: AddressCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Address).filter(Address.id == address_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Address not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/addresses/{address_id}")
def delete_address(address_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Address).filter(Address.id == address_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Address not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Address deleted successfully",
            "id": address_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/user-roles")
def create_user_role(data: UserRoleCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    user_role = UserRole(
        user_id=data.user_id,
        role=data.role
        )
    db.add(user_role)
    db.commit()
    db.refresh(user_role)
    return user_role
@app.get("/user-roles")
def get_user_roles(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(UserRole).all()
@app.get("/user-roles/{role_id}")
def get_role_id(role_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(UserRole).filter(
        UserRole.id == role_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="User role not found")
    return record
@app.put("/user-roles/{role_id}")
def update_userrole(role_id: int,data: UserRoleCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(UserRole).filter(UserRole.id == role_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="UserRole not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/user-roles/{role_id}")
def delete_userrole(role_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(UserRole).filter(UserRole.id == role_id).first()
    if not record:
        raise fastapi.HTTPException(
            status_code=404,
            detail="UserRole not found"
        )
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "UserRole deleted successfully",
            "id": role_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/doctors")
def create_doctor(data: DoctorCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    doctor = Doctor(
        name=data.name,
        qualification=data.qualification,
        specializations=data.specializations,
        pincode=data.pincode,
        experience_years=data.experience_years,
        consultation_fee=data.consultation_fee,
        rating=data.rating,
        verification_status=data.verification_status,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return model_response(doctor)
@app.get("/doctors")
def get_doctors(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return [model_response(item) for item in db.query(Doctor).all()]
@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id).first()
    if not doctor:
        raise fastapi.HTTPException(status_code=404,detail="Doctor not found")
    return model_response(doctor)
@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: int,data: DoctorCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Doctor not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Doctor not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Doctor deleted successfully",
            "id": doctor_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/clinics-hospitals")
def create_clinic_hospital(data: ClinicHospitalCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    facility = ClinicHospital(
        name=data.name,
        facility_type=data.facility_type,
        phone=data.phone,
        emergency_available=data.emergency_available,
        open_24x7=data.open_24x7,
        verification_status=data.verification_status,
        rating=data.rating
    )
    db.add(facility)
    db.commit()
    db.refresh(facility)
    return facility
@app.get("/clinics-hospitals")
def get_clinics_hospitals(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(ClinicHospital).all()
@app.get("/clinics-hospitals/{facility_id}")
def get_clinic_hospital(facility_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    facility = db.query(ClinicHospital).filter(
        ClinicHospital.id == facility_id).first()
    if not facility:
        raise fastapi.HTTPException(status_code=404,detail="Clinic or hospital not found")
    return facility
@app.put("/clinics-hospitals/{facility_id}")
def update_clinichospital(facility_id: int,data: ClinicHospitalCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(ClinicHospital).filter(ClinicHospital.id == facility_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="ClinicHospital not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/clinics-hospitals/{facility_id}")
def delete_clinichospital(facility_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(ClinicHospital).filter(ClinicHospital.id == facility_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="ClinicHospital not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "ClinicHospital deleted successfully",
            "id": facility_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/availability-slots")
def create_availability_slot(data: AvailabilitySlotCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    doctor = db.query(Doctor).filter(
        Doctor.id == data.doctor_id).first()
    if not doctor:
        raise fastapi.HTTPException(status_code=404,detail="Doctor not found")
    slot = AvailabilitySlot(
        doctor_id=data.doctor_id,
        day_of_week=data.day_of_week,
        start_time=data.start_time,
        end_time=data.end_time,
        consultation_type=data.consultation_type,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return model_response(slot)
@app.get("/availability-slots")
def get_availability_slots(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return [model_response(item) for item in db.query(AvailabilitySlot).all()]
@app.get("/availability-slots/{slot_id}")
def get_availability_slot(slot_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    slot = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.id == slot_id).first()
    if not slot:
        raise fastapi.HTTPException(status_code=404,detail="Availability slot not found")
    return model_response(slot)
@app.put("/availability-slots/{slot_id}")
def update_availabilityslot(slot_id: int,data: AvailabilitySlotCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(AvailabilitySlot).filter(AvailabilitySlot.id == slot_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="AvailabilitySlot not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/availability-slots/{slot_id}")
def delete_availabilityslot(slot_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(AvailabilitySlot).filter(AvailabilitySlot.id == slot_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="AvailabilitySlot not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "AvailabilitySlot deleted successfully",
            "id": slot_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/doctor-documents")
def create_doctor_document(data: DoctorDocumentCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    doctor = db.query(Doctor).filter(
        Doctor.id == data.doctor_id).first()
    if not doctor:
        raise fastapi.HTTPException(status_code=404,detail="Doctor not found")
    document = DoctorDocument(
        doctor_id=data.doctor_id,
        document_type=data.document_type,
        status=data.status
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document
@app.get("/doctor-documents")
def get_doctor_documents(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(DoctorDocument).all()
@app.get("/doctor-documents/{document_id}")
def get_doctor_document(document_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    document = db.query(DoctorDocument).filter(
        DoctorDocument.id == document_id).first()
    if not document:
        raise fastapi.HTTPException(status_code=404,detail="Doctor document not found")
    return document
@app.put("/doctor-documents/{document_id}")
def update_doctordocument(document_id: int,data: DoctorDocumentCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(DoctorDocument).filter(DoctorDocument.id == document_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="DoctorDocument not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/doctor-documents/{document_id}")
def delete_doctordocument(document_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(DoctorDocument).filter(DoctorDocument.id == document_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="DoctorDocument not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "DoctorDocument deleted successfully",
            "id": document_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/appointments")
def create_appointment(data:AppointmentCreate,db:sqlalchemy.orm.Session=fastapi.Depends(get_db)):
    pet =db.query(Pet).filter(Pet.id==data.pet_id).first()
    if not pet:
        raise fastapi.HTTPException(status_code=404 , detail= "Pet Not Found")
    doctor = db.query(Doctor).filter(Doctor.id == data.doctor_id).first()
    if not doctor:
        raise fastapi.HTTPException(status_code=404 , detail="Doctor Not Found")
    appointment = Appointment(
        pet_id = data.pet_id,
        doctor_id = data.doctor_id,
        appointment_date = data.appointment_date,
        appointment_time = data.appointment_time,
        appointment_type = data.appointment_type,
        status = data.status,
        payment_status = data.payment_status,
        consultation_fee=data.consultation_fee
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment
@app.get("/appointments")
def get_appointments(db:sqlalchemy.orm.Session=fastapi.Depends(get_db)):
    return db.query(Appointment).all()
@app.get("/appointments/{appointment_id}")
def get_appointment(appointment_id :int,db:sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    appointment =db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise fastapi.HTTPException(status_code=404 , detail="Appointment Not Found")
    return appointment
@app.put("/appointments/{appointment_id}")
def update_appointment(appointment_id: int,data: AppointmentCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Appointment not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Appointment not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Appointment deleted successfully",
            "id": appointment_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/consultations")
def create_consultation(data:ConsultationCreate,db:sqlalchemy.orm.Session=fastapi.Depends(get_db)):
    appointment = db.query(Appointment).filter(
        Appointment.id == data.appointment_id).first()
    if not appointment:
        raise fastapi.HTTPException(status_code=404 , detail="Appointment Not Found")
    consultation = Consultation(
        appointment_id = data.appointment_id,
        consultation_mode = data.consultation_mode,
        diagnosis = data.diagnosis,
        follow_up_date = data.follow_up_date
    )
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    return consultation
@app.get("/consultations")
def get_consultations(db:sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(Consultation).all()
@app.get("/consultations/{consultation_id}")
def get_consultation(consultation_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    consultation = db.query(Consultation).filter(
        Consultation.id == consultation_id).first()
    if not consultation:
        raise fastapi.HTTPException(status_code=404, detail="Consultation not found")
    return consultation
@app.put("/consultations/{consultation_id}")
def update_consultation(consultation_id: int,data: ConsultationCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Consultation not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/consultations/{consultation_id}")
def delete_consultation(consultation_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Consultation not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Consultation deleted successfully",
            "id": consultation_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/prescriptions")
def create_prescription(data: PrescriptionCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    doctor = db.query(Doctor).filter(
        Doctor.id == data.doctor_id).first()
    if not doctor:
        raise fastapi.HTTPException(status_code=404, detail="Doctor not found")
    pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
    if not pet:
        raise fastapi.HTTPException(status_code=404, detail="Pet not found")
    prescription = Prescription(
        doctor_id=data.doctor_id,
        pet_id=data.pet_id,
        valid_until=data.valid_until
    )
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    return prescription
@app.get("/prescriptions")
def get_prescriptions(db:sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(Prescription).all()
@app.get("/prescriptions/{prescription_id}")
def get_prescription(prescription_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id).first()
    if not prescription:
        raise fastapi.HTTPException(status_code=404, detail="Prescription not found")
    return prescription
@app.put("/prescriptions/{prescription_id}")
def update_prescription(prescription_id: int,data: PrescriptionCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Prescription not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/prescriptions/{prescription_id}")
def delete_prescription(prescription_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Prescription not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Prescription deleted successfully",
            "id": prescription_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/service-providers")
def create_service_provider(data: ServiceProviderCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    provider = ServiceProvider(
        name=data.name,
        provider_type=data.provider_type,
        phone=data.phone,
        verification_status=data.verification_status,
        rating=data.rating,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return model_response(provider)
@app.get("/service-providers")
def get_service_providers(db:sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return [model_response(item) for item in db.query(ServiceProvider).all()]
@app.get("/service-providers/{provider_id}")
def get_service_provider(provider_id:int , db:sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    provider = db.query(ServiceProvider).filter(
        ServiceProvider.id == provider_id).first()
    if not provider:
        raise fastapi.HTTPException(status_code=404 , detail="Provider Not Found")
    return model_response(provider)
@app.put("/service-providers/{provider_id}")
def update_serviceprovider(provider_id: int,data: ServiceProviderCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="ServiceProvider not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/service-providers/{provider_id}")
def delete_serviceprovider(provider_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(ServiceProvider).filter(ServiceProvider.id == provider_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="ServiceProvider not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "ServiceProvider deleted successfully",
            "id": provider_id
        }

    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/services")
def create_service(data: ServiceCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    service = Service(
        title=data.title,
        service_type=data.service_type,
        price=data.price,
        duration_minutes=data.duration_minutes,
        home_service=data.home_service,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    return model_response(service)
@app.get("/services")
def get_services(db:sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return [model_response(item) for item in db.query(Service).all()]
@app.get("/services/{service_id}")
def get_service_id(service_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Service).filter(Service.id == service_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Service not found")
    return record
@app.put("/services/{service_id}")
def update_service(service_id: int,data: ServiceCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Service).filter(Service.id == service_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Service not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/services/{service_id}")
def delete_service(service_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Service).filter(Service.id == service_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Service not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Service deleted successfully",
            "id": service_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/service-bookings")
def create_service_booking(data: ServiceBookingCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    try:
        service = db.query(Service).filter(
            Service.id == data.service_id).first()
        if not service:
            raise fastapi.HTTPException(status_code=404,detail="Service not found")
        provider = db.query(ServiceProvider).filter(
            ServiceProvider.id == data.provider_id).first()
        if not provider:
            raise fastapi.HTTPException(status_code=404,detail="Service provider not found")
        pet = db.query(Pet).filter(Pet.id == data.pet_id).first()
        if not pet:
            raise fastapi.HTTPException(status_code=404,detail="Pet not found")
        booking = ServiceBooking(
            service_id=data.service_id,
            provider_id=data.provider_id,
            pet_id=data.pet_id,
            booking_date=data.booking_date,
            booking_time=data.booking_time,
            price=data.price,
            status=data.status,
            payment_status=data.payment_status
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print("ERROR:", str(e))
        raise fastapi.HTTPException(status_code=500,detail=str(e))
@app.get("/service-bookings")
def get_service_bookings(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(ServiceBooking).all()
@app.get("/service-bookings/{booking_id}")
def get_service_booking(booking_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    booking = db.query(ServiceBooking).filter(
        ServiceBooking.id == booking_id).first()
    if not booking:
        raise fastapi.HTTPException(status_code=404, detail="Service booking not found")
    return booking
@app.put("/service-bookings/{booking_id}")
def update_servicebooking(booking_id: int,data: ServiceBookingCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(ServiceBooking).filter(ServiceBooking.id == booking_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="ServiceBooking not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/service-bookings/{booking_id}")
def delete_servicebooking(booking_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(ServiceBooking).filter(ServiceBooking.id == booking_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="ServiceBooking not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "ServiceBooking deleted successfully",
            "id": booking_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/products")
def create_product(data: ProductCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    product = Product(
        name=data.name,
        price=data.price,
        mrp=data.mrp,
        discount_percent=data.discount_percent,
        pincode=data.pincode,
        stock_quantity=data.stock_quantity,
        is_prescription_required=data.is_prescription_required,
        rating=data.rating,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return model_response(product)
@app.get("/products")
def get_products(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return [model_response(item) for item in db.query(Product).all()]
@app.get("/products/{product_id}")
def get_product_id(product_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Product).filter(Product.id == product_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Product not found")
    return record
@app.put("/products/{product_id}")
def update_product(product_id: int,data: ProductCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Product).filter(Product.id == product_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Product not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/products/{product_id}")
def delete_product(product_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Product).filter(Product.id == product_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Product not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Product deleted successfully",
            "id": product_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/inventory")
def create_inventory(data: InventoryCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise fastapi.HTTPException(status_code=404, detail="Product not found")
    seller = db.query(SellerStore).filter(SellerStore.id == data.seller_id).first()
    if not seller:
        raise fastapi.HTTPException(status_code=404, detail="Seller/store not found")
    inventory = Inventory(
        product_id=data.product_id,
        seller_id=data.seller_id,
        pincode=data.pincode,
        inventory_source=data.inventory_source,
        available_quantity=data.available_quantity,
        reserved_quantity=data.reserved_quantity,
        reorder_level=data.reorder_level
    )
    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    return inventory
@app.get("/inventory")
def get_inventory(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(Inventory).all()
@app.get("/inventory/{inventory_id}")
def get_inventory_id(inventory_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Inventory not found")
    return record
@app.put("/inventory/{inventory_id}")
def update_inventory(inventory_id: int,data: InventoryCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Inventory not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/inventory/{inventory_id}")
def delete_inventory(inventory_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Inventory not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Inventory deleted successfully",
            "id": inventory_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/categories")
def create_category(data: CategoryCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    category = Category(
        name=data.name,
        slug=data.slug,
        sort_order=data.sort_order,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return model_response(category)
@app.get("/categories")
def get_categories(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return [model_response(item) for item in db.query(Category).all()]
@app.get("/categories/{category_id}")
def get_category_id(category_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Category).filter(
        Category.id == category_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Category not found")
    return record
@app.put("/categories/{category_id}")
def update_category(category_id: int,data: CategoryCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Category).filter(Category.id == category_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Category not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/categories/{category_id}")
def delete_category(category_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Category).filter(Category.id == category_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Category not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Category deleted successfully",
            "id": category_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/brands")
def create_brand(data: BrandCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    brand = Brand(name=data.name,is_active=yes_no_to_bool(data.is_active))
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return model_response(brand)
@app.get("/brands")
def get_brands(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return [model_response(item) for item in db.query(Brand).all()]
@app.get("/brands/{brand_id}")
def get_brand_id(brand_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Brand).filter(
        Brand.id == brand_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Brand not found")
    return record
@app.put("/brands/{brand_id}")
def update_brand(brand_id: int,data: BrandCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Brand).filter(Brand.id == brand_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Brand not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/brands/{brand_id}")
def delete_brand(brand_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Brand).filter(Brand.id == brand_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Brand not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Brand deleted successfully",
            "id": brand_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/seller-stores")
def create_seller_store(data: SellerStoreCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    seller = SellerStore(
        business_name=data.business_name,
        seller_type=data.seller_type,
        phone=data.phone,
        commission_rate=data.commission_rate,
        verification_status=data.verification_status,
        rating=data.rating,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(seller)
    db.commit()
    db.refresh(seller)
    return model_response(seller)
@app.get("/seller-stores")
def get_seller_stores(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return [model_response(item) for item in db.query(SellerStore).all()]
@app.get("/seller-stores/{seller_id}")
def get_seller_id(seller_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(SellerStore).filter(SellerStore.id == seller_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Seller store not found")
    return record
@app.put("/seller-stores/{seller_id}")
def update_sellerstore(seller_id: int,data: SellerStoreCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(SellerStore).filter(SellerStore.id == seller_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="SellerStore not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/seller-stores/{seller_id}")
def delete_sellerstore(seller_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(SellerStore).filter(SellerStore.id == seller_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="SellerStore not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "SellerStore deleted successfully",
            "id": seller_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/warehouses")
def create_warehouse(data: WarehouseCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    seller = db.query(SellerStore).filter(SellerStore.id == data.seller_id).first()
    if not seller:
        raise fastapi.HTTPException(status_code=404, detail="Seller/store not found")
    warehouse = Warehouse(
        name=data.name,
        seller_id=data.seller_id,
        is_zenve_owned=data.is_zenve_owned,
        contact_phone=data.contact_phone,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return model_response(warehouse)
@app.get("/warehouses")
def get_warehouses(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return [model_response(item) for item in db.query(Warehouse).all()]
@app.get("/warehouses/{warehouse_id}")
def get_warehouse_id(warehouse_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Warehouse not found")
    return record
@app.put("/warehouses/{warehouse_id}")
def update_warehouse(warehouse_id: int,data: WarehouseCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Warehouse not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/warehouses/{warehouse_id}")
def delete_warehouse(warehouse_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Warehouse not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Warehouse deleted successfully",
            "id": warehouse_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/carts")
def create_cart(data: CartCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    cart = Cart(user_id=data.user_id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart
@app.get("/carts")
def get_carts(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(Cart).all()
@app.get("/carts/{cart_id}")
def get_cart_id(cart_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Cart).filter(Cart.id == cart_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Cart not found")
    return record
@app.put("/carts/{cart_id}")
def update_cart(cart_id: int,data: CartCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Cart).filter(Cart.id == cart_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Cart not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/carts/{cart_id}")
def delete_cart(cart_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Cart).filter(Cart.id == cart_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Cart not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Cart deleted successfully",
            "id": cart_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/cart-items")
def create_cart_item(data: CartItemCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    cart = db.query(Cart).filter(Cart.id == data.cart_id).first()
    if not cart:
        raise fastapi.HTTPException(status_code=404, detail="Cart not found")
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise fastapi.HTTPException(status_code=404, detail="Product not found")
    cart_item = CartItem(
        cart_id=data.cart_id,
        product_id=data.product_id,
        quantity=data.quantity,
        price=data.price,
        saved_for_later=data.saved_for_later
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item
@app.get("/cart-items")
def get_cart_items(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(CartItem).all()
@app.get("/cart-items/{cart_item_id}")
def get_cart_item_id(cart_item_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Cart item not found")
    return record
@app.put("/cart-items/{cart_item_id}")
def update_cartitem(cart_item_id: int,data: CartItemCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="CartItem not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/cart-items/{cart_item_id}")
def delete_cartitem(cart_item_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="CartItem not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "CartItem deleted successfully",
            "id": cart_item_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/orders")
def create_order(data: OrderCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    order = Order(
        order_number=data.order_number,
        total_amount=data.total_amount,
        status=data.status,
        payment_status=data.payment_status
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
@app.get("/orders")
def get_order(db :sqlalchemy.orm.Session =fastapi.Depends(get_db)):
    return db.query(Order).all()
@app.get("/orders/{order_id}")
def get_order_id(order_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Order).filter(Order.id == order_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Order not found")
    return record
@app.put("/orders/{order_id}")
def update_order(order_id: int,data: OrderCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Order).filter(Order.id == order_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Order not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/orders/{order_id}")
def delete_order(order_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Order).filter(Order.id == order_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Order not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Order deleted successfully",
            "id": order_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/order-items")
def create_order_item(data: OrderItemCreate , db : sqlalchemy.orm.Session=fastapi.Depends(get_db)):
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        return fastapi.HTTPException(status_code=404 , detail="order not found")
    item = OrderItem(
        order_id = data.order_id,
        product_name = data.product_name,
        quantity = data.quantity,
        unit_price = data.unit_price,
        total_price = data.total_price,
        status = data.status
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
@app.get("/order-items")
def get_order_items(db :sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(OrderItem).all()
@app.get("/order-items/{item_id}")
def get_item_id(item_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(OrderItem).filter(OrderItem.id == item_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Order item not found")
    return record
@app.put("/order-items/{item_id}")
def update_orderitem(item_id: int,data: OrderItemCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(OrderItem).filter(OrderItem.id == item_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="OrderItem not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/order-items/{item_id}")
def delete_orderitem(item_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(OrderItem).filter(OrderItem.id == item_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="OrderItem not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "OrderItem deleted successfully",
            "id": item_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/deliveries")
def create_delivery(data: DeliveryCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        raise fastapi.HTTPException(status_code=404, detail="Order not found")
    delivery = Delivery(**data.model_dump())
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return delivery
@app.get("/deliveries")
def get_deliveries(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(Delivery).all()
@app.get("/deliveries/{delivery_id}")
def get_delivery_id(delivery_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Delivery not found")
    return record
@app.put("/deliveries/{delivery_id}")
def update_delivery(delivery_id: int,data: DeliveryCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Delivery not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/deliveries/{delivery_id}")
def delete_delivery(delivery_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Delivery not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Delivery deleted successfully",
            "id": delivery_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/payments")
def create_payment(data: PaymentCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        raise fastapi.HTTPException(status_code=404,detail="Order not found")
    payment = Payment(
        order_id=data.order_id,
        amount=data.amount,
        gateway=data.gateway,
        status=data.status,
        webhook_verified=data.webhook_verified
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
@app.get("/payments")
def get_payment(db:sqlalchemy.orm.Session=fastapi.Depends(get_db)):
    return db.query(Payment).all()
@app.get("/payments/{payment_id}")
def get_payment_id(payment_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Payment).filter(Payment.id == payment_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Payment not found")
    return record
@app.put("/payments/{payment_id}")
def update_payment(payment_id: int,data: PaymentCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Payment).filter(Payment.id == payment_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Payment not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/payments/{payment_id}")
def delete_payment(payment_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Payment).filter(Payment.id == payment_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Payment not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Payment deleted successfully",
            "id": payment_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/refunds")
def create_refund(data: RefundCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == data.payment_id).first()
    if not payment:
        raise fastapi.HTTPException(status_code=404, detail="Payment not found")
    refund = Refund(**data.model_dump())
    db.add(refund)
    db.commit()
    db.refresh(refund)
    return refund
@app.get("/refunds")
def get_refunds(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(Refund).all()
@app.get("/refunds/{refund_id}")
def get_refund_id(refund_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Refund).filter(Refund.id == refund_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Refund not found")
    return record
@app.put("/refunds/{refund_id}")
def update_refund(refund_id: int,data: RefundCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Refund).filter(Refund.id == refund_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Refund not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/refunds/{refund_id}")
def delete_refund(refund_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Refund).filter(Refund.id == refund_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Refund not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Refund deleted successfully",
            "id": refund_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/payouts")
def create_payout(data: PayoutCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    payout = Payout(**data.model_dump())
    db.add(payout)
    db.commit()
    db.refresh(payout)
    return payout
@app.get("/payouts")
def get_payouts(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(Payout).all()
@app.get("/payouts/{payout_id}")
def get_payout_id(payout_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Payout).filter(Payout.id == payout_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Payout not found")
    return record
@app.put("/payouts/{payout_id}")
def update_payout(payout_id: int,data: PayoutCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Payout).filter(Payout.id == payout_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Payout not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/payouts/{payout_id}")
def delete_payout(payout_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Payout).filter(Payout.id == payout_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Payout not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Payout deleted successfully",
            "id": payout_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/commission-rules")
def create_commission_rule(data: CommissionRuleCreate, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    rule_data = data.model_dump()
    rule_data["is_active"] = yes_no_to_bool(rule_data["is_active"])
    rule = CommissionRule(**rule_data)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return model_response(rule)
@app.get("/commission-rules")
def get_commission_rules(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return [model_response(item) for item in db.query(CommissionRule).all()]
@app.get("/commission-rules/{rule_id}")
def get_rule_id(rule_id: int, db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(CommissionRule).filter(
        CommissionRule.id == rule_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Commission rule not found")
    return model_response(record)
@app.put("/commission-rules/{rule_id}")
def update_commissionrule(rule_id: int,data: CommissionRuleCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(CommissionRule).filter(CommissionRule.id == rule_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="CommissionRule not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/commission-rules/{rule_id}")
def delete_commissionrule(rule_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(CommissionRule).filter(CommissionRule.id == rule_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="CommissionRule not found" )
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "CommissionRule deleted successfully",
            "id": rule_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/gps-locations")
def create_gps_location(data: GPSLocationCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    location = GPSLocation(**data.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)
    return location
@app.get("/gps-locations")
def get_gps_locations(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(GPSLocation).all()
@app.get("/gps-locations/{location_id}")
def get_gps_location(location_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    location = db.query(GPSLocation).filter(GPSLocation.id == location_id).first()
    if not location:
        raise fastapi.HTTPException(status_code=404,detail="GPS location not found")
    return location
@app.put("/gps-locations/{location_id}")
def update_gpslocation(location_id: int,data: GPSLocationCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(GPSLocation).filter(GPSLocation.id == location_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="GPSLocation not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/gps-locations/{location_id}")
def delete_gpslocation(location_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(GPSLocation).filter(GPSLocation.id == location_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="GPSLocation not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "GPSLocation deleted successfully",
            "id": location_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/reviews")
def create_review(data: ReviewCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    review = Review(**data.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
@app.get("/reviews")
def get_reviews(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(Review).all()
@app.get("/reviews/{review_id}")
def get_review(review_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise fastapi.HTTPException(status_code=404,detail="Review not found")
    return review
@app.put("/reviews/{review_id}")
def update_review(review_id: int,data: ReviewCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Review).filter(Review.id == review_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Review not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/reviews/{review_id}")
def delete_review(review_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Review).filter(Review.id == review_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Review not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Review deleted successfully",
            "id": review_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/notifications")
def create_notification(data: NotificationCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    notification = Notification(**data.model_dump())
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification
@app.get("/notifications")
def get_notifications(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(Notification).all()
@app.get("/notifications/{notification_id}")
def get_notification(notification_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise fastapi.HTTPException(status_code=404,detail="Notification not found")
    return notification
@app.put("/notifications/{notification_id}")
def update_notification(notification_id: int,data: NotificationCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Notification).filter(Notification.id == notification_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Notification not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/notifications/{notification_id}")
def delete_notification(notification_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Notification).filter(Notification.id == notification_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404, detail="Notification not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Notification deleted successfully",
            "id": notification_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/membership-plans")
def create_membership_plan(data: MembershipPlanCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    plan_data = data.model_dump()
    plan_data["is_active"] = yes_no_to_bool(plan_data["is_active"])
    plan = MembershipPlan(**plan_data)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return model_response(plan)
@app.get("/membership-plans")
def get_membership_plans(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return [model_response(item) for item in db.query(MembershipPlan).all()]
@app.get("/membership-plans/{plan_id}")
def get_membership_plan(plan_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    plan = db.query(MembershipPlan).filter(MembershipPlan.id == plan_id).first()
    if not plan:
        raise fastapi.HTTPException(status_code=404,detail="Membership plan not found")
    return model_response(plan)
@app.put("/membership-plans/{plan_id}")
def update_membershipplan(plan_id: int,data: MembershipPlanCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(MembershipPlan).filter(MembershipPlan.id == plan_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="MembershipPlan not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/membership-plans/{plan_id}")
def delete_membershipplan(plan_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(MembershipPlan).filter(MembershipPlan.id == plan_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="MembershipPlan not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "MembershipPlan deleted successfully",
            "id": plan_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/plan-benefits")
def create_plan_benefit(data: PlanBenefitCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    plan = db.query(MembershipPlan).filter(MembershipPlan.id == data.plan_id).first()
    if not plan:
        raise fastapi.HTTPException(status_code=404,detail="Membership plan not found")
    benefit = PlanBenefit(**data.model_dump())
    db.add(benefit)
    db.commit()
    db.refresh(benefit)
    return benefit
@app.get("/plan-benefits")
def get_plan_benefits(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(PlanBenefit).all()
@app.get("/plan-benefits/{benefit_id}")
def get_plan_benefit(benefit_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    benefit = db.query(PlanBenefit).filter(PlanBenefit.id == benefit_id).first()
    if not benefit:
        raise fastapi.HTTPException(status_code=404,detail="Plan benefit not found")
    return benefit
@app.put("/plan-benefits/{benefit_id}")
def update_planbenefit(benefit_id: int,data: PlanBenefitCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(PlanBenefit).filter(PlanBenefit.id == benefit_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="PlanBenefit not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/plan-benefits/{benefit_id}")
def delete_planbenefit(benefit_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(PlanBenefit).filter(PlanBenefit.id == benefit_id).first()
    if not record:
        raise fastapi.HTTPException( status_code=404,detail="PlanBenefit not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "PlanBenefit deleted successfully",
            "id": benefit_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400, detail=str(e))
@app.post("/memberships")
def create_membership(data: MembershipCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    plan = db.query(MembershipPlan).filter(
        MembershipPlan.id == data.plan_id).first()
    if not plan:
        raise fastapi.HTTPException(status_code=404,detail="Membership plan not found")
    membership = Membership(**data.model_dump())
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership
@app.get("/memberships")
def get_memberships(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(Membership).all()
@app.get("/memberships/{membership_id}")
def get_membership(membership_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    membership = db.query(Membership).filter(
        Membership.id == membership_id).first()
    if not membership:
        raise fastapi.HTTPException(status_code=404,detail="Membership not found")
    return membership
@app.put("/memberships/{membership_id}")
def update_membership(membership_id: int,data: MembershipCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Membership).filter(Membership.id == membership_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Membership not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e) )
@app.delete("/memberships/{membership_id}")
def delete_membership(membership_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(Membership).filter(Membership.id == membership_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="Membership not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "Membership deleted successfully",
            "id": membership_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/support-tickets")
def create_support_ticket(data: SupportTicketCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    ticket = SupportTicket(**data.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket
@app.get("/support-tickets")
def get_support_tickets(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(SupportTicket).all()
@app.get("/support-tickets/{ticket_id}")
def get_support_ticket(ticket_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    ticket = db.query(SupportTicket).filter(
        SupportTicket.id == ticket_id).first()
    if not ticket:
        raise fastapi.HTTPException(status_code=404,detail="Support ticket not found")
    return ticket
@app.put("/support-tickets/{ticket_id}")
def update_supportticket(ticket_id: int,data: SupportTicketCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="SupportTicket not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/support-tickets/{ticket_id}")
def delete_supportticket(ticket_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="SupportTicket not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "SupportTicket deleted successfully",
            "id": ticket_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/geocoding-cache")
def create_geocoding_cache(data: GeocodingCacheCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    cache = GeocodingCache(**data.model_dump())
    db.add(cache)
    db.commit()
    db.refresh(cache)
    return cache
@app.get("/geocoding-cache")
def get_geocoding_cache(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(GeocodingCache).all()
@app.get("/geocoding-cache/{cache_id}")
def get_geocoding_cache_by_id(cache_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    cache = db.query(GeocodingCache).filter(
        GeocodingCache.id == cache_id).first()
    if not cache:
        raise fastapi.HTTPException(status_code=404,detail="Geocoding cache not found")
    return cache
@app.put("/geocoding-cache/{cache_id}")
def update_geocodingcache(cache_id: int,data: GeocodingCacheCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(GeocodingCache).filter(GeocodingCache.id == cache_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="GeocodingCache not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/geocoding-cache/{cache_id}")
def delete_geocodingcache(cache_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(GeocodingCache).filter(GeocodingCache.id == cache_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="GeocodingCache not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "GeocodingCache deleted successfully",
            "id": cache_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.post("/audit-logs")
def create_audit_log(data: AuditLogCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    log = AuditLog(**data.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
@app.get("/audit-logs")
def get_audit_logs(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(AuditLog).all()
@app.get("/audit-logs/{log_id}")
def get_audit_log(log_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not log:
        raise fastapi.HTTPException(status_code=404,detail="Audit log not found")
    return log
@app.put("/audit-logs/{log_id}")
def update_auditlog(log_id: int,data: AuditLogCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="AuditLog not found")
    try:
        update_data = data.model_dump(exclude_unset=True)
        if "is_active" in update_data:
            update_data["is_active"] = yes_no_to_bool(update_data["is_active"])
        for field, value in update_data.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return model_response(record) if hasattr(record, "is_active") else record
    except fastapi.HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400,detail=str(e))
@app.delete("/audit-logs/{log_id}")
def delete_auditlog(log_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    record = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    if not record:
        raise fastapi.HTTPException(status_code=404,detail="AuditLog not found")
    try:
        db.delete(record)
        db.commit()
        return {
            "message": "AuditLog deleted successfully",
            "id": log_id
        }
    except Exception as e:
        db.rollback()
        raise fastapi.HTTPException(status_code=400, detail=str(e))
@app.post("/sales-executives")
def create_sales_executive(data: SalesExecutiveCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    executive = SalesExecutive(
        name=data.name,
        code=data.code,
        phone=data.phone,
        email=data.email,
        region=data.region,
        city=data.city,
        monthly_target=data.monthly_target,
        is_active=yes_no_to_bool(data.is_active)
    )
    db.add(executive)
    db.commit()
    db.refresh(executive)
    return model_response(executive)
@app.get("/sales-executives")
def get_sales_executives(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return [
        model_response(item)
        for item in db.query(SalesExecutive).all()
    ]
@app.get("/sales-executives/{executive_id}")
def get_sales_executive(executive_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    executive = db.query(SalesExecutive).filter(SalesExecutive.id == executive_id).first()
    if not executive:
        raise fastapi.HTTPException(status_code=404,detail="Sales executive not found")
    return model_response(executive)
@app.put("/sales-executives/{executive_id}")
def update_sales_executive(executive_id: int,data: SalesExecutiveCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    executive = db.query(SalesExecutive).filter(SalesExecutive.id == executive_id).first()
    if not executive:
        raise fastapi.HTTPException( status_code=404, detail="Sales executive not found")
    update_data = data.model_dump(exclude_unset=True)
    if "is_active" in update_data:
        update_data["is_active"] = yes_no_to_bool(
            update_data["is_active"]
        )
    for field, value in update_data.items():
        setattr(executive, field, value)
    db.commit()
    db.refresh(executive)
    return model_response(executive)
@app.delete("/sales-executives/{executive_id}")
def delete_sales_executive(executive_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    executive = db.query(SalesExecutive).filter(SalesExecutive.id == executive_id).first()
    if not executive:
        raise fastapi.HTTPException(status_code=404,detail="Sales executive not found")
    db.delete(executive)
    db.commit()
    return {
        "message": "Sales executive deleted successfully",
        "id": executive_id
    }
@app.post("/pincode-coverages")
def create_pincode_coverage(data: PincodeCoverageCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    executive = db.query(SalesExecutive).filter(SalesExecutive.id == data.executive_id).first()
    if not executive:
        raise fastapi.HTTPException(status_code=404,detail="Sales executive not found")
    coverage = PincodeCoverage(
        executive_id=data.executive_id,
        pincode=data.pincode,
        city=data.city,
        state=data.state
    )
    db.add(coverage)
    db.commit()
    db.refresh(coverage)
    return coverage
@app.get("/pincode-coverages")
def get_pincode_coverages(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(PincodeCoverage).all()
@app.get("/pincode-coverages/{coverage_id}")
def get_pincode_coverage(coverage_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    coverage = db.query(PincodeCoverage).filter(PincodeCoverage.id == coverage_id).first()
    if not coverage:
        raise fastapi.HTTPException(status_code=404,detail="Pincode coverage not found")
    return coverage
@app.put("/pincode-coverages/{coverage_id}")
def update_pincode_coverage(coverage_id: int,data: PincodeCoverageCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    coverage = db.query(PincodeCoverage).filter(PincodeCoverage.id == coverage_id).first()
    if not coverage:
        raise fastapi.HTTPException(
            status_code=404,
            detail="Pincode coverage not found"
        )
    executive = db.query(SalesExecutive).filter(SalesExecutive.id == data.executive_id).first()
    if not executive:
        raise fastapi.HTTPException(status_code=404,detail="Sales executive not found")
    coverage.executive_id = data.executive_id
    coverage.pincode = data.pincode
    coverage.city = data.city
    coverage.state = data.state
    db.commit()
    db.refresh(coverage)
    return coverage
@app.delete("/pincode-coverages/{coverage_id}")
def delete_pincode_coverage(coverage_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    coverage = db.query(PincodeCoverage).filter(PincodeCoverage.id == coverage_id).first()
    if not coverage:
        raise fastapi.HTTPException(status_code=404,detail="Pincode coverage not found")
    db.delete(coverage)
    db.commit()
    return {
        "message": "Pincode coverage deleted successfully",
        "id": coverage_id
    }
@app.post("/executive-tasks")
def create_executive_task(data: ExecutiveTaskCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    task = ExecutiveTask(
        title=data.title,
        task_type=data.task_type,
        entity_type=data.entity_type,
        pincode=data.pincode,
        priority=data.priority,
        status=data.status,
        due_date=data.due_date
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
@app.get("/executive-tasks")
def get_executive_tasks(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(ExecutiveTask).all()
@app.get("/executive-tasks/{task_id}")
def get_executive_task(task_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    task = db.query(ExecutiveTask).filter(ExecutiveTask.id == task_id).first()
    if not task:
        raise fastapi.HTTPException(status_code=404,detail="Executive task not found")
    return task
@app.put("/executive-tasks/{task_id}")
def update_executive_task(task_id: int,data: ExecutiveTaskCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    task = db.query(ExecutiveTask).filter(ExecutiveTask.id == task_id).first()
    if not task:
        raise fastapi.HTTPException(
            status_code=404,
            detail="Executive task not found"
        )
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task
@app.delete("/executive-tasks/{task_id}")
def delete_executive_task(task_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    task = db.query(ExecutiveTask).filter(ExecutiveTask.id == task_id).first()
    if not task:
        raise fastapi.HTTPException(status_code=404,detail="Executive task not found")
    db.delete(task)
    db.commit()
    return {
        "message": "Executive task deleted successfully",
        "id": task_id
    }
@app.post("/executive-alerts")
def create_executive_alert(data: ExecutiveAlertCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    alert = ExecutiveAlert(
        title=data.title,
        severity=data.severity,
        entity_type=data.entity_type,
        pincode=data.pincode,
        is_read=data.is_read
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
@app.get("/executive-alerts")
def get_executive_alerts(db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    return db.query(ExecutiveAlert).all()
@app.get("/executive-alerts/{alert_id}")
def get_executive_alert(alert_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    alert = db.query(ExecutiveAlert).filter(ExecutiveAlert.id == alert_id).first()
    if not alert:
        raise fastapi.HTTPException(status_code=404,detail="Executive alert not found")
    return alert
@app.put("/executive-alerts/{alert_id}")
def update_executive_alert(alert_id: int,data: ExecutiveAlertCreate,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    alert = db.query(ExecutiveAlert).filter(ExecutiveAlert.id == alert_id).first()
    if not alert:
        raise fastapi.HTTPException(status_code=404,detail="Executive alert not found")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alert, field, value)
    db.commit()
    db.refresh(alert)
    return alert
@app.delete("/executive-alerts/{alert_id}")
def delete_executive_alert(alert_id: int,db: sqlalchemy.orm.Session = fastapi.Depends(get_db)):
    alert = db.query(ExecutiveAlert).filter(ExecutiveAlert.id == alert_id).first()
    if not alert:
        raise fastapi.HTTPException(status_code=404,detail="Executive alert not found")
    db.delete(alert)
    db.commit()
    return {
        "message": "Executive alert deleted successfully",
        "id": alert_id
    }