import { createServerSupabase } from "@/lib/supabase/server"
import { NextResponse } from "next/server"

export async function GET() {
  const supabase = await createServerSupabase()
  const { data } = await supabase.auth.getUser()
  const user = data?.user ?? null

  return NextResponse.json({ user })
}
