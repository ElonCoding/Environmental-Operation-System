import React from 'react';

interface MetricCardProps {
  title: string;
  value: string;
  subtitle: string;
  icon: React.ReactNode;
  valueColor?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  valueColor = 'text-white'
}) => (
  <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 shadow-sm">
    <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
      <span>{title}</span>
      {icon}
    </div>
    <div className={`text-2xl font-bold ${valueColor}`}>{value}</div>
    <p className="text-xs text-slate-400 mt-1">{subtitle}</p>
  </div>
);
