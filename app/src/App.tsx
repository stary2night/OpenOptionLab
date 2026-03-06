import { useState } from 'react';
import { TrendingUp } from 'lucide-react';
import Navbar from '@/sections/Navbar';
import MarketOverview from '@/sections/MarketOverview';
import VolatilityPanel from '@/sections/VolatilityPanel';
import FlowMonitor from '@/sections/FlowMonitor';
import StrategyBuilder from '@/sections/StrategyBuilder';
import TradePanel from '@/sections/TradePanel';
import { useTheme } from '@/hooks/useTheme';
import type { TabType } from '@/types';
import './App.css';

// Main App Component
function App() {
  const [activeTab, setActiveTab] = useState<TabType>('market');
  const { theme, toggleTheme } = useTheme();

  const renderContent = () => {
    switch (activeTab) {
      case 'market':
        return <MarketOverview />;
      case 'volatility':
        return <VolatilityPanel />;
      case 'flow':
        return <FlowMonitor />;
      case 'strategy':
        return <StrategyBuilder />;
      case 'trade':
        return <TradePanel />;
      default:
        return <MarketOverview />;
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-300">
      {/* Background Grid */}
      <div className="fixed inset-0 bg-grid opacity-30 pointer-events-none transition-opacity duration-300" />
      
      {/* Navbar */}
      <Navbar 
        activeTab={activeTab} 
        onTabChange={setActiveTab}
        theme={theme}
        onToggleTheme={toggleTheme}
      />
      
      {/* Main Content */}
      <main className="relative z-10 w-full px-4 sm:px-6 lg:px-8 py-6">
        <div className="max-w-[1600px] mx-auto">
          {renderContent()}
        </div>
      </main>
      
      {/* Footer */}
      <footer className="relative z-10 border-t border-border/50 mt-12 transition-colors duration-300">
        <div className="w-full px-4 sm:px-6 lg:px-8 py-6">
          <div className="max-w-[1600px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded bg-primary/20">
                <TrendingUp className="h-4 w-4 text-primary" />
              </div>
              <span className="text-sm font-medium">
                OpenOptions<span className="text-primary">Lab</span>
              </span>
            </div>
            <div className="text-sm text-muted-foreground text-center">
              专业的期权数据分析平台 | 数据仅供参考，不构成投资建议
            </div>
            <div className="text-sm text-muted-foreground">
              © 2025 OpenOptions Lab
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
