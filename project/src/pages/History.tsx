import { useState, useEffect } from 'react';
import { Clock, Database, Trash2, RefreshCw, Search, Play, AlertCircle, CheckCircle } from 'lucide-react';
import { get, del } from '../lib/api';

interface HistoryItem {
  id: string;
  query_text: string;
  generated_sql: string;
  query_type: string;
  status: string;
  result_count?: number;
  error_message?: string;
  execution_time_ms?: number;
  created_at: string;
}

interface HistoryResponse {
  total: number;
  limit: number;
  offset: number;
  items: HistoryItem[];
}

export default function History() {
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [stats, setStats] = useState<any>(null);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const data = await get<HistoryResponse>('/history/list?limit=100');
      setHistoryItems(data.items);
      
      const statsData = await get<any>('/history/stats');
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteItem = async (id: string) => {
    if (!confirm('Are you sure you want to delete this query from history?')) return;
    
    try {
      await del(`/history/delete/${id}`);
      setHistoryItems(items => items.filter(item => item.id !== id));
    } catch (error) {
      console.error('Failed to delete item:', error);
    }
  };

  const clearAll = async () => {
    if (!confirm('Are you sure you want to clear all history? This cannot be undone.')) return;
    
    try {
      await del('/history/clear');
      setHistoryItems([]);
      setStats(null);
    } catch (error) {
      console.error('Failed to clear history:', error);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const filteredItems = historyItems.filter(item =>
    item.query_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.generated_sql.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleString();
  };

  return (
    <div className="py-24 px-4">
      <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-[#00ff00] to-[#00cc00]">
        Query History
      </h1>
      <p className="text-gray-400 mb-8 text-lg">View and manage your past queries</p>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-black/30 border border-[#00ff00]/30 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">Total Queries</div>
            <div className="text-2xl font-bold text-[#00ff00]">{stats.total_queries}</div>
          </div>
          <div className="bg-black/30 border border-[#00ff00]/30 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">Success Rate</div>
            <div className="text-2xl font-bold text-green-400">
              {stats.total_queries > 0 ? Math.round((stats.success_count / stats.total_queries) * 100) : 0}%
            </div>
          </div>
          <div className="bg-black/30 border border-[#00ff00]/30 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">Avg Time</div>
            <div className="text-2xl font-bold text-cyan-400">{stats.avg_execution_time_ms}ms</div>
          </div>
          <div className="bg-black/30 border border-[#00ff00]/30 rounded-lg p-4">
            <div className="text-gray-400 text-sm mb-1">MySQL / MongoDB</div>
            <div className="text-2xl font-bold text-blue-400">{stats.mysql_count} / {stats.mongodb_count}</div>
          </div>
        </div>
      )}

      <div className="mb-6 flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search queries..."
            className="w-full pl-10 pr-4 py-2 bg-black/50 border border-[#00ff00]/30 rounded-md
              focus:outline-none focus:ring-2 focus:ring-[#00ff00]/50 text-white
              placeholder:text-gray-500 transition-all duration-300 hover:border-[#00ff00]/50"
          />
        </div>
        <button
          onClick={loadHistory}
          className="px-4 py-2 bg-[#00ff00]/10 text-[#00ff00] rounded-md hover:bg-[#00ff00]/20 
            transition-all duration-300 hover-glow border border-[#00ff00]/30 flex items-center justify-center"
        >
          <RefreshCw className="h-5 w-5 mr-2" />
          Refresh
        </button>
        <button
          onClick={clearAll}
          className="px-4 py-2 bg-red-500/10 text-red-400 rounded-md hover:bg-red-500/20 
            transition-all duration-300 border border-red-500/30 flex items-center justify-center"
        >
          <Trash2 className="h-5 w-5 mr-2" />
          Clear All
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <RefreshCw className="h-8 w-8 animate-spin text-[#00ff00] mx-auto mb-4" />
          <p className="text-gray-400">Loading history...</p>
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="text-center py-12 border border-[#00ff00]/30 rounded-lg bg-black/30">
          <Database className="h-16 w-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No query history found</p>
          {searchTerm && <p className="text-gray-500 text-sm mt-2">Try a different search term</p>}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredItems.map((item) => (
            <div key={item.id} 
              className="border border-[#00ff00]/30 rounded-lg p-6 hover:border-[#00ff00]/50
                transition-all duration-300 bg-black/30">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-[#00ff00] text-sm px-2 py-1 rounded-full border border-[#00ff00]/30 flex items-center gap-1">
                    <Database className="h-3 w-3" />
                    {item.query_type.toUpperCase()}
                  </span>
                  {item.status === 'success' ? (
                    <span className="px-2 py-1 rounded-full text-sm bg-green-500/20 text-green-400 flex items-center gap-1">
                      <CheckCircle className="h-3 w-3" />
                      Success
                    </span>
                  ) : (
                    <span className="px-2 py-1 rounded-full text-sm bg-red-500/20 text-red-400 flex items-center gap-1">
                      <AlertCircle className="h-3 w-3" />
                      Error
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-400 text-sm flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {formatDate(item.created_at)}
                  </span>
                  <button
                    onClick={() => deleteItem(item.id)}
                    className="text-red-400 hover:text-red-300 p-1 rounded hover:bg-red-500/10 transition-colors"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                <div>
                  <p className="text-xs text-gray-500 mb-1">Natural Language Query:</p>
                  <p className="text-white">{item.query_text}</p>
                </div>
                
                <div>
                  <p className="text-xs text-gray-500 mb-1">Generated {item.query_type.toUpperCase()}:</p>
                  <pre className="text-sm text-cyan-400 bg-black/50 p-3 rounded border border-cyan-500/30 overflow-x-auto font-mono">
                    {item.generated_sql}
                  </pre>
                </div>

                <div className="flex items-center gap-4 text-xs text-gray-400">
                  {item.result_count !== null && item.result_count !== undefined && (
                    <span>Results: {item.result_count}</span>
                  )}
                  {item.execution_time_ms && (
                    <span>Execution Time: {item.execution_time_ms}ms</span>
                  )}
                  {item.error_message && (
                    <span className="text-red-400">Error: {item.error_message}</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}