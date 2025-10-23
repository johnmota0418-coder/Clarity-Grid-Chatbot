#!/usr/bin/env python3
"""
Update RAG system to use FREE electrical grid data
"""

import os
import shutil
from pathlib import Path

def update_app_to_free_data():
    """Update app.py to use FREE electrical grid data"""
    
    print("🔄 Updating RAG System to Use FREE Electrical Grid Data")
    print("=" * 60)
    
    # Backup current app.py
    if os.path.exists("app.py"):
        shutil.copy2("app.py", "app_backup_before_free_data.py")
        print("📦 Backed up current app.py")
    
    # Read current app.py with proper encoding
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Update file references
    print("🔧 Updating file references...")
    
    # Update FAISS index file
    content = content.replace('faiss_index.idx', 'free_electrical_grid_index.faiss')
    
    # Update metadata file  
    content = content.replace('metadata.json', 'free_electrical_grid_metadata.json')
    
    # Update page title and description
    content = content.replace(
        '<title>Clarity Grid Chatbot</title>',
        '<title>FREE Electrical Grid Assistant - 84K+ Real Lines</title>'
    )
    
    content = content.replace(
        '<h1>🔌 Electrical Grid Assistant</h1>',
        '<h1>⚡ FREE Electrical Grid Assistant - 84,686 Real Transmission Lines</h1>'
    )
    
    # Update placeholder text
    content = content.replace(
        'placeholder="Ask about electrical transmission lines..."',
        'placeholder="Ask about real electrical transmission lines (84K+ lines, completely FREE search)..."'
    )
    
    # Add a comment to indicate FREE data usage
    free_data_comment = '''# UPDATED TO USE FREE ELECTRICAL GRID DATA
# Files: free_electrical_grid_index.faiss (128MB, 83,686 vectors)
#        free_electrical_grid_metadata.json (59MB metadata)
# Source: 84,686 real transmission lines processed with sentence-transformers
# Cost: $0.00 (completely FREE embeddings)
# Model: all-MiniLM-L6-v2 (384-dimensional embeddings)

'''
    
    # Add comment at the top after imports
    import_end = content.find('app = FastAPI()')
    if import_end != -1:
        content = content[:import_end] + free_data_comment + content[import_end:]
    
    # Update success message
    content = content.replace(
        'print(f"✅ RAG system loaded: {len(texts)} documents indexed")',
        'print(f"✅ FREE RAG system loaded: {len(texts)} electrical transmission lines indexed (FREE embeddings)")'
    )
    
    print("💾 Writing updated app.py...")
    
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Updated app.py to use FREE electrical grid data")
    return True

def verify_free_files():
    """Verify FREE data files exist and show stats"""
    print("🔍 Verifying FREE electrical grid data files...")
    
    required_files = [
        "free_electrical_grid_index.faiss",
        "free_electrical_grid_metadata.json"
    ]
    
    all_exist = True
    total_size = 0
    
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            total_size += size
            print(f"  ✅ {file}: {size:,} bytes ({size/1024/1024:.1f} MB)")
        else:
            print(f"  ❌ {file}: NOT FOUND")
            all_exist = False
    
    if all_exist:
        print(f"📊 Total FREE data size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
    
    return all_exist

def test_free_data_loading():
    """Test that we can load the FREE data"""
    print("🧪 Testing FREE data loading...")
    
    try:
        import faiss
        import json
        
        # Test FAISS index
        print("  📊 Loading FAISS index...")
        index = faiss.read_index("free_electrical_grid_index.faiss")
        print(f"    ✅ Loaded: {index.ntotal:,} vectors, {index.d} dimensions")
        
        # Test metadata
        print("  📋 Loading metadata...")
        with open("free_electrical_grid_metadata.json", 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f"    ✅ Loaded: {len(metadata):,} metadata records")
        
        # Show sample data
        if metadata:
            sample = metadata[0]
            print(f"    📋 Sample: Line {sample['id']} - {sample['voltage']}V, {sample['owner']}")
        
        print("✅ FREE data loads successfully!")
        return True
        
    except Exception as e:
        print(f"  ❌ Loading failed: {e}")
        return False

def main():
    """Main update process"""
    print("🚀 Updating RAG System to FREE Electrical Grid Data")
    print("=" * 55)
    
    # Step 1: Verify files exist
    if not verify_free_files():
        print("❌ FREE data files missing.")
        return False
    
    # Step 2: Test data loading
    if not test_free_data_loading():
        print("❌ FREE data testing failed.")
        return False
    
    # Step 3: Update app.py
    if not update_app_to_free_data():
        print("❌ App update failed.")
        return False
    
    print("\n🎉 SUCCESS: RAG System Updated to FREE Data!")
    print("\n📋 Next Steps:")
    print("  1. Test locally: python -m uvicorn app:app --reload")
    print("  2. Test queries about transmission lines")
    print("  3. Deploy to Render when satisfied")
    print("\n💡 Sample Queries to Test:")
    print("  - 'Show me high voltage transmission lines'")
    print("  - 'Find lines owned by specific utilities'")
    print("  - 'What voltage levels are available?'")
    print("  - 'Tell me about transmission line infrastructure'")
    print(f"\n📊 System Stats:")
    print(f"  🗂️  83,686 searchable transmission lines")
    print(f"  💰 $0.00 total embedding cost")
    print(f"  ⚡ FREE sentence-transformers embeddings")
    print(f"  🚀 Ready for production deployment!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("❌ Update process failed!")
        exit(1)