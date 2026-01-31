import { useState, useEffect } from 'react';
import { Database, Table2, Search, Layout, List, RefreshCw, Maximize2, Minimize2 } from 'lucide-react';
import { post } from '../lib/api';
import MongoDBERDiagram from '../components/MongoDBERDiagram';

interface MongoDBSchema {
  collections: Record<string, string[]>;
}

interface CollectionDetail {
  name: string;
  fields: string[];
}

export default function MongoDBSchemaWorkbench() {
  const [schema, setSchema] = useState<MongoDBSchema | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState<'list' | 'diagram'>(() => {
    // Check URL parameter for initial view
    const params = new URLSearchParams(window.location.search);
    return params.get('view') === 'diagram' ? 'diagram' : 'list';
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCollection, setSelectedCollection] = useState<string | null>(null);
  const [collections, setCollections] = useState<CollectionDetail[]>([]);
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    loadSchema();
  }, []);

  const loadSchema = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await post<{ db_type: string }, MongoDBSchema>('/mongodb/inspect', {
        db_type: 'mongodb'
      });
      setSchema(data);
      
      // Parse collections with sample fields
      const sampleFields: Record<string, string[]> = {
        users: ['user_id', 'username', 'email', 'full_name', 'status', 'is_premium', 'age', 'country', 'created_at'],
        customers: ['customer_id', 'name', 'email', 'phone', 'address', 'city', 'state', 'customer_type', 'total_orders', 'total_spent'],
        products: ['product_id', 'name', 'sku', 'category_id', 'price', 'cost', 'stock_quantity', 'weight', 'is_active', 'rating'],
        orders: ['order_id', 'order_number', 'customer_id', 'employee_id', 'order_date', 'status', 'subtotal', 'tax_amount', 'total_amount'],
        employees: ['employee_id', 'employee_number', 'first_name', 'last_name', 'email', 'position', 'department_id', 'salary', 'hire_date'],
        departments: ['department_id', 'name', 'code', 'location', 'budget'],
        categories: ['category_id', 'name', 'slug', 'description'],
        suppliers: ['supplier_id', 'company_name', 'contact_name', 'email', 'phone', 'rating'],
        order_items: ['order_item_id', 'order_id', 'product_id', 'quantity', 'unit_price', 'subtotal'],
        payments: ['payment_id', 'order_id', 'payment_date', 'amount', 'payment_method', 'status'],
        shipments: ['shipment_id', 'order_id', 'tracking_number', 'carrier', 'shipped_date', 'status'],
        reviews: ['review_id', 'product_id', 'customer_id', 'rating', 'title', 'comment', 'review_date'],
        inventory: ['inventory_id', 'product_id', 'warehouse_location', 'quantity_available', 'quantity_reserved'],
        sales: ['sale_id', 'order_id', 'employee_id', 'customer_id', 'sale_date', 'amount', 'commission', 'region'],
        promotions: ['promotion_id', 'code', 'description', 'discount_type', 'discount_value', 'is_active']
      };
      
      const collectionsList: CollectionDetail[] = [];
      if (data.collections) {
        Object.entries(data.collections).forEach(([dbName, cols]) => {
          if (Array.isArray(cols)) {
            cols.forEach((colName: string) => {
              collectionsList.push({
                name: colName,
                fields: sampleFields[colName] || ['_id', 'created_at', 'updated_at']
              });
            });
          }
        });
      }
      
      setCollections(collectionsList);
      if (collectionsList.length > 0) {
        setSelectedCollection(collectionsList[0].name);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load schema');
    } finally {
      setLoading(false);
    }
  };

  const filteredCollections = collections.filter(col =>
    col.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectedCollectionDetail = collections.find(c => c.name === selectedCollection);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading MongoDB schema...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-gray-900 min-h-screen">
        <div className="bg-red-900/20 border border-red-500/30 text-red-300 px-4 py-3 rounded">
          <p className="font-bold">Error</p>
          <p>{error}</p>
          <button
            onClick={loadSchema}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 border-b border-green-500/30 p-4 relative" style={{ zIndex: 50 }}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-green-400 flex items-center gap-2">
              <Database className="w-6 h-6" />
              MongoDB Schema Explorer
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              {collections.length} collections • Database: mydb
            </p>
          </div>
          <div className="flex gap-2 relative" style={{ zIndex: 100 }}>
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                setViewMode('list');
              }}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 cursor-pointer transition-colors ${
                viewMode === 'list'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              <List className="w-4 h-4" />
              List
            </button>
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                setViewMode('diagram');
              }}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 cursor-pointer transition-colors ${
                viewMode === 'diagram'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              <Layout className="w-4 h-4" />
              Diagram
            </button>
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                loadSchema();
              }}
              className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 flex items-center gap-2 cursor-pointer transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
            {viewMode === 'diagram' && (
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault();
                  setIsFullscreen(!isFullscreen);
                }}
                className="px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 flex items-center gap-2 cursor-pointer transition-colors"
                title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
              >
                {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </button>
            )}
          </div>
        </div>
      </div>

      <div className={`flex flex-1 overflow-hidden ${isFullscreen ? 'fixed inset-0 z-50 bg-gray-900' : ''}`}>
        {/* Sidebar - Collections List */}
        <div className={`bg-gray-800 border-r border-green-500/30 flex flex-col ${isFullscreen ? 'hidden' : 'w-80'}`}>
          <div className="p-4 border-b border-green-500/30">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search collections..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-green-500/30 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-2">
            {filteredCollections.map((collection) => (
              <button
                key={collection.name}
                onClick={() => setSelectedCollection(collection.name)}
                className={`w-full text-left px-3 py-2 rounded-lg mb-1 flex items-center gap-2 transition-colors ${
                  selectedCollection === collection.name
                    ? 'bg-green-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                <Table2 className="w-4 h-4 text-green-500" />
                <div className="flex-1">
                  <div className="font-medium">{collection.name}</div>
                  <div className="text-xs text-gray-400">{collection.fields.length} fields</div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className={`flex-1 ${isFullscreen ? 'p-0' : 'p-6'}`} style={{ height: isFullscreen ? '100vh' : 'calc(100vh - 80px)' }}>
          {viewMode === 'list' && selectedCollectionDetail && (
            <div>
              <div className="bg-gray-800 rounded-lg border border-green-500/30 overflow-hidden">
                <div className="bg-gray-900 p-4 border-b border-green-500/30">
                  <h2 className="text-xl font-bold text-green-400 flex items-center gap-2">
                    <Table2 className="w-5 h-5" />
                    {selectedCollectionDetail.name}
                  </h2>
                  <p className="text-sm text-gray-400 mt-1">
                    Collection with {selectedCollectionDetail.fields.length} fields
                  </p>
                </div>

                {/* Fields Table */}
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-900 border-b border-green-500/30">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-green-400 uppercase tracking-wider">
                          Field Name
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-green-400 uppercase tracking-wider">
                          Type
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-green-400 uppercase tracking-wider">
                          Description
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-green-500/20">
                      {selectedCollectionDetail.fields.map((field, idx) => (
                        <tr key={field} className="hover:bg-green-500/10">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              {field === '_id' && (
                                <span className="mr-2 text-yellow-400 text-xs">🔑</span>
                              )}
                              <span className="text-sm font-medium text-gray-200">{field}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="text-sm text-gray-400">
                              {field.includes('_id') ? 'ObjectId' : 
                               field.includes('date') || field.includes('at') ? 'Date' :
                               field.includes('is_') ? 'Boolean' :
                               field.includes('count') || field.includes('quantity') ? 'Number' :
                               field.includes('price') || field.includes('amount') ? 'Decimal' :
                               'String'}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <span className="text-sm text-gray-500">
                              {field === '_id' ? 'Primary identifier' :
                               field.includes('email') ? 'Email address' :
                               field.includes('date') ? 'Timestamp' :
                               field.includes('status') ? 'Status indicator' :
                               'Field data'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Collection Stats */}
              <div className="mt-6 grid grid-cols-3 gap-4">
                <div className="bg-gray-800 border border-green-500/30 rounded-lg p-4">
                  <div className="text-sm text-gray-400">Total Fields</div>
                  <div className="text-2xl font-bold text-green-400 mt-1">
                    {selectedCollectionDetail.fields.length}
                  </div>
                </div>
                <div className="bg-gray-800 border border-green-500/30 rounded-lg p-4">
                  <div className="text-sm text-gray-400">Collection Type</div>
                  <div className="text-2xl font-bold text-green-400 mt-1">Document</div>
                </div>
                <div className="bg-gray-800 border border-green-500/30 rounded-lg p-4">
                  <div className="text-sm text-gray-400">Database</div>
                  <div className="text-2xl font-bold text-green-400 mt-1">mydb</div>
                </div>
              </div>
            </div>
          )}

          {viewMode === 'diagram' && (
            <div 
              className={`w-full bg-gray-900 overflow-hidden ${isFullscreen ? '' : 'rounded-lg border border-green-500/30'}`}
              style={{ height: isFullscreen ? '100vh' : 'calc(100vh - 160px)', position: 'relative', zIndex: 1 }}
            >
              <MongoDBERDiagram collections={collections} />
            </div>
          )}
        </div>
      </div>
      {/* Floating view toggle */}
      <div className="fixed bottom-6 right-6 z-[10001] flex gap-2">
        <button
          type="button"
          onClick={() => setViewMode('list')}
          className={`px-4 py-2 rounded-lg shadow-lg border ${
            viewMode === 'list'
              ? 'bg-green-600 text-white border-green-400'
              : 'bg-gray-800/80 text-gray-200 border-green-500/30 hover:bg-gray-700'
          }`}
          aria-label="List view"
        >
          List
        </button>
        <button
          type="button"
          onClick={() => setViewMode('diagram')}
          className={`px-4 py-2 rounded-lg shadow-lg border ${
            viewMode === 'diagram'
              ? 'bg-green-600 text-white border-green-400'
              : 'bg-gray-800/80 text-gray-200 border-green-500/30 hover:bg-gray-700'
          }`}
          aria-label="Diagram view"
        >
          Diagram
        </button>
      </div>
    </div>
  );
}
