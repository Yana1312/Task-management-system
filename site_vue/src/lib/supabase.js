import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = 'https://ezkogxtpkdolmfjetvua.supabase.co'
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6a29neHRwa2RvbG1mamV0dnVhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg0MzMwNjUsImV4cCI6MjA3NDAwOTA2NX0.NQiS8QuFXZtcKdMRcH8XvYFR2pQC-pqY7u4NrbCIGNs'

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)