from typing import Literal
from pydantic import BaseModel, Field


class MentalHealthInput(BaseModel):
    age: int = Field(..., ge=10, le=100, description="Age between 10 and 100")
    gender: Literal["Male", "Female"]
    country: str = Field(..., min_length=1, description="Country of residence")
    academic_level: Literal["High School", "Undergraduate", "Graduate"]
    most_used_platform: Literal[
        "Facebook",
        "Instagram",
        "Snapchat",
        "Twitter",
        "YouTube",
        "TikTok",
        "LinkedIn",
        "LINE",
        "KakaoTalk",
        "VKontakte",
        "WhatsApp",
        "WeChat",
    ]
    purpose_of_use: Literal["Networking", "Education", "Entertainment", "News"]
    avg_daily_usage_hours: float = Field(..., ge=0, le=24, description="Screen hours per day")
    daily_unlocks: int = Field(..., ge=0, description="Daily device unlocks")
    study_hours: float = Field(..., ge=0, le=24, description="Study hours per day")
    physical_activity_hours: float = Field(..., ge=0, le=24, description="Exercise hours per day")
    sleep_hours_per_night: float = Field(..., ge=0, le=24, description="Sleep hours per night")
    stress_level: Literal["Low", "Medium", "High", "Very High"]


class MentalHealthOutput(BaseModel):
    mental_health_score: float
    band: str
    context: str
