import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

export default function Documentation() {
  const documentation = `
# Talk with Database - Complete Documentation

## 🚀 Getting Started

Talk with Database is an AI-powered platform that helps you interact with MySQL and MongoDB databases using natural language. The system generates, validates, and executes queries with built-in safety features.

---

## 📋 Table of Contents

1. [Features Overview](#features-overview)
2. [SQL Query Page](#sql-query-page)
3. [SQL Workbench](#sql-workbench)
4. [Schema Workbench](#schema-workbench)
5. [MongoDB Query](#mongodb-query)
6. [Query History](#query-history)
7. [Safety Features](#safety-features)
8. [Configuration](#configuration)
9. [API Reference](#api-reference)

---

## ✨ Features Overview

### Core Features
- **Natural Language to SQL**: Convert plain English to SQL queries
- **SQL Workbench**: Direct SQL editor with schema browser
- **Schema Visualization**: Interactive ER diagrams and table explorer
- **MongoDB Support**: Query MongoDB collections
- **Query History**: Track all executed queries with statistics
- **Safety Validation**: Prevent dangerous operations

---

## 💬 SQL Query Page

### How to Use
1. Navigate to **SQL Query** page
2. Type your request in natural language
3. Click **Generate SQL**
4. Review the generated query
5. Execute automatically or copy to workbench

### Example Queries

\`\`\`text
Show all customers
Get the top 5 orders by amount
Find customers who ordered in the last month
List employees in the Sales department
Calculate total revenue by product category
\`\`\`

### Generated Output

\`\`\`sql
-- Example: "Show all customers"
SELECT * FROM customers LIMIT 10;

-- Example: "Get top 5 orders by amount"
SELECT * FROM orders 
ORDER BY amount DESC 
LIMIT 5;
\`\`\`

### 🛡️ Dangerous Query Warning
When the AI generates a potentially dangerous query (DELETE without WHERE, UPDATE without WHERE, TRUNCATE, DROP), a prominent warning appears:

- **Red warning box** with detailed explanation
- **Recommendation** to add WHERE clauses
- Guidance on safer alternatives

---

## 🛠️ SQL Workbench

### Features
- **Schema Browser** (left panel): Browse tables and columns
- **Query Editor** (top panel): Write SQL directly
- **Results Viewer** (bottom panel): See query output

### Keyboard Shortcuts
- **Ctrl + Enter**: Execute query
- **Double-click table**: Insert table name
- **Double-click column**: Insert column name

### Example Usage

\`\`\`sql
-- Direct SQL execution
SELECT c.name, COUNT(o.id) as order_count
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name
ORDER BY order_count DESC
LIMIT 10;
\`\`\`

### Safety Confirmations
Dangerous queries trigger a confirmation dialog:
- DELETE without WHERE
- UPDATE without WHERE
- TRUNCATE TABLE
- DROP TABLE/DATABASE

---

## 📊 Schema Workbench

### List View
- View all tables with detailed information
- Expandable rows show:
  - Column names and data types
  - Primary keys (highlighted in yellow)
  - Foreign key relationships
  - Indexes

### Diagram View
- **Interactive ER Diagram** showing:
  - Tables as draggable nodes
  - Foreign key relationships as lines
  - Primary keys highlighted
  - Zoom and pan controls
  - Minimap for navigation

### Example Schema Info

\`\`\`text
Table: customers
├─ id (int) - PK
├─ name (varchar)
├─ email (varchar)
└─ created_at (datetime)

Foreign Keys:
orders.customer_id → customers.id
\`\`\`

---

## 🍃 MongoDB Query

### Features
- Database and collection selection
- Natural language to MongoDB operations
- Support for: find, insert, update, delete

### Example Queries

\`\`\`text
Find all users
Insert a new document
Update user names
Delete old records
\`\`\`

### Generated MongoDB Operations

\`\`\`javascript
// Find operation
db.users.find({})

// Insert operation
db.users.insertOne({ name: "John", age: 30 })

// Update operation
db.users.updateMany(
  { status: "active" },
  { $set: { updated_at: new Date() } }
)
\`\`\`

---

## 📜 Query History

### What's Tracked
- Natural language query input
- Generated SQL/MongoDB query
- Execution status (success/error)
- Result count
- Execution time (milliseconds)
- Error messages (if any)

### Statistics Dashboard
- **Total Queries**: All executed queries
- **Success Rate**: Percentage of successful executions
- **Avg Execution Time**: Performance metrics
- **MySQL vs MongoDB**: Query type breakdown

### Features
- **Search**: Filter queries by text
- **Delete**: Remove individual queries
- **Clear All**: Reset history
- **Refresh**: Update list

---

## 🛡️ Safety Features

### 1. Query Validation
All queries are validated before execution:
- **DDL Blocked**: DROP, TRUNCATE not allowed by default
- **WHERE Required**: DELETE/UPDATE must have WHERE clause
- **Limit Enforcement**: SELECT queries capped at 1000 rows
- **No Escaped Identifiers**: Clean MySQL syntax required

### 2. Dangerous Query Detection

\`\`\`sql
-- ⚠️ Triggers Warning
DELETE FROM customers;

-- ✅ Safe Alternative
DELETE FROM customers WHERE id = 1;
\`\`\`

### 3. Confirmation Dialogs
User must confirm before executing:
- DELETE without WHERE
- UPDATE without WHERE
- TRUNCATE operations
- DROP statements

---

## ⚙️ Configuration

### Backend Configuration (.env)

\`\`\`bash
# Database
DB_TYPE=mysql
DB_URI=mysql+pymysql://user:pass@host:port/dbname
MONGO_URI=mongodb+srv://user:pass@cluster/db

# AI Generator
GENERATOR_PROVIDER=mixtral
MISTRAL_API_KEY=your_api_key_here
GENERATOR_TEMPERATURE=0.2
GENERATOR_N_CANDIDATES=5

# Safety
SAFETY_BLOCK_DDL=true
SAFETY_REQUIRE_WHERE=true
SELECT_LIMIT_CAP=1000
\`\`\`

### Frontend Configuration

\`\`\`bash
# API Base URL
VITE_API_BASE=http://127.0.0.1:8000
\`\`\`

---

## 🔌 API Reference

### Endpoints

#### 1. Schema Inspection
\`\`\`http
POST /schema/inspect
Body: { "db_type": "mysql" }
Response: { tables, columns, primary_keys, indexes, foreign_keys }
\`\`\`

#### 2. Generate Query
\`\`\`http
POST /generate
Body: { "text": "show all customers", "db_type": "mysql", "schema": {...} }
Response: { "candidates": ["SELECT * FROM customers LIMIT 10;"] }
\`\`\`

#### 3. Validate Query
\`\`\`http
POST /validate
Body: { "candidates": ["SELECT..."], "db_type": "mysql" }
Response: { "valid": true, "blocked": false }
\`\`\`

#### 4. Execute Query
\`\`\`http
POST /execute
Body: { "query": "SELECT...", "db_type": "mysql" }
Response: { "rows": [...], "row_count": 10 }
\`\`\`

#### 5. Query History
\`\`\`http
GET /history/list?limit=100
POST /history/save
DELETE /history/delete/{id}
DELETE /history/clear
GET /history/stats
\`\`\`

---

## 📚 Best Practices

### Writing Good Natural Language Queries
✅ **Good**: "Show customers who placed orders in the last 30 days"
❌ **Bad**: "customers"

✅ **Good**: "Get top 10 products by revenue with category names"
❌ **Bad**: "products"

### SQL Workbench Tips
1. Always test queries with LIMIT first
2. Use WHERE clauses for UPDATE/DELETE
3. Review foreign key relationships before joins
4. Check execution time in history

### Safety Guidelines
1. Never run DELETE/UPDATE without WHERE in production
2. Always backup before running TRUNCATE
3. Test on sample data first
4. Review query history regularly

---

## 🆘 Troubleshooting

### Common Issues

**1. CORS Errors**
- Ensure backend is running on port 8000
- Check CORS configuration in main.py

**2. MySQL Connection Failed**
- Verify MySQL is running
- Check DB_URI in .env file
- Test connection manually

**3. Query Generation Fails**
- Check MISTRAL_API_KEY is valid
- Verify schema is loaded correctly
- Try more specific natural language

**4. Queries Not Executing**
- Check safety validation settings
- Verify database permissions
- Review backend logs for errors

---

## 🎯 Quick Start Commands

### Start Backend
\`\`\`bash
cd backend
uvicorn fastapi_app.main:app --reload --host 0.0.0.0 --port 8000
\`\`\`

### Start Frontend
\`\`\`bash
cd project
npm run dev
\`\`\`

### Test Backend Health
\`\`\`bash
curl http://127.0.0.1:8000/
# Response: {"message":"FastAPI service is running"}
\`\`\`

---

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review query history for error messages
- Check backend terminal for Python tracebacks
- Verify .env configuration

---

**Version**: 1.0.0  
**Last Updated**: September 2025
`;

  return (
    <div className="py-24 px-4 max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-[#00ff00] to-[#00cc00]">
        Documentation
      </h1>
      <p className="text-gray-400 mb-8 text-lg">Learn how to use the Database Assistant effectively</p>

      <div className="prose prose-invert max-w-none">
        <ReactMarkdown
          components={{
            code({node, inline, className, children, ...props}) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <SyntaxHighlighter
                  style={atomDark}
                  language={match[1]}
                  PreTag="div"
                  className="border border-[#00ff00]/30 rounded-lg !bg-black/30"
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className="bg-black/30 px-1 rounded" {...props}>
                  {children}
                </code>
              );
            }
          }}
        >
          {documentation}
        </ReactMarkdown>
      </div>
    </div>
  );
}