export const NAV_GROUPS = [
  { label: "Pet parents", items: [
    { key: "pet_parents", label: "Pet parents" },
    { key: "pets", label: "Pets" },
    { key: "medical_records", label: "Medical records" },
    { key: "vaccinations", label: "Vaccinations" },
    { key: "addresses", label: "Addresses" },
    { key: "user_roles", label: "User roles" },
  ]},
  { label: "Doctors & clinics", items: [
    { key: "doctors", label: "Doctors" },
    { key: "clinics", label: "Clinics & hospitals" },
    { key: "availability_slots", label: "Availability slots" },
    { key: "doctor_documents", label: "Doctor documents" },
  ]},
  { label: "Bookings", items: [
    { key: "appointments", label: "Appointments" },
    { key: "consultations", label: "Consultations" },
    { key: "prescriptions", label: "Prescriptions" },
    { key: "service_providers", label: "Service providers" },
    { key: "services", label: "Services" },
    { key: "service_bookings", label: "Service bookings" },
  ]},
  { label: "Commerce", items: [
    { key: "products", label: "Medicines & products" },
    { key: "inventory", label: "Inventory" },
    { key: "categories", label: "Categories" },
    { key: "brands", label: "Brands" },
    { key: "sellers", label: "Sellers & stores" },
    { key: "warehouses", label: "Warehouses" },
    { key: "carts", label: "Carts" },
    { key: "cart_items", label: "Cart items" },
  ]},
  { label: "Orders & payments", items: [
    { key: "orders", label: "Orders" },
    { key: "order_items", label: "Order items" },
    { key: "deliveries", label: "Deliveries" },
    { key: "payments", label: "Payments" },
    { key: "refunds", label: "Refunds" },
    { key: "payouts", label: "Payouts" },
    { key: "commission_rules", label: "Commission rules" },
  ]},
  { label: "Platform", items: [
    { key: "gps_locations", label: "GPS locations" },
    { key: "reviews", label: "Reviews" },
    { key: "notifications", label: "Notifications" },
    { key: "membership_plans", label: "Membership plans" },
    { key: "plan_benefits", label: "Plan benefits" },
    { key: "memberships", label: "Memberships" },
    { key: "support_tickets", label: "Support tickets" },
    { key: "geocoding_cache", label: "Geocoding cache" },
    { key: "audit_logs", label: "Audit logs" },
  ]},
  { label: "Sales team", items: [
    { key: "sales_regional_manager", label: "Regional manager" },
    { key: "sales_manager", label: "Sales manager" },
    { key: "sales_executive_crm", label: "Sales executives" },
    { key: "pincode_coverage", label: "Pin code coverage" },
    { key: "executive_tasks", label: "Executive tasks" },
    { key: "executive_alerts", label: "Executive alerts" },
  ]},
];

export const STATS = [
  { key: "profiles", label: "profiles", tableKey: "pet_parents" },
  { key: "pets", label: "pets", tableKey: "pets" },
  { key: "doctors", label: "doctors", tableKey: "doctors" },
  { key: "clinics", label: "clinics", tableKey: "clinics" },
  { key: "appointments", label: "appointments", tableKey: "appointments" },
  { key: "products", label: "products", tableKey: "products" },
  { key: "inventory", label: "inventory", tableKey: "inventory" },
  { key: "orders", label: "orders", tableKey: "orders" },
  { key: "sellers", label: "sellers", tableKey: "sellers" },
  { key: "services", label: "services", tableKey: "services" },
  { key: "payments", label: "payments", tableKey: "payments" },
  { key: "support_tickets", label: "support_tickets", tableKey: "support_tickets" },
];


export function findLabel(key) {
  for (const group of NAV_GROUPS) {
    for (const item of group.items) {
      if (item.key === key) return item.label;
    }
  }
  return key;
}
