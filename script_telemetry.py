import pandas as pd
import json
import streamlit as st
import os

feature_map = {}
attribute_map = {}
user_readable_mapping={
    "PTPolicylistGen": "Policy Tags",
    "Dot11Gen": "Global Radio Configs",
    "FlexpolicyGen": "Flex Profiles",
    "RadiusServerGroup": "AAA->RADIUS Server Groups",
    "RfProfileDefaultGen": "Multi-Screen Attributes",
    "AaaNeSettings": "AAA->Method Lists",
    "RadiusNeSettings": "AAA->RADIUS Servers",
    "SiteTagConfigGen": "Site Tags",
    "MeshConfigGen": "Mesh->Global",
    "InterfaceConfig": "VLAN->VLAN",
    "ApJoinProfileGen": "AP Join Profiles",
    "RrmGen": "RRM",
    "WirelessAaaPolicyConfigGen": "AAA Policy",
    "MeshProfileGen": "Mesh Profiles",
    "ApTagGen": "Static AP Tag Mapping",
    "GuestlanMapGen": "Guest LAN Map",
    "WlanConfigProfileGen": "WLAN Profiles",
    "WlanPolicyProfileGen": "Policy Profiles",
    "GuestlanConfigGen": "Guest LAN Profiles",
    "NgwcInterfaceConfig": "VLAN->SVI",
    "RfTagGen": "RF Tags",
    "RfProfileGen": "RF Profiles"
}

def write_json(file_path, data):
    """
    Write data to a JSON file.
    
    Args:
    - file_path: Path to the output JSON file.
    - data: Data to be written to the file.
    """
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)  # Indent for better readability
    print(f"Data written to {file_path}")

def plot_attribute_map(attribute_map, feature_name):
    """
    Plot the attribute map data as a bar plot.
    
    Args:
    - attribute_map: Dictionary containing attribute names as keys and usage counts as values.
    - feature_name: Name of the feature for which attributes are being plotted.
    """
    st.subheader(f'Usage Count of Attributes for {feature_name}')
    st.bar_chart(attribute_map)

def plot_data(feature_map, attribute_map):
    """
    Plot the feature map data as a bar plot.
    
    Args:
    - feature_map: Dictionary containing feature names as keys and usage counts as values.
    - attribute_map: Dictionary containing feature names as keys and nested dictionaries containing attribute names and usage counts as values.
    """
    st.subheader('Usage Count of Feature Config Names')
    st.bar_chart(feature_map)

def analyze_csv(csv_file):
    """
    Analyze telemetry data from a CSV file and create a JSON output with aggregated counts of attributes per feature.
    Also plot the data.
    
    Args:
    - csv_file: Path to the CSV file containing telemetry data.
    """
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file)

        # Iterate over each row in the DataFrame
        for index, row in df.iterrows():
            # Access values of specific columns for the current row
            feature_name = row['feature_name']
            attribute_name = row['attribute_name']
            count = row['count']
            
            # Check if the feature name contains "Configuration"
            if "Configuration" in feature_name:
                # Extract model/table name from the feature name
                model_table_name = feature_name.split("_")[0]
                readable_name = user_readable_mapping.get(model_table_name, model_table_name)
                # Update attribute count for the current model/table
                current_attr_count = attribute_map.setdefault(readable_name, {}).setdefault(attribute_name, 0)
                current_attr_count += count
                attribute_map[readable_name][attribute_name] = current_attr_count
                
                # Update maximum count for the current model/table
                feature_map[readable_name] = max(feature_map.get(readable_name, 0), current_attr_count)
        
        # Plot the data
        plot_data(feature_map, attribute_map)
        for feature_name, attributes in attribute_map.items():
            plot_attribute_map(attributes, feature_name)
            
        # Create download buttons for JSON files
        output_json_bytes = json.dumps(feature_map, indent=4).encode()
        st.download_button(label="Download Feature Map JSON", data=output_json_bytes, file_name="output.json", mime="application/json")

        attributes_json_bytes = json.dumps(attribute_map, indent=4).encode()
        st.download_button(label="Download Attribute Map JSON", data=attributes_json_bytes, file_name="attributes.json", mime="application/json")

    except Exception as e:
        print(f"Error occurred: {e}")

# Streamlit app
def main():
    st.title("Telemetry Analysis")
    st.write("Upload a CSV file to analyze telemetry data.")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        if uploaded_file.seek(0, os.SEEK_END) == 0:
            st.write("Uploaded file is empty. Please upload a file with data.")
        else:
            st.write("File uploaded successfully!")
            # Save uploaded file locally
            with open("uploaded_file.csv", "wb") as file:
                file.write(uploaded_file.getvalue())
            st.write("Uploaded file saved locally as 'uploaded_file.csv'")
            # Analyze data
            analyze_csv("uploaded_file.csv")

if __name__ == "__main__":
    main()
