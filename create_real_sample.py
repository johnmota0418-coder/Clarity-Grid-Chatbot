#!/usr/bin/env python3
"""
Create a small but real electrical grid dataset from our sample for immediate deployment
"""

import json
import numpy as np
import faiss
import os
import google.generativeai as genai
from pathlib import Path

def create_real_sample_dataset():
    """Create a small real dataset from our validated sample"""
    
    print("🔬 Creating Real Sample Dataset from Test Data")
    print("=" * 50)
    
    # Configure API
    api_key = os.getenv("GOOGLE_AI_API_KEY", "AIzaSyDu_A4_boYS532-NDub0lXnXKjFEXDB_jQ")
    genai.configure(api_key=api_key)
    
    # Load our test sample
    with open("sample_test.geojson", 'r') as f:
        sample_data = json.load(f)
    
    print(f"📊 Processing {len(sample_data['features'])} real transmission lines...")
    
    # Process each feature
    all_metadata = []
    all_embeddings = []
    
    for i, feature in enumerate(sample_data['features']):
        # Convert to RAG content
        rag_content = feature_to_rag_content(feature)
        print(f"  📝 Feature {i+1}: {rag_content['id']} - {rag_content['owner']}")
        
        # Generate embedding
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=rag_content['content'],
                task_type="retrieval_document"
            )
            embedding = np.array(result['embedding'], dtype=np.float32)
            
            all_embeddings.append(embedding)
            all_metadata.append(rag_content)
            
            print(f"    ✅ Generated embedding: {embedding.shape}")
            
        except Exception as e:
            print(f"    ❌ Embedding failed: {e}")
    
    if not all_embeddings:
        print("❌ No embeddings generated")
        return False
    
    # Create FAISS index
    print(f"\n🗂️  Creating FAISS index with {len(all_embeddings)} vectors...")
    embeddings_matrix = np.vstack(all_embeddings)
    
    index = faiss.IndexFlatL2(embeddings_matrix.shape[1])
    index.add(embeddings_matrix)
    
    # Save files
    index_path = "electrical_grid_index.faiss" 
    metadata_path = "electrical_grid_metadata.json"
    
    faiss.write_index(index, index_path)
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(all_metadata, f, indent=2, ensure_ascii=False)
    
    # Verify files
    index_size = os.path.getsize(index_path)
    metadata_size = os.path.getsize(metadata_path) 
    
    print(f"\n💾 Real Dataset Created:")
    print(f"  📊 {index_path}: {index_size:,} bytes ({len(all_embeddings)} vectors)")
    print(f"  📋 {metadata_path}: {metadata_size:,} bytes ({len(all_metadata)} records)")
    
    # Test the index
    print(f"\n🧪 Testing created index...")
    test_index = faiss.read_index(index_path)
    with open(metadata_path, 'r') as f:
        test_metadata = json.load(f)
    
    print(f"✅ Index verification: {test_index.ntotal} vectors")
    print(f"✅ Metadata verification: {len(test_metadata)} records")
    
    # Show sample data
    print(f"\n📋 Sample Real Data:")
    for i, item in enumerate(test_metadata):
        print(f"  {i+1}. {item['id']}: {item['voltage']}V, {item['owner']}")
    
    return True

def feature_to_rag_content(feature):
    """Convert GeoJSON feature to RAG content"""
    props = feature.get('properties', {})
    
    line_id = props.get('ID', f"OBJ_{props.get('OBJECTID', 'Unknown')}")
    line_type = props.get('TYPE', 'Transmission Line')
    status = props.get('STATUS', 'Unknown')
    voltage = props.get('VOLTAGE', 'Unknown')
    volt_class = props.get('VOLT_CLASS', 'Unknown')
    owner = props.get('OWNER', 'Not Available')
    sub_1 = props.get('SUB_1', 'Unknown')
    sub_2 = props.get('SUB_2', 'Unknown')
    length = props.get('SHAPE__Len', 'Unknown')
    
    # Build comprehensive content
    content_parts = []
    content_parts.append(f"Transmission Line {line_id} is a {line_type} electrical power line.")
    content_parts.append(f"The line status is {status}.")
    
    if voltage != 'Unknown' and voltage != -999999:
        content_parts.append(f"It operates at {voltage} volts in the {volt_class} voltage class.")
    else:
        content_parts.append(f"It operates in the {volt_class} voltage class.")
    
    if owner not in ['NOT AVAILABLE', 'Unknown']:
        content_parts.append(f"The line is owned by {owner}.")
    
    if sub_1 != 'Unknown' and sub_2 != 'Unknown':
        content_parts.append(f"It connects {sub_1} substation to {sub_2} substation.")
    
    if isinstance(length, (int, float)) and length > 0:
        length_km = length / 1000
        content_parts.append(f"The transmission line is approximately {length_km:.1f} kilometers long.")
    
    content_parts.append("This is electrical grid infrastructure for power transmission and control.")
    
    # Add location info from geometry if available
    geometry = feature.get('geometry', {})
    if geometry.get('coordinates'):
        coords = geometry['coordinates'][0][0]  # First point of first line
        if len(coords) >= 2:
            lon, lat = coords[0], coords[1]
            content_parts.append(f"The line is located at approximately {lat:.3f}°N, {abs(lon):.3f}°W.")
    
    content = ' '.join(content_parts)
    
    return {
        'id': line_id,
        'content': content,
        'voltage': voltage,
        'voltage_class': volt_class,
        'owner': owner,
        'status': status,
        'substations': [sub_1, sub_2],
        'length_km': length / 1000 if isinstance(length, (int, float)) and length > 0 else None,
        'line_type': line_type
    }

if __name__ == "__main__":
    success = create_real_sample_dataset()
    
    if success:
        print(f"\n🎉 Real Sample Dataset Created Successfully!")
        print(f"🔄 Ready to update app.py with real electrical grid data")
        print(f"📝 Run: python update_to_real_data.py")
    else:
        print(f"❌ Failed to create dataset")