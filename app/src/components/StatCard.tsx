import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { TrendingUp, TrendingDown, Activity, BarChart3 } from 'lucide-react';
import SparklineChart from './SparklineChart';
import { generateSparklineData } from '@/data/marketData';

interface StatCardItem {
  id: string;
  symbol: string;
  name: string;
  impliedVol?: number;
  ivChange?: number;
  premium?: number;
  realizedVol?: number;
  category?: string;
}

interface StatCardProps {
  title: string;
  data: StatCardItem[];
  type: 'iv-rise' | 'iv-fall' | 'premium-high' | 'premium-low';
  isLoading?: boolean;
}

const typeConfig = {
  'iv-rise': {
    icon: TrendingUp,
    titleColor: 'text-up',
    bgColor: 'bg-up/10',
    valueKey: 'ivChange' as const,
    unit: '',
    showSparkline: true,
  },
  'iv-fall': {
    icon: TrendingDown,
    titleColor: 'text-down',
    bgColor: 'bg-down/10',
    valueKey: 'ivChange' as const,
    unit: '',
    showSparkline: true,
  },
  'premium-high': {
    icon: Activity,
    titleColor: 'text-highlight',
    bgColor: 'bg-highlight/10',
    valueKey: 'premium' as const,
    unit: '',
    showSparkline: false,
  },
  'premium-low': {
    icon: BarChart3,
    titleColor: 'text-primary',
    bgColor: 'bg-primary/10',
    valueKey: 'premium' as const,
    unit: '',
    showSparkline: false,
  },
};

export default function StatCard({ title, data, type, isLoading = false }: StatCardProps) {
  const config = typeConfig[type];
  const Icon = config.icon;

  if (isLoading) {
    return (
      <Card className="bg-card border-border/50 overflow-hidden">
        <CardContent className="p-4">
          <div className="flex items-center gap-2 mb-3">
            <Skeleton className="h-7 w-7 rounded-lg" />
            <Skeleton className="h-5 w-24" />
          </div>
          <div className="space-y-2">
            {Array(5).fill(0).map((_, idx) => (
              <div key={idx} className="flex items-center justify-between py-1.5 px-2">
                <div className="flex items-center gap-2">
                  <Skeleton className="h-4 w-4" />
                  <div className="flex flex-col">
                    <Skeleton className="h-4 w-16" />
                    <Skeleton className="h-3 w-10 mt-1" />
                  </div>
                </div>
                <Skeleton className="h-4 w-14" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-card border-border/50 overflow-hidden">
      <CardContent className="p-4">
        {/* Header */}
        <div className="flex items-center gap-2 mb-3">
          <div className={`p-1.5 rounded-lg ${config.bgColor}`}>
            <Icon className={`h-4 w-4 ${config.titleColor}`} />
          </div>
          <h3 className={`text-sm font-medium ${config.titleColor}`}>{title}</h3>
        </div>

        {/* List */}
        <div className="space-y-2">
          {data.length === 0 ? (
            <div className="text-center py-4 text-muted-foreground text-sm">
              暂无数据
            </div>
          ) : (
            data.map((item, idx) => {
              const value = config.valueKey === 'ivChange' ? item.ivChange : item.premium;
              const isPositive = (value || 0) >= 0;
              const sparklineData = generateSparklineData(15);

              return (
                <div 
                  key={item.id}
                  className="flex items-center justify-between py-1.5 px-2 rounded-lg hover:bg-secondary/30 transition-colors"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="text-xs text-muted-foreground w-4">{idx + 1}</span>
                    <div className="flex flex-col min-w-0">
                      <span className="text-sm font-medium truncate">{item.name}</span>
                      <span className="text-xs text-muted-foreground font-mono">{item.symbol}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3">
                    {/* Value */}
                    <span className={`text-sm font-mono font-medium ${
                      type === 'iv-rise' || type === 'premium-high'
                        ? isPositive ? 'text-up' : 'text-down'
                        : isPositive ? 'text-up' : 'text-down'
                    }`}>
                      {value !== null && value !== undefined
                        ? `${value > 0 && config.valueKey === 'ivChange' ? '+' : ''}${value.toFixed(2)}`
                        : '--'}
                    </span>
                    
                    {/* Sparkline for IV cards */}
                    {config.showSparkline && (
                      <div className="w-16">
                        <SparklineChart 
                          data={sparklineData} 
                          width={60} 
                          height={20}
                          isPositive={isPositive}
                        />
                      </div>
                    )}
                    
                    {/* IV/RV/Premium for premium cards */}
                    {!config.showSparkline && item.impliedVol && (
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span className="font-mono">IV:{item.impliedVol.toFixed(1)}</span>
                        {item.realizedVol && (
                          <span className="font-mono">RV:{item.realizedVol.toFixed(1)}</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </CardContent>
    </Card>
  );
}
