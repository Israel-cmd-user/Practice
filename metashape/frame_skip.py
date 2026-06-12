import pandas as pd

input_file = (r'F:\1\2026-05-26-11-08-30\metashape.csv')
output_file = 'metashape.csv'

df = pd.read_csv(input_file)
df = df.iloc[360:].reset_index(drop=True)
column_name = 'label' 
df[column_name] = [f"frame{i}" for i in range(len(df))]

df.to_csv(output_file, index=False)

print(f"Done! Saved to {output_file}. New frame range: frame 0 through frame {len(df) - 1}")