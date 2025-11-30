from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import csv, io

from app.schemas import CustomerIn
from app.models import Customer
from app.database import get_db
from app.auth import get_current_user

router = APIRouter()

@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV allowed")

    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))

    success, errors = 0, []

    for row in reader:
        try:
            validated = CustomerIn(
                name=row["name"].strip(),
                email=row["email"].strip(),
                age=int(row["age"])
            )

            entry = Customer(
                name=validated.name,
                email=validated.email,
                age=validated.age,
            )
            db.add(entry)
            db.commit()
            success += 1

        except Exception as e:
            db.rollback()
            errors.append({"record": row, "error": str(e)})

    return {
        "status": "Completed",
        "success_count": success,
        "error_count": len(errors),
        "errors": errors
    }
