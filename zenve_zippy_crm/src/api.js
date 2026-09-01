// Connects the Zenve Zippy CRM to the FastAPI + MySQL backend.
// Change this if your backend runs somewhere else.
export const API_BASE = "http://127.0.0.1:8000";

/**
 * TABLE_CONFIG maps every dashboard key (from data.js / NAV_GROUPS) to:
 *  - path: the FastAPI resource path
 *  - fields: the editable fields, in the order they should appear as
 *            table columns and in the New/Edit modal
 *
 * field.type:
 *   "text"    - plain string
 *   "number"  - integer/float, sent as a Number
 *   "date"    - YYYY-MM-DD
 *   "time"    - HH:MM
 *   "datetime"- ISO datetime, read-only (server sets it)
 *   "yesno"   - fields the backend stores as bool but accepts/returns as
 *               the strings "Yes"/"No" (is_active-style fields)
 *   "bool"    - fields the backend stores and returns as real true/false
 */
export const TABLE_CONFIG = {
  pet_parents: {
    path: "/pet-parents",
    fields: [
      { key: "full_name", type: "text", required: true },
      { key: "email", type: "text", required: true },
      { key: "phone", type: "text" },
      { key: "city", type: "text" },
      { key: "created_at", type: "datetime", readOnly: true },
    ],
  },
  pets: {
    path: "/pets",
    fields: [
      { key: "parent_id", type: "number", required: true },
      { key: "name", type: "text", required: true },
      { key: "species", type: "text" },
      { key: "breed", type: "text" },
      { key: "gender", type: "text" },
      { key: "weight_kg", type: "number" },
      { key: "is_active", type: "yesno", default: "Yes" },
    ],
  },
  medical_records: {
    path: "/medical-records",
    fields: [
      { key: "pet_id", type: "number", required: true },
      { key: "record_type", type: "text" },
      { key: "title", type: "text" },
      { key: "diagnosis", type: "text" },
      { key: "record_date", type: "date" },
    ],
  },
  vaccinations: {
    path: "/vaccinations",
    fields: [
      { key: "pet_id", type: "number", required: true },
      { key: "vaccine_name", type: "text", required: true },
      { key: "administered_on", type: "date" },
      { key: "next_due_on", type: "date" },
      { key: "batch_number", type: "text" },
    ],
  },
  addresses: {
    path: "/addresses",
    fields: [
      { key: "parent_id", type: "number", required: true },
      { key: "label", type: "text" },
      { key: "contact_name", type: "text" },
      { key: "line1", type: "text" },
      { key: "city", type: "text" },
      { key: "pincode", type: "text" },
      { key: "is_default", type: "bool", default: false },
    ],
  },
  user_roles: {
    path: "/user-roles",
    fields: [
      { key: "user_id", type: "number", required: true },
      { key: "role", type: "text", required: true },
      { key: "created_at", type: "datetime", readOnly: true },
    ],
  },
  doctors: {
    path: "/doctors",
    fields: [
      { key: "name", type: "text", required: true },
      { key: "qualification", type: "text" },
      { key: "specializations", type: "text" },
      { key: "pincode", type: "text" },
      { key: "experience_years", type: "number" },
      { key: "consultation_fee", type: "number" },
      { key: "rating", type: "number" },
      { key: "verification_status", type: "text", default: "pending" },
      { key: "is_active", type: "yesno", default: "Yes" },
    ],
  },
  clinics: {
    path: "/clinics-hospitals",
    fields: [
      { key: "name", type: "text", required: true },
      { key: "facility_type", type: "text" },
      { key: "phone", type: "text" },
      { key: "emergency_available", type: "bool", default: false },
      { key: "open_24x7", type: "bool", default: false },
      { key: "verification_status", type: "text", default: "pending" },
      { key: "rating", type: "number" },
    ],
  },
  availability_slots: {
    path: "/availability-slots",
    fields: [
      { key: "doctor_id", type: "number", required: true },
      { key: "day_of_week", type: "text", required: true },
      { key: "start_time", type: "time", required: true },
      { key: "end_time", type: "time", required: true },
      { key: "consultation_type", type: "text" },
      { key: "is_active", type: "yesno", default: "Yes" },
    ],
  },
  doctor_documents: {
    path: "/doctor-documents",
    fields: [
      { key: "doctor_id", type: "number", required: true },
      { key: "document_type", type: "text", required: true },
      { key: "status", type: "text", default: "pending" },
      { key: "created_at", type: "datetime", readOnly: true},

    ],
  },
  appointments: {
    path: "/appointments",
    fields: [
    
      { key: "pet_id", type: "number", required: true },
      { key: "doctor_id", type: "number", required: true },
      { key: "appointment_date", type: "date", required: true },
      { key: "appointment_time", type: "time", required: true },
      { key: "appointment_type", type: "text" },
      { key: "status", type: "text", default: "pending" },
      { key: "payment_status", type: "text", default: "pending" },
      { key: "consultation_fee", type: "number" },
    ],
  },
  consultations: {
    path: "/consultations",
    fields: [
      
      { key: "appointment_id", type: "number", required: true },
      { key: "consultation_mode", type: "text" },
      { key: "diagnosis", type: "text" },
      { key: "follow_up_date", type: "date" },
      { key: "created_at", type: "datetime", readOnly: true },

    ],
  },
  prescriptions: {
    path: "/prescriptions",
    fields: [
      { key: "doctor_id", type: "number", required: true },
      { key: "pet_id", type: "number", required: true },
      { key: "valid_until", type: "date" },
      { key: "created_at", type: "datetime", readOnly: true },

    ],
  },
  service_providers: {
    path: "/service-providers",
    fields: [
      { key: "name", type: "text", required: true },
      { key: "provider_type", type: "text" },
      { key: "phone", type: "text" },
      { key: "verification_status", type: "text", default: "pending" },
      { key: "rating", type: "number" },
      { key: "is_active", type: "yesno", default: "Yes" },
    ],
  },
  services: {
    path: "/services",
    fields: [
      { key: "title", type: "text", required: true },
      { key: "service_type", type: "text" },
      { key: "price", type: "number" },
      { key: "duration_minutes", type: "number" },
      { key: "home_service", type: "bool", default: false },
      { key: "is_active", type: "yesno", default: "Yes" },
    ],
  },
  service_bookings: {
    path: "/service-bookings",
    fields: [
    
      { key: "service_id", type: "number", required: true },
      { key: "provider_id", type: "number", required: true },
      { key: "pet_id", type: "number", required: true },
      { key: "booking_date", type: "date", required: true },
      { key: "booking_time", type: "time", required: true },
      { key: "price", type: "number" },
      { key: "status", type: "text", default: "pending" },
      { key: "payment_status", type: "text", default: "pending" },
    ],
  },
  products: {
    path: "/products",
    fields: [
      { key: "name", type: "text", required: true },
      { key: "price", type: "number" },
      { key: "mrp", type: "number" },
      { key: "discount_percent", type: "number" },
      { key: "pincode", type: "text" },
      { key: "stock_quantity", type: "number" },
      { key: "is_prescription_required", type: "bool", default: false },
      { key: "rating", type: "number" },
      { key: "is_active", type: "yesno", default: "Yes" },
    ],
  },
  inventory: {
    path: "/inventory",
    fields: [
      { key: "product_id", type: "number", required: true },
      { key: "seller_id", type: "number", required: true },
      { key: "pincode", type: "text" },
      { key: "inventory_source", type: "text" },
      { key: "available_quantity", type: "number" },
      { key: "reserved_quantity", type: "number" },
      { key: "reorder_level", type: "number" },
    ],
  },
  categories: {
    path: "/categories",
    fields: [
      { key: "name", type: "text", required: true },
      { key: "slug", type: "text" },
      { key: "sort_order", type: "number" },
      { key: "is_active", type: "yesno", default: "Yes" },
    ],
  },
  brands: {
    path: "/brands",
    fields: [
      { key: "name", type: "text", required: true },
      { key: "is_active", type: "yesno", default: "Yes" },
      { key: "created_at", type: "datetime", readOnly: true },
    ],
  },
  sellers: {
    path: "/seller-stores",
    fields: [
      { key: "business_name", type: "text", required: true },
      { key: "seller_type", type: "text" },
      { key: "phone", type: "text" },
      { key: "commission_rate", type: "number" },
      { key: "verification_status", type: "text", default: "pending" },
      { key: "rating", type: "number" },
      { key: "is_active", type: "yesno", default: "Yes" },
    ],
  },
  warehouses: {
    path: "/warehouses",
    fields: [
      { key: "name", type: "text", required: true },
      { key: "seller_id", type: "number", required: true },
      { key: "is_zenve_owned", type: "bool", default: false },
      { key: "contact_phone", type: "text" },
      { key: "is_active", type: "yesno", default: "Yes" },
    ],
  },
  carts: {
    path: "/carts",
    fields: [
      { key: "user_id", type: "number", required: true },
      { key: "created_at", type: "datetime", readOnly: true },
      { key: "updated_at", type: "datetime", readOnly: true },
    ],
  },
  cart_items: {
    path: "/cart-items",
    fields: [
      { key: "cart_id", type: "number", required: true },
      { key: "product_id", type: "number", required: true },
      { key: "quantity", type: "number", default: 1 },
      { key: "price", type: "number" },
      { key: "saved_for_later", type: "bool", default: false },
    ],
  },
  orders: {
    path: "/orders",
    fields: [
      { key: "order_number", type: "text", required: true },
      { key: "total_amount", type: "number" },
      { key: "status", type: "text", default: "pending" },
      { key: "payment_status", type: "text", default: "pending" },
      { key: "placed_at", type: "datetime", readOnly: true },
    ],
  },
  order_items: {
    path: "/order-items",
    fields: [
      { key: "order_id", type: "number", required: true },        
      { key: "product_name", type: "text", required: true },
      { key: "quantity", type: "number", default: 1 },
      { key: "unit_price", type: "number" },
      { key: "total_price", type: "number" },
      { key: "status", type: "text", default: "CONFIRMED" },
    ],
  },
  deliveries: {
    path: "/deliveries",
    fields: [
      { key: "order_id", type: "number", required: true },
      { key: "tracking_number", type: "text" },
      { key: "status", type: "text", default: "pending" },
      { key: "estimated_delivery", type: "date" },
      { key: "delivered_at", type: "datetime" },
    ],
  },
  payments: {
    path: "/payments",
    fields: [
      { key: "order_id", type: "number", required: true },  
      { key: "amount", type: "number" },
      { key: "gateway", type: "text" },
      { key: "status", type: "text", default: "pending" },
      { key: "webhook_verified", type: "bool", default: false },
      {key: "created_at", type: "datetime", readOnly: true },

    ],
  },
  refunds: {
    path: "/refunds",
    fields: [
      { key: "payment_id", type: "number", required: true },
      { key: "amount", type: "number" },
      { key: "reason", type: "text" },
      { key: "status", type: "text", default: "pending" },
      {key: "created_at", type: "datetime", readOnly: true },

    ],
  },
  payouts: {
    path: "/payouts",
    fields: [
      { key: "payee_type", type: "text", required: true },
      { key: "payee_id", type: "number", required: true },
      { key: "amount", type: "number" },
      { key: "commission_amount", type: "number" },
      { key: "status", type: "text", default: "pending" },
    ],
  },
  commission_rules: {
    path: "/commission-rules",
    fields: [
      { key: "scope", type: "text", required: true },
      { key: "percentage", type: "number" },
      { key: "fixed_fee", type: "number" },
      { key: "effective_from", type: "date" },
      { key: "is_active", type: "yesno", default: "Yes" },
    ],
  },
  gps_locations: {
    path: "/gps-locations",
    fields: [
      { key: "entity_type", type: "text", required: true },
      { key: "city", type: "text" },
      { key: "address", type: "text" },
      { key: "latitude", type: "number" },
      { key: "longitude", type: "number" },
      { key: "service_radius_km", type: "number" },
      { key: "is_primary", type: "bool", default: false },
    ],
  },
  reviews: {
    path: "/reviews",
    fields: [
      { key: "target_type", type: "text", required: true },
      { key: "rating", type: "number" },
      { key: "review_text", type: "text" },
      { key: "status", type: "text", default: "pending" },
      {key: "created_at", type: "datetime", readOnly: true },

    ],
  },
  notifications: {
    path: "/notifications",
    fields: [
      { key: "event_type", type: "text", required: true },
      { key: "title", type: "text", required: true },
      { key: "channel", type: "text" },
      { key: "is_read", type: "bool", default: false },
      {key: "created_at", type: "datetime", readOnly: true },

    ],
  },
  membership_plans: {
    path: "/membership-plans",
    fields: [
      { key: "name", type: "text", required: true },
      { key: "price", type: "number" },
      { key: "duration_days", type: "number" },
      { key: "is_active", type: "yesno", default: "Yes" },
    ],
  },
  plan_benefits: {
    path: "/plan-benefits",
    fields: [
      { key: "plan_id", type: "number", required: true },
      { key: "benefit", type: "text", required: true },
      { key: "value", type: "text" },
    ],
  },
  memberships: {
    path: "/memberships",
    fields: [
      { key: "user_id", type: "number", required: true },
      { key: "plan_id", type: "number", required: true },
      { key: "started_on", type: "date" },
      { key: "expires_on", type: "date" },
      { key: "status", type: "text", default: "active" },
    ],
  },
  support_tickets: {
    path: "/support-tickets",
    fields: [
      { key: "subject", type: "text", required: true },
      { key: "category", type: "text" },
      { key: "status", type: "text", default: "open" },
      {key: "created_at", type: "datetime", readOnly: true },

    ],
  },
  geocoding_cache: {
    path: "/geocoding-cache",
    fields: [
      { key: "query", type: "text", required: true },
      { key: "latitude", type: "number" },
      { key: "longitude", type: "number" },
      { key: "formatted_address", type: "text" },
    ],
  },
  audit_logs: {
    path: "/audit-logs",
    fields: [
      { key: "action", type: "text", required: true },
      { key: "entity_type", type: "text" },
      { key: "entity_id", type: "number" },
      {key: "created_at", type: "datetime", readOnly: true },

    ],
  },
  sales_executives: {
    path: "/sales-executives",
    fields: [
      { key: "name", type: "text", required: true },
      { key: "code", type: "text", required: true },
      { key: "phone", type: "text" },
      { key: "email", type: "text" },
      { key: "region", type: "text" },
      { key: "city", type: "text" },
      { key: "monthly_target", type: "number" },
      { key: "is_active", type: "yesno", default: "Yes" },
    ],
  },
  pincode_coverage: {
    path: "/pincode-coverages",
    fields: [
      { key: "executive_id", type: "number", required: true },
      { key: "pincode", type: "text", required: true },
      { key: "city", type: "text" },
      { key: "state", type: "text" },
      {key: "created_at", type: "datetime", readOnly: true },
     
    ],
  },
  executive_tasks: {
    path: "/executive-tasks",
    fields: [
      { key: "title", type: "text", required: true },
      { key: "task_type", type: "text" },
      { key: "entity_type", type: "text" },
      { key: "pincode", type: "text" },
      { key: "priority", type: "text" },
      { key: "status", type: "text", default: "pending" },
      { key: "due_date", type: "date" },
    ],
  },
  executive_alerts: {
    path: "/executive-alerts",
    fields: [
      { key: "title", type: "text", required: true },
      { key: "severity", type: "text" },
      { key: "entity_type", type: "text" },
      { key: "pincode", type: "text" },
      { key: "is_read", type: "bool", default: false },
      {key: "created_at", type: "datetime", readOnly: true },

    ],
  },
};

async function handleResponse(res) {
  if (!res.ok) {
    let detail = res.statusText;

    try {
      const body = await res.json();

      if (typeof body.detail === "string") {
        detail = body.detail;
      } else if (body.detail) {
        detail = JSON.stringify(body.detail);
      } else {
        detail = JSON.stringify(body);
      }
    } catch (_) {
      // ignore parse errors
    }

    throw new Error(detail);
  }

  if (res.status === 204) return null;

  return res.json();
}

export async function fetchList(tableKey) {
  const config = TABLE_CONFIG[tableKey];
  if (!config) throw new Error(`Unknown table: ${tableKey}`);
  const res = await fetch(`${API_BASE}${config.path}`);
  return handleResponse(res);
}

// Returns the live record count for a table by fetching its list and
// reading .length. The backend has no dedicated count endpoint, so this
// is the simplest option that works for every resource without changes
// to the Python file. Fine for the current data volumes; if a table
// grows very large, add a `/{resource}/count` endpoint on the backend
// and swap this to call it instead.
export async function fetchCount(tableKey) {
  const list = await fetchList(tableKey);
  return Array.isArray(list) ? list.length : 0;
}

// Fetches counts for a list of {key, tableKey} stat definitions in
// parallel and returns { [key]: count }.
export async function fetchStatCounts(statConfig) {
  const entries = await Promise.all(
    statConfig.map(async (stat) => {
      try {
        const count = await fetchCount(stat.tableKey);
        return [stat.key, count];
      } catch (_) {
        return [stat.key, null]; // null = failed to load, shown as "—"
      }
    })
  );
  return Object.fromEntries(entries);
}

export async function fetchOne(tableKey, id) {
  const config = TABLE_CONFIG[tableKey];
  const res = await fetch(`${API_BASE}${config.path}/${id}`);
  return handleResponse(res);
}

export async function createRecord(tableKey, payload) {
  const config = TABLE_CONFIG[tableKey];
  const res = await fetch(`${API_BASE}${config.path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function updateRecord(tableKey, id, payload) {
  const config = TABLE_CONFIG[tableKey];
  const res = await fetch(`${API_BASE}${config.path}/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(res);
}

export async function deleteRecord(tableKey, id) {
  const config = TABLE_CONFIG[tableKey];
  const res = await fetch(`${API_BASE}${config.path}/${id}`, {
    method: "DELETE",
  });
  return handleResponse(res);
}

// Coerce a raw form value (always a string from an <input>) into the
// correct JSON type for the backend, based on the field's declared type.
export function coerceFieldValue(field, rawValue) {
  if (field.type === "number") {
    if (rawValue === "" || rawValue === null || rawValue === undefined) return null;
    const n = Number(rawValue);
    return Number.isNaN(n) ? null : n;
  }
  if (field.type === "bool") {
    return rawValue === true || rawValue === "true" || rawValue === "Yes";
  }
  if (field.type === "yesno") {
    const truthy = rawValue === true || rawValue === "true" || rawValue === "Yes";
    return truthy ? "Yes" : "No";
  }
  return rawValue === undefined ? "" : rawValue;
}

// Turn a display value (as it will be shown in the table/modal) into a
// normalized string/boolean for form inputs.
export function displayFieldValue(field, record) {
  const raw = record ? record[field.key] : undefined;
  if (raw === undefined || raw === null) return field.type === "bool" ? false : "";
  if (field.type === "bool") return raw === true || raw === "true";
  if (field.type === "yesno") return raw === "Yes" || raw === true;
  return String(raw);
}
