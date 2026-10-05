const API_BASE_URL = "http://127.0.0.1:8000";

export async function classifyNews(text) {
  const response = await fetch(
    `${API_BASE_URL}/api/ai/classify`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: text,
      }),
    }
  );

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `Backend error ${response.status}: ${errorText}`
    );
  }

  return await response.json();
}