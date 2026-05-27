#!/usr/bin/env python3
import os
import re
from typing import List, Dict, Any, Optional, Tuple

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx


class AnalyzeRequest(BaseModel):
    report_text: str = Field(..., min_length=1)
    report_type: str = Field(..., min_length=1)


class AnalyzeResponse(BaseModel):
    summary: str
    key_findings: List[str]
    recommendations: List[str]
    disclaimer: str
    source: str
    parse_warning: bool = False  # True when the model response couldn't be fully parsed


app = FastAPI(title="MedExplain AI API")


@app.get("/")
def read_root():
    return {"message": "MedExplain AI API is running. POST to /api/analyze to use the model."}


@app.get("/health")
def health_check():
    return {"status": "ok"}


DISCLAIMER = (
    "This information is for education only and is not medical advice. "
    "Consult a licensed clinician for diagnosis or treatment."
)


HF_TOKEN = os.getenv("HF_TOKEN", "")
MODEL_NAME = os.getenv("MODEL_NAME", "baidu/ERNIE-4.5-VL-28B-A3B-Thinking")
HF_INFERENCE_URL = os.getenv("HF_INFERENCE_URL", f"https://api-inference.huggingface.co/models/{MODEL_NAME}")
MODEL_LOCAL_PATH = os.getenv("MODEL_LOCAL_PATH", "")
_LOCAL_MODEL: Optional[Tuple[Any, Any]] = None


def build_prompt(report_text: str, report_type: str) -> str:
    return (
        "System: You are MedExplain, a medical report explanation assistant.\n"
        "You must be clear, concise, and avoid giving medical advice.\n"
        f"User report type: {report_type}\n"
        f"User report text: {report_text}\n"
        "Task: Provide a structured explanation for a non-medical reader.\n"
        "Required format — use EXACTLY these labels:\n"
        "- Summary: <plain-language summary>\n"
        "- Key findings: <comma-separated list>\n"
        "- Recommendations: <safe next steps>\n"
        "- Disclaimer: <safety notice>\n"
    )

# Expanded keyword list — covers more common report terms
KNOWN_FINDINGS = [
    "cardiomegaly",
    "pneumonia",
    "anemia",
    "elevated glucose",
    "cholesterol",
    "renal",
    "dehydration",
    "no acute disease",
    "fracture",
    "effusion",
    "edema",
    "hypertension",
    "tachycardia",
    "atrial fibrillation",
    "infiltrate",
    "consolidation",
    "nodule",
    "mass",
    "obstruction",
    "ischemia",
]

# Label aliases the model might use instead of the exact prompt labels.
# Each tuple is (canonical_key, [accepted_prefixes]).
_LABEL_ALIASES: List[Tuple[str, List[str]]] = [
    ("summary",         ["summary", "overview", "impression", "conclusion", "assessment"]),
    ("key_findings",    ["key findings", "findings", "notable findings", "results", "abnormalities"]),
    ("recommendations", ["recommendations", "recommendation", "next steps", "plan", "follow-up", "follow up"]),
    ("disclaimer",      ["disclaimer", "note", "caution", "warning"]),
]


def _match_label(lowered: str) -> Optional[str]:
    """Return the canonical key if the line starts with a known label alias."""
    for canonical, aliases in _LABEL_ALIASES:
        for alias in aliases:
            if lowered.startswith(alias + ":") or lowered.startswith(alias + " -"):
                return canonical
    return None


def fallback_parse(report_text: str, report_type: str) -> AnalyzeResponse:
    lowered = report_text.lower()
    findings = [term for term in KNOWN_FINDINGS if term in lowered]
    if not findings:
        findings = ["no specific findings detected from provided text"]

    summary = f"This {report_type} report mentions {', '.join(findings)}."
    recommendations = [
        "Review this report with a licensed clinician.",
        "Seek urgent care if symptoms worsen or new symptoms appear.",
    ]

    return AnalyzeResponse(
        summary=summary,
        key_findings=findings,
        recommendations=recommendations,
        disclaimer=DISCLAIMER,
        source="fallback",
        parse_warning=False,
    )


def parse_structured_response(text: str, source: str) -> AnalyzeResponse:
    """
    Parse the model's free-text output into a structured response.

    Handles label aliases (e.g. "Overview:" → summary, "Impression:" → summary)
    so a single mis-label doesn't silently wipe the summary field.
    Sets parse_warning=True when the summary could not be extracted at all.
    """
    summary = ""
    findings: List[str] = []
    recommendations: List[str] = []
    disclaimer = DISCLAIMER

    for line in text.splitlines():
        cleaned = line.strip().lstrip("-•* ").strip()
        lowered = cleaned.lower()

        canonical = _match_label(lowered)
        if canonical is None:
            continue

        # Extract the value after the separator (":" or " -")
        sep = ":" if ":" in cleaned else "-"
        value = cleaned.split(sep, 1)[1].strip() if sep in cleaned else ""

        if canonical == "summary" and not summary:
            summary = value
        elif canonical == "key_findings" and not findings:
            findings = [item.strip() for item in re.split(r"[,;]", value) if item.strip()]
        elif canonical == "recommendations" and not recommendations:
            recommendations = [item.strip() for item in re.split(r"[,;]", value) if item.strip()]
        elif canonical == "disclaimer":
            disclaimer = value or disclaimer

    parse_warning = not bool(summary)

    if not summary:
        summary = "Summary unavailable from model response."
    if not findings:
        findings = ["not provided"]
    if not recommendations:
        recommendations = ["Review this report with a licensed clinician."]

    return AnalyzeResponse(
        summary=summary,
        key_findings=findings,
        recommendations=recommendations,
        disclaimer=disclaimer,
        source=source,
        parse_warning=parse_warning,
    )


def call_hf_inference(prompt: str) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 300}}
    retries = 2
    for attempt in range(retries + 1):
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(HF_INFERENCE_URL, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError:
            if attempt == retries:
                raise


def load_local_model() -> Tuple[Any, Any]:
    global _LOCAL_MODEL
    if _LOCAL_MODEL is not None:
        return _LOCAL_MODEL

    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    tokenizer = AutoTokenizer.from_pretrained(MODEL_LOCAL_PATH)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_LOCAL_PATH,
        device_map="auto",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )
    _LOCAL_MODEL = (model, tokenizer)
    return _LOCAL_MODEL


def call_local_inference(prompt: str) -> str:
    model, tokenizer = load_local_model()
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=300)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze_report(request: AnalyzeRequest) -> AnalyzeResponse:
    report_text = request.report_text.strip()
    report_type = request.report_type.strip()

    prompt = build_prompt(report_text, report_type)

    if MODEL_LOCAL_PATH and os.path.exists(MODEL_LOCAL_PATH):
        try:
            generated_text = call_local_inference(prompt)
            return parse_structured_response(generated_text, source="local_model")
        except Exception:
            return fallback_parse(report_text, report_type)

    try:
        result = call_hf_inference(prompt)
    except Exception:
        return fallback_parse(report_text, report_type)

    generated_text = ""
    if isinstance(result, list) and result:
        generated_text = result[0].get("generated_text", "")
    elif isinstance(result, dict) and "generated_text" in result:
        generated_text = result.get("generated_text", "")
    elif isinstance(result, dict) and "error" in result:
        return fallback_parse(report_text, report_type)

    if not generated_text:
        return fallback_parse(report_text, report_type)

    return parse_structured_response(generated_text, source="hf_inference")
