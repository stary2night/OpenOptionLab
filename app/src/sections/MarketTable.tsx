import { useState, useMemo } from 'react';
import { 
  ArrowUpDown, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  Search,
  Download,
  ChevronUp,
  ChevronDown,
  Calendar,
  LayoutGrid,
  TrendingUp as TrendingUpIcon,
  Circle,
  Flame,
  Wheat,
  Mountain,
  Beaker,
  Zap,
  RefreshCw,
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import type { SymbolData } from '@/types/api';
import { categories, exchanges, generateSparklineData } from '@/data/marketData';
import { useSymbols } from '@/hooks';
import SparklineChart from '@/components/SparklineChart';
import GaugeChart from '@/components/GaugeChart';

type SortKey = keyof SymbolData;
type SortOrder = 'asc' | 'desc';

interface MarketTableProps {
  onSymbolClick?: (symbol: string) => void;
  filterCategory?: string;
  filterExchange?: string;
}

const categoryIcons: Record<string, React.ElementType> = {
  all: LayoutGrid,
  index: TrendingUpIcon,
  metal: Circle,
  energy: Flame,
  agri: Wheat,
  black: Mountain,
  chemical: Beaker,
  new: Zap,
};

export default function MarketTable({ 
  onSymbolClick, 
  filterCategory = 'all',
  filterExchange = 'all'
}: MarketTableProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortKey, setSortKey] = useState<SortKey>('priceChangePercent');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [localFilterCategory, setLocalFilterCategory] = useState(filterCategory);
  const [localFilterExchange, setLocalFilterExchange] = useState(filterExchange);
  const [showForeign, setShowForeign] = useState(true);

  // 使用 React Query 获取数据
  const { data: symbolsData, isLoading, refetch } = useSymbols({
    category: localFilterCategory,
    exchange: localFilterExchange,
    search: searchTerm,
    page: 1,
    pageSize: 100,
  });

  const filteredAndSortedData = useMemo(() => {
    let data = symbolsData?.items || [];

    // Filter foreign
    if (!showForeign) {
      data = data.filter((d: SymbolData) => !d.isForeign);
    }

    // Sort
    data.sort((a: SymbolData, b: SymbolData) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      
      if (aVal === null && bVal === null) return 0;
      if (aVal === null) return 1;
      if (bVal === null) return -1;
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
      }
      
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortOrder === 'asc' 
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }
      
      return 0;
    });

    return data;
  }, [symbolsData, sortKey, sortOrder, showForeign]);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortOrder('desc');
    }
  };

  const formatNumber = (val: number | null, decimals: number = 2) => {
    if (val === null || val === undefined) return '--';
    return val.toFixed(decimals);
  };

  const formatPercent = (val: number | null) => {
    if (val === null || val === undefined) return '--';
    const sign = val > 0 ? '+' : '';
    return `${sign}${val.toFixed(2)}%`;
  };

  const SortHeader = ({ label, tooltip, sortKey: key }: { label: string; tooltip?: string; sortKey: SortKey }) => (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            onClick={() => handleSort(key)}
            className="flex items-center gap-1 hover:text-primary transition-colors"
          >
            {label}
            {sortKey === key && (
              sortOrder === 'desc' ? <ChevronDown className="h-3 w-3" /> : <ChevronUp className="h-3 w-3" />
            )}
            {sortKey !== key && <ArrowUpDown className="h-3 w-3 opacity-30" />}
          </button>
        </TooltipTrigger>
        {tooltip && (
          <TooltipContent side="top" className="max-w-xs">
            <p className="text-xs">{tooltip}</p>
          </TooltipContent>
        )}
      </Tooltip>
    </TooltipProvider>
  );

  return (
    <TooltipProvider>
      <div className="space-y-4">
        {/* Filter Tabs - Categories */}
        <div className="flex flex-wrap gap-1.5">
          {categories.map((cat) => {
            const Icon = categoryIcons[cat.id] || LayoutGrid;
            const isActive = localFilterCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setLocalFilterCategory(cat.id)}
                className={`
                  flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all
                  ${isActive 
                    ? 'bg-primary text-primary-foreground' 
                    : 'bg-secondary/50 text-muted-foreground hover:bg-secondary hover:text-foreground'
                  }
                `}
              >
                <Icon className="h-3.5 w-3.5" />
                {cat.name}
              </button>
            );
          })}
        </div>

        {/* Filter Tabs - Exchanges */}
        <div className="flex flex-wrap gap-1">
          {exchanges.map((ex) => {
            const isActive = localFilterExchange === ex.id;
            return (
              <button
                key={ex.id}
                onClick={() => setLocalFilterExchange(ex.id)}
                className={`
                  px-2.5 py-1 rounded-md text-xs font-medium transition-all
                  ${isActive 
                    ? 'bg-secondary text-foreground border border-primary/50' 
                    : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50'
                  }
                `}
              >
                {ex.name}
              </button>
            );
          })}
        </div>

        {/* Toolbar */}
        <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between p-3 rounded-xl bg-card border border-border/50">
          <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
            {/* Search */}
            <div className="relative w-full sm:w-56">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="搜索品种..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 h-9 bg-secondary/50 border-border/50 text-sm"
              />
            </div>
            
            {/* Expiry Filter */}
            <Select defaultValue="all">
              <SelectTrigger className="w-36 h-9 bg-secondary/50 border-border/50 text-sm">
                <Calendar className="h-3.5 w-3.5 mr-2 text-muted-foreground" />
                <SelectValue placeholder="到期日" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部到期日</SelectItem>
                <SelectItem value="2025-03">2025年3月</SelectItem>
                <SelectItem value="2025-04">2025年4月</SelectItem>
                <SelectItem value="2025-05">2025年5月</SelectItem>
                <SelectItem value="2025-06">2025年6月</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center gap-3">
            {/* Foreign Toggle */}
            <div className="flex items-center gap-2">
              <Switch 
                id="show-foreign" 
                checked={showForeign}
                onCheckedChange={setShowForeign}
              />
              <Label htmlFor="show-foreign" className="text-sm text-muted-foreground">外盘</Label>
            </div>
            
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RefreshCw className="h-4 w-4" />
            </Button>
            
            <Button variant="outline" size="sm" className="gap-2 h-9">
              <Download className="h-4 w-4" />
              导出
            </Button>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto rounded-xl border border-border/50 bg-card">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border/50 bg-secondary/30">
                <th className="px-3 py-3 text-left font-medium text-muted-foreground whitespace-nowrap">
                  <SortHeader label="名称" sortKey="name" />
                </th>
                <th className="px-3 py-3 text-right font-medium text-muted-foreground whitespace-nowrap">
                  <SortHeader label="最新价" tooltip="标的最新成交价格" sortKey="latestPrice" />
                </th>
                <th className="px-3 py-3 text-right font-medium text-muted-foreground whitespace-nowrap">
                  <SortHeader label="标的涨幅%" tooltip="标的价格的涨跌幅，基于当前最新价格和前一交易日收盘价计算" sortKey="priceChangePercent" />
                </th>
                <th className="px-3 py-3 text-right font-medium text-muted-foreground whitespace-nowrap">
                  <SortHeader label="剩余时间" sortKey="daysToExpiry" />
                </th>
                <th className="px-3 py-3 text-right font-medium text-muted-foreground whitespace-nowrap">
                  <SortHeader label="当月隐波" tooltip="当月期权的隐含波动率" sortKey="impliedVol" />
                </th>
                <th className="px-3 py-3 text-right font-medium text-muted-foreground whitespace-nowrap">
                  <SortHeader label="隐波变化" tooltip="隐含波动率的变化值" sortKey="ivChange" />
                </th>
                <th className="px-3 py-3 text-right font-medium text-muted-foreground whitespace-nowrap">
                  <SortHeader label="隐波涨速" tooltip="隐含波动率的变化速度" sortKey="ivSpeed" />
                </th>
                <th className="px-3 py-3 text-right font-medium text-muted-foreground whitespace-nowrap">
                  <SortHeader label="实波" tooltip="历史实际波动率" sortKey="realizedVol" />
                </th>
                <th className="px-3 py-3 text-right font-medium text-muted-foreground whitespace-nowrap">
                  <SortHeader label="溢价" tooltip="隐含波动率与实际波动率的差值" sortKey="premium" />
                </th>
                <th className="px-3 py-3 text-right font-medium text-muted-foreground whitespace-nowrap">
                  <SortHeader label="当月偏度" tooltip="波动率偏度指标" sortKey="skew" />
                </th>
                <th className="px-3 py-3 text-center font-medium text-muted-foreground whitespace-nowrap">
                  <SortHeader label="隐波百分位" tooltip="当前隐含波动率在历史数据中的百分位位置" sortKey="ivPercentile" />
                </th>
                <th className="px-3 py-3 text-center font-medium text-muted-foreground whitespace-nowrap">
                  <SortHeader label="偏度百分位" tooltip="当前偏度在历史数据中的百分位位置" sortKey="skewPercentile" />
                </th>
                <th className="px-3 py-3 text-center font-medium text-muted-foreground whitespace-nowrap">
                  走势预览
                </th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                // Loading skeleton
                Array(10).fill(0).map((_, idx) => (
                  <tr key={idx} className="border-b border-border/30">
                    <td className="px-3 py-3"><Skeleton className="h-8 w-24" /></td>
                    <td className="px-3 py-3"><Skeleton className="h-8 w-20 ml-auto" /></td>
                    <td className="px-3 py-3"><Skeleton className="h-8 w-16 ml-auto" /></td>
                    <td className="px-3 py-3"><Skeleton className="h-8 w-12 ml-auto" /></td>
                    <td className="px-3 py-3"><Skeleton className="h-8 w-14 ml-auto" /></td>
                    <td className="px-3 py-3"><Skeleton className="h-8 w-14 ml-auto" /></td>
                    <td className="px-3 py-3"><Skeleton className="h-8 w-14 ml-auto" /></td>
                    <td className="px-3 py-3"><Skeleton className="h-8 w-14 ml-auto" /></td>
                    <td className="px-3 py-3"><Skeleton className="h-8 w-14 ml-auto" /></td>
                    <td className="px-3 py-3"><Skeleton className="h-8 w-14 ml-auto" /></td>
                    <td className="px-3 py-3"><Skeleton className="h-8 w-20 mx-auto" /></td>
                    <td className="px-3 py-3"><Skeleton className="h-8 w-12 mx-auto" /></td>
                    <td className="px-3 py-3"><Skeleton className="h-8 w-16 mx-auto" /></td>
                  </tr>
                ))
              ) : (
                filteredAndSortedData.map((row: SymbolData) => {
                  const sparklineData = generateSparklineData(20);
                  const isPriceUp = row.priceChangePercent > 0;
                  
                  return (
                    <tr 
                      key={row.id}
                      className="border-b border-border/30 hover:bg-secondary/20 transition-colors cursor-pointer"
                      onClick={() => onSymbolClick?.(row.symbol)}
                    >
                      <td className="px-3 py-3">
                        <div className="flex items-center gap-2">
                          <div className="flex flex-col">
                            <div className="flex items-center gap-1.5">
                              <span className="font-medium">{row.name}</span>
                              {row.isMain && (
                                <Badge variant="secondary" className="text-[10px] px-1 py-0 h-4">主</Badge>
                              )}
                              {row.isForeign && (
                                <Badge variant="outline" className="text-[10px] px-1 py-0 h-4 border-highlight text-highlight">外</Badge>
                              )}
                            </div>
                            <span className="text-xs text-muted-foreground font-mono">
                              {row.symbol} {row.expiry?.slice(2, 4)}
                            </span>
                          </div>
                        </div>
                      </td>
                      <td className="px-3 py-3 text-right">
                        <span className="font-mono font-medium tabular-nums">
                          {row.latestPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-right">
                        <div className={`flex items-center justify-end gap-1 font-mono ${
                          row.priceChangePercent > 0 ? 'text-up' : row.priceChangePercent < 0 ? 'text-down' : 'text-neutral'
                        }`}>
                          {row.priceChangePercent > 0 ? (
                            <TrendingUp className="h-3.5 w-3.5" />
                          ) : row.priceChangePercent < 0 ? (
                            <TrendingDown className="h-3.5 w-3.5" />
                          ) : (
                            <Minus className="h-3.5 w-3.5" />
                          )}
                          <span className="tabular-nums">{formatPercent(row.priceChangePercent)}</span>
                        </div>
                      </td>
                      <td className="px-3 py-3 text-right">
                        <span className="font-mono tabular-nums text-muted-foreground">
                          {row.daysToExpiry}天
                        </span>
                      </td>
                      <td className="px-3 py-3 text-right">
                        <span className="font-mono tabular-nums">
                          {formatNumber(row.impliedVol)}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-right">
                        <span className={`font-mono tabular-nums ${
                          (row.ivChange || 0) > 0 ? 'text-up' : (row.ivChange || 0) < 0 ? 'text-down' : ''
                        }`}>
                          {row.ivChange !== null && row.ivChange !== undefined
                            ? `${row.ivChange > 0 ? '+' : ''}${row.ivChange.toFixed(2)}`
                            : '--'}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-right">
                        <span className={`inline-block px-2 py-0.5 rounded text-xs font-mono ${
                          (row.ivSpeed || 0) > 0.5 ? 'bg-up/20 text-up' : 
                          (row.ivSpeed || 0) < -0.5 ? 'bg-down/20 text-down' : ''
                        }`}>
                          {formatNumber(row.ivSpeed, 3)}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-right">
                        <span className="font-mono tabular-nums text-muted-foreground">
                          {formatNumber(row.realizedVol)}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-right">
                        <span className={`font-mono tabular-nums ${
                          (row.premium || 0) > 0 ? 'text-up' : (row.premium || 0) < 0 ? 'text-down' : ''
                        }`}>
                          {formatNumber(row.premium)}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-right">
                        <span className="font-mono tabular-nums">
                          {formatNumber(row.skew, 2)}
                        </span>
                      </td>
                      <td className="px-3 py-3 text-center">
                        {row.ivPercentile !== null ? (
                          <div className="flex items-center justify-center gap-2">
                            <div className="w-14 h-2 bg-secondary rounded-full overflow-hidden">
                              <div 
                                className={`h-full rounded-full ${
                                  row.ivPercentile >= 80 ? 'bg-down' :
                                  row.ivPercentile >= 60 ? 'bg-highlight' :
                                  row.ivPercentile >= 40 ? 'bg-primary' :
                                  'bg-up'
                                }`}
                                style={{ width: `${row.ivPercentile}%` }}
                              />
                            </div>
                            <span className="font-mono text-xs tabular-nums w-8">{row.ivPercentile}%</span>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">--</span>
                        )}
                      </td>
                      <td className="px-3 py-3 text-center">
                        {row.skewPercentile !== null ? (
                          <div className="flex justify-center">
                            <GaugeChart value={row.skewPercentile} size={50} strokeWidth={4} />
                          </div>
                        ) : (
                          <span className="text-muted-foreground">--</span>
                        )}
                      </td>
                      <td className="px-3 py-3 text-center">
                        <SparklineChart 
                          data={sparklineData} 
                          width={70} 
                          height={25}
                          isPositive={isPriceUp}
                        />
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Summary Stats */}
        <div className="flex flex-wrap gap-4 text-sm text-muted-foreground px-1">
          <span>共 {filteredAndSortedData.length} 个品种</span>
          <span className="text-up">↑ 上涨: {filteredAndSortedData.filter((d: SymbolData) => d.priceChangePercent > 0).length}</span>
          <span className="text-down">↓ 下跌: {filteredAndSortedData.filter((d: SymbolData) => d.priceChangePercent < 0).length}</span>
          <span>平盘: {filteredAndSortedData.filter((d: SymbolData) => d.priceChangePercent === 0).length}</span>
        </div>
      </div>
    </TooltipProvider>
  );
}
