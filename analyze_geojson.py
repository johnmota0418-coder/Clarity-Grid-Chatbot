#!/usr/bin/env python3
"""
Real GeoJSON analyzer for Phase 2 data integration planning
"""

import json
import os

def analyze_geojson_structure(filename):
    """Analyze GeoJSON file structure without loading entire file"""
    
    print(f"🔍 Analyzing {filename}...")
    
    # Get file size
    file_size = os.path.getsize(filename)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"📊 File size: {file_size_mb:.1f}MB ({file_size:,} bytes)")
    
    feature_count = 0
    sample_properties = None
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            # Read line by line to avoid memory issues
            for line_num, line in enumerate(f):
                
                # Count features by looking for OBJECTID (unique per feature)
                if '"OBJECTID":' in line:
                    feature_count += 1
                
                # Extract first complete feature properties for analysis
                if sample_properties is None and '"properties":' in line:
                    try:
                        # Find the properties object in this line or continue reading
                        properties_start = line.find('"properties":')
                        if properties_start != -1:
                            # Read from properties start
                            remaining = line[properties_start:]
                            # Simple extraction of properties content
                            if '"OBJECTID":' in remaining:
                                # Extract key properties from the line
                                sample_properties = {}
                                
                                # Extract common fields we see
                                fields_to_extract = [
                                    'OBJECTID', 'ID', 'TYPE', 'STATUS', 'OWNER', 
                                    'VOLTAGE', 'VOLT_CLASS', 'SUB_1', 'SUB_2', 'SHAPE__Len'
                                ]
                                
                                for field in fields_to_extract:
                                    field_pattern = f'"{field}":'
                                    if field_pattern in remaining:
                                        start = remaining.find(field_pattern) + len(field_pattern)
                                        # Find the value (simple extraction)
                                        value_part = remaining[start:start+100].strip()
                                        if value_part.startswith(' "'):
                                            # String value
                                            end_quote = value_part.find('"', 2)
                                            if end_quote != -1:
                                                sample_properties[field] = value_part[2:end_quote]
                                        elif value_part.startswith(' '):
                                            # Numeric value
                                            comma_pos = value_part.find(',')
                                            if comma_pos != -1:
                                                try:
                                                    sample_properties[field] = float(value_part[1:comma_pos])
                                                except:
                                                    sample_properties[field] = value_part[1:comma_pos].strip()
                    except Exception as e:
                        print(f"⚠️  Could not parse sample properties: {e}")
                
                # Don't read entire file, just enough to get statistics
                if line_num > 1000 and feature_count > 0:
                    break
    
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None
    
    print(f"📈 Found {feature_count} features in sample (extrapolating...)")
    
    # Extrapolate total features based on sample
    if feature_count > 0:
        # Rough estimation: features per line ratio
        estimated_total = int(feature_count * (84694 / min(1000, line_num + 1)))
        print(f"📊 Estimated total features: {estimated_total:,}")
        
        # API cost estimation for embedding generation
        tokens_per_feature = 150  # Conservative estimate
        total_tokens = estimated_total * tokens_per_feature
        cost_per_1k_tokens = 0.00002  # Google embedding API cost
        estimated_cost = (total_tokens / 1000) * cost_per_1k_tokens
        
        print(f"💰 Estimated API cost: ${estimated_cost:.2f}")
        print(f"🎯 Estimated tokens: {total_tokens:,}")
        
        # Batch processing recommendations
        print(f"\n📦 Batch Processing Recommendations:")
        for batch_size in [100, 500, 1000]:
            num_batches = estimated_total // batch_size
            cost_per_batch = (batch_size * tokens_per_feature / 1000) * cost_per_1k_tokens
            print(f"  {batch_size:,} features/batch = {num_batches:,} batches (${cost_per_batch:.4f}/batch)")
    
    # Show sample properties
    if sample_properties:
        print(f"\n🔑 Sample Feature Properties:")
        for key, value in sample_properties.items():
            print(f"  {key}: {value}")
    
    return {
        'file_size_mb': file_size_mb,
        'estimated_features': estimated_total if feature_count > 0 else None,
        'sample_properties': sample_properties,
        'estimated_cost': estimated_cost if feature_count > 0 else None
    }

def create_rag_content_template(sample_props):
    """Create template for converting GeoJSON features to RAG content"""
    
    if not sample_props:
        return None
    
    template = """
def geojson_to_rag_content(feature):
    '''Convert GeoJSON feature to RAG-friendly text content'''
    props = feature.get('properties', {})
    
    # Core identification
    line_id = props.get('ID', 'Unknown')
    line_type = props.get('TYPE', 'Unknown')
    status = props.get('STATUS', 'Unknown')
    
    # Electrical specifications
    voltage = props.get('VOLTAGE', 'Unknown')
    volt_class = props.get('VOLT_CLASS', 'Unknown')
    
    # Infrastructure details
    owner = props.get('OWNER', 'Not Available')
    sub_1 = props.get('SUB_1', 'Unknown')
    sub_2 = props.get('SUB_2', 'Unknown')
    length = props.get('SHAPE__Len', 'Unknown')
    
    # Location info from geometry
    geometry = feature.get('geometry', {})
    geom_type = geometry.get('type', 'Unknown')
    
    # Build comprehensive text content
    content = f"Transmission Line {line_id}: {line_type} line with {voltage}V capacity ({volt_class} class). "
    content += f"Status: {status}. Owned by: {owner}. "
    content += f"Connects {sub_1} to {sub_2}. "
    content += f"Line length: {length} meters. "
    content += f"Geometry type: {geom_type}. "
    content += f"Infrastructure type: Electric power transmission and control system."
    
    return {
        'id': line_id,
        'content': content,
        'voltage': voltage,
        'owner': owner,
        'status': status,
        'substations': [sub_1, sub_2],
        'length': length
    }
"""
    
    print(f"\n📝 RAG Content Template:")
    print(template)
    
    return template

if __name__ == "__main__":
    filename = "Electric-Power-Transmission-Lines.geojson"
    
    analysis = analyze_geojson_structure(filename)
    
    if analysis and analysis['sample_properties']:
        create_rag_content_template(analysis['sample_properties'])
        
        print(f"\n✨ Phase 2 Implementation Plan:")
        print(f"  1. Process {analysis['estimated_features']:,} transmission lines")
        print(f"  2. Generate embeddings in batches of 500-1000")
        print(f"  3. Estimated cost: ${analysis['estimated_cost']:.2f}")
        print(f"  4. Replace current fake data with real electrical grid data")
        print(f"  5. Maintain same FAISS vector search functionality")
    else:
        print("❌ Could not analyze file structure")