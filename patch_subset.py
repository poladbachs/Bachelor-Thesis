import pandas as pd

INPUT_CSV = "subset_360.csv"
OUTPUT_CSV = "subset_362_final.csv"

manual_injections = {
    "6367670a1a6d9265ec0179cf": """public static char toChar(final Character ch, final char defaultValue){
  return ch.charValue();
}""",
    "636766f91a6d9265ec01777f": """public static boolean toBoolean(Boolean bool){
  return bool.booleanValue();
}"""
}

df = pd.read_csv(INPUT_CSV)
new_rows = []

for idx, row in df.iterrows():
    new_rows.append(row)
    func_id = row["_id"]
    if row["exit_code"] == 0 and func_id in manual_injections:
        injected_row = row.copy()
        injected_row["candidate"] = manual_injections[func_id]
        injected_row["exit_code"] = 1
        injected_row["generated_by"] = "manual_injection"
        new_rows.append(injected_row)

patched_df = pd.DataFrame(new_rows)
patched_df.to_csv(OUTPUT_CSV, index=False)

<<<<<<< HEAD
print(f"Final dataset created: {OUTPUT_CSV} with {len(patched_df)} rows and {patched_df['_id'].nunique()} unique function IDs.")
=======
print(f"Final dataset created: {OUTPUT_CSV} with {len(patched_df)} rows and {patched_df['_id'].nunique()} unique function IDs.")
>>>>>>> 4a40ad669ff873b71e9ab9e18a32448a90f7b4eb
