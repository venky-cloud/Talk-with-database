import { BarChart3, Users, Database as DatabaseIcon, Clock, TrendingUp, Loader2 } from 'lucide-react';
import { useState, useEffect, useMemo } from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, PieChart, Pie, Cell, Legend, BarChart, Bar } from 'recharts';

interface HistoryItem {
  id: number;
  query_text: string;
  query_type: string;
  status: string;
  result_count: number;
  execution_time_ms: number;
  created_at: string;
}

interface Stats {
  total_queries: number;
  success_rate: number;
  avg_execution_time: number;
  mysql_count: number;
  mongodb_count: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [recentQueries, setRecentQueries] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [range, setRange] = useState<'7d' | '30d' | 'custom'>('7d');
  const [customStart, setCustomStart] = useState<string>('');
  const [customEnd, setCustomEnd] = useState<string>('');

  useEffect(() => {
    loadDashboardData();
    // Refresh every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      // Fetch stats and recent history from FastAPI
      const [statsRes, listRes] = await Promise.all([
        fetch('http://localhost:8000/history/stats'),
        fetch('http://localhost:8000/history/list?limit=100&offset=0'),
      ]);

      const statsJson = await statsRes.json();
      const listJson = await listRes.json();

      const total = statsJson.total_queries || 0;
      const successCount = statsJson.success_count || 0;
      const successRate = total > 0 ? (successCount / total) * 100 : 0;

      setStats({
        total_queries: total,
        success_rate: successRate,
        avg_execution_time: statsJson.avg_execution_time_ms || 0,
        mysql_count: statsJson.mysql_count || 0,
        mongodb_count: statsJson.mongodb_count || 0,
      });

      const items = Array.isArray(listJson.items) ? listJson.items : [];
      setRecentQueries((items as HistoryItem[]).slice(0, 5));
      // persist larger cache for charts
      try { localStorage.setItem('dashboard_history_cache', JSON.stringify(items)); } catch {}
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Build chart data from history and stats
  const { timeSeries, typeSeries } = useMemo(() => {
    try {
      // Derive a time series (per day) from recent history + counts
      const raw = JSON.parse(localStorage.getItem('dashboard_history_cache') || '[]');
      // Fallback: combine the five recent items we have
      const base: HistoryItem[] = Array.isArray(raw) && raw.length ? raw : recentQueries;
      // filter by range
      const now = new Date();
      let startBoundary = new Date(0);
      if (range === '7d') {
        startBoundary = new Date(now.getTime() - 7*24*3600*1000);
      } else if (range === '30d') {
        startBoundary = new Date(now.getTime() - 30*24*3600*1000);
      } else if (range === 'custom' && customStart) {
        startBoundary = new Date(customStart);
      }
      const endBoundary = range === 'custom' && customEnd ? new Date(customEnd) : now;

      const map: Record<string, { keyISO: string; date: string; total: number; success: number; error: number }> = {};
      base.forEach((h) => {
        const d = new Date(h.created_at);
        if (d < startBoundary || d > endBoundary) return;
        const key = `${d.getFullYear()}-${d.getMonth()+1}-${d.getDate()}`;
        if (!map[key]) {
          map[key] = { keyISO: d.toISOString(), date: d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }), total: 0, success: 0, error: 0 };
        }
        map[key].total += 1;
        if (h.status === 'success') map[key].success += 1; else map[key].error += 1;
      });
      const timeSeries = Object.values(map).sort((a,b) => new Date(a.keyISO).getTime() - new Date(b.keyISO).getTime());

      const typeSeries = [
        { name: 'MySQL', value: stats?.mysql_count || 0 },
        { name: 'MongoDB', value: stats?.mongodb_count || 0 },
      ];

      return { timeSeries, typeSeries };
    } catch {
      return { timeSeries: [], typeSeries: [] };
    }
  }, [recentQueries, stats]);

  const formatTimeAgo = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
    return `${Math.floor(seconds / 86400)} days ago`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-green-500" />
      </div>
    );
  }

  const metrics = [
    { icon: Users, label: 'Total Queries', value: stats?.total_queries.toString() || '0', change: '' },
    { icon: DatabaseIcon, label: 'MySQL Queries', value: stats?.mysql_count.toString() || '0', change: '' },
    { icon: DatabaseIcon, label: 'MongoDB Queries', value: stats?.mongodb_count.toString() || '0', change: '' },
    { icon: Clock, label: 'Avg. Response', value: `${(stats?.avg_execution_time || 0).toFixed(0)}ms`, change: '' },
    { icon: BarChart3, label: 'Success Rate', value: `${(stats?.success_rate || 0).toFixed(1)}%`, change: '' },
    { icon: TrendingUp, label: 'Active Today', value: recentQueries.length.toString(), change: '' }
  ];

  return (
    <div className="py-24 px-4">
      <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-[#00ff00] to-[#00cc00]">
        Dashboard
      </h1>
      <p className="text-gray-400 mb-8 text-lg">Monitor your database interactions</p>

      {/* Time range selector */}
      <div className="flex items-center gap-3 mb-6">
        <select
          value={range}
          onChange={(e) => setRange(e.target.value as any)}
          className="bg-black/50 border border-[#00ff00]/30 rounded-md px-3 py-2 text-sm"
        >
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="custom">Custom range</option>
        </select>
        {range === 'custom' && (
          <>
            <input type="date" value={customStart} onChange={(e)=>setCustomStart(e.target.value)} className="bg-black/50 border border-[#00ff00]/30 rounded-md px-3 py-2 text-sm" />
            <input type="date" value={customEnd} onChange={(e)=>setCustomEnd(e.target.value)} className="bg-black/50 border border-[#00ff00]/30 rounded-md px-3 py-2 text-sm" />
          </>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {metrics.map(({ icon: Icon, label, value }) => (
          <div key={label} className="border border-[#00ff00]/30 rounded-lg p-6 hover-glow transition-all duration-300 bg-black/30">
            <div className="flex items-center justify-between mb-4">
              <Icon className="h-6 w-6 text-[#00ff00]" />
            </div>
            <p className="text-gray-400 text-sm">{label}</p>
            <p className="text-2xl font-bold text-white mt-1">{value}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 border border-[#00ff00]/30 rounded-lg p-4 bg-black/30">
          <h3 className="text-[#00ff00] mb-2">Success vs Error over time</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={timeSeries} margin={{ left: 10, right: 10, top: 10, bottom: 10 }}>
                <defs>
                  <linearGradient id="colorSuccess" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorError" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                <XAxis dataKey="date" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip contentStyle={{ background: '#111827', border: '1px solid #10b981', color: '#e5e7eb' }} />
                <Legend />
                <Area type="monotone" dataKey="success" stackId="1" stroke="#22c55e" fill="url(#colorSuccess)" name="Success" />
                <Area type="monotone" dataKey="error" stackId="1" stroke="#ef4444" fill="url(#colorError)" name="Error" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="border border-[#00ff00]/30 rounded-lg p-4 bg-black/30">
          <h3 className="text-[#00ff00] mb-2">Type breakdown</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={typeSeries} dataKey="value" nameKey="name" outerRadius={90} label>
                  {typeSeries.map((entry, idx) => (
                    <Cell key={`cell-${idx}`} fill={idx === 0 ? '#22c55e' : '#06b6d4'} />
                  ))}
                </Pie>
                <Legend />
                <Tooltip contentStyle={{ background: '#111827', border: '1px solid #10b981', color: '#e5e7eb' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="border border-[#00ff00]/30 rounded-lg p-6 hover-glow transition-all duration-300 bg-black/30">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-[#00ff00]">Recent Queries</h2>
          <button 
            onClick={loadDashboardData}
            className="text-xs text-gray-400 hover:text-green-400 flex items-center gap-1"
          >
            <Loader2 className="w-3 h-3" />
            Refresh
          </button>
        </div>
        <div className="space-y-4">
          {recentQueries.length > 0 ? (
            recentQueries.map((item) => (
              <div key={item.id} className="border-b border-[#00ff00]/10 last:border-0 pb-4 last:pb-0">
                <div className="flex items-center justify-between gap-4">
                  <p className="text-white truncate flex-1">{item.query_text}</p>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-2 py-1 rounded-full border ${
                      item.status === 'success' 
                        ? 'text-green-400 border-green-500/30 bg-green-500/10' 
                        : 'text-red-400 border-red-500/30 bg-red-500/10'
                    }`}>
                      {item.status}
                    </span>
                    <span className="text-[#00ff00] text-sm px-2 py-1 rounded-full border border-[#00ff00]/30">
                      {item.query_type.toUpperCase()}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-4 mt-2">
                  <p className="text-gray-500 text-xs">{formatTimeAgo(item.created_at)}</p>
                  <p className="text-gray-500 text-xs">⚡ {item.execution_time_ms}ms</p>
                  {item.result_count > 0 && (
                    <p className="text-gray-500 text-xs">📊 {item.result_count} results</p>
                  )}
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-500 text-center py-4">No queries yet. Start querying to see history!</p>
          )}
        </div>
      </div>
    </div>
  );
}