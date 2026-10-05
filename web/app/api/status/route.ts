const API_URL = process.env.API_INTERNAL_URL ?? 'http://127.0.0.1:8000';

export async function GET() {
  try {
    const response = await fetch(`${API_URL}/health`, { cache: 'no-store' });
    return new Response(response.body, {
      status: response.status,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch {
    return Response.json(
      { status: 'unhealthy', storage: 'unavailable' },
      { status: 502 },
    );
  }
}
