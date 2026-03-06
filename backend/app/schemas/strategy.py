"""
Strategy Analysis Schemas
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class StrategyLeg(BaseModel):
    """Strategy leg"""
    symbol: str = Field(..., description="Option symbol")
    side: str = Field(..., pattern=r'^(buy|sell)$', description="buy or sell")
    quantity: int = Field(..., gt=0, description="Number of contracts")
    option_type: Optional[str] = Field(None, pattern=r'^(call|put)$')
    strike: Optional[float] = None
    expiry: Optional[str] = None
    price: Optional[float] = None


class StrategyAnalysisRequest(BaseModel):
    """Strategy analysis request"""
    underlying_symbol: str = Field(..., description="Underlying symbol")
    underlying_price: Optional[float] = None
    legs: List[StrategyLeg] = Field(..., min_length=1)
    analysis_price_range: Optional[tuple[float, float]] = Field(
        default=(0.8, 1.2),
        description="Price range for analysis (as ratio of underlying price)"
    )


class PayoffPoint(BaseModel):
    """Payoff curve point"""
    underlying_price: float
    payoff: float
    pnl: float
    pnl_percent: float


class GreeksSummary(BaseModel):
    """Combined greeks for strategy"""
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float


class StrategyMetrics(BaseModel):
    """Strategy metrics"""
    max_profit: Optional[float]
    max_loss: Optional[float]
    break_even_points: List[float]
    probability_of_profit: float
    risk_reward_ratio: Optional[float]
    initial_capital: float


class StrategyAnalysisResponse(BaseModel):
    """Strategy analysis response"""
    underlying_symbol: str
    underlying_price: float
    strategy_type: str
    legs: List[StrategyLeg]
    metrics: StrategyMetrics
    greeks: GreeksSummary
    payoff_curve: List[PayoffPoint]
    expiration_payoff: List[PayoffPoint]


class StrategyTemplate(BaseModel):
    """Strategy template"""
    id: str
    name: str
    description: str
    category: str
    leg_count: int
    default_legs: List[Dict[str, Any]]
    parameters: Optional[Dict[str, Any]]


class StrategyTemplateResponse(BaseModel):
    """Strategy template response"""
    templates: List[StrategyTemplate]


class BacktestRequest(BaseModel):
    """Strategy backtest request"""
    strategy_id: Optional[str]
    legs: Optional[List[StrategyLeg]]
    start_date: str
    end_date: str
    initial_capital: float = Field(default=100000)
    commission_per_trade: float = Field(default=5.0)


class BacktestTrade(BaseModel):
    """Backtest trade record"""
    timestamp: str
    action: str
    symbol: str
    quantity: int
    price: float
    pnl: float


class BacktestResult(BaseModel):
    """Backtest result"""
    total_return: float
    total_return_percent: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_percent: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_profit: float
    avg_loss: float
    profit_factor: float
    equity_curve: List[Dict[str, Any]]
    trades: List[BacktestTrade]


class RiskAnalysisRequest(BaseModel):
    """Risk analysis request"""
    strategy_id: Optional[str]
    legs: Optional[List[StrategyLeg]]
    scenarios: Optional[List[Dict[str, Any]]] = None


class RiskScenario(BaseModel):
    """Risk scenario result"""
    name: str
    underlying_price_change: float
    iv_change: float
    time_decay_days: int
    estimated_pnl: float
    estimated_pnl_percent: float


class RiskAnalysisResponse(BaseModel):
    """Risk analysis response"""
    current_exposure: Dict[str, float]
    scenarios: List[RiskScenario]
    var_95: float  # Value at Risk (95% confidence)
    var_99: float  # Value at Risk (99% confidence)
    expected_shortfall: float
