CREATE TABLE IF NOT EXISTS public.hotel_orders (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_name text NOT NULL
        CHECK (char_length(btrim(customer_name)) BETWEEN 1 AND 120),
    phone text NOT NULL
        CHECK (char_length(btrim(phone)) BETWEEN 1 AND 40),
    email text NOT NULL
        CHECK (char_length(btrim(email)) BETWEEN 3 AND 254),
    order_details text NOT NULL
        CHECK (char_length(btrim(order_details)) BETWEEN 1 AND 5000),
    status text NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
    consent_received boolean NOT NULL DEFAULT false
        CHECK (consent_received),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS hotel_orders_created_at_idx
    ON public.hotel_orders (created_at DESC);
