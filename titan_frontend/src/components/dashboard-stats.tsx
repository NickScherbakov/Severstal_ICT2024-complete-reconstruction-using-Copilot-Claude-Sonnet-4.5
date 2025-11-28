/**
 * TITAN Analytics Platform - Dashboard Components
 * Enhanced UI components for analytics visualization
 */

import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import {
  IconReportAnalytics,
  IconTemplate,
  IconSearch,
  IconTrendingUp,
  IconTrendingDown,
  IconMinus,
  IconUsers,
  IconRobot,
  IconChartBar
} from '@tabler/icons-react';

// Stats Card Component
interface StatCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  description?: string;
}

export function StatCard({ 
  title, 
  value, 
  change, 
  changeLabel = 'vs last period',
  icon,
  description 
}: StatCardProps) {
  const getTrendIcon = () => {
    if (change === undefined) return null;
    if (change > 0) return <IconTrendingUp size={16} className="text-green-500" />;
    if (change < 0) return <IconTrendingDown size={16} className="text-red-500" />;
    return <IconMinus size={16} className="text-muted-foreground" />;
  };

  const getTrendColor = () => {
    if (change === undefined) return '';
    if (change > 0) return 'text-green-500';
    if (change < 0) return 'text-red-500';
    return 'text-muted-foreground';
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon && <div className="text-muted-foreground">{icon}</div>}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {(change !== undefined || description) && (
          <p className="text-xs text-muted-foreground mt-1">
            {change !== undefined && (
              <span className={`inline-flex items-center gap-1 ${getTrendColor()}`}>
                {getTrendIcon()}
                {change > 0 ? '+' : ''}{change}%
              </span>
            )}
            {change !== undefined && description && ' • '}
            {description || changeLabel}
          </p>
        )}
      </CardContent>
    </Card>
  );
}

// Dashboard Stats Grid
interface DashboardStatsProps {
  stats: {
    totalReports: number;
    reportsChange?: number;
    totalTemplates: number;
    templatesChange?: number;
    totalSearches: number;
    searchesChange?: number;
    aiProcessed: number;
    aiChange?: number;
  };
}

export function DashboardStats({ stats }: DashboardStatsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <StatCard
        title="Total Reports"
        value={stats.totalReports}
        change={stats.reportsChange}
        icon={<IconReportAnalytics size={20} />}
      />
      <StatCard
        title="Active Templates"
        value={stats.totalTemplates}
        change={stats.templatesChange}
        icon={<IconTemplate size={20} />}
      />
      <StatCard
        title="Search Queries"
        value={stats.totalSearches}
        change={stats.searchesChange}
        icon={<IconSearch size={20} />}
      />
      <StatCard
        title="AI Analyses"
        value={stats.aiProcessed}
        change={stats.aiChange}
        icon={<IconRobot size={20} />}
      />
    </div>
  );
}

// Quick Actions Component
interface QuickAction {
  title: string;
  description: string;
  icon: React.ReactNode;
  onClick: () => void;
  variant?: 'default' | 'primary';
}

interface QuickActionsProps {
  actions: QuickAction[];
}

export function QuickActions({ actions }: QuickActionsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
        <CardDescription>Get started with common tasks</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {actions.map((action, index) => (
            <button
              key={index}
              onClick={action.onClick}
              className={`flex items-center gap-4 p-4 rounded-lg border transition-colors text-left ${
                action.variant === 'primary'
                  ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                  : 'hover:bg-accent'
              }`}
            >
              <div className={action.variant === 'primary' ? '' : 'text-primary'}>
                {action.icon}
              </div>
              <div>
                <div className="font-medium">{action.title}</div>
                <div className={`text-sm ${
                  action.variant === 'primary' 
                    ? 'text-primary-foreground/80' 
                    : 'text-muted-foreground'
                }`}>
                  {action.description}
                </div>
              </div>
            </button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

// Recent Activity Component
interface ActivityItem {
  id: string;
  type: 'report' | 'template' | 'search' | 'analysis';
  title: string;
  timestamp: string;
  status?: 'completed' | 'processing' | 'error';
}

interface RecentActivityProps {
  activities: ActivityItem[];
  onViewAll?: () => void;
}

export function RecentActivity({ activities, onViewAll }: RecentActivityProps) {
  const getActivityIcon = (type: ActivityItem['type']) => {
    switch (type) {
      case 'report':
        return <IconReportAnalytics size={16} className="text-blue-500" />;
      case 'template':
        return <IconTemplate size={16} className="text-purple-500" />;
      case 'search':
        return <IconSearch size={16} className="text-green-500" />;
      case 'analysis':
        return <IconChartBar size={16} className="text-orange-500" />;
    }
  };

  const getStatusBadge = (status?: ActivityItem['status']) => {
    if (!status) return null;
    
    const styles = {
      completed: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
      processing: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300',
      error: 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300',
    };

    return (
      <span className={`px-2 py-0.5 text-xs rounded-full ${styles[status]}`}>
        {status}
      </span>
    );
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Your latest actions and updates</CardDescription>
        </div>
        {onViewAll && (
          <button 
            onClick={onViewAll}
            className="text-sm text-primary hover:underline"
          >
            View all
          </button>
        )}
      </CardHeader>
      <CardContent>
        {activities.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No recent activity
          </div>
        ) : (
          <div className="space-y-4">
            {activities.map(activity => (
              <div key={activity.id} className="flex items-center gap-4">
                <div className="p-2 rounded-full bg-muted">
                  {getActivityIcon(activity.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{activity.title}</p>
                  <p className="text-sm text-muted-foreground">{activity.timestamp}</p>
                </div>
                {getStatusBadge(activity.status)}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Usage Limits Component (for license tiers)
interface UsageLimitsProps {
  tier: 'community' | 'professional' | 'enterprise';
  usage: {
    reports: { used: number; limit: number };
    templates: { used: number; limit: number };
    aiRequests: { used: number; limit: number };
    storage: { used: number; limit: number; unit: string };
  };
}

export function UsageLimits({ tier, usage }: UsageLimitsProps) {
  const tierLabels = {
    community: 'Community',
    professional: 'Professional',
    enterprise: 'Enterprise',
  };

  const tierColors = {
    community: 'bg-gray-100 text-gray-700',
    professional: 'bg-blue-100 text-blue-700',
    enterprise: 'bg-gradient-to-r from-purple-500 to-blue-500 text-white',
  };

  const getPercentage = (used: number, limit: number) => {
    if (limit === 0) return 0; // Unlimited
    return Math.min((used / limit) * 100, 100);
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 70) return 'bg-yellow-500';
    return 'bg-primary';
  };

  const formatLimit = (limit: number) => limit === 0 ? '∞' : limit.toLocaleString();

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Usage & Limits</CardTitle>
          <span className={`px-3 py-1 text-sm rounded-full ${tierColors[tier]}`}>
            {tierLabels[tier]}
          </span>
        </div>
        <CardDescription>Your current usage this billing period</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Reports */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Reports Generated</span>
            <span>{usage.reports.used} / {formatLimit(usage.reports.limit)}</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div 
              className={`h-full ${getProgressColor(getPercentage(usage.reports.used, usage.reports.limit))}`}
              style={{ width: `${getPercentage(usage.reports.used, usage.reports.limit)}%` }}
            />
          </div>
        </div>

        {/* Templates */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Custom Templates</span>
            <span>{usage.templates.used} / {formatLimit(usage.templates.limit)}</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div 
              className={`h-full ${getProgressColor(getPercentage(usage.templates.used, usage.templates.limit))}`}
              style={{ width: `${getPercentage(usage.templates.used, usage.templates.limit)}%` }}
            />
          </div>
        </div>

        {/* AI Requests */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>AI Requests Today</span>
            <span>{usage.aiRequests.used} / {formatLimit(usage.aiRequests.limit)}</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div 
              className={`h-full ${getProgressColor(getPercentage(usage.aiRequests.used, usage.aiRequests.limit))}`}
              style={{ width: `${getPercentage(usage.aiRequests.used, usage.aiRequests.limit)}%` }}
            />
          </div>
        </div>

        {tier !== 'enterprise' && (
          <div className="pt-4 border-t">
            <p className="text-sm text-muted-foreground mb-3">
              Need more? Upgrade your plan for higher limits and enterprise features.
            </p>
            <button className="text-sm text-primary hover:underline">
              View upgrade options →
            </button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default { StatCard, DashboardStats, QuickActions, RecentActivity, UsageLimits };
