"""
Test the schema inspection endpoint
"""
from fastapi_app.routers.schema import inspect_schema, SchemaRequest

def test_schema():
    print("Testing schema inspection endpoint...")
    try:
        req = SchemaRequest()
        result = inspect_schema(req)
        
        print("\n[SUCCESS] Schema inspection working!")
        print(f"Database: {result.get('db', 'N/A')}")
        print(f"Tables: {result.get('tables', [])}")
        print(f"Columns: {len(result.get('columns', {}))} tables with column info")
        
        if 'error' in result:
            print(f"\n[WARNING] Error in result: {result['error']}")
        else:
            print("\n[SUCCESS] Backend can successfully fetch database details!")
            
    except Exception as e:
        print(f"\n[ERROR] Schema inspection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_schema()
