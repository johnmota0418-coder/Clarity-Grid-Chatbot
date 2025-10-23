#!/usr/bin/env python3
"""
FREE Streaming Processor - Handle large GeoJSON files efficiently
"""

import json
import numpy as np
import faiss
import os
import time
from pathlib import Path

# Import free local embedding model
from sentence_transformers import SentenceTransformer

class FreeStreamingProcessor:
    """Stream large GeoJSON files and generate FREE embeddings"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"📥 Loading FREE streaming processor with {model_name}")
        self.model = SentenceTransformer(model_name)
        print(f"✅ Ready for streaming processing - completely FREE!")
    
    def feature_to_rag_content(self, feature):
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
    
    def stream_geojson_features(self, filepath: str):
        """Stream features from large GeoJSON file line by line"""
        
        print("📖 Streaming large GeoJSON file...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            in_features = False
            feature_count = 0
            current_feature = ""
            brace_count = 0
            
            for line_num, line in enumerate(f):
                line = line.strip()
                
                # Skip until we find features array
                if '"features"' in line:
                    in_features = True
                    continue
                
                if not in_features:
                    continue
                
                # Skip array opening bracket
                if line == '[':
                    continue
                
                # End of features array
                if line.startswith(']'):
                    break
                
                # Handle feature objects
                if line.startswith('{'):
                    current_feature = line
                    brace_count = line.count('{') - line.count('}')
                elif current_feature:
                    current_feature += " " + line
                    brace_count += line.count('{') - line.count('}')
                
                # Complete feature found
                if current_feature and brace_count == 0:
                    # Clean up the feature string
                    feature_str = current_feature.rstrip(',').strip()
                    
                    try:
                        feature = json.loads(feature_str)
                        yield feature
                        feature_count += 1
                        
                        if feature_count % 5000 == 0:
                            print(f"  📈 Streamed {feature_count:,} features...")
                    except json.JSONDecodeError:
                        # Skip invalid features
                        pass
                    
                    current_feature = ""
                    brace_count = 0
        
        print(f"✅ Total features streamed: {feature_count:,}")
    
    def process_streaming(self, filepath: str, batch_size: int = 1000):
        """Process large file with streaming and FREE embeddings"""
        
        print(f"🚀 FREE Streaming Processing")
        print(f"📁 File: {filepath}")
        print(f"💰 Cost: $0.00 (completely free!)")
        print(f"📦 Batch size: {batch_size}")
        print("=" * 60)
        
        all_texts = []
        all_metadata = []
        processed_count = 0
        
        start_time = time.time()
        
        # Stream and convert features
        print("📝 Converting features to RAG content...")
        
        for feature in self.stream_geojson_features(filepath):
            try:
                rag_content = self.feature_to_rag_content(feature)
                all_texts.append(rag_content['content'])
                all_metadata.append(rag_content)
                processed_count += 1
                
                # Process in batches to save memory
                if len(all_texts) >= batch_size:
                    # Generate embeddings for this batch
                    print(f"  ⚡ Processing batch {processed_count//batch_size} ({len(all_texts)} features)...")
                    
                    batch_embeddings = self.model.encode(all_texts, batch_size=100, show_progress_bar=False)
                    
                    # Save intermediate results
                    self.save_batch_results(batch_embeddings, all_texts, all_metadata, processed_count)
                    
                    # Clear batch
                    all_texts = []
                    all_metadata = []
                
            except Exception as e:
                print(f"  ⚠️  Skipped feature: {e}")
                continue
        
        # Process final batch
        if all_texts:
            print(f"  ⚡ Processing final batch ({len(all_texts)} features)...")
            batch_embeddings = self.model.encode(all_texts, batch_size=100, show_progress_bar=False)
            self.save_batch_results(batch_embeddings, all_texts, all_metadata, processed_count)
        
        # Combine all batches
        print("🔗 Combining all batches...")
        final_index, final_metadata = self.combine_batches()
        
        processing_time = time.time() - start_time
        
        print(f"\n🎉 FREE Streaming Processing COMPLETED!")
        print(f"⏱️  Total time: {processing_time:.1f} seconds")
        print(f"📊 Processed: {processed_count:,} transmission lines")
        print(f"💰 Total cost: $0.00 (FREE!)")
        print(f"💾 Files: {final_index}, {final_metadata}")
        
        return final_index, final_metadata
    
    def save_batch_results(self, embeddings, texts, metadata, count):
        """Save batch results to temporary files"""
        
        batch_num = count // 1000 + 1
        
        # Save embeddings
        embedding_file = f"batch_{batch_num}_embeddings.npy"
        np.save(embedding_file, embeddings)
        
        # Save metadata  
        metadata_file = f"batch_{batch_num}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f)
        
        print(f"    💾 Saved batch {batch_num}: {len(embeddings)} vectors")
    
    def combine_batches(self):
        """Combine all batch files into final results"""
        
        # Find all batch files
        import glob
        
        embedding_files = sorted(glob.glob("batch_*_embeddings.npy"))
        metadata_files = sorted(glob.glob("batch_*_metadata.json"))
        
        print(f"🔍 Found {len(embedding_files)} embedding batches")
        
        # Load and combine embeddings
        all_embeddings = []
        all_metadata = []
        
        for i, (emb_file, meta_file) in enumerate(zip(embedding_files, metadata_files)):
            print(f"  📂 Loading batch {i+1}...")
            
            # Load embeddings
            batch_embeddings = np.load(emb_file)
            all_embeddings.append(batch_embeddings)
            
            # Load metadata
            with open(meta_file, 'r') as f:
                batch_metadata = json.load(f)
                all_metadata.extend(batch_metadata)
            
            # Clean up batch file
            os.remove(emb_file)
            os.remove(meta_file)
        
        # Combine all embeddings
        final_embeddings = np.vstack(all_embeddings)
        
        # Create FAISS index
        print(f"🗂️  Creating final FAISS index...")
        index = faiss.IndexFlatL2(final_embeddings.shape[1])
        index.add(final_embeddings.astype(np.float32))
        
        # Save final results
        final_index_file = "free_electrical_grid_index.faiss"
        final_metadata_file = "free_electrical_grid_metadata.json"
        
        faiss.write_index(index, final_index_file)
        
        with open(final_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(all_metadata, f, indent=2, ensure_ascii=False)
        
        # Get file sizes
        index_size = os.path.getsize(final_index_file)
        metadata_size = os.path.getsize(final_metadata_file)
        
        print(f"✅ Final files created:")
        print(f"  🗂️  {final_index_file}: {index_size:,} bytes ({len(all_metadata):,} vectors)")
        print(f"  📋 {final_metadata_file}: {metadata_size:,} bytes")
        
        return final_index_file, final_metadata_file

if __name__ == "__main__":
    processor = FreeStreamingProcessor()
    
    if os.path.exists('Electric-Power-Transmission-Lines.geojson'):
        index_file, metadata_file = processor.process_streaming(
            'Electric-Power-Transmission-Lines.geojson',
            batch_size=1000
        )
        print(f"\n🎉 COMPLETED: {index_file}, {metadata_file}")
    else:
        print("❌ Dataset file not found")