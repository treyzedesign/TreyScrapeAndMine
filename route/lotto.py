from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from schema.lotto import WinningNumberCreate, WinningNumberResponse
from services.lotto import scrape_numbers, scrape_and_get_frequency, scrape_ontario_numbers, scrape_and_get_ontario49_frequency, scrape_lottario_wining_numbers, scrape_lottario_winning_frequency

from config.database import get_db
import asyncio

# Create an APIRouter instance with the prefix
router = APIRouter()
# lottomax
@router.get("/winning_numbers/{lottoname}", response_model=dict)
async def trigger_scraping(lottoname: str, db: Session = Depends(get_db)):
    """
        Triggers the background task to scrape lotto winning numbers.
    """
    try:
        query = await scrape_numbers(db, lottoname)
        if query:
            return FileResponse(
                path=query,
                filename=query,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        return {"status": 200,"message": "Successfully scraped", "data": query}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500
         
# This router gets the frequency of numbers occurred for either lotto-max or lotto-649
@router.get("/frequency_of_numbers/{lottoname}")
async def trigger_scraping(lottoname: str, db: Session = Depends(get_db)) -> dict:
    """
    Triggers the background task to scrape the frequency of Number Occurrence.
    
    Args:
        lottoname (str): The name of the lottery to scrape (e.g., "lotto-649").
        db (Session): Database session dependency.

    Returns:
        Dict: Status and message about the scraping task.
    """
    try:
        # Pass the 'lottoname' parameter to the scraping function
        query = await scrape_and_get_frequency(db, lottoname)
        if query:
            return FileResponse(
                path=query,
                filename=query,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        return {"status": 200, "message": f"Successfully scraped {lottoname}", "data": query}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500
    

# Ontario49
@router.get("/ontario/winning_numbers")
async def trigger_scraping(db: Session = Depends(get_db)) -> dict:
    """
   
    """
    try:
        query = await scrape_ontario_numbers(db)
        if query:
            return FileResponse(
                path=query,
                filename=query,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        return {"status": 200, "message": f"Successfully scraped {query}", "data": query}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


@router.get("/ontario/frequency_of_numbers")
async def trigger_scraping(db: Session = Depends(get_db)) -> dict:
    """
   
    """
    try:
        query = await scrape_and_get_ontario49_frequency(db)
        if query:
            return FileResponse(
                path=query,
                filename=query,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        return {"status": 200, "message": f"Successfully scraped {query}", "data": query}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@router.get("/lottario/winning_numbers")
async def trigger_scraping(db: Session = Depends(get_db)) -> dict:
    """
   
    """
    try:
        query = await scrape_lottario_wining_numbers(db)
        if query:
            return FileResponse(
                path=query,
                filename=query,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        return {"status": 200, "message": f"Successfully scraped {query}", "data": query}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500
    
@router.get("/lottario/frequency_of_numbers")
async def trigger_scraping(db: Session = Depends(get_db)) -> dict:
    """
    """
    try:
        query = await scrape_lottario_winning_frequency(db)
        if query:
            return FileResponse(
                path=query,
                filename=query,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        return {"status": 200, "message": f"Successfully scraped {query}", "data": query}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500