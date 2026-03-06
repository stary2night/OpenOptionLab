import { useState } from 'react';
import { 
  ShoppingCart, 
  TrendingUp, 
  TrendingDown,
  Wallet,
  History,
  BarChart3,
  Clock,
  AlertCircle
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { marketData } from '@/data/marketData';

export default function TradePanel() {
  const [selectedSymbol, setSelectedSymbol] = useState('510300');
  const [orderType, setOrderType] = useState<'limit' | 'market'>('limit');
  const [side, setSide] = useState<'buy' | 'sell'>('buy');
  const [quantity, setQuantity] = useState(1);
  const [price, setPrice] = useState('');

  const symbolData = marketData.find(d => d.symbol === selectedSymbol);

  const recentOrders = [
    { id: '1', symbol: '510300', side: 'buy', type: 'call', strike: 4.1, quantity: 2, price: 0.085, status: 'filled', time: '14:32:15' },
    { id: '2', symbol: '510500', side: 'sell', type: 'put', strike: 5.2, quantity: 1, price: 0.152, status: 'pending', time: '14:28:42' },
    { id: '3', symbol: 'IM', side: 'buy', type: 'call', strike: 6200, quantity: 3, price: 45.5, status: 'filled', time: '14:25:18' },
  ];

  const positions = [
    { symbol: '510300', type: 'call', strike: 4.0, quantity: 5, avgPrice: 0.12, currentPrice: 0.152, pnl: 1600, pnlPercent: 26.7 },
    { symbol: '510500', type: 'put', strike: 5.5, quantity: -2, avgPrice: 0.18, currentPrice: 0.145, pnl: 700, pnlPercent: 19.4 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10">
            <ShoppingCart className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">交易</h2>
            <p className="text-sm text-muted-foreground">快速下单与持仓管理</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm">
            <Wallet className="h-4 w-4 text-muted-foreground" />
            <span className="text-muted-foreground">可用资金:</span>
            <span className="font-mono font-medium">¥128,450.00</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Order Form */}
        <div className="space-y-4">
          <Card className="bg-card border-border/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-base">下单</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Symbol Selection */}
              <div className="space-y-2">
                <Label className="text-sm">标的</Label>
                <Select value={selectedSymbol} onValueChange={setSelectedSymbol}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="510300">沪深300ETF (510300)</SelectItem>
                    <SelectItem value="510500">中证500ETF (510500)</SelectItem>
                    <SelectItem value="159915">创业板ETF (159915)</SelectItem>
                    <SelectItem value="IM">中证1000期货 (IM)</SelectItem>
                  </SelectContent>
                </Select>
                {symbolData && (
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-muted-foreground">最新:</span>
                    <span className="font-mono">{symbolData.latestPrice}</span>
                    <span className={symbolData.priceChangePercent > 0 ? 'text-up' : 'text-down'}>
                      {symbolData.priceChangePercent > 0 ? '+' : ''}{symbolData.priceChangePercent}%
                    </span>
                  </div>
                )}
              </div>

              {/* Buy/Sell Toggle */}
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setSide('buy')}
                  className={`flex items-center justify-center gap-2 py-3 rounded-lg font-medium transition-all ${
                    side === 'buy'
                      ? 'bg-up text-white'
                      : 'bg-secondary/50 text-muted-foreground hover:bg-secondary'
                  }`}
                >
                  <TrendingUp className="h-4 w-4" />
                  买入
                </button>
                <button
                  onClick={() => setSide('sell')}
                  className={`flex items-center justify-center gap-2 py-3 rounded-lg font-medium transition-all ${
                    side === 'sell'
                      ? 'bg-down text-white'
                      : 'bg-secondary/50 text-muted-foreground hover:bg-secondary'
                  }`}
                >
                  <TrendingDown className="h-4 w-4" />
                  卖出
                </button>
              </div>

              {/* Option Selection */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label className="text-sm">期权类型</Label>
                  <Select defaultValue="call">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="call">认购 (Call)</SelectItem>
                      <SelectItem value="put">认沽 (Put)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label className="text-sm">到期月份</Label>
                  <Select defaultValue="2025-03">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="2025-03">2025年3月</SelectItem>
                      <SelectItem value="2025-04">2025年4月</SelectItem>
                      <SelectItem value="2025-06">2025年6月</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Strike Selection */}
              <div className="space-y-2">
                <Label className="text-sm">行权价</Label>
                <div className="grid grid-cols-4 gap-2">
                  {['3.9', '4.0', '4.1', '4.2'].map((strike) => (
                    <button
                      key={strike}
                      className="py-2 px-3 rounded-lg bg-secondary/50 hover:bg-secondary text-sm font-mono transition-colors"
                    >
                      {strike}
                    </button>
                  ))}
                </div>
              </div>

              {/* Order Type */}
              <div className="space-y-2">
                <Label className="text-sm">订单类型</Label>
                <div className="flex gap-2">
                  <button
                    onClick={() => setOrderType('limit')}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                      orderType === 'limit'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary/50 text-muted-foreground'
                    }`}
                  >
                    限价
                  </button>
                  <button
                    onClick={() => setOrderType('market')}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                      orderType === 'market'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-secondary/50 text-muted-foreground'
                    }`}
                  >
                    市价
                  </button>
                </div>
              </div>

              {/* Price & Quantity */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label className="text-sm">价格</Label>
                  <Input
                    type="number"
                    step="0.001"
                    placeholder="0.000"
                    value={price}
                    onChange={(e) => setPrice(e.target.value)}
                    className="font-mono"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-sm">数量 (张)</Label>
                  <Input
                    type="number"
                    min={1}
                    value={quantity}
                    onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                    className="font-mono"
                  />
                </div>
              </div>

              {/* Order Summary */}
              <div className="p-3 rounded-lg bg-secondary/30 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">预估权利金</span>
                  <span className="font-mono">
                    ¥{price ? (parseFloat(price) * quantity * 10000).toFixed(0) : '0'}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">手续费</span>
                  <span className="font-mono">¥{(quantity * 5).toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm font-medium pt-2 border-t border-border/30">
                  <span>合计</span>
                  <span className="font-mono">
                    ¥{price ? (parseFloat(price) * quantity * 10000 + quantity * 5).toFixed(0) : '0'}
                  </span>
                </div>
              </div>

              {/* Submit Button */}
              <Button 
                className={`w-full py-6 text-lg font-medium ${
                  side === 'buy' 
                    ? 'bg-up hover:bg-up/90' 
                    : 'bg-down hover:bg-down/90'
                }`}
              >
                {side === 'buy' ? '买入下单' : '卖出下单'}
              </Button>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-3">
            <Card className="bg-card border-border/50">
              <CardContent className="p-3">
                <div className="text-xs text-muted-foreground mb-1">今日成交</div>
                <div className="text-lg font-bold font-mono">12</div>
              </CardContent>
            </Card>
            <Card className="bg-card border-border/50">
              <CardContent className="p-3">
                <div className="text-xs text-muted-foreground mb-1">今日盈亏</div>
                <div className="text-lg font-bold font-mono text-up">+¥2,340</div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Positions & Orders */}
        <div className="lg:col-span-2 space-y-4">
          <Tabs defaultValue="positions" className="w-full">
            <TabsList className="bg-secondary/50 border-border/50">
              <TabsTrigger value="positions" className="gap-2">
                <BarChart3 className="h-4 w-4" />
                持仓
              </TabsTrigger>
              <TabsTrigger value="orders" className="gap-2">
                <History className="h-4 w-4" />
                委托
              </TabsTrigger>
              <TabsTrigger value="history" className="gap-2">
                <Clock className="h-4 w-4" />
                成交
              </TabsTrigger>
            </TabsList>

            <TabsContent value="positions" className="mt-4">
              <Card className="bg-card border-border/50">
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-border/50 bg-secondary/30">
                          <th className="px-4 py-3 text-left font-medium text-muted-foreground">品种</th>
                          <th className="px-4 py-3 text-left font-medium text-muted-foreground">类型</th>
                          <th className="px-4 py-3 text-right font-medium text-muted-foreground">持仓</th>
                          <th className="px-4 py-3 text-right font-medium text-muted-foreground">均价</th>
                          <th className="px-4 py-3 text-right font-medium text-muted-foreground">现价</th>
                          <th className="px-4 py-3 text-right font-medium text-muted-foreground">盈亏</th>
                          <th className="px-4 py-3 text-right font-medium text-muted-foreground">盈亏%</th>
                          <th className="px-4 py-3 text-center font-medium text-muted-foreground">操作</th>
                        </tr>
                      </thead>
                      <tbody>
                        {positions.map((pos, idx) => (
                          <tr key={idx} className="border-b border-border/30 hover:bg-secondary/20">
                            <td className="px-4 py-3">
                              <div className="font-medium">{pos.symbol}</div>
                              <div className="text-xs text-muted-foreground font-mono">{pos.strike}</div>
                            </td>
                            <td className="px-4 py-3">
                              <Badge 
                                variant="secondary" 
                                className={pos.type === 'call' ? 'bg-up/20 text-up' : 'bg-down/20 text-down'}
                              >
                                {pos.type.toUpperCase()}
                              </Badge>
                            </td>
                            <td className="px-4 py-3 text-right font-mono">
                              <span className={pos.quantity > 0 ? 'text-up' : 'text-down'}>
                                {pos.quantity > 0 ? '+' : ''}{pos.quantity}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-right font-mono">{pos.avgPrice}</td>
                            <td className="px-4 py-3 text-right font-mono">{pos.currentPrice}</td>
                            <td className="px-4 py-3 text-right">
                              <span className={pos.pnl >= 0 ? 'text-up' : 'text-down'}>
                                {pos.pnl >= 0 ? '+' : ''}¥{pos.pnl}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-right">
                              <span className={pos.pnlPercent >= 0 ? 'text-up' : 'text-down'}>
                                {pos.pnlPercent >= 0 ? '+' : ''}{pos.pnlPercent.toFixed(1)}%
                              </span>
                            </td>
                            <td className="px-4 py-3 text-center">
                              <div className="flex justify-center gap-2">
                                <Button variant="outline" size="sm" className="h-7 px-2 text-xs">
                                  平仓
                                </Button>
                                <Button variant="outline" size="sm" className="h-7 px-2 text-xs">
                                  加仓
                                </Button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="orders" className="mt-4">
              <Card className="bg-card border-border/50">
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-border/50 bg-secondary/30">
                          <th className="px-4 py-3 text-left font-medium text-muted-foreground">时间</th>
                          <th className="px-4 py-3 text-left font-medium text-muted-foreground">品种</th>
                          <th className="px-4 py-3 text-left font-medium text-muted-foreground">方向</th>
                          <th className="px-4 py-3 text-right font-medium text-muted-foreground">数量</th>
                          <th className="px-4 py-3 text-right font-medium text-muted-foreground">价格</th>
                          <th className="px-4 py-3 text-center font-medium text-muted-foreground">状态</th>
                          <th className="px-4 py-3 text-center font-medium text-muted-foreground">操作</th>
                        </tr>
                      </thead>
                      <tbody>
                        {recentOrders.map((order) => (
                          <tr key={order.id} className="border-b border-border/30 hover:bg-secondary/20">
                            <td className="px-4 py-3 text-muted-foreground font-mono">{order.time}</td>
                            <td className="px-4 py-3">
                              <div className="font-medium">{order.symbol}</div>
                              <div className="text-xs text-muted-foreground font-mono">{order.strike} {order.type.toUpperCase()}</div>
                            </td>
                            <td className="px-4 py-3">
                              <Badge 
                                variant="secondary" 
                                className={order.side === 'buy' ? 'bg-up/20 text-up' : 'bg-down/20 text-down'}
                              >
                                {order.side === 'buy' ? '买入' : '卖出'}
                              </Badge>
                            </td>
                            <td className="px-4 py-3 text-right font-mono">{order.quantity}</td>
                            <td className="px-4 py-3 text-right font-mono">{order.price}</td>
                            <td className="px-4 py-3 text-center">
                              <Badge 
                                variant="outline" 
                                className={order.status === 'filled' ? 'border-up text-up' : 'border-highlight text-highlight'}
                              >
                                {order.status === 'filled' ? '已成交' : '委托中'}
                              </Badge>
                            </td>
                            <td className="px-4 py-3 text-center">
                              {order.status === 'pending' && (
                                <Button variant="ghost" size="sm" className="h-7 px-2 text-xs text-down">
                                  撤单
                                </Button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="history" className="mt-4">
              <Card className="bg-card border-border/50">
                <CardContent className="p-8 text-center">
                  <History className="h-12 w-12 text-muted-foreground/30 mx-auto mb-3" />
                  <p className="text-muted-foreground">今日暂无成交记录</p>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Risk Warning */}
          <div className="flex items-start gap-2 p-4 rounded-lg bg-highlight/10 border border-highlight/30">
            <AlertCircle className="h-4 w-4 text-highlight mt-0.5" />
            <div className="text-xs text-muted-foreground">
              <span className="text-highlight font-medium">交易提示:</span>
              {' '}请确保您已充分了解期权交易风险。建议设置止损止盈，合理控制仓位。
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
