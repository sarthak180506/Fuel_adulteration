-- Supabase migration: create readings table (FR-C2)
-- Run via: supabase db push  OR  paste in Supabase SQL editor

create extension if not exists "uuid-ossp";

create table if not exists public.readings (
  id                uuid         primary key default uuid_generate_v4(),
  created_at        timestamptz  not null    default now(),
  device_id         text         not null,
  timestamp_ms      bigint       not null,
  label_cls         smallint     not null check (label_cls between 0 and 4),
  label_name        text         not null,
  adulterant_type   text         not null,
  concentration_pct numeric(5,2) not null check (concentration_pct between 0 and 100),
  temperature_c     numeric(5,2) not null,
  cap_raw           numeric(10,6),
  opt_raw           numeric(8,6),
  tof_raw           numeric(8,3),
  confidence_cls    numeric(5,4)
);

-- Index for time-series dashboard queries
create index readings_created_at_idx on public.readings (created_at desc);
create index readings_device_id_idx  on public.readings (device_id);

-- Enable Row Level Security (RLS) — adjust policies for your auth setup
alter table public.readings enable row level security;

-- Policy: allow anonymous reads for dashboard
create policy "Allow anon read"
  on public.readings for select
  using (true);

-- Policy: allow service role insert (ESP32 via MQTT bridge)
create policy "Allow service insert"
  on public.readings for insert
  with check (true);
