import json

# Paths
input_file = r"C:\Users\johnj\Plan-1\data.json"
output_file = r"C:\Users\johnj\Plan-1\data_preprocessed.jsonl"

# Load GeoJSON
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Function to convert a feature to text
def feature_to_text(feature):
    props = feature["properties"]
    geom = feature.get("geometry", {})
    coords = geom.get("coordinates", [])
    
    # Flatten geometry to a simple summary
    if coords and isinstance(coords[0][0], list):
        start = coords[0][0]
        end = coords[0][-1]
        geom_text = f"From {start} to {end}"
    else:
        geom_text = str(coords)
    
    text = (
        f"ID: {props.get('ID')}\n"
        f"Type: {props.get('TYPE')}\n"
        f"Status: {props.get('STATUS')}\n"
        f"Voltage: {props.get('VOLTAGE')}\n"
        f"Owner: {props.get('OWNER')}\n"
        f"Substations: {props.get('SUB_1')} -> {props.get('SUB_2')}\n"
        f"Source: {props.get('SOURCE')} ({props.get('SOURCEDATE')})\n"
        f"Geometry: {geom_text}"
    )
    return text

# Process all features and write to JSONL
with open(output_file, "w", encoding="utf-8") as f_out:
    for feature in data.get("features", []):
        chunk = {"text": feature_to_text(feature)}
        f_out.write(json.dumps(chunk) + "\n")

print(f"Preprocessed {len(data.get('features', []))} features and saved to {output_file}")
