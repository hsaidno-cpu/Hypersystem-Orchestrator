import { NextResponse } from "next/server";
import { createSupabaseServerClient } from "@/lib/supabase/server";
export const runtime = "nodejs";
export async function POST() {
  const supabase = await createSupabaseServerClient();
  const { data:userData, error:authError } = await supabase.auth.getUser();
  if (authError || !userData.user) return NextResponse.json({error:"unauthorized"},{status:401});
  const { data:member, error:memberError } = await supabase.from("hso_members").select("role,active").eq("user_id",userData.user.id).maybeSingle();
  if (memberError || !member?.active) return NextResponse.json({error:"not_an_active_hso_member"},{status:403});
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL; const token = process.env.HSO_SYNC_TOKEN;
  if (!url || !token) return NextResponse.json({error:"sync_not_configured"},{status:503});
  const response = await fetch(url + "/functions/v1/hso-reconcile",{
    method:"POST",headers:{"content-type":"application/json","x-hso-sync-token":token},
    body:JSON.stringify({trigger_kind:"manual",requested_by:userData.user.id}),cache:"no-store",signal:AbortSignal.timeout(60000)
  });
  const data = await response.json().catch(()=>({error:"invalid_sync_response"}));
  return NextResponse.json(data,{status:response.status});
}
