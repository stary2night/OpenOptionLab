import { 
  TrendingUp, 
  BarChart3,
  Zap,
  Activity,
  ArrowRight,
  LayoutGrid,
  RefreshCw
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import MarketTable from '@/sections/MarketTable';
import StatCard from '@/components/StatCard';
import { 
  useMarketOverview,
  useIvRank,
  usePremiumRank,
  usePriceChangeRank,
  useRefreshMarketData,
} from '@/hooks';
import { marketData } from '@/data/marketData';

export default function MarketOverview() {
  // 使用 React Query 获取数据
  const { data: overview, isLoading: overviewLoading } = useMarketOverview();
  const { data: ivRankData, isLoading: ivRankLoading } = useIvRank(10);
  const { data: premiumRankData, isLoading: premiumLoading } = usePremiumRank(10);
  const { data: priceChangeData, isLoading: priceChangeLoading } = usePriceChangeRank(10);
  const refreshMutation = useRefreshMarketData();

  // 转换 API 数据为组件需要的格式
  const topIvRise = ivRankData?.filter(d => d.ivChange > 0).slice(0, 5).map(d => ({
    id: d.symbol,
    symbol: d.symbol,
    name: d.name,
    impliedVol: d.impliedVol,
    ivChange: d.ivChange,
    category: d.category,
  })) || [];

  const topIvFall = ivRankData?.filter(d => d.ivChange < 0).slice(0, 5).map(d => ({
    id: d.symbol,
    symbol: d.symbol,
    name: d.name,
    impliedVol: d.impliedVol,
    ivChange: d.ivChange,
    category: d.category,
  })) || [];

  const topPremiumHigh = premiumRankData?.filter(d => d.premium > 0).slice(0, 5).map(d => ({
    id: d.symbol,
    symbol: d.symbol,
    name: d.name,
    premium: d.premium,
    impliedVol: d.impliedVol,
    category: d.category,
  })) || [];

  const topPremiumLow = premiumRankData?.filter(d => d.premium <= 0).slice(0, 5).map(d => ({
    id: d.symbol,
    symbol: d.symbol,
    name: d.name,
    premium: d.premium,
    impliedVol: d.impliedVol,
    category: d.category,
  })) || [];

  const topGainers = priceChangeData?.filter(d => d.priceChangePercent > 0).slice(0, 5).map(d => ({
    id: d.symbol,
    symbol: d.symbol,
    name: d.name,
    latestPrice: d.latestPrice,
    priceChangePercent: d.priceChangePercent,
    category: d.category,
  })) || [];

  const highIv = ivRankData?.slice(0, 5).map(d => ({
    id: d.symbol,
    symbol: d.symbol,
    name: d.name,
    impliedVol: d.impliedVol,
    ivPercentile: d.ivPercentile,
    category: d.category,
  })) || [];

  // 处理刷新
  const handleRefresh = () => {
    refreshMutation.mutate();
  };

  return (
    <div className="space-y-6">
      {/* Header with refresh button */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">市场概览</h2>
          <p className="text-sm text-muted-foreground">实时行情数据监控</p>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleRefresh}
          disabled={refreshMutation.isPending}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${refreshMutation.isPending ? 'animate-spin' : ''}`} />
          刷新数据
        </Button>
      </div>

      {/* Hero Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-card border-border/50 overflow-hidden relative">
          <div className="absolute top-0 right-0 p-3 opacity-10">
            <LayoutGrid className="h-16 w-16" />
          </div>
          <CardContent className="p-4">
            <div className="text-sm text-muted-foreground mb-1">总品种数</div>
            {overviewLoading ? (
              <Skeleton className="h-9 w-20" />
            ) : (
              <div className="text-3xl font-bold font-mono">{overview?.total_symbols || marketData.length}</div>
            )}
            <div className="text-xs text-muted-foreground mt-2">覆盖期货与期权</div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border/50 overflow-hidden relative">
          <div className="absolute top-0 right-0 p-3 opacity-10">
            <TrendingUp className="h-16 w-16 text-up" />
          </div>
          <CardContent className="p-4">
            <div className="text-sm text-muted-foreground mb-1">IV 上升</div>
            {overviewLoading ? (
              <Skeleton className="h-9 w-20" />
            ) : (
              <div className="text-3xl font-bold font-mono text-up">
                {overview?.iv_rise_count || '-'}
              </div>
            )}
            <div className="text-xs text-up mt-2">今日隐波上涨</div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border/50 overflow-hidden relative">
          <div className="absolute top-0 right-0 p-3 opacity-10">
            <Activity className="h-16 w-16 text-primary" />
          </div>
          <CardContent className="p-4">
            <div className="text-sm text-muted-foreground mb-1">平均隐波</div>
            {overviewLoading ? (
              <Skeleton className="h-9 w-20" />
            ) : (
              <div className="text-3xl font-bold font-mono">
                {overview?.avg_iv ? overview.avg_iv.toFixed(1) : '-'}%
              </div>
            )}
            <div className="text-xs text-muted-foreground mt-2">加权平均</div>
          </CardContent>
        </Card>
        
        <Card className="bg-card border-border/50 overflow-hidden relative">
          <div className="absolute top-0 right-0 p-3 opacity-10">
            <Zap className="h-16 w-16 text-highlight" />
          </div>
          <CardContent className="p-4">
            <div className="text-sm text-muted-foreground mb-1">高 IV 品种</div>
            {overviewLoading ? (
              <Skeleton className="h-9 w-20" />
            ) : (
              <div className="text-3xl font-bold font-mono text-highlight">
                {overview?.high_iv_count || '-'}
              </div>
            )}
            <div className="text-xs text-highlight mt-2">IV 分位 &gt; 80%</div>
          </CardContent>
        </Card>
      </div>

      {/* Four Stat Cards - IV Rise/Fall, Premium High/Low */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <StatCard 
          title="隐波最大上升" 
          data={topIvRise} 
          type="iv-rise" 
          isLoading={ivRankLoading}
        />
        <StatCard 
          title="隐波最大下降" 
          data={topIvFall} 
          type="iv-fall" 
          isLoading={ivRankLoading}
        />
        <StatCard 
          title="波动率溢价最高" 
          data={topPremiumHigh} 
          type="premium-high" 
          isLoading={premiumLoading}
        />
        <StatCard 
          title="波动率溢价最低" 
          data={topPremiumLow} 
          type="premium-low" 
          isLoading={premiumLoading}
        />
      </div>

      {/* Top Movers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Gainers */}
        <Card className="bg-card border-border/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-up" />
                <h3 className="font-semibold">涨幅榜</h3>
              </div>
              <Button variant="ghost" size="sm" className="gap-1 text-xs">
                查看更多 <ArrowRight className="h-3 w-3" />
              </Button>
            </div>
            <div className="space-y-2">
              {priceChangeLoading ? (
                Array(5).fill(0).map((_, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-secondary/30">
                    <Skeleton className="h-12 w-full" />
                  </div>
                ))
              ) : (
                topGainers.slice(0, 5).map((item, idx) => (
                  <div 
                    key={item.symbol} 
                    className="flex items-center justify-between p-3 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-muted-foreground w-4">{idx + 1}</span>
                      <div>
                        <div className="font-medium">{item.name}</div>
                        <div className="text-xs text-muted-foreground font-mono">{item.symbol}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-mono font-medium">{item.latestPrice.toLocaleString()}</div>
                      <div className="text-up text-sm font-mono">+{item.priceChangePercent}%</div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* High IV */}
        <Card className="bg-card border-border/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-primary" />
                <h3 className="font-semibold">高波动率</h3>
              </div>
              <Button variant="ghost" size="sm" className="gap-1 text-xs">
                查看更多 <ArrowRight className="h-3 w-3" />
              </Button>
            </div>
            <div className="space-y-2">
              {ivRankLoading ? (
                Array(5).fill(0).map((_, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-secondary/30">
                    <Skeleton className="h-12 w-full" />
                  </div>
                ))
              ) : (
                highIv.slice(0, 5).map((item, idx) => (
                  <div 
                    key={item.symbol} 
                    className="flex items-center justify-between p-3 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-muted-foreground w-4">{idx + 1}</span>
                      <div>
                        <div className="font-medium">{item.name}</div>
                        <div className="text-xs text-muted-foreground font-mono">{item.symbol}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-mono font-medium">{item.impliedVol}%</div>
                      <div className="text-xs text-muted-foreground font-mono">
                        分位: {item.ivPercentile}%
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Full Market Table */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">市场行情</h3>
          <div className="flex gap-2">
            <Badge variant="secondary" className="text-xs">实时更新</Badge>
          </div>
        </div>
        <MarketTable />
      </div>
    </div>
  );
}
