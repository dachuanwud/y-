import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowUp, ArrowDown, Activity } from 'lucide-react';
import { SummaryData, MetricItem } from '@/api';
import { cn } from '@/lib/utils';

interface SummaryCardsProps {
  summary: SummaryData | undefined;
  isLoading: boolean;
}

const MetricCard = ({ title, item, prefix = "" }: { title: string, item?: MetricItem, prefix?: string }) => {
  if (!item) return (
    <Card className="bg-card/50 backdrop-blur">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <Activity className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="h-8 w-24 animate-pulse rounded bg-muted"></div>
      </CardContent>
    </Card>
  );

  const isPositive = item.change > 0;
  const isNeutral = item.change === 0;
  
  return (
    <Card className="bg-card/50 backdrop-blur border-white/5 transition-all hover:bg-card/80 hover:border-white/10">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">{title}</CardTitle>
        {isPositive ? (
            <ArrowUp className="h-4 w-4 text-emerald-500" />
        ) : isNeutral ? (
            <Activity className="h-4 w-4 text-muted-foreground" />
        ) : (
            <ArrowDown className="h-4 w-4 text-rose-500" />
        )}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold tracking-tight tabular-nums text-foreground">
            {prefix}{item.value.toFixed(2)}
        </div>
        <p className={cn(
            "text-xs font-medium mt-1 flex items-center",
            isPositive ? "text-emerald-500" : isNeutral ? "text-muted-foreground" : "text-rose-500"
        )}>
          {isPositive ? "+" : ""}{item.change.toFixed(2)} (24h)
        </p>
        <p className="text-[10px] text-muted-foreground mt-2 text-right opacity-50">
            {item.date}
        </p>
      </CardContent>
    </Card>
  );
};

const SummaryCards: React.FC<SummaryCardsProps> = ({ summary, isLoading }) => {
  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
         {[1,2,3,4].map(i => <MetricCard key={i} title="Loading..." />)}
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <MetricCard 
        title="Y指数 (30天)" 
        item={summary?.y_idx_30} 
      />
      <MetricCard 
        title="Y指数 (90天)" 
        item={summary?.y_idx_90} 
      />
      <MetricCard 
        title="山寨指数 (30天)" 
        item={summary?.altcoin_30} 
      />
      <MetricCard 
        title="全市场涨跌 (30天)" 
        item={summary?.market_30} 
      />
    </div>
  );
};

export default SummaryCards;

