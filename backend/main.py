#!/usr/bin/env python3
import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    report_text: str = Field(..., min_length=1)
    report_type: str = Field(..., min_length=1)


class AnalyzeResponse(BaseModel):
    summary: str
    key_findings: List[str]
    recommendations: List[str]
    disclaimer: str


app = FastAPI(title="MedExplain AI API")

DISCLAIMER = (
    "This information is for education only and is not medical advice. "
    "Consult a licensed clinician for diagnosis or treatment."
)
KNOWN_FINDINGS = [
    "cardiomegaly",
    "pneumonia",
    "anemia",
    "elevated glucose",
    "cholesterol",
    "renal",
    "dehydration",
    "no acute disease",
]

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
    )
