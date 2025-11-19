import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useSummary, useRefreshData } from './api';
import SummaryCards from './components/dashboard/SummaryCards';
import ChartWidget from './components/dashboard/ChartWidget';
import { Button } from '@/components/ui/card'; // We need a real button, let's just use HTML button for now styled with Tailwind
import { RefreshCw, LayoutDashboard, PieChart, Activity as ActivityIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

// Initialize Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const Dashboard = () => {
  const [marketType, setMarketType] = useState<string>('spot');
  const { data: summary, isLoading: isSummaryLoading } = useSummary(marketType);
  const refreshMutation = useRefreshData();

  const handleRefresh = () => {
    refreshMutation.mutate();
  };

  return (
    <div className="min-h-screen bg-background font-sans text-foreground p-6 md:p-8 space-y-8">
      {/* Header */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/40 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
            Crypto Market Index
          </h1>
          <p className="text-muted-foreground mt-1">
             实时监控山寨指数、市场涨跌幅和Y指数趋势
          </p>
        </div>
        
        <div className="flex items-center gap-4 bg-card/30 p-1.5 rounded-lg border border-border/50 backdrop-blur-sm">
          <button
            onClick={() => setMarketType('spot')}
            className={cn(
              "px-4 py-2 rounded-md text-sm font-medium transition-all duration-200",
              marketType === 'spot' 
                ? "bg-primary text-primary-foreground shadow-lg" 
                : "text-muted-foreground hover:bg-white/5"
            )}
          >
            现货 Spot
          </button>
          <button
            onClick={() => setMarketType('swap')}
            className={cn(
              "px-4 py-2 rounded-md text-sm font-medium transition-all duration-200",
              marketType === 'swap' 
                ? "bg-primary text-primary-foreground shadow-lg" 
                : "text-muted-foreground hover:bg-white/5"
            )}
          >
            合约 Swap
          </button>
          
          <div className="w-px h-6 bg-border mx-2"></div>

          <button
            onClick={handleRefresh}
            disabled={refreshMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={cn("h-4 w-4", refreshMutation.isPending && "animate-spin")} />
            {refreshMutation.isPending ? "计算中..." : "刷新数据"}
          </button>
        </div>
      </header>

      {/* Metrics Cards */}
      <section>
        <div className="flex items-center gap-2 mb-4">
            <LayoutDashboard className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">核心指标</h2>
        </div>
        <SummaryCards summary={summary} isLoading={isSummaryLoading} />
      </section>

      {/* Y-Index Charts */}
      <section className="space-y-4">
        <div className="flex items-center gap-2 mb-4 pt-4 border-t border-border/40">
            <ActivityIcon className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">Y指数趋势</h2>
            <span className="text-xs text-muted-foreground ml-2 bg-muted px-2 py-0.5 rounded">市场热度综合指标</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ChartWidget 
            title="Y指数 (30天)" 
            description="30天短期市场情绪波动"
            marketType={marketType} 
            chartKey="y_idx_30" 
            dataKey="Y_idx"
            color="hsl(var(--chart-1))"
          />
          <ChartWidget 
            title="Y指数 (90天)" 
            description="90天中期趋势判断 (高位>150 过热)"
            marketType={marketType} 
            chartKey="y_idx_90" 
            dataKey="Y_idx90"
            color="hsl(var(--chart-4))"
          />
        </div>
      </section>

      {/* Altcoin & Market Charts */}
      <section className="space-y-4">
        <div className="flex items-center gap-2 mb-4 pt-4 border-t border-border/40">
            <PieChart className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold">山寨指数与市场涨跌</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
           <ChartWidget 
            title="山寨指数 (30天)" 
            marketType={marketType} 
            chartKey="altcoin_30" 
            dataKey="山寨指数"
            color="hsl(var(--chart-2))"
            height={250}
          />
           <ChartWidget 
            title="山寨指数 (90天)" 
            marketType={marketType} 
            chartKey="altcoin_90" 
            dataKey="山寨指数"
            color="hsl(var(--chart-2))"
            height={250}
          />
          <ChartWidget 
            title="市场涨跌幅 (30天)" 
            marketType={marketType} 
            chartKey="market_30" 
            dataKey="全市场涨跌幅指数30d"
            color="hsl(var(--chart-5))"
            height={250}
          />
        </div>
      </section>

      <footer className="pt-8 pb-4 text-center text-sm text-muted-foreground border-t border-border/40 mt-8">
        <p> Crypto Dashboard v2.0 • {new Date().getFullYear()} </p>
      </footer>
    </div>
  );
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  );
}

export default App;
