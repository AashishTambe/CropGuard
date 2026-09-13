"""Minimal Vercel health endpoint for the Streamlit project."""


def app(environ, start_response):
    body = b"CropGuard deployment is healthy. Run the Streamlit UI with streamlit run app.py."
    start_response(
        "200 OK",
        [
            ("Content-Type", "text/plain; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ],
    )
    return [body]
