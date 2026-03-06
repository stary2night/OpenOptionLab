

interface GaugeChartProps {
  value: number;
  size?: number;
  strokeWidth?: number;
}

export default function GaugeChart({
  value,
  size = 50,
  strokeWidth = 4,
}: GaugeChartProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * Math.PI; // Half circle
  const center = size / 2;

  // Determine color based on value
  const getColor = (v: number) => {
    if (v >= 80) return 'hsl(0, 70%, 55%)';    // High - red
    if (v >= 60) return 'hsl(45, 100%, 55%)';  // Medium-high - yellow
    if (v >= 40) return 'hsl(210, 100%, 50%)'; // Medium - blue
    if (v >= 20) return 'hsl(145, 70%, 45%)';  // Low-medium - green
    return 'hsl(145, 70%, 45%)';               // Very low - green
  };

  const color = getColor(value);
  const strokeDashoffset = circumference - (value / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size / 2 + 10 }}>
      <svg width={size} height={size / 2 + 5} className="overflow-visible">
        {/* Background arc */}
        <path
          d={`M ${strokeWidth / 2} ${center} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${center}`}
          fill="none"
          stroke="hsl(var(--muted))"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        {/* Value arc */}
        <path
          d={`M ${strokeWidth / 2} ${center} A ${radius} ${radius} 0 0 1 ${size - strokeWidth / 2} ${center}`}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{ transformOrigin: 'center', transform: 'rotate(0deg)' }}
          className="transition-all duration-500"
        />
        {/* Needle */}
        <line
          x1={center}
          y1={center}
          x2={center + radius * 0.85 * Math.cos(Math.PI - (value / 100) * Math.PI)}
          y2={center - radius * 0.85 * Math.sin(Math.PI - (value / 100) * Math.PI)}
          stroke={color}
          strokeWidth={2}
          strokeLinecap="round"
          className="transition-all duration-500"
        />
        {/* Center dot */}
        <circle
          cx={center}
          cy={center}
          r={3}
          fill="hsl(var(--foreground))"
        />
      </svg>
      {/* Value text */}
      <span 
        className="absolute text-xs font-mono font-medium"
        style={{ 
          bottom: -2, 
          color,
        }}
      >
        {value}
      </span>
    </div>
  );
}
