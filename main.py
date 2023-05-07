import json
import translators
from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

PROJECT_NAME = "oasst-translate-plugin"
ACCOUNT_NAME = "someone13574"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/translate-text", operation_id="translateText", summary="Translate text from one language to another")
async def translate_text(src_text: str = Query(..., description="text to be translated"), src_lang: str = Query(..., description="language of text to be translated (i18n locale code or 'auto')"), dst_lang: str = Query(..., description="language to translate text to (i18n locale code)")) -> Response:
    try:
        translated_text = translators.translate_text(
            src_text, "google", src_lang, dst_lang, False)
        formatted_text = f"The translated text is: {translated_text}\nThought: I now know the final answer"
        return Response(content=formatted_text, media_type="text/plain")
    except Exception as err:
        print(err)
        error_message = f"Failed to translate with error: {err}. If this is due to the parameters which you supplied please correct them, if this error is outside of your control, please notify the user of the problem."
        return JSONResponse(content={"error": error_message}, status_code=500)


@app.get("/icon.png", include_in_schema=False)
async def api_icon():
    with open("icon.png", "rb") as f:
        icon = f.read()
    return Response(content=icon, media_type="image/png")


@app.get("/ai-plugin.json", include_in_schema=False)
async def api_ai_plugin():
    with open("ai-plugin.json", "r") as f:
        ai_plugin_json = json.load(f)
    return Response(content=json.dumps(ai_plugin_json), media_type="application/json")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Translator Plugin",
        version="0.1",
        routes=app.routes,
    )
    openapi_schema["servers"] = [
        {
            "url": f"https://{PROJECT_NAME}-{ACCOUNT_NAME}.vercel.app",
        },
    ]
    openapi_schema["tags"] = [
        {
            "name": "oasst-translate-plugin",
            "description": "",
        },
    ]
    openapi_schema.pop("components", None)
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
