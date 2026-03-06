import { useMemo } from 'react';

interface SparklineChartProps {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
  fillOpacity?: number;
  isPositive?: boolean;
}

export default function SparklineChart({
  data,
  width = 80,
  height = 30,
  color,
  fillOpacity = 0.2,
  isPositive = true,
}: SparklineChartProps) {
  const strokeColor = color || (isPositive ? 'hsl(145, 70%, 45%)' : 'hsl(0, 70%, 55%)');
  const fillColor = strokeColor;

  const pathD = useMemo(() => {
    if (data.length < 2) return '';
    
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;
    
    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * width;
      const y = height - ((value - min) / range) * height * 0.8 - height * 0.1;
      return { x, y };
    });
    
    // Create smooth line path
    let d = `M ${points[0].x} ${points[0].y}`;
    
    for (let i = 1; i < points.length; i++) {
      const prev = points[i - 1];
      const curr = points[i];
      const cpX = (prev.x + curr.x) / 2;
      d += ` C ${cpX} ${prev.y}, ${cpX} ${curr.y}, ${curr.x} ${curr.y}`;
    }
    
    return d;
  }, [data, width, height]);

  const areaD = useMemo(() => {
    if (data.length < 2) return '';
    
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;
    
    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * width;
      const y = height - ((value - min) / range) * height * 0.8 - height * 0.1;
      return { x, y };
    });
    
    let d = `M ${points[0].x} ${height}`;
    d += ` L ${points[0].x} ${points[0].y}`;
    
    for (let i = 1; i < points.length; i++) {
      const prev = points[i - 1];
      const curr = points[i];
      const cpX = (prev.x + curr.x) / 2;
      d += ` C ${cpX} ${prev.y}, ${cpX} ${curr.y}, ${curr.x} ${curr.y}`;
    }
    
    d += ` L ${points[points.length - 1].x} ${height} Z`;
    return d;
  }, [data, width, height]);

  return (
    <svg width={width} height={height} className="overflow-visible">
      <defs>
        <linearGradient id={`gradient-${isPositive}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={fillColor} stopOpacity={fillOpacity} />
          <stop offset="100%" stopColor={fillColor} stopOpacity={0} />
        </linearGradient>
      </defs>
      <path
        d={areaD}
        fill={`url(#gradient-${isPositive})`}
      />
      <path
        d={pathD}
        fill="none"
        stroke={strokeColor}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
