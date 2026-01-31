import { useState, useEffect } from 'react';
import { Database, Table2, Key, Link2, Search, Layout, List } from 'lucide-react';
import { post } from '../lib/api';
import ERDiagram from '../components/ERDiagram';
import { useToast } from '../contexts/ToastContext';
import { useNavigate } from 'react-router-dom';

interface Column {
  name: string;
  type: string;
  nullable: string;
  key: string;
  default: string | null;
  extra: string;
}

interface Index {
  name: string;
  columns: string[];
  unique: boolean;
}

interface ForeignKey {
  from_table: string;
  from_column: string;
  to_table: string;
  to_column: string;
  constraint_name: string;
}

interface SchemaData {
  db: string;
  tables: string[];
  columns: Record<string, Column[]>;
  primary_keys: Record<string, string[]>;
  indexes: Record<string, Index[]>;
  foreign_keys: ForeignKey[];
}

export default function SchemaWorkbench() {
  const { show } = useToast();
  const navigate = useNavigate();
  const [schema, setSchema] = useState<SchemaData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState<'list' | 'diagram'>('list');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTable, setSelectedTable] = useState<string | null>(null);

  useEffect(() => {
    loadSchema();
  }, []);

  const loadSchema = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await post<{ db_type: string }, SchemaData>('/schema/inspect', {
        db_type: 'mysql'
      });
      setSchema(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load schema');
    } finally {
      setLoading(false);
    }
  };

  const filteredTables = schema?.tables.filter(table =>
    table.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const getRelatedTables = (tableName: string): { incoming: ForeignKey[]; outgoing: ForeignKey[] } => {
    if (!schema) return { incoming: [], outgoing: [] };
    
    return {
      outgoing: schema.foreign_keys.filter(fk => fk.from_table === tableName),
      incoming: schema.foreign_keys.filter(fk => fk.to_table === tableName)
    };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading schema...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
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

  if (!schema) {
    return null;
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4 relative" style={{ zIndex: 50 }}>
          <div>
            <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-2">
              <Database className="w-8 h-8" />
              Schema Workbench
            </h1>
            <p className="text-gray-600 mt-1">
              Database: <span className="font-semibold">{schema.db}</span> • {schema.tables.length} tables
            </p>
          </div>
          
          {/* View Mode Toggle */}
          <div></div>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search tables..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Content */}
      {viewMode === 'list' ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Tables List */}
          <div className="space-y-4">
            {filteredTables.map((tableName) => {
              const columns = schema.columns[tableName] || [];
              const primaryKeys = schema.primary_keys[tableName] || [];
              const indexes = schema.indexes[tableName] || [];
              const relations = getRelatedTables(tableName);
              const isSelected = selectedTable === tableName;

              return (
                <div
                  key={tableName}
                  className={`bg-white border rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer ${
                    isSelected ? 'ring-2 ring-blue-500' : ''
                  }`}
                  onClick={() => setSelectedTable(isSelected ? null : tableName)}
                >
                  <div className="p-4 border-b bg-gray-50">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                        <Table2 className="w-5 h-5 text-blue-600" />
                        {tableName}
                      </h3>
                      <span className="text-sm text-gray-500">
                        {columns.length} columns
                      </span>
                    </div>
                  </div>

                  {isSelected && (
                    <div className="p-4 space-y-4">
                      {/* Quick Actions */}
                      <div className="flex flex-wrap gap-2">
                        <button
                          onClick={() => {
                            try {
                              const ddlCols = columns.map(c => `  ${c.name} ${c.type}${(c.nullable === 'NO') ? ' NOT NULL' : ''}${c.extra ? ' ' + c.extra : ''}`).join(',\n');
                              const pk = (schema.primary_keys[tableName] || []).length ? `,\n  PRIMARY KEY(${schema.primary_keys[tableName].join(', ')})` : '';
                              const ddl = `CREATE TABLE ${tableName} (\n${ddlCols}${pk}\n);`;
                              navigator.clipboard.writeText(ddl);
                              show('DDL copied', { type: 'success' });
                            } catch {}
                          }}
                          className="px-3 py-1.5 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                          Copy DDL
                        </button>
                        <button
                          onClick={() => {
                            const sel = `SELECT *\nFROM ${tableName}\nLIMIT 100;`;
                            localStorage.setItem('sqlWorkbenchQuery', sel);
                            navigate('/sql-workbench');
                          }}
                          className="px-3 py-1.5 text-xs bg-green-600 text-white rounded hover:bg-green-700"
                        >
                          Open SELECT template
                        </button>
                        {getRelatedTables(tableName).outgoing.length > 0 && (
                          <button
                            onClick={() => {
                              const fk = getRelatedTables(tableName).outgoing[0];
                              const join = `SELECT *\nFROM ${tableName} t\nJOIN ${fk.to_table} r ON t.${fk.from_column} = r.${fk.to_column}\nLIMIT 100;`;
                              localStorage.setItem('sqlWorkbenchQuery', join);
                              navigate('/sql-workbench');
                            }}
                            className="px-3 py-1.5 text-xs bg-purple-600 text-white rounded hover:bg-purple-700"
                          >
                            Open JOIN template
                          </button>
                        )}
                      </div>
                      {/* Columns */}
                      <div>
                        <h4 className="font-semibold text-gray-700 mb-2">Columns</h4>
                        <div className="space-y-1">
                          {columns.map((col) => (
                            <div
                              key={col.name}
                              className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm"
                            >
                              <div className="flex items-center gap-2">
                                {col.key === 'PRI' && (
                                  <div title="Primary Key">
                                    <Key className="w-4 h-4 text-yellow-500" />
                                  </div>
                                )}
                                <span className="font-medium">{col.name}</span>
                                <span className="text-gray-500">{col.type}</span>
                              </div>
                              <div className="flex items-center gap-2 text-xs text-gray-500">
                                {col.nullable === 'YES' && (
                                  <span className="bg-gray-200 px-2 py-1 rounded">nullable</span>
                                )}
                                {col.extra && (
                                  <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded">
                                    {col.extra}
                                  </span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Primary Keys */}
                      {primaryKeys.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
                            <Key className="w-4 h-4 text-yellow-500" />
                            Primary Keys
                          </h4>
                          <div className="text-sm text-gray-600 bg-yellow-50 p-2 rounded">
                            {primaryKeys.join(', ')}
                          </div>
                        </div>
                      )}

                      {/* Indexes */}
                      {indexes.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-gray-700 mb-2">Indexes</h4>
                          <div className="space-y-1">
                            {indexes.map((idx, i) => (
                              <div key={i} className="text-sm bg-gray-50 p-2 rounded">
                                <span className="font-medium">{idx.name}</span>
                                {idx.unique && (
                                  <span className="ml-2 bg-purple-100 text-purple-700 px-2 py-0.5 rounded text-xs">
                                    UNIQUE
                                  </span>
                                )}
                                <div className="text-gray-500 text-xs mt-1">
                                  Columns: {idx.columns.join(', ')}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Foreign Key Relationships */}
                      {(relations.outgoing.length > 0 || relations.incoming.length > 0) && (
                        <div>
                          <h4 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
                            <Link2 className="w-4 h-4 text-green-500" />
                            Relationships
                          </h4>
                          <div className="space-y-2">
                            {relations.outgoing.map((fk, i) => (
                              <div key={i} className="text-sm bg-green-50 p-2 rounded">
                                <div className="font-medium text-green-700">→ References</div>
                                <div className="text-gray-600">
                                  {fk.from_column} → {fk.to_table}.{fk.to_column}
                                </div>
                              </div>
                            ))}
                            {relations.incoming.map((fk, i) => (
                              <div key={i} className="text-sm bg-blue-50 p-2 rounded">
                                <div className="font-medium text-blue-700">← Referenced by</div>
                                <div className="text-gray-600">
                                  {fk.from_table}.{fk.from_column} → {fk.to_column}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Relationships Overview */}
          <div className="lg:sticky lg:top-6 h-fit">
            <div className="bg-white border rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                <Link2 className="w-5 h-5 text-green-500" />
                Foreign Key Relationships
              </h3>
              {schema.foreign_keys.length === 0 ? (
                <p className="text-gray-500 text-sm">No foreign key relationships found.</p>
              ) : (
                <div className="space-y-3">
                  {schema.foreign_keys.map((fk, i) => (
                    <div key={i} className="bg-gray-50 p-3 rounded-lg border border-gray-200">
                      <div className="flex items-center gap-2 text-sm">
                        <span className="font-semibold text-blue-600">{fk.from_table}</span>
                        <span className="text-gray-500">.{fk.from_column}</span>
                        <span className="text-gray-400">→</span>
                        <span className="font-semibold text-green-600">{fk.to_table}</span>
                        <span className="text-gray-500">.{fk.to_column}</span>
                      </div>
                      <div className="text-xs text-gray-400 mt-1">{fk.constraint_name}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-black border rounded-lg shadow-sm p-6 relative" style={{ zIndex: 1 }}>
          <ERDiagram tables={schema.tables} columns={schema.columns} foreign_keys={schema.foreign_keys} />
        </div>
      )}

      {/* Floating view toggle */}
      <div className="fixed bottom-6 right-6 z-[10001] flex gap-2">
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
