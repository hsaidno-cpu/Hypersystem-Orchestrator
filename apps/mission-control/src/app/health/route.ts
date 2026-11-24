export async function GET() {
  return Response.json({service:"hso-mission-control",status:"ok",version:"0.1.0"},{headers:{"cache-control":"no-store"}});
}
