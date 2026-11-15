from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.pdf.generator import generate_affidavit
from backend.schemas import AffidavitRequest

router = APIRouter(prefix="/api")


@router.post("/generate-affidavit")
async def generate_affidavit_endpoint(request: AffidavitRequest):
    """
    Generate affidavit PDF from expense data.

    - **vendor**: Vendor name from expected expense
    - **price**: Price from expected expense
    - **date**: Date in YYYY-MM-DD format
    - **cardholder_name**: Full cardholder name with role

    Returns PDF binary stream.
    """
    try:
        pdf_bytes = generate_affidavit(
            vendor=request.vendor,
            price=request.price,
            date=request.date,
            cardholder_name=request.cardholder_name
        )

        filename = f"affidavit_{request.vendor.replace(' ', '_')}_{request.date}.pdf"

        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=f"Template file not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Affidavit generation failed: {str(e)}")
