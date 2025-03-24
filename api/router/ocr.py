import base64
import json
import os

import pymupdf
from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from openai import OpenAI

OCR_MODEL = os.getenv("API_KEY_OCR_MODEL", "allenai/olmOCR-7B-0225-preview")
API_KEY_RUNPOD = os.getenv("API_KEY_OCR_LLM", "")
API_BASE_URL_OCR_MODEL = os.getenv(
    "API_BASE_URL_OCR_MODEL", "https://api.runpod.ai/v2/5hwezmg13oviky/openai/v1"
)

client = OpenAI(
    api_key=API_KEY_RUNPOD,
    base_url=API_BASE_URL_OCR_MODEL,
)

router = APIRouter(prefix="/ocr")


# This is a base prompt that will be used for training and running the fine tuned model
# It's simplified from the prompt which was used to generate the silver data, and can change from dataset to dataset
def build_finetuning_prompt(base_text: str) -> str:
    return (
        f"Below is the image of one page of a document, as well as some raw textual content that was previously extracted for it. "
        f"Just return the plain text representation of this document as if you were reading it naturally.\n"
        f"Do not hallucinate.\n"
        f"RAW_TEXT_START\n{base_text}\nRAW_TEXT_END"
    )


@router.post("/")
async def ocr_file(file: UploadFile):
    if file.content_type not in ["application/pdf", "image/png"]:
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDF and PNG are supported."
        )

    if file.content_type == "application/pdf":
        doc = pymupdf.open(file.file)
        text_pages = []
        for page in doc:
            pix = page.get_pixmap()
            page_image = base64.b64encode(pix.tobytes("png")).decode()
            text = page.get_text().encode("utf8")
            parsed_text = ocr_image(page_image, text)
            text_pages.append(parsed_text)

        return JSONResponse(content={"text": "---".join(text_pages)})

    elif file.content_type == "image/png":
        image = file.file.read()
        # Assuming you have a function `ocr_image` to process the image and extract text
        text = ocr_image(image)
        return JSONResponse(content={"text": text})


def ocr_image(image: bytes, text: str = "No text available") -> str:
    # Implement your OCR logic here
    img = base64.b64encode(image).decode()
    prompt = build_finetuning_prompt(text)

    # Build the full prompt
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img}"},
                },
            ],
        }
    ]

    response = client.chat.completions.create(
        model=OCR_MODEL,
        messages=messages,
        temperature=0.8,
        max_completion_tokens=2000,
        max_tokens=2001,
        presence_penalty=0.3,
        stream=False,
    )

    return json.loads(response.choices[0].message.content)["natural_text"]
