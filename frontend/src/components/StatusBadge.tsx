import React from 'react';
import { CheckCircle2, AlertTriangle, HelpCircle, ArrowRightLeft, Clock, RefreshCw } from 'lucide-react';

interface StatusBadgeProps {
  type: string;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ type, size = 'md' }) => {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3 py-1.5 gap-2',
  }[size];

  switch (type) {
    case 'CORROBORATES':
      return (
        <span className={`inline-flex items-center font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 ${sizeClasses}`}>
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          Corroboration
        </span>
      );

    case 'CONTRADICTS':
      return (
        <span className={`inline-flex items-center font-semibold rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30 ${sizeClasses}`}>
          <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
          Contradiction
        </span>
      );

    case 'RECONCILED_BY_CONTEXT':
      return (
        <span className={`inline-flex items-center font-semibold rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/30 ${sizeClasses}`}>
          <ArrowRightLeft className="w-3.5 h-3.5 text-sky-400" />
          Reconciled by Context
        </span>
      );

    case 'UNCERTAIN':
      return (
        <span className={`inline-flex items-center font-semibold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 ${sizeClasses}`}>
          <HelpCircle className="w-3.5 h-3.5 text-amber-400" />
          Uncertain
        </span>
      );

    case 'COMPLETED':
      return (
        <span className={`inline-flex items-center font-medium rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 ${sizeClasses}`}>
          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
          Completed
        </span>
      );

    case 'EXTRACTING':
    case 'ANALYZING':
      return (
        <span className={`inline-flex items-center font-medium rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 ${sizeClasses}`}>
          <RefreshCw className="w-3 h-3 text-indigo-400 animate-spin" />
          {type === 'EXTRACTING' ? 'Extracting Facts...' : 'Analyzing Facts...'}
        </span>
      );

    case 'UPLOADED':
      return (
        <span className={`inline-flex items-center font-medium rounded-full bg-slate-500/10 text-slate-400 border border-slate-500/20 ${sizeClasses}`}>
          <Clock className="w-3 h-3 text-slate-400" />
          Queued
        </span>
      );

    case 'FAILED':
      return (
        <span className={`inline-flex items-center font-medium rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 ${sizeClasses}`}>
          <AlertTriangle className="w-3 h-3 text-rose-400" />
          Failed
        </span>
      );

    default:
      return (
        <span className={`inline-flex items-center font-medium rounded-full bg-slate-800 text-slate-300 border border-slate-700 ${sizeClasses}`}>
          {type}
        </span>
      );
  }
};
