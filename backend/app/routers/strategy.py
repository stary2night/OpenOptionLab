"""
Strategy Analysis Router
"""
from typing import List, Optional, Dict, Any
from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

router = APIRouter()


# Pydantic models
class StrategyLeg(BaseModel):
    side: str = Field(..., description="buy or sell")
    option_type: str = Field(..., description="call, put, or stock")
    strike: float
    expiry: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., ge=0)


class StrategyAnalysisRequest(BaseModel):
    underlying_price: float = Field(..., gt=0)
    legs: List[StrategyLeg]
    

class PayoffPoint(BaseModel):
    price: float
    pnl: float


class StrategyAnalysisResponse(BaseModel):
    net_premium: float
    max_profit: Optional[str]
    max_loss: Optional[str]
    breakeven_points: List[float]
    payoff_curve: List[PayoffPoint]
    greeks: Dict[str, float]


def calculate_strategy_payoff(
    underlying_price: float,
    legs: List[StrategyLeg]
) -> StrategyAnalysisResponse:
    """
    Calculate strategy payoff analysis
    
    This is a simplified calculation. In production, you'd use more
    sophisticated models with proper option pricing (Black-Scholes, etc.)
    """
    # Calculate net premium
    net_premium = sum(
        leg.price * leg.quantity * (10000 if leg.option_type != 'stock' else 1) * 
        (1 if leg.side == 'sell' else -1)
        for leg in legs
    )
    
    # Generate payoff curve
    price_range = [underlying_price * (0.5 + i * 0.05) for i in range(21)]
    payoff_curve = []
    
    for price in price_range:
        pnl = net_premium
        for leg in legs:
            if leg.option_type == 'stock':
                # Stock position
                intrinsic = (price - leg.strike) * leg.quantity
                if leg.side == 'buy':
                    pnl += intrinsic
                else:
                    pnl -= intrinsic
            else:
                # Option position
                if leg.option_type == 'call':
                    intrinsic = max(0, price - leg.strike)
                else:  # put
                    intrinsic = max(0, leg.strike - price)
                
                option_value = intrinsic * leg.quantity * 10000
                if leg.side == 'buy':
                    pnl += option_value - leg.price * leg.quantity * 10000
                else:
                    pnl += leg.price * leg.quantity * 10000 - option_value
        
        payoff_curve.append(PayoffPoint(price=round(price, 2), pnl=round(pnl, 2)))
    
    # Find max profit/loss
    pnls = [p.pnl for p in payoff_curve]
    max_pnl = max(pnls)
    min_pnl = min(pnls)
    
    # Find breakeven points (where pnl = 0)
    breakeven_points = []
    for i in range(len(payoff_curve) - 1):
        if payoff_curve[i].pnl * payoff_curve[i + 1].pnl < 0:
            # Linear interpolation
            x1, y1 = payoff_curve[i].price, payoff_curve[i].pnl
            x2, y2 = payoff_curve[i + 1].price, payoff_curve[i + 1].pnl
            breakeven = x1 - y1 * (x2 - x1) / (y2 - y1)
            breakeven_points.append(round(breakeven, 2))
    
    # Simplified Greeks (placeholder)
    greeks = {
        "delta": round(sum(
            (0.5 if leg.option_type == 'call' else -0.5) * leg.quantity * (1 if leg.side == 'buy' else -1)
            for leg in legs if leg.option_type != 'stock'
        ), 4),
        "gamma": 0.0,
        "theta": 0.0,
        "vega": 0.0,
    }
    
    return StrategyAnalysisResponse(
        net_premium=round(net_premium, 2),
        max_profit="Unlimited" if max_pnl > 1000000 else str(round(max_pnl, 2)),
        max_loss="Unlimited" if min_pnl < -1000000 else str(round(min_pnl, 2)),
        breakeven_points=breakeven_points,
        payoff_curve=payoff_curve,
        greeks=greeks
    )


@router.post("/analyze", response_model=StrategyAnalysisResponse)
async def analyze_strategy(request: StrategyAnalysisRequest):
    """
    Analyze an options strategy
    
    Calculates payoff curve, max profit/loss, breakeven points, and Greeks.
    """
    return calculate_strategy_payoff(request.underlying_price, request.legs)


@router.get("/templates")
async def get_strategy_templates():
    """Get predefined strategy templates"""
    templates = [
        {
            "id": "long-call",
            "name": "买入看涨",
            "type": "directional",
            "description": "看涨市场，风险有限，收益无限",
            "legs": [
                {"side": "buy", "option_type": "call", "strike": 100, "quantity": 1}
            ]
        },
        {
            "id": "long-put",
            "name": "买入看跌",
            "type": "directional",
            "description": "看跌市场，风险有限，收益无限",
            "legs": [
                {"side": "buy", "option_type": "put", "strike": 100, "quantity": 1}
            ]
        },
        {
            "id": "bull-spread",
            "name": "牛市价差",
            "type": "spread",
            "description": "温和看涨，降低成本",
            "legs": [
                {"side": "buy", "option_type": "call", "strike": 100, "quantity": 1},
                {"side": "sell", "option_type": "call", "strike": 110, "quantity": 1}
            ]
        },
        {
            "id": "bear-spread",
            "name": "熊市价差",
            "type": "spread",
            "description": "温和看跌，降低成本",
            "legs": [
                {"side": "buy", "option_type": "put", "strike": 100, "quantity": 1},
                {"side": "sell", "option_type": "put", "strike": 90, "quantity": 1}
            ]
        },
        {
            "id": "iron-condor",
            "name": "铁鹰价差",
            "type": "iron",
            "description": "震荡市场，收取权利金",
            "legs": [
                {"side": "sell", "option_type": "put", "strike": 90, "quantity": 1},
                {"side": "buy", "option_type": "put", "strike": 85, "quantity": 1},
                {"side": "sell", "option_type": "call", "strike": 110, "quantity": 1},
                {"side": "buy", "option_type": "call", "strike": 115, "quantity": 1}
            ]
        },
        {
            "id": "straddle",
            "name": "跨式组合",
            "type": "volatility",
            "description": "波动率交易，双向盈利",
            "legs": [
                {"side": "buy", "option_type": "call", "strike": 100, "quantity": 1},
                {"side": "buy", "option_type": "put", "strike": 100, "quantity": 1}
            ]
        },
        {
            "id": "strangle",
            "name": "宽跨式",
            "type": "volatility",
            "description": "低成本波动率交易",
            "legs": [
                {"side": "buy", "option_type": "call", "strike": 105, "quantity": 1},
                {"side": "buy", "option_type": "put", "strike": 95, "quantity": 1}
            ]
        },
        {
            "id": "calendar",
            "name": "日历价差",
            "type": "calendar",
            "description": "时间价值套利",
            "legs": [
                {"side": "sell", "option_type": "call", "strike": 100, "expiry": "near", "quantity": 1},
                {"side": "buy", "option_type": "call", "strike": 100, "expiry": "far", "quantity": 1}
            ]
        },
    ]
    
    return templates
