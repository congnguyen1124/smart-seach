const API_URL = process.env.API_INTERNAL_URL ?? 'http://127.0.0.1:8000';

export async function POST(request: Request) {
  try {
    const body = await request.text();
    const response = await fetch(`${API_URL}/api/v1/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
    });
    return new Response(response.body, {
      status: response.status,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch {
    return Response.json(
      { error: 'backend_unavailable', message: 'Search API is unavailable' },
      { status: 502 },
    );
  }
}
