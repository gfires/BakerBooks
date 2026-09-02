from pydantic import BaseModel, Field
from typing import List


class ReconcileRequest(BaseModel):
    cardholder_name: str = Field(..., min_length=1, description="Name of cardholder to filter")
    start_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Start date in YYYY-MM-DD format")
    expected_expenses: str = Field(..., description="Expected expenses text block (paste from Kristen's email)")
    sheet_link: str = Field(..., description="Link to the Google Sheets purchase form spreadsheet")

    class Config:
        json_schema_extra = {
            "example": {
                "cardholder_name": "Gavin Firestone (Treasurer)",
                "start_date": "2025-11-01",
                "expected_expenses": "11/1/25 - Trader Joe's - $25.25\n11/3/25 - Target - $9.99"
            }
        }


class ExpectedExpenseSchema(BaseModel):
    date: str
    vendor: str
    price: float

    @classmethod
    def from_dataclass(cls, exp):
        return cls(
            date=exp.date.isoformat(),
            vendor=exp.vendor,
            price=exp.price
        )


class ReportItemSchema(BaseModel):
    description: str
    activity: str
    date: str
    price: float
    vendor: str
    receipts: List[str]
    flyer: str
    needsAffidavit: bool

    @classmethod
    def from_dataclass(cls, item):
        return cls(
            description=item.description,
            activity=item.activity,
            date=item.date.isoformat(),
            price=item.price,
            vendor=item.vendor,
            receipts=item.receipts,
            flyer=item.flyer,
            needsAffidavit=item.needsAffidavit
        )


class MatchedPair(BaseModel):
    expected: ExpectedExpenseSchema
    actual: ReportItemSchema


class ReconcileResponse(BaseModel):
    matched: List[MatchedPair]
    unmatched_expected: List[ExpectedExpenseSchema]
    unmatched_actual: List[ReportItemSchema]


class AffidavitRequest(BaseModel):
    vendor: str = Field(..., min_length=1, description="Vendor name from expected expense")
    price: float = Field(..., gt=0, description="Price from expected expense")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date in YYYY-MM-DD format")
    cardholder_name: str = Field(..., min_length=1, description="Full cardholder name with role")
