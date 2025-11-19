import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { useChartData } from '@/api';
import { Loader2, AlertCircle } from 'lucide-react';

interface ChartWidgetProps {
  title: string;
  description?: string;
  marketType: string;
  chartKey: string;
  dataKey: string; // Key in the data object to plot (e.g., 'Y_idx', '山寨指数')
  color?: string;
  height?: number;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border bg-popover p-3 shadow-md text-popover-foreground text-xs">
        <div className="mb-1 font-medium text-muted-foreground">
            {label ? format(parseISO(label), 'yyyy-MM-dd') : ''}
        </div>
        <div className="flex items-center gap-2 font-mono text-sm font-bold">
           <span className="h-2 w-2 rounded-full bg-[hsl(var(--primary))]"></span>
           {payload[0].value.toFixed(2)}
        </div>
      </div>
    );
  }
  return null;
};

const ChartWidget: React.FC<ChartWidgetProps> = ({
  title,
  description,
  marketType,
  chartKey,
  dataKey,
  color = "hsl(var(--chart-1))",
  height = 300
}) => {
  const { data: chartResponse, isLoading, isError } = useChartData(marketType, chartKey);
  
  const config = chartResponse?.config || {};
  const data = chartResponse?.data || [];

  // 动态生成参考线
  const renderReferenceLines = () => {
    const lines = [];
    if (config.axhline_high !== undefined) lines.push({ y: config.axhline_high, color: 'hsl(var(--destructive))' });
    if (config.axhline_low !== undefined) lines.push({ y: config.axhline_low, color: 'hsl(var(--chart-2))' });
    if (config.axhline_low2 !== undefined) lines.push({ y: config.axhline_low2, color: 'hsl(var(--muted-foreground))' });
    
    return lines.map((line, idx) => (
      <ReferenceLine 
        key={idx} 
        y={line.y} 
        stroke={line.color} 
        strokeDasharray="3 3" 
        strokeOpacity={0.5}
        label={{ 
            value: line.y, 
            position: 'insideRight', 
            fill: line.color, 
            fontSize: 10 
        }} 
      />
    ));
  };

  return (
    <Card className="col-span-1 overflow-hidden">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        {isLoading ? (
           <div className="flex h-[300px] w-full items-center justify-center text-muted-foreground">
             <Loader2 className="mr-2 h-5 w-5 animate-spin" /> 加载中...
           </div>
        ) : isError ? (
            <div className="flex h-[300px] w-full items-center justify-center text-destructive">
                <AlertCircle className="mr-2 h-5 w-5" /> 数据加载失败
            </div>
        ) : (
            <div style={{ height: height, width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                    <linearGradient id={`color${chartKey}`} x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={color} stopOpacity={0.3}/>
                        <stop offset="95%" stopColor={color} stopOpacity={0}/>
                    </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.4} />
                    <XAxis 
                        dataKey="date" 
                        tickFormatter={(str) => {
                            try {
                                return format(parseISO(str), 'MM-dd');
                            } catch {
                                return str;
                            }
                        }}
                        tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
                        axisLine={false}
                        tickLine={false}
                        minTickGap={30}
                    />
                    <YAxis 
                        domain={[config.min_val || 'auto', config.max_val || 'auto']}
                        tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 10 }}
                        axisLine={false}
                        tickLine={false}
                    />
                    <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'hsl(var(--muted-foreground))', strokeWidth: 1 }} />
                    {renderReferenceLines()}
                    <Area 
                        type="monotone" 
                        dataKey={dataKey} 
                        stroke={color} 
                        strokeWidth={2}
                        fillOpacity={1} 
                        fill={`url(#color${chartKey})`} 
                        isAnimationActive={true}
                    />
                </AreaChart>
                </ResponsiveContainer>
            </div>
        )}
      </CardContent>
    </Card>
  );
};

export default ChartWidget;

