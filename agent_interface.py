# agent_interface.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class DailyCheckRequest(BaseModel):
    user_address: str
    day_number: int
    victory_status: bool  # True = porn-free day

@app.post("/report-victory")
async def report_daily_victory(request: DailyCheckRequest):
    """Standardized endpoint for AI agents to report user progress"""
    # Implementation would interact with contract
    return {"tx_hash": "0x..."}

@app.get("/user-status/{address}")
async def get_user_status(address: str):
    """For AI agents to check user's staked days and progress"""
    return {
        "active_novena": True,
        "days_completed": 3,
        "eth_donated_to_anti_trafficking": "0.002 ETH"
    }