import { useState, useMemo } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Area,
  ReferenceLine,
  ComposedChart,
  Bar
} from 'recharts';
import { 
  Activity, 
  Calendar,
  BarChart3,
  Layers
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { generateChartData, termStructureData } from '@/data/marketData';

const chartData = generateChartData(30);

const volatilityMetrics = [
  { label: '当前IV', value: '15.23', change: '-0.89', changePercent: '-5.5%', trend: 'down' as const },
  { label: '20日HV', value: '17.15', change: '+0.32', changePercent: '+1.9%', trend: 'up' as const },
  { label: 'IV百分位', value: '15%', change: '', changePercent: '历史低位', trend: 'neutral' as const },
  { label: 'IV-RV差', value: '-1.92', change: '', changePercent: '负溢价', trend: 'down' as const },
];

const skewData = [
  { strike: '90%', iv: 18.5, callVolume: 1200, putVolume: 3500 },
  { strike: '95%', iv: 16.8, callVolume: 2800, putVolume: 4200 },
  { strike: '100%', iv: 15.2, callVolume: 5600, putVolume: 4800 },
  { strike: '105%', iv: 16.5, callVolume: 4200, putVolume: 3200 },
  { strike: '110%', iv: 18.2, callVolume: 2100, putVolume: 1800 },
];

export default function VolatilityPanel() {
  const [selectedSymbol, setSelectedSymbol] = useState('510300');
  const [timeRange, setTimeRange] = useState('1M');

  const symbolTermStructure = useMemo(() => {
    return termStructureData.filter(d => d.symbol === selectedSymbol);
  }, [selectedSymbol]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10">
            <Activity className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">波动率分析</h2>
            <p className="text-sm text-muted-foreground">实时监控隐含波动率与历史波动率</p>
          </div>
        </div>
        
        <div className="flex gap-2">
          <Select value={selectedSymbol} onValueChange={setSelectedSymbol}>
            <SelectTrigger className="w-40 bg-secondary/50 border-border/50">
              <SelectValue placeholder="选择品种" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="510300">沪深300ETF</SelectItem>
              <SelectItem value="510500">中证500ETF</SelectItem>
              <SelectItem value="IM">中证1000期货</SelectItem>
              <SelectItem value="IF">沪深300期货</SelectItem>
              <SelectItem value="LC">碳酸锂</SelectItem>
              <SelectItem value="PT">铂</SelectItem>
            </SelectContent>
          </Select>
          
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-24 bg-secondary/50 border-border/50">
              <SelectValue placeholder="时间范围" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1W">1周</SelectItem>
              <SelectItem value="1M">1月</SelectItem>
              <SelectItem value="3M">3月</SelectItem>
              <SelectItem value="6M">6月</SelectItem>
              <SelectItem value="1Y">1年</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {volatilityMetrics.map((metric, idx) => (
          <Card key={idx} className="bg-card border-border/50">
            <CardContent className="p-4">
              <div className="text-sm text-muted-foreground mb-1">{metric.label}</div>
              <div className="flex items-end gap-2">
                <span className="text-2xl font-bold font-mono">{metric.value}</span>
                {metric.change && (
                  <span className={`text-sm font-mono mb-1 ${
                    metric.trend === 'up' ? 'text-up' : metric.trend === 'down' ? 'text-down' : 'text-neutral'
                  }`}>
                    {metric.change}
                  </span>
                )}
              </div>
              {metric.changePercent && (
                <Badge 
                  variant="secondary" 
                  className={`mt-2 text-xs ${
                    metric.trend === 'up' ? 'bg-up/20 text-up' : 
                    metric.trend === 'down' ? 'bg-down/20 text-down' : ''
                  }`}
                >
                  {metric.changePercent}
                </Badge>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts */}
      <Tabs defaultValue="iv-rv" className="w-full">
        <TabsList className="bg-secondary/50 border-border/50">
          <TabsTrigger value="iv-rv" className="gap-2">
            <Activity className="h-4 w-4" />
            IV/RV 走势
          </TabsTrigger>
          <TabsTrigger value="term" className="gap-2">
            <Calendar className="h-4 w-4" />
            期限结构
          </TabsTrigger>
          <TabsTrigger value="skew" className="gap-2">
            <BarChart3 className="h-4 w-4" />
            波动率偏度
          </TabsTrigger>
          <TabsTrigger value="surface" className="gap-2">
            <Layers className="h-4 w-4" />
            波动率曲面
          </TabsTrigger>
        </TabsList>

        <TabsContent value="iv-rv" className="mt-4">
          <Card className="bg-card border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                隐含波动率 vs 历史波动率
                <Badge variant="outline" className="text-xs">{selectedSymbol}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[350px]">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={chartData}>
                    <defs>
                      <linearGradient id="ivGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(210, 100%, 50%)" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="hsl(210, 100%, 50%)" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="rvGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(145, 70%, 45%)" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="hsl(145, 70%, 45%)" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
                    <XAxis 
                      dataKey="time" 
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={12}
                      tickLine={false}
                    />
                    <YAxis 
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={12}
                      tickLine={false}
                      domain={['dataMin - 2', 'dataMax + 2']}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                      }}
                      labelStyle={{ color: 'hsl(var(--foreground))' }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="iv" 
                      stroke="hsl(210, 100%, 50%)" 
                      strokeWidth={2}
                      fill="url(#ivGradient)"
                      name="隐含波动率"
                    />
                    <Area 
                      type="monotone" 
                      dataKey="rv" 
                      stroke="hsl(145, 70%, 45%)" 
                      strokeWidth={2}
                      fill="url(#rvGradient)"
                      name="历史波动率"
                    />
                    <ReferenceLine y={15.23} stroke="hsl(210, 100%, 50%)" strokeDasharray="5 5" opacity={0.5} />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="term" className="mt-4">
          <Card className="bg-card border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                期限结构
                <Badge variant="outline" className="text-xs">{selectedSymbol}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[350px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={symbolTermStructure.length > 0 ? symbolTermStructure : termStructureData.filter(d => d.symbol === '510300')}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
                    <XAxis 
                      dataKey="expiry" 
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={12}
                      tickLine={false}
                    />
                    <YAxis 
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={12}
                      tickLine={false}
                      domain={['dataMin - 1', 'dataMax + 1']}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                      }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="atmIv" 
                      stroke="hsl(210, 100%, 50%)" 
                      strokeWidth={3}
                      dot={{ fill: 'hsl(210, 100%, 50%)', r: 5 }}
                      name="ATM IV"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="skew25" 
                      stroke="hsl(45, 100%, 55%)" 
                      strokeWidth={2}
                      dot={{ fill: 'hsl(45, 100%, 55%)', r: 4 }}
                      name="25 Delta Skew"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="skew" className="mt-4">
          <Card className="bg-card border-border/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">波动率偏度与成交量分布</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[350px]">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={skewData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
                    <XAxis 
                      dataKey="strike" 
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={12}
                      tickLine={false}
                    />
                    <YAxis 
                      yAxisId="left"
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={12}
                      tickLine={false}
                      domain={['dataMin - 1', 'dataMax + 1']}
                    />
                    <YAxis 
                      yAxisId="right"
                      orientation="right"
                      stroke="hsl(var(--muted-foreground))"
                      fontSize={12}
                      tickLine={false}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                      }}
                    />
                    <Bar yAxisId="right" dataKey="callVolume" fill="hsl(210, 100%, 50%, 0.6)" name="Call 成交量" />
                    <Bar yAxisId="right" dataKey="putVolume" fill="hsl(0, 70%, 55%, 0.6)" name="Put 成交量" />
                    <Line 
                      yAxisId="left"
                      type="monotone" 
                      dataKey="iv" 
                      stroke="hsl(45, 100%, 55%)" 
                      strokeWidth={3}
                      dot={{ fill: 'hsl(45, 100%, 55%)', r: 5 }}
                      name="IV"
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="surface" className="mt-4">
          <Card className="bg-card border-border/50">
            <CardContent className="p-8">
              <div className="flex flex-col items-center justify-center h-[350px] text-center space-y-4">
                <Layers className="h-16 w-16 text-muted-foreground/50" />
                <div>
                  <h3 className="text-lg font-medium">3D 波动率曲面</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    交互式 3D 波动率曲面分析功能即将上线
                  </p>
                </div>
                <Badge variant="outline" className="text-highlight border-highlight">Pro 功能</Badge>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
