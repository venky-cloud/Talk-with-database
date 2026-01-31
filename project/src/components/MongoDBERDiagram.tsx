import ReactFlow, { Background, Controls, MiniMap, Node, Edge } from 'reactflow';
import 'reactflow/dist/style.css';

interface CollectionDetail {
  name: string;
  fields: string[];
}

interface MongoDBERDiagramProps {
  collections: CollectionDetail[];
}

export default function MongoDBERDiagram({ collections }: MongoDBERDiagramProps) {
  // Layout nodes in a grid
  const nodeSpacingX = 350;
  const nodeSpacingY = 280;

  const nodes: Node[] = collections.map((collection, i) => ({
    id: collection.name,
    type: 'default',
    position: {
      x: (i % 4) * nodeSpacingX,
      y: Math.floor(i / 4) * nodeSpacingY,
    },
    data: {
      label: (
        <div className="bg-gray-800 border-2 border-green-400 rounded-lg shadow-lg min-w-[200px] max-w-[280px]">
          <div className="px-3 py-2 bg-green-600 text-white font-bold rounded-t-lg text-center">
            {collection.name}
          </div>
          <div className="px-3 py-2 max-h-[180px] overflow-y-auto">
            <table className="w-full text-xs">
              <tbody>
                {collection.fields.slice(0, 10).map((field) => (
                  <tr key={field}>
                    <td className={`pr-2 font-mono ${
                      field === '_id' ? 'text-yellow-400 font-bold' : 'text-gray-200'
                    }`}>
                      {field}
                    </td>
                    <td className="text-gray-400 text-right">
                      {field === '_id' ? 'ObjectId' :
                       field.includes('_id') ? 'ObjectId' :
                       field.includes('date') || field.includes('at') ? 'Date' :
                       field.includes('is_') ? 'Boolean' :
                       field.includes('count') || field.includes('quantity') ? 'Number' :
                       'String'}
                    </td>
                    <td className="pl-2">
                      {field === '_id' && <span className="text-yellow-400 text-[10px]">PK</span>}
                    </td>
                  </tr>
                ))}
                {collection.fields.length > 10 && (
                  <tr>
                    <td colSpan={3} className="text-gray-500 text-center pt-1">
                      +{collection.fields.length - 10} more fields
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      ),
    },
  }));

  // Create edges for relationships (MongoDB references)
  const edges: Edge[] = [];
  
  // Add relationships based on common patterns
  const relationships = [
    { from: 'orders', to: 'customers', field: 'customer_id' },
    { from: 'orders', to: 'employees', field: 'employee_id' },
    { from: 'order_items', to: 'orders', field: 'order_id' },
    { from: 'order_items', to: 'products', field: 'product_id' },
    { from: 'products', to: 'categories', field: 'category_id' },
    { from: 'employees', to: 'departments', field: 'department_id' },
    { from: 'payments', to: 'orders', field: 'order_id' },
    { from: 'shipments', to: 'orders', field: 'order_id' },
    { from: 'reviews', to: 'products', field: 'product_id' },
    { from: 'reviews', to: 'customers', field: 'customer_id' },
    { from: 'inventory', to: 'products', field: 'product_id' },
    { from: 'sales', to: 'orders', field: 'order_id' },
    { from: 'sales', to: 'employees', field: 'employee_id' },
    { from: 'sales', to: 'customers', field: 'customer_id' },
  ];

  relationships.forEach((rel, idx) => {
    const fromExists = collections.find(c => c.name === rel.from);
    const toExists = collections.find(c => c.name === rel.to);
    
    if (fromExists && toExists) {
      edges.push({
        id: `e${idx}`,
        source: rel.from,
        target: rel.to,
        animated: true,
        style: { stroke: '#10b981', strokeWidth: 2 },
        label: rel.field,
        labelStyle: { fill: '#10b981', fontSize: 10 },
      });
    }
  });

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        minZoom={0.1}
        maxZoom={1.5}
        defaultViewport={{ x: 0, y: 0, zoom: 0.5 }}
        nodesDraggable={true}
        nodesConnectable={false}
        elementsSelectable={true}
      >
        <Background color="#1f2937" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={() => '#10b981'}
          maskColor="rgba(0, 0, 0, 0.6)"
        />
      </ReactFlow>
    </div>
  );
}
