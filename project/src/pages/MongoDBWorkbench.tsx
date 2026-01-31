import React, { useState, useEffect } from 'react';
import { Play, Database, Table, FileJson, AlertCircle, CheckCircle, Loader, RefreshCw, ChevronRight, ChevronDown } from 'lucide-react';
import Editor from '@monaco-editor/react';
import { useToast } from '../contexts/ToastContext';
import DeerLoader from '../components/DeerLoader';

interface Collection {
  name: string;
  expanded?: boolean;
  fields?: string[];
}

interface DatabaseInfo {
  name: string;
  collections: Collection[];
  expanded?: boolean;
}

const MongoDBWorkbench: React.FC = () => {
  const { show } = useToast();
  const [databases, setDatabases] = useState<DatabaseInfo[]>([]);
  const [selectedDatabase, setSelectedDatabase] = useState<string>('');
  const [selectedCollection, setSelectedCollection] = useState<string>('');
  // Tabs for queries
  const [tabs, setTabs] = useState<Array<{ id: string; title: string; query: string }>>(() => {
    const saved = localStorage.getItem('mongoWorkbenchTabs');
    if (saved) {
      try { return JSON.parse(saved); } catch {}
    }
    return [{ id: 'tab-1', title: 'Query 1', query: localStorage.getItem('mongoWorkbenchQuery') || '{}' }];
  });
  const [activeTabId, setActiveTabId] = useState<string>(() => (JSON.parse(localStorage.getItem('mongoWorkbenchActive') || 'null') || 'tab-1'));
  const activeTab = tabs.find(t => t.id === activeTabId) || tabs[0];
  const query = activeTab?.query || '{}';
  const [operation, setOperation] = useState(() => {
    return localStorage.getItem('mongoWorkbenchOperation') || 'find';
  });
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [schemaLoading, setSchemaLoading] = useState<boolean>(false);
  const [saveHistory, setSaveHistory] = useState<boolean>(true);

  useEffect(() => {
    loadSchema();
  }, []);

  // Save query to localStorage whenever it changes
  const persistTabs = (next: typeof tabs, nextActive?: string) => {
    localStorage.setItem('mongoWorkbenchTabs', JSON.stringify(next));
    if (nextActive) localStorage.setItem('mongoWorkbenchActive', JSON.stringify(nextActive));
  };

  const handleQueryChange = (value: string | undefined) => {
    const newQuery = value || '{}';
    setTabs((prev: Array<{ id: string; title: string; query: string }>) => {
      const next = prev.map(t => t.id === activeTabId ? { ...t, query: newQuery } : t);
      persistTabs(next);
      return next;
    });
    localStorage.setItem('mongoWorkbenchQuery', newQuery);
  };

  // Save operation to localStorage
  const handleOperationChange = (newOperation: string) => {
    setOperation(newOperation);
    localStorage.setItem('mongoWorkbenchOperation', newOperation);
  };

  const loadSchema = async () => {
    setSchemaLoading(true);
    try {
      const response = await fetch('http://localhost:8000/mongodb/inspect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ db_type: 'mongodb' })
      });
      
      if (response.ok) {
        const data = await response.json();
        const dbList: DatabaseInfo[] = [];
        
        // Sample fields for each collection (you can fetch real schema later)
        const sampleFields: Record<string, string[]> = {
          users: ['user_id', 'username', 'email', 'status', 'is_premium'],
          customers: ['customer_id', 'name', 'email', 'phone', 'customer_type'],
          products: ['product_id', 'name', 'sku', 'price', 'stock_quantity'],
          orders: ['order_id', 'order_number', 'customer_id', 'status', 'total_amount'],
          employees: ['employee_id', 'employee_number', 'first_name', 'last_name', 'salary'],
          departments: ['department_id', 'name', 'code', 'budget'],
          categories: ['category_id', 'name', 'description'],
          suppliers: ['supplier_id', 'company_name', 'contact_name', 'email'],
          order_items: ['order_item_id', 'order_id', 'product_id', 'quantity'],
          payments: ['payment_id', 'order_id', 'amount', 'payment_method', 'status'],
          shipments: ['shipment_id', 'order_id', 'tracking_number', 'carrier', 'status'],
          reviews: ['review_id', 'product_id', 'customer_id', 'rating', 'comment'],
          inventory: ['inventory_id', 'product_id', 'quantity_available', 'warehouse_location'],
          sales: ['sale_id', 'order_id', 'employee_id', 'amount', 'commission'],
          promotions: ['promotion_id', 'code', 'discount_type', 'discount_value', 'is_active']
        };
        
        if (data.collections) {
          Object.entries(data.collections).forEach(([dbName, collections]: [string, any]) => {
            if (Array.isArray(collections)) {
              dbList.push({
                name: dbName,
                expanded: true,
                collections: collections.map((col: string) => ({ 
                  name: col,
                  expanded: false,
                  fields: sampleFields[col] || ['_id', 'created_at', 'updated_at']
                }))
              });
            }
          });
        }
        
        setDatabases(dbList);
        if (dbList.length > 0 && !selectedDatabase) {
          setSelectedDatabase(dbList[0].name);
          if (dbList[0].collections.length > 0) {
            setSelectedCollection(dbList[0].collections[0].name);
          }
        }
      }
    } catch (err) {
      console.error('Schema load failed:', err);
    } finally {
      setSchemaLoading(false);
    }
  };

  const toggleDatabase = (dbName: string) => {
    setDatabases(databases.map(db => 
      db.name === dbName ? { ...db, expanded: !db.expanded } : db
    ));
  };

  const toggleCollection = (dbName: string, colName: string) => {
    setDatabases(databases.map(db => 
      db.name === dbName ? {
        ...db,
        collections: db.collections.map(col =>
          col.name === colName ? { ...col, expanded: !col.expanded } : col
        )
      } : db
    ));
  };

  const insertField = (field: string) => {
    const newQuery = query === '{}' ? `{"${field}": ""}` : query;
    handleQueryChange(newQuery);
  };

  const insertCollection = (colName: string) => {
    handleQueryChange('{}');
    setSelectedCollection(colName);
  };

  const executeQuery = async () => {
    if (!selectedDatabase || !selectedCollection) {
      setError('Select database and collection');
      return;
    }

    const startTime = performance.now();
    let querySuccess = false;
    let resultCount = 0;
    let errorMessage = '';

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const parsedQuery = JSON.parse(query);
      
      // Create the request body
      const requestBody: any = {
        db_name: selectedDatabase,
        collection_name: selectedCollection,
        query: parsedQuery,
        operation: operation
      };

      // Only include document for insert/update operations
      if (['insert', 'update'].includes(operation)) {
        requestBody.document = parsedQuery;
      }

      const response = await fetch('http://localhost:8000/mongodb/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();

      if (response.ok) {
        setResults(data);
        setSuccess(`${operation.toUpperCase()} executed successfully`);
        querySuccess = true;
        resultCount = data.documents?.length || data.count || 0;
      } else {
        errorMessage = data.detail || 'Execution failed';
        setError(errorMessage);
      }
    } catch (err: any) {
      errorMessage = err.message || 'Failed to execute';
      setError(errorMessage);
    } finally {
      setLoading(false);
      
      // Calculate execution time
      const executionTime = performance.now() - startTime;
      
      // Save to history
      if (saveHistory) {
        try {
          const queryText = `${selectedCollection}.${operation}(${query})`;
          await fetch('http://localhost:8000/history/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              query_text: queryText,
              generated_sql: queryText,
              query_type: 'mongodb',
              status: querySuccess ? 'success' : 'error',
              result_count: resultCount,
              error_message: errorMessage || null,
              execution_time_ms: Math.round(executionTime)
            })
          });
          show('Saved to history', { type: 'success' });
        } catch (historyError) {
          console.error('Failed to save to history:', historyError);
        }
      }
    }
  };

  return (
    <div className="flex h-screen bg-gray-900">
      {/* Sidebar */}
      <div className="w-64 bg-gray-800 border-r border-gray-700 overflow-y-auto">
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-green-500" />
            MongoDB
          </h2>
          <button onClick={loadSchema} className="p-1 hover:bg-gray-700 rounded">
            <RefreshCw className="w-4 h-4 text-gray-400" />
          </button>
        </div>

        <div className="p-3 text-xs text-gray-500">
          {databases.reduce((acc, db) => acc + db.collections.length, 0)} collections
        </div>
        
        {databases.map((db) => (
          <div key={db.name}>
            {/* Database Header */}
            <div 
              className="px-3 py-2 cursor-pointer flex items-center gap-2 hover:bg-gray-750 text-gray-300"
              onClick={() => toggleDatabase(db.name)}
            >
              {db.expanded ? 
                <ChevronDown className="w-4 h-4" /> : 
                <ChevronRight className="w-4 h-4" />
              }
              <Database className="w-4 h-4 text-green-500" />
              <span className="font-semibold">{db.name}</span>
            </div>
            
            {/* Collections */}
            {db.expanded && db.collections.map((col) => (
              <div key={col.name}>
                {/* Collection Name */}
                <div
                  className={`pl-6 pr-3 py-2 cursor-pointer flex items-center gap-2 hover:bg-gray-750 ${
                    selectedCollection === col.name && selectedDatabase === db.name
                      ? 'bg-gray-700 text-green-400'
                      : 'text-gray-400'
                  }`}
                  onClick={() => toggleCollection(db.name, col.name)}
                  onDoubleClick={() => insertCollection(col.name)}
                >
                  {col.expanded ? 
                    <ChevronDown className="w-3 h-3" /> : 
                    <ChevronRight className="w-3 h-3" />
                  }
                  <Table className="w-4 h-4 text-green-500" />
                  <span className="text-sm">{col.name}</span>
                </div>
                
                {/* Fields */}
                {col.expanded && col.fields && col.fields.map((field) => (
                  <div
                    key={field}
                    className="pl-14 pr-3 py-1 cursor-pointer flex items-center gap-2 hover:bg-gray-750 text-gray-500 text-xs"
                    onDoubleClick={() => insertField(field)}
                    title="Double-click to insert"
                  >
                    <span className="w-2 h-2 rounded-full bg-gray-600"></span>
                    <span>{field}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        ))}
        
        {/* Helper Text */}
        <div className="p-3 border-t border-gray-700 mt-auto">
          <div className="text-xs text-gray-500 flex items-center gap-2">
            <span>💡</span>
            <span>Double-click to insert</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-gray-800 border-b border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">MongoDB Workbench</h1>
              <p className="text-sm text-gray-400 mt-1">
                {selectedDatabase && selectedCollection 
                  ? `${selectedDatabase}.${selectedCollection}`
                  : 'Select a collection'}
              </p>
            </div>
            <div className="flex gap-2 items-center">
              <select
                value={operation}
                onChange={(e) => handleOperationChange(e.target.value)}
                className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
              >
                <option value="find">Find</option>
                <option value="insert">Insert</option>
                <option value="update">Update</option>
                <option value="delete">Delete</option>
                <option value="count">Count</option>
              </select>
              <label className="text-xs text-gray-400 ml-3">Save</label>
              <input type="checkbox" checked={saveHistory} onChange={(e)=>setSaveHistory(e.target.checked)} />
              <button onClick={()=>{ navigator.clipboard.writeText(query); show('Copied query', { type: 'success' }); }} className="px-2 py-1 text-xs border border-green-500/30 rounded text-green-300 hover:bg-green-900/20">Copy</button>
            </div>
          </div>
        </div>

        {/* Tabs + Query Editor */}
        <div className="flex-1 flex flex-col">
          {/* Tabs */}
          <div className="bg-gray-800 px-4 py-2 border-b border-gray-700 flex items-center justify-between">
            <div className="flex items-center gap-2 overflow-x-auto">
              {tabs.map(t => (
                <div key={t.id} className={`flex items-center gap-2 px-3 py-1.5 rounded-md border ${t.id === activeTabId ? 'border-green-500/50 bg-green-900/20 text-green-300' : 'border-green-500/20 bg-gray-900/40 text-gray-300'}`}>
                  <button onClick={() => { setActiveTabId(t.id); persistTabs(tabs, t.id); }} className="text-sm font-medium">{t.title}</button>
                  <button onClick={() => { if(tabs.length>1){ const idx = tabs.findIndex(x=>x.id===t.id); const next = tabs.filter(x=>x.id!==t.id); const nextActive = t.id===activeTabId ? (next[Math.max(0, idx-1)]?.id || next[0].id) : activeTabId; setTabs(next); setActiveTabId(nextActive); persistTabs(next, nextActive);} }} className="text-xs text-gray-400 hover:text-red-400">✕</button>
                </div>
              ))}
              <button onClick={() => { const id = `tab-${Math.random().toString(36).slice(2)}`; const next = [...tabs, { id, title: `Query ${tabs.length+1}`, query: '{}' }]; setTabs(next); setActiveTabId(id); persistTabs(next, id); }} className="px-2 py-1.5 text-sm border border-green-500/30 rounded text-green-300 hover:bg-green-900/20">+ New</button>
            </div>
          </div>
          <div className="bg-gray-800 px-4 py-2 border-b border-gray-700 flex items-center justify-between">
            <span className="text-sm text-gray-400">Query Editor</span>
            <div className="flex gap-2 text-xs">
              <button onClick={() => handleQueryChange('{}')} className="px-2 py-1 bg-gray-700 rounded hover:bg-gray-600 text-gray-300">
                Clear
              </button>
              <button onClick={() => handleQueryChange('{ "status": "active" }')} className="px-2 py-1 bg-gray-700 rounded hover:bg-gray-600 text-gray-300">
                Sample
              </button>
            </div>
          </div>
          
          <div className="h-48 bg-gray-900">
            <Editor
              height="100%"
              language="json"
              theme="vs-dark"
              value={query}
              onChange={handleQueryChange}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
              }}
            />
          </div>

          <div className="bg-gray-800 p-3 border-t border-b border-gray-700 flex gap-2">
            <button
              onClick={executeQuery}
              disabled={loading}
              className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium flex items-center gap-2 disabled:opacity-50"
            >
              {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              Execute
            </button>
          </div>

          {/* Messages */}
          {error && (
            <div className="mx-4 mt-4 p-3 bg-red-900/50 border border-red-700 rounded-lg flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-red-200">{error}</div>
            </div>
          )}

          {success && (
            <div className="mx-4 mt-4 p-3 bg-green-900/50 border border-green-700 rounded-lg flex items-start gap-2">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-green-200">{success}</div>
            </div>
          )}

          {/* Results */}
          {results && (
            <div className="flex-1 overflow-auto p-4">
              <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <FileJson className="w-5 h-5 text-blue-400" />
                    Results
                  </h3>
                  <span className="text-sm text-gray-400">
                    {results.count !== undefined ? `${results.count} documents` : ''}
                  </span>
                </div>
                
                <pre className="bg-gray-900 p-4 rounded-lg overflow-x-auto text-sm text-gray-300">
                  {JSON.stringify(results, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MongoDBWorkbench;
