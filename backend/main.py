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
    return AnalyzeResponse(
        summary="Analysis pending implementation.",
        key_findings=[],
        recommendations=[],
        disclaimer="For informational purposes only.",
    )
