import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// ─── Widget Types ──────────────────────────────────────────
export type WidgetType = 'weather' | 'crypto' | 'news' | 'stocks' | 'ai-chat' | 'tasks' | 'clock' | 'calendar';
export type WidgetSize = 'small' | 'medium' | 'large';

export interface WidgetConfig {
    id: string;
    type: WidgetType;
    title: string;
    icon: string;
    size: WidgetSize;
    position: number;
    enabled: boolean;
    settings?: Record<string, unknown>;
}

// ─── Widget Catalog ────────────────────────────────────────
export const WIDGET_CATALOG: Record<WidgetType, { title: string; icon: string; description: string; defaultSize: WidgetSize }> = {
    weather: { title: 'Weather', icon: '🌤️', description: 'Current weather & forecast', defaultSize: 'medium' },
    crypto: { title: 'Crypto', icon: '📈', description: 'Live cryptocurrency prices', defaultSize: 'medium' },
    news: { title: 'News', icon: '📰', description: 'Latest headlines & articles', defaultSize: 'large' },
    stocks: { title: 'Stocks', icon: '📊', description: 'Stock market tracker', defaultSize: 'medium' },
    'ai-chat': { title: 'AI Chat', icon: '🤖', description: 'Quick text chat with Aether', defaultSize: 'large' },
    tasks: { title: 'Tasks', icon: '✅', description: 'Task list & reminders', defaultSize: 'medium' },
    clock: { title: 'Clock', icon: '⏰', description: 'World clock & timer', defaultSize: 'small' },
    calendar: { title: 'Calendar', icon: '📅', description: 'Calendar & events', defaultSize: 'medium' },
};

// ─── Default Widgets ───────────────────────────────────────
const DEFAULT_WIDGETS: WidgetConfig[] = [
    { id: 'w-weather-1', type: 'weather', title: 'Weather', icon: '🌤️', size: 'medium', position: 0, enabled: true },
    { id: 'w-crypto-1', type: 'crypto', title: 'Crypto', icon: '📈', size: 'medium', position: 1, enabled: true },
    { id: 'w-news-1', type: 'news', title: 'News', icon: '📰', size: 'large', position: 2, enabled: true },
    { id: 'w-tasks-1', type: 'tasks', title: 'Tasks', icon: '✅', size: 'medium', position: 3, enabled: true },
];

// ─── Store Interface ───────────────────────────────────────
interface WidgetStoreState {
    widgets: WidgetConfig[];
    storeOpen: boolean;
    editMode: boolean;

    // Actions
    addWidget: (type: WidgetType) => void;
    removeWidget: (id: string) => void;
    moveWidget: (fromIndex: number, toIndex: number) => void;
    resizeWidget: (id: string, size: WidgetSize) => void;
    toggleWidget: (id: string) => void;
    updateWidgetSettings: (id: string, settings: Record<string, unknown>) => void;
    setStoreOpen: (open: boolean) => void;
    setEditMode: (edit: boolean) => void;
    resetWidgets: () => void;
}

export const useWidgetStore = create<WidgetStoreState>()(
    persist(
        (set) => ({
            widgets: DEFAULT_WIDGETS,
            storeOpen: false,
            editMode: false,

            addWidget: (type) => set((state) => {
                const catalog = WIDGET_CATALOG[type];
                const newWidget: WidgetConfig = {
                    id: `w-${type}-${Date.now()}`,
                    type,
                    title: catalog.title,
                    icon: catalog.icon,
                    size: catalog.defaultSize,
                    position: state.widgets.length,
                    enabled: true,
                };
                return { widgets: [...state.widgets, newWidget] };
            }),

            removeWidget: (id) => set((state) => ({
                widgets: state.widgets
                    .filter((w) => w.id !== id)
                    .map((w, i) => ({ ...w, position: i })),
            })),

            moveWidget: (fromIndex, toIndex) => set((state) => {
                const widgets = [...state.widgets];
                const [moved] = widgets.splice(fromIndex, 1);
                widgets.splice(toIndex, 0, moved);
                return { widgets: widgets.map((w, i) => ({ ...w, position: i })) };
            }),

            resizeWidget: (id, size) => set((state) => ({
                widgets: state.widgets.map((w) =>
                    w.id === id ? { ...w, size } : w
                ),
            })),

            toggleWidget: (id) => set((state) => ({
                widgets: state.widgets.map((w) =>
                    w.id === id ? { ...w, enabled: !w.enabled } : w
                ),
            })),

            updateWidgetSettings: (id, settings) => set((state) => ({
                widgets: state.widgets.map((w) =>
                    w.id === id ? { ...w, settings: { ...w.settings, ...settings } } : w
                ),
            })),

            setStoreOpen: (storeOpen) => set({ storeOpen }),
            setEditMode: (editMode) => set({ editMode }),
            resetWidgets: () => set({ widgets: DEFAULT_WIDGETS }),
        }),
        {
            name: 'aether-widgets',
            partialize: (state) => ({ widgets: state.widgets }),
        }
    )
);
