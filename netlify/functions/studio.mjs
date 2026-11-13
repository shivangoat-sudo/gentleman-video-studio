// API placeholder. Generation is deliberately disabled until authentication
// and a private WanGP worker are configured. Never put secrets in Vite.
export default async (request) => {
  const path = new URL(request.url).pathname;
  if (request.method === "GET" && path.endsWith("/health")) {
    return Response.json({
      status: "studio-shell-ready",
      generation: "not-configured",
      message: "The web interface is ready, but no private WanGP worker is connected."
    });
  }
  if (request.method === "POST" && path.endsWith("/generate")) {
    return Response.json({
      error: "GENERATION_NOT_CONFIGURED",
      message: "The WanGP generation worker is not connected yet. No video was generated."
    }, { status: 503 });
  }
  return Response.json({ error: "NOT_FOUND" }, { status: 404 });
};
export const config = { path: "/api/*" };
