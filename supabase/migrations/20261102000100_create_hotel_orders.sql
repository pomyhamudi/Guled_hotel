create table if not exists public.hotel_orders (
    id uuid primary key default gen_random_uuid(),
    customer_name text not null check (char_length(btrim(customer_name)) between 1 and 120),
    phone text not null check (char_length(btrim(phone)) between 1 and 40),
    email text not null check (char_length(btrim(email)) between 3 and 254),
    order_details text not null check (char_length(btrim(order_details)) between 1 and 5000),
    consent_received boolean not null default false check (consent_received),
    created_at timestamptz not null default now()
);

alter table public.hotel_orders enable row level security;

revoke all on table public.hotel_orders from anon, authenticated;
grant select, insert on table public.hotel_orders to service_role;