import { useState, useEffect } from 'react';
import { 
  Zap, 
  TrendingUp, 
  TrendingDown,
  Clock,
  Filter,
  Bell,
  ArrowRight,
  Flame,
  Activity
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { unusualFlows } from '@/data/marketData';
import type { UnusualFlow } from '@/types';

interface FlowCardProps {
  flow: UnusualFlow;
  index: number;
}

function FlowCard({ flow, index }: FlowCardProps) {
  const isCall = flow.optionType === 'call';
  const isBullish = flow.sentiment === 'bullish';
  
  return (
    <div 
      className="relative p-4 rounded-xl border border-border/50 bg-card hover:bg-secondary/20 transition-all duration-300 animate-slide-in"
      style={{ animationDelay: `${index * 50}ms` }}
    >
      {/* Glow effect for high premium */}
      {flow.premium > 3000000 && (
        <div className={`absolute inset-0 rounded-xl opacity-20 ${
          isBullish ? 'bg-up shadow-glow-up' : 'bg-down shadow-glow-down'
        }`} />
      )}
      
      <div className="relative">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className={`p-1.5 rounded-lg ${
              isCall ? 'bg-up/20' : 'bg-down/20'
            }`}>
              {isCall ? (
                <TrendingUp className={`h-4 w-4 ${isCall ? 'text-up' : 'text-down'}`} />
              ) : (
                <TrendingDown className="h-4 w-4 text-down" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold">{flow.symbol}</span>
                <Badge 
                  variant="secondary" 
                  className={`text-xs ${isCall ? 'bg-up/20 text-up' : 'bg-down/20 text-down'}`}
                >
                  {isCall ? 'CALL' : 'PUT'}
                </Badge>
              </div>
              <div className="text-xs text-muted-foreground font-mono">
                {flow.strike} | {flow.expiry}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            {flow.timestamp}
          </div>
        </div>
        
        <div className="grid grid-cols-3 gap-4 mb-3">
          <div>
            <div className="text-xs text-muted-foreground mb-1">成交量</div>
            <div className="font-mono font-medium">{flow.volume.toLocaleString()}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground mb-1">持仓量</div>
            <div className="font-mono font-medium">{flow.openInterest.toLocaleString()}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground mb-1">权利金</div>
            <div className={`font-mono font-medium ${
              flow.premium > 3000000 ? 'text-highlight' : ''
            }`}>
              ¥{(flow.premium / 10000).toFixed(1)}万
            </div>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <Badge 
            variant="outline" 
            className={`text-xs ${
              isBullish 
                ? 'border-up text-up bg-up/10' 
                : 'border-down text-down bg-down/10'
            }`}
          >
            {isBullish ? '看涨' : '看跌'}情绪
          </Badge>
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Activity className="h-3 w-3" />
            成交量/OI: {(flow.volume / flow.openInterest * 100).toFixed(1)}%
          </div>
        </div>
      </div>
    </div>
  );
}

export default function FlowMonitor() {
  const [flows, setFlows] = useState<UnusualFlow[]>(unusualFlows);
  const [filterType, setFilterType] = useState<string>('all');
  const [filterSentiment, setFilterSentiment] = useState<string>('all');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [minPremium, setMinPremium] = useState<string>('0');

  // Simulate real-time updates
  useEffect(() => {
    if (!autoRefresh) return;
    
    const interval = setInterval(() => {
      // Randomly update timestamps
      setFlows(prev => prev.map(flow => ({
        ...flow,
        timestamp: new Date().toTimeString().slice(0, 8)
      })));
    }, 5000);

    return () => clearInterval(interval);
  }, [autoRefresh]);

  const filteredFlows = flows.filter(flow => {
    if (filterType !== 'all' && flow.optionType !== filterType) return false;
    if (filterSentiment !== 'all' && flow.sentiment !== filterSentiment) return false;
    if (flow.premium < parseInt(minPremium) * 10000) return false;
    return true;
  });

  const stats = {
    total: flows.length,
    calls: flows.filter(f => f.optionType === 'call').length,
    puts: flows.filter(f => f.optionType === 'put').length,
    bullish: flows.filter(f => f.sentiment === 'bullish').length,
    bearish: flows.filter(f => f.sentiment === 'bearish').length,
    totalPremium: flows.reduce((sum, f) => sum + f.premium, 0),
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-highlight/10 animate-pulse-glow">
            <Zap className="h-5 w-5 text-highlight" />
          </div>
          <div>
            <h2 className="text-lg font-semibold">异动监控</h2>
            <p className="text-sm text-muted-foreground">实时追踪大额期权交易与异常成交</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Switch 
              id="auto-refresh" 
              checked={autoRefresh}
              onCheckedChange={setAutoRefresh}
            />
            <Label htmlFor="auto-refresh" className="text-sm">自动刷新</Label>
          </div>
          <Button variant="outline" size="sm" className="gap-2">
            <Bell className="h-4 w-4" />
            设置提醒
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <Card className="bg-card border-border/50">
          <CardContent className="p-3">
            <div className="text-xs text-muted-foreground">今日异动</div>
            <div className="text-xl font-bold font-mono">{stats.total}</div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border/50">
          <CardContent className="p-3">
            <div className="text-xs text-muted-foreground">Call 成交</div>
            <div className="text-xl font-bold font-mono text-up">{stats.calls}</div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border/50">
          <CardContent className="p-3">
            <div className="text-xs text-muted-foreground">Put 成交</div>
            <div className="text-xl font-bold font-mono text-down">{stats.puts}</div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border/50">
          <CardContent className="p-3">
            <div className="text-xs text-muted-foreground">看涨情绪</div>
            <div className="text-xl font-bold font-mono text-up">{stats.bullish}</div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border/50">
          <CardContent className="p-3">
            <div className="text-xs text-muted-foreground">看跌情绪</div>
            <div className="text-xl font-bold font-mono text-down">{stats.bearish}</div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border/50">
          <CardContent className="p-3">
            <div className="text-xs text-muted-foreground">总权利金</div>
            <div className="text-xl font-bold font-mono text-highlight">
              ¥{(stats.totalPremium / 1000000).toFixed(1)}M
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <Select value={filterType} onValueChange={setFilterType}>
          <SelectTrigger className="w-32 bg-secondary/50 border-border/50">
            <Filter className="h-4 w-4 mr-2" />
            <SelectValue placeholder="期权类型" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部类型</SelectItem>
            <SelectItem value="call">Call</SelectItem>
            <SelectItem value="put">Put</SelectItem>
          </SelectContent>
        </Select>

        <Select value={filterSentiment} onValueChange={setFilterSentiment}>
          <SelectTrigger className="w-32 bg-secondary/50 border-border/50">
            <TrendingUp className="h-4 w-4 mr-2" />
            <SelectValue placeholder="情绪" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部情绪</SelectItem>
            <SelectItem value="bullish">看涨</SelectItem>
            <SelectItem value="bearish">看跌</SelectItem>
          </SelectContent>
        </Select>

        <Select value={minPremium} onValueChange={setMinPremium}>
          <SelectTrigger className="w-40 bg-secondary/50 border-border/50">
            <Flame className="h-4 w-4 mr-2" />
            <SelectValue placeholder="最小权利金" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="0">全部</SelectItem>
            <SelectItem value="100">≥ 100万</SelectItem>
            <SelectItem value="300">≥ 300万</SelectItem>
            <SelectItem value="500">≥ 500万</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Flow Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredFlows.map((flow, index) => (
          <FlowCard key={flow.id} flow={flow} index={index} />
        ))}
      </div>

      {filteredFlows.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <Zap className="h-12 w-12 text-muted-foreground/30 mb-4" />
          <p className="text-muted-foreground">暂无符合条件的异动数据</p>
          <Button 
            variant="outline" 
            className="mt-4"
            onClick={() => {
              setFilterType('all');
              setFilterSentiment('all');
              setMinPremium('0');
            }}
          >
            重置筛选
          </Button>
        </div>
      )}

      {/* Load More */}
      {filteredFlows.length > 0 && (
        <div className="flex justify-center">
          <Button variant="outline" className="gap-2">
            加载更多
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
