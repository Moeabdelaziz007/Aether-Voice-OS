import React from 'react';
import type { WidgetSpec } from './schema';

export const renderWidgets = (specs: WidgetSpec[]): React.ReactNode[] => {
  return specs.map((spec, index) => {
    return React.createElement('div', { key: spec.id || index, className: 'widget-fallback p-4 bg-white/5 border border-white/10 rounded' },
      React.createElement('h3', { className: 'text-cyan-400 text-sm' }, spec.title || 'Widget'),
      React.createElement('p', { className: 'text-white/50 text-xs' }, 'Widget rendering not implemented in fallback.')
    );
  });
};
