// TypeScript types mirroring the Supabase `readings` table schema (FR-C2)

export type FuelClass =
  | 'Pure Fuel'
  | 'Kerosene-Adulterated Petrol'
  | 'Diesel-Adulterated Petrol'
  | 'Kerosene-Adulterated Diesel'
  | 'Water-Adulterated Diesel'

export interface Reading {
  id:                 string        // uuid
  created_at:         string        // ISO 8601
  device_id:          string        // e.g. "FG-001"
  timestamp_ms:       number        // epoch ms (device clock)
  label_cls:          number        // 0–4
  label_name:         FuelClass
  adulterant_type:    string        // "none" | "kerosene" | "diesel" | "water"
  concentration_pct:  number        // regression output 0–100
  temperature_c:      number
  cap_raw:            number
  opt_raw:            number
  tof_raw:            number | null
  confidence_cls:     number | null // softmax max probability
}

// Supabase Database type stub (extend as schema grows)
export interface Database {
  public: {
    Tables: {
      readings: {
        Row:    Reading
        Insert: Omit<Reading, 'id' | 'created_at'>
        Update: Partial<Omit<Reading, 'id'>>
      }
    }
  }
}
