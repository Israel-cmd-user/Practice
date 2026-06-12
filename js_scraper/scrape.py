import json
import os
import pandas as pd

json_files = [
    "1.json",
    "2.json",
    "3.json",
    "4.json",
]  

all_records = []

# Ingest and merge records from all 4 files
for file_name in json_files:
    if not os.path.exists(file_name):
        print(f" Warning: File '{file_name}' not found. Skipping.")
        continue

    print(f" Reading {file_name}...")
    with open(file_name, "r") as f:
        raw_data = json.load(f)

    # Standardize data structure handling
    records = (
        raw_data.get("data", raw_data)
        if isinstance(raw_data, dict)
        else raw_data
    )
    all_records.extend(records)

# De-duplicate records by structure_no to keep the script efficient
df_temp = pd.DataFrame(all_records)
if "structure_no" in df_temp.columns:
    df_temp = df_temp.drop_duplicates(subset=["structure_no"])
    records = df_temp.to_dict("records")
else:
    print(" Error: No 'structure_no' field found in JSON files.")
    records = []

all_urls = []
pdf_types = ["IVS", "IVPS", "ISS", "ISPS"]

# Process every unique structure across the dataset
print(f" Processing {len(records)} unique structures...")
for record in records:
    struct_id = record.get("structure_no")
    insp_date = record.get("inspdate")

    if not struct_id:
        continue

    # --- Generate PDFs ---
    for pdf_type in pdf_types:
        all_urls.append(
            {
                "structure_no": struct_id,
                "asset_type": "PDF",  # Standardized category name
                "asset_sub_type": f"PDF_{pdf_type}",
                "url": f"https://strumanweb.co.za/nara/structurefile/{struct_id}/{pdf_type}",
            }
        )

    # --- Generate Speculative Images (S01-S18 & V01-V18) ---
    if insp_date:
        try:
            # Reformat 'YYYY-MM-DD' to 'DD_MM_YYYY'
            year, month, day = insp_date.split("-")
            formatted_date = f"{day}_{month}_{year}"

            # Create prefixes list: S01 to S18 and V01 to V18
            prefixes = []
            for i in range(1, 19):
                num_str = str(i).zfill(2)  
                prefixes.append(f"S{num_str}")
                prefixes.append(f"V{num_str}")

            # Loop through all 36 potential image variants per bridge
            for prefix in prefixes:
                filename = f"{struct_id}_{prefix}_{formatted_date}.jpg"

                all_urls.append(
                    {
                        "structure_no": struct_id,
                        "asset_type": "Image",  # Standardized category name
                        "asset_sub_type": f"Image_{prefix}",
                        "url": f"https://strumanweb.co.za/nara/photo/{struct_id}/{filename}",
                    }
                )
        except ValueError:
            continue  # Skip entry if inspection date layout is malformed

# Convert to DataFrame
df_assets = pd.DataFrame(all_urls)

# Save the master tracking manifest
df_assets.to_csv("download_manifest.csv", index=False)


# Isolate and save PDF URLs
pdf_urls = df_assets[df_assets["asset_type"] == "PDF"]["url"].tolist()
with open("pdf_url_list.txt", "w") as f:
    f.write("\n".join(pdf_urls))

# Isolate and save Image URLs
image_urls = df_assets[df_assets["asset_type"] == "Image"]["url"].tolist()
with open("image_url_list.txt", "w") as f:
    f.write("\n".join(image_urls))

print(f"\n Complete! Generated {len(df_assets)} total potential targets.")
print(f" Isolated PDF Links: {len(pdf_urls)} saved to 'pdf_url_list.txt'")
print(f" Isolated Image Links: {len(image_urls)} saved to 'image_url_list.txt'")
print(" Full tracking sheet saved to 'download_manifest.csv'")