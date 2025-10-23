#!/usr/bin/env python3
"""
Sample GeoJSON data to understand structure and plan Phase 2 data integration
"""

import json

def sample_geojson(filename, num_features=5):
    """Sample first few features from GeoJSON file"""
    print(f"📊 Sampling {filename}...")
    
    # Read just enough data to understand structure
    with open(filename, 'r', encoding='utf-8') as f:
        # Read line by line to handle large files
        content = ""
        bracket_count = 0
        features_found = 0
        in_features = False
        
        for line in f:
            content += line
            
            # Count brackets to know when we have complete JSON
            bracket_count += line.count('{') - line.count('}')
            
            # Look for features array start
            if '"features":' in line:
                in_features = True
            
            # Count complete features (look for feature closing)
            if in_features and '"geometry":' in line and '}' in line:
                features_found += 1
                
                if features_found >= num_features:
                    # Add closing brackets for valid JSON
                    content += "\n]}\n"
                    break
    
    try:
        # Parse the sampled JSON
        data = json.loads(content)
        
        print(f"✅ Successfully parsed {len(data.get('features', []))} features")
        
        # Analyze structure
        if 'features' in data and data['features']:
            sample_feature = data['features'][0]
            properties = sample_feature.get('properties', {})
            
            print(f"\n📋 Sample Feature Properties:")
            for key, value in properties.items():
                value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                print(f"  {key}: {value_str}")
            
            print(f"\n🗺️  Sample Geometry Type: {sample_feature.get('geometry', {}).get('type')}")
            
            # Extract key fields for RAG content
            key_fields = ['ID', 'TYPE', 'STATUS', 'OWNER', 'VOLTAGE', 'VOLT_CLASS', 'SUB_1', 'SUB_2', 'SHAPE__Len']
            
            print(f"\n📝 Sample RAG Content Structure:")
            for field in key_fields:
                if field in properties:
                    print(f"  {field}: {properties[field]}")
            
            return data, properties.keys()
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parse Error: {e}")
        # Show problematic content
        print("Problematic content ending:")
        print(content[-200:])
        return None, None

def estimate_processing_plan(sample_data, total_file_size_mb):
    """Estimate processing requirements for full dataset"""
    
    if not sample_data or 'features' not in sample_data:
        return
    
    sample_features = len(sample_data['features'])
    
    # Estimate total features (rough calculation)
    # Assuming linear relationship between file size and feature count
    estimated_features = int((total_file_size_mb / 1) * sample_features * 8)  # rough estimate
    
    print(f"\n📈 Processing Estimates:")
    print(f"  Sample features: {sample_features}")
    print(f"  Estimated total features: {estimated_features:,}")
    print(f"  File size: {total_file_size_mb}MB")
    
    # Embedding API cost estimation
    # Assuming ~200 tokens per feature, $0.000020 per 1K tokens
    estimated_tokens = estimated_features * 200
    estimated_cost = (estimated_tokens / 1000) * 0.000020
    
    print(f"  Estimated tokens: {estimated_tokens:,}")
    print(f"  Estimated API cost: ${estimated_cost:.2f}")
    
    # Batch size recommendations
    batch_sizes = [100, 500, 1000]
    print(f"\n📦 Recommended batch sizes:")
    for batch_size in batch_sizes:
        batches = estimated_features // batch_size
        print(f"  {batch_size} features/batch = {batches} batches")

if __name__ == "__main__":
    filename = "Electric-Power-Transmission-Lines.geojson"
    file_size_mb = 130  # From earlier check
    
    sample_data, field_names = sample_geojson(filename, num_features=3)
    
    if sample_data:
        estimate_processing_plan(sample_data, file_size_mb)
        
        print(f"\n🔑 All Available Fields ({len(field_names) if field_names else 0}):")
        if field_names:
            for field in sorted(field_names):
                print(f"  - {field}")
        
        print(f"\n✨ Ready for Phase 2 implementation!")
    else:
        print("❌ Failed to parse sample data")