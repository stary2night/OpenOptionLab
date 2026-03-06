import { useState } from 'react';
import { 
  BarChart3, 
  Activity, 
  TrendingUp, 
  Zap, 
  Layers, 
  ShoppingCart, 
  Users, 
  Crown,
  ChevronDown,
  Menu,
  X,
  Sun,
  Moon
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import type { TabType } from '@/types';

interface NavbarProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
}

const navItems = [
  { id: 'market' as TabType, label: '行情', icon: BarChart3 },
  { id: 'volatility' as TabType, label: '波动率', icon: Activity },
  { id: 'flow' as TabType, label: '异动', icon: Zap },
  { id: 'strategy' as TabType, label: '策略', icon: Layers },
  { id: 'trade' as TabType, label: '交易', icon: ShoppingCart },
];

export default function Navbar({ activeTab, onTabChange, theme, onToggleTheme }: NavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border/50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="w-full px-4 sm:px-6 lg:px-8">
        <div className="flex h-14 items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2">
              <div className="relative flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-primary/70">
                <TrendingUp className="h-5 w-5 text-primary-foreground" />
                <div className="absolute -right-1 -top-1 h-2 w-2 rounded-full bg-up animate-pulse" />
              </div>
              <span className="text-lg font-bold tracking-tight">
                OpenOptions<span className="text-primary">Lab</span>
              </span>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  className={`
                    relative flex items-center gap-2 px-4 py-2 text-sm font-medium transition-all duration-200 rounded-lg
                    ${isActive 
                      ? 'text-foreground bg-secondary' 
                      : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50'
                    }
                  `}
                >
                  <Icon className={`h-4 w-4 ${isActive ? 'text-primary' : ''}`} />
                  {item.label}
                  {isActive && (
                    <span className="absolute bottom-0 left-1/2 -translate-x-1/2 h-0.5 w-6 bg-primary rounded-full" />
                  )}
                </button>
              );
            })}
          </div>

          {/* Right Side Actions */}
          <div className="hidden md:flex items-center gap-2">
            {/* Theme Toggle Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggleTheme}
              className="gap-2"
              title={theme === 'dark' ? '切换到浅色模式' : '切换到深色模式'}
            >
              {theme === 'dark' ? (
                <>
                  <Sun className="h-4 w-4 text-highlight" />
                  <span className="text-xs text-muted-foreground">浅色</span>
                </>
              ) : (
                <>
                  <Moon className="h-4 w-4 text-primary" />
                  <span className="text-xs text-muted-foreground">深色</span>
                </>
              )}
            </Button>

            {/* Community Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="gap-1">
                  <Users className="h-4 w-4" />
                  社区
                  <ChevronDown className="h-3 w-3" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem>讨论区</DropdownMenuItem>
                <DropdownMenuItem>策略分享</DropdownMenuItem>
                <DropdownMenuItem>直播课程</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Pro Badge */}
            <Button variant="ghost" size="sm" className="gap-1 text-highlight">
              <Crown className="h-4 w-4" />
              Pro
            </Button>

            {/* Login Button */}
            <Button size="sm" variant="outline" className="border-primary/50 text-primary hover:bg-primary/10">
              登录
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 rounded-lg hover:bg-secondary"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-border/50">
            <div className="flex flex-col gap-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      onTabChange(item.id);
                      setMobileMenuOpen(false);
                    }}
                    className={`
                      flex items-center gap-3 px-4 py-3 text-sm font-medium transition-all rounded-lg
                      ${isActive 
                        ? 'text-foreground bg-secondary' 
                        : 'text-muted-foreground hover:text-foreground hover:bg-secondary/50'
                      }
                    `}
                  >
                    <Icon className={`h-5 w-5 ${isActive ? 'text-primary' : ''}`} />
                    {item.label}
                  </button>
                );
              })}
              <div className="mt-4 pt-4 border-t border-border/50 flex flex-col gap-2">
                {/* Mobile Theme Toggle */}
                <Button 
                  variant="outline" 
                  className="w-full justify-start gap-2"
                  onClick={() => {
                    onToggleTheme();
                    setMobileMenuOpen(false);
                  }}
                >
                  {theme === 'dark' ? (
                    <>
                      <Sun className="h-4 w-4 text-highlight" />
                      切换到浅色模式
                    </>
                  ) : (
                    <>
                      <Moon className="h-4 w-4 text-primary" />
                      切换到深色模式
                    </>
                  )}
                </Button>
                <Button variant="outline" className="w-full justify-start gap-2">
                  <Users className="h-4 w-4" />
                  社区
                </Button>
                <Button variant="outline" className="w-full justify-start gap-2 text-highlight">
                  <Crown className="h-4 w-4" />
                  Pro 版本
                </Button>
                <Button className="w-full">登录</Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
