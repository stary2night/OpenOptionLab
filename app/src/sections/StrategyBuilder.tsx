import { useState } from 'react';
import { 
  Layers, 
  Plus, 
  Trash2, 
  Save,
  Play,
  Calculator,
  Activity
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';


interface StrategyLeg {
  id: string;
  side: 'buy' | 'sell';
  optionType: 'call' | 'put';
  strike: number;
  expiry: string;
  quantity: number;
  price: number;
}

const strategyTemplates = [
  { id: 'long-call', name: '买入看涨', type: 'directional', description: '看涨市场，风险有限，收益无限' },
  { id: 'long-put', name: '买入看跌', type: 'directional', description: '看跌市场，风险有限，收益无限' },
  { id: 'bull-spread', name: '牛市价差', type: 'spread', description: '温和看涨，降低成本' },
  { id: 'bear-spread', name: '熊市价差', type: 'spread', description: '温和看跌，降低成本' },
  { id: 'iron-condor', name: '铁鹰价差', type: 'iron', description: '震荡市场，收取权利金' },
  { id: 'straddle', name: '跨式组合', type: 'volatility', description: '波动率交易，双向盈利' },
  { id: 'strangle', name: '宽跨式', type: 'volatility', description: '低成本波动率交易' },
  { id: 'calendar', name: '日历价差', type: 'calendar', description: '时间价值套利' },
];

export default function StrategyBuilder() {
  const [legs, setLegs] = useState<StrategyLeg[]>([
    { id: '1', side: 'buy', optionType: 'call', strike: 4.1, expiry: '2025-03-26', quantity: 1, price: 0.085 },
  ]);
  const [selectedSymbol, setSelectedSymbol] = useState('510300');

  const addLeg = () => {
    const newLeg: StrategyLeg = {
      id: Date.now().toString(),
      side: 'buy',
      optionType: 'call',
      strike: 4.0,
      expiry: '2025-03-26',
      quantity: 1,
      price: 0.05,
    };
    setLegs([...legs, newLeg]);
  };

  const removeLeg = (id: string) => {
    setLegs(legs.filter(l => l.id !== id));
  };

  const updateLeg = (id: string, field: keyof StrategyLeg, value: any) => {
    setLegs(legs.map(l => l.id === id ? { ...l, [field]: value } : l));
  };

  const calculatePayoff = () => {
    const netPremium = legs.reduce((sum, leg) => {
      const sign = leg.side === 'buy' ? -1 : 1;
      return sum + sign * leg.price * leg.quantity * 10000;
    }, 0);

    const maxRisk = Math.abs(netPremium);
    const maxReward = netPremium < 0 ? 'Unlimited' : 'Limited';

    return { netPremium, maxRisk, maxReward };
  };

  const payoff = calculatePayoff();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10">
            <Layers className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">策略构建器</h2>
            <p className="text-sm text-muted-foreground">可视化构建与回测期权策略</p>
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="gap-2">
            <Save className="h-4 w-4" />
            保存
          </Button>
          <Button size="sm" className="gap-2">
            <Play className="h-4 w-4" />
            回测
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel - Strategy Builder */}
        <div className="lg:col-span-2 space-y-4">
          {/* Symbol Selection */}
          <Card className="bg-card border-border/50">
            <CardContent className="p-4">
              <div className="flex flex-wrap gap-4 items-center">
                <div className="flex items-center gap-2">
                  <Label className="text-sm">标的:</Label>
                  <Select value={selectedSymbol} onValueChange={setSelectedSymbol}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="510300">沪深300ETF</SelectItem>
                      <SelectItem value="510500">中证500ETF</SelectItem>
                      <SelectItem value="159915">创业板ETF</SelectItem>
                      <SelectItem value="IM">中证1000期货</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="text-sm text-muted-foreground">
                  最新价: <span className="font-mono text-foreground">4.042</span>
                  <span className="text-up ml-2">+1.52%</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Strategy Legs */}
          <Card className="bg-card border-border/50">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">策略腿</CardTitle>
                <Button variant="outline" size="sm" onClick={addLeg} className="gap-1">
                  <Plus className="h-4 w-4" />
                  添加
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {legs.map((leg, index) => (
                <div 
                  key={leg.id} 
                  className="grid grid-cols-12 gap-2 items-center p-3 rounded-lg bg-secondary/30 border border-border/30"
                >
                  <div className="col-span-1 text-xs text-muted-foreground font-mono">
                    #{index + 1}
                  </div>
                  <div className="col-span-2">
                    <Select 
                      value={leg.side} 
                      onValueChange={(v) => updateLeg(leg.id, 'side', v)}
                    >
                      <SelectTrigger className="h-8 text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="buy">买入</SelectItem>
                        <SelectItem value="sell">卖出</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="col-span-2">
                    <Select 
                      value={leg.optionType} 
                      onValueChange={(v) => updateLeg(leg.id, 'optionType', v)}
                    >
                      <SelectTrigger className="h-8 text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="call">Call</SelectItem>
                        <SelectItem value="put">Put</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="col-span-2">
                    <Input
                      type="number"
                      step="0.001"
                      value={leg.strike}
                      onChange={(e) => updateLeg(leg.id, 'strike', parseFloat(e.target.value))}
                      className="h-8 text-xs font-mono"
                      placeholder="行权价"
                    />
                  </div>
                  <div className="col-span-2">
                    <Select 
                      value={leg.expiry} 
                      onValueChange={(v) => updateLeg(leg.id, 'expiry', v)}
                    >
                      <SelectTrigger className="h-8 text-xs">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="2025-03-26">3月</SelectItem>
                        <SelectItem value="2025-04-23">4月</SelectItem>
                        <SelectItem value="2025-06-25">6月</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="col-span-1">
                    <Input
                      type="number"
                      value={leg.quantity}
                      onChange={(e) => updateLeg(leg.id, 'quantity', parseInt(e.target.value))}
                      className="h-8 text-xs font-mono"
                    />
                  </div>
                  <div className="col-span-1">
                    <Input
                      type="number"
                      step="0.001"
                      value={leg.price}
                      onChange={(e) => updateLeg(leg.id, 'price', parseFloat(e.target.value))}
                      className="h-8 text-xs font-mono"
                      placeholder="价格"
                    />
                  </div>
                  <div className="col-span-1 flex justify-end">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => removeLeg(leg.id)}
                      className="h-8 w-8 p-0 text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Payoff Chart Placeholder */}
          <Card className="bg-card border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">盈亏分析</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] flex items-center justify-center bg-secondary/20 rounded-lg border border-border/30 border-dashed">
                <div className="text-center">
                  <Activity className="h-12 w-12 text-muted-foreground/30 mx-auto mb-3" />
                  <p className="text-sm text-muted-foreground">策略盈亏图将在此显示</p>
                  <p className="text-xs text-muted-foreground mt-1">添加至少两条腿以生成图表</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Panel - Analysis & Templates */}
        <div className="space-y-4">
          {/* Strategy Metrics */}
          <Card className="bg-card border-border/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Calculator className="h-4 w-4" />
                策略指标
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">净权利金</span>
                <span className={`font-mono font-medium ${
                  payoff.netPremium >= 0 ? 'text-up' : 'text-down'
                }`}>
                  {payoff.netPremium >= 0 ? '+' : ''}{payoff.netPremium.toFixed(0)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">最大风险</span>
                <span className="font-mono font-medium text-down">
                  -{payoff.maxRisk.toFixed(0)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">最大收益</span>
                <span className="font-mono font-medium text-up">
                  {payoff.maxReward === 'Unlimited' ? '无限' : payoff.maxReward}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">盈亏平衡点</span>
                <span className="font-mono font-medium">4.185 / 4.315</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">希腊字母风险</span>
                <Badge variant="outline" className="text-xs">Delta: 0.45</Badge>
              </div>
            </CardContent>
          </Card>

          {/* Strategy Templates */}
          <Card className="bg-card border-border/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">策略模板</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {strategyTemplates.map((template) => (
                <button
                  key={template.id}
                  className="w-full text-left p-3 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors border border-border/30 hover:border-primary/30"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm">{template.name}</span>
                    <Badge variant="secondary" className="text-[10px]">{template.type}</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">{template.description}</p>
                </button>
              ))}
            </CardContent>
          </Card>

          {/* Risk Warning */}
          <div className="p-4 rounded-lg bg-highlight/10 border border-highlight/30">
            <div className="flex items-start gap-2">
              <Activity className="h-4 w-4 text-highlight mt-0.5" />
              <div className="text-xs text-muted-foreground">
                <span className="text-highlight font-medium">风险提示:</span>
                {' '}期权交易涉及重大风险，可能导致本金损失。请确保您充分理解相关风险。
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
