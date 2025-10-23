#!/usr/bin/env python3
"""
Update RAG system to use real electrical grid data instead of fake data
"""

import os
import shutil
from pathlib import Path

def update_app_for_real_data():
    """Update app.py to use electrical grid data files"""
    
    print("🔄 Updating app.py for real electrical grid data...")
    
    # Read current app.py
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Update file references
    updated_content = content.replace(
        'index = faiss.read_index("faiss_index.idx")',
        'index = faiss.read_index("electrical_grid_index.faiss")'
    ).replace(
        'with open("metadata.json", "r", encoding="utf-8") as f:',
        'with open("electrical_grid_metadata.json", "r", encoding="utf-8") as f:'
    ).replace(
        'print(f"✅ RAG system loaded: {len(texts)} documents indexed")',
        'print(f"✅ RAG system loaded: {len(texts)} electrical transmission lines indexed")'
    )
    
    # Update title and description
    updated_content = updated_content.replace(
        'title="Clarity Grid Chatbot"',
        'title="Clarity Grid Chatbot - Real Electrical Grid Data"'
    )
    
    # Save updated app.py
    with open("app.py", "w") as f:
        f.write(updated_content)
    
    print("✅ Updated app.py for electrical grid data")
    return True

def update_generate_embeddings():
    """Update generate_embeddings.py to use real data (if needed)"""
    
    if not os.path.exists("generate_embeddings.py"):
        print("⚠️  generate_embeddings.py not found - skipping")
        return True
    
    print("🔄 Updating generate_embeddings.py...")
    
    with open("generate_embeddings.py", "r") as f:
        content = f.read()
    
    # Update output file references
    updated_content = content.replace(
        '"faiss_index.idx"',
        '"electrical_grid_index.faiss"'
    ).replace(
        '"metadata.json"',
        '"electrical_grid_metadata.json"'
    )
    
    with open("generate_embeddings.py", "w") as f:
        f.write(updated_content)
    
    print("✅ Updated generate_embeddings.py")
    return True

def backup_fake_data():
    """Backup original fake data files"""
    
    print("💾 Backing up original fake data files...")
    
    backup_dir = Path("backup_fake_data")
    backup_dir.mkdir(exist_ok=True)
    
    files_to_backup = [
        "faiss_index.idx",
        "metadata.json", 
        "data.json",
        "data_preprocessed.jsonl"
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, backup_dir / file)
            print(f"  📁 Backed up: {file}")
    
    print("✅ Fake data backed up to backup_fake_data/")
    return True

def verify_real_data_files():
    """Verify that real data files exist"""
    
    print("🔍 Verifying real electrical grid data files...")
    
    required_files = [
        "electrical_grid_index.faiss",
        "electrical_grid_metadata.json"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            size = os.path.getsize(file)
            print(f"  ✅ {file}: {size:,} bytes")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        print("   Run phase 2 processing first to generate these files")
        return False
    
    print("✅ All real data files present")
    return True

def test_updated_system():
    """Test the updated system works"""
    
    print("🧪 Testing updated system...")
    
    try:
        # Import updated modules
        import json
        import faiss
        
        # Test loading
        index = faiss.read_index("electrical_grid_index.faiss")
        with open("electrical_grid_metadata.json", "r") as f:
            metadata = json.load(f)
        
        print(f"✅ FAISS index loaded: {index.ntotal:,} vectors")
        print(f"✅ Metadata loaded: {len(metadata):,} records")
        
        # Test sample data
        if metadata:
            sample = metadata[0]
            print(f"✅ Sample record: {sample.get('id', 'Unknown')} - {sample.get('owner', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main update process"""
    
    print("🌟 Phase 2: Update RAG System for Real Electrical Grid Data")
    print("=" * 60)
    
    # Step 1: Verify real data files exist
    if not verify_real_data_files():
        print("\n❌ Cannot proceed without real data files")
        print("   Wait for fast_phase2.py to complete, or run it first")
        return False
    
    # Step 2: Backup fake data
    backup_fake_data()
    
    # Step 3: Update application files
    if not update_app_for_real_data():
        print("❌ Failed to update app.py")
        return False
    
    update_generate_embeddings()
    
    # Step 4: Test updated system
    if not test_updated_system():
        print("❌ System test failed")
        return False
    
    print("\n🎉 System Successfully Updated!")
    print("✅ Now using real electrical transmission line data")
    print("🔄 Ready for deployment with real data")
    
    # Show sample queries
    print(f"\n📋 Sample queries now supported:")
    print("  • 'Find transmission lines in Massachusetts'")
    print("  • 'Show me 161kV power lines'") 
    print("  • 'What lines are owned by Niagara Mohawk?'")
    print("  • 'Find overhead AC transmission lines'")
    
    return True

if __name__ == "__main__":
    main()