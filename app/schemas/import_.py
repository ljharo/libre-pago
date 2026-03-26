from enum import Enum

from pydantic import BaseModel


class SpreadsheetType(str, Enum):
    CLOSED_CONVERSATIONS = "closed_conversations"
    LIFECYCLES = "lifecycles"
    ADS = "ads"
    CSAT = "csat"


class ImportResponse(BaseModel):
    success: bool
    message: str
    rows_imported: int = 0
    rows_failed: int = 0
    errors: list[str] = []


class ImportTemplateResponse(BaseModel):
    spreadsheet_type: SpreadsheetType
    columns: list[str]
    sample_data: list[dict]
