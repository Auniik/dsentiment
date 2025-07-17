

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query

from services.stock_service import StockDataService
from utils.response import api_response


router = APIRouter(prefix="/dse", tags=["dse"])

stock_service = StockDataService()


@router.get("/latest")
async def get_stock_data():
    """Get latest stock data"""
    try:
        data = await stock_service.get_stock_data()
        return api_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dsexdata")
async def get_dsex_data(symbol: Optional[str] = Query(None, description="Stock symbol to filter")):
    """Get DSEX data with optional symbol filter"""
    try:
        data = await stock_service.get_dsex_data(symbol)
        return api_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top30")
async def get_top30():
    """Get top 30 stocks data"""
    try:
        data = await stock_service.get_top30()
        return api_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical")
async def get_historical_data(
    startDate: str = Query(..., description="Start date"),
    endDate: str = Query(..., description="End date"),
    inst: str = Query("All Instrument", description="Trading code")
):
    """Get historical stock data"""
    try:
        data = await stock_service.get_historical_data(startDate, endDate, inst)
        return api_response(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))