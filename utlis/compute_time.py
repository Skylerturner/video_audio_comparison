import pandas as pd
import numpy as np

all_hashes_df = pd.read_csv("all_hashes.csv")
all_hashes_1fps_df = pd.read_csv("all_hashes_1fps.csv")
comp_scott_dl_df = pd.read_csv("comparison_metrics_scottkress_halloween_dl.csv")
comp_scott_dl_1fps_df = pd.read_csv("comparison_metrics_scottkress_halloween_dl_1fps.csv")
comp_scott_dl_allv1_df = pd.read_csv("comparison_metrics_allv1_scottkress_halloween_dl.csv")

comp_scott_time = comp_scott_dl_df['comparison_seconds'].sum()
comp_scott_time_1fs = comp_scott_dl_1fps_df['comparison_seconds'].sum()
comp_scott_time_allv1 = comp_scott_dl_allv1_df['comparison_seconds'].sum()  
all_hash_time = all_hashes_df.groupby('video')['processing_seconds'].first().sum()
all_hash_1fps_time = all_hashes_1fps_df.groupby('video')['processing_seconds'].first().sum()

all_resize_hashes_df = pd.read_csv("all_resize_hashes.csv")
all_resize_hashes_1fps_df = pd.read_csv("all_resize_hashes_1fps.csv")
comp_resize_scott_dl_df = pd.read_csv("comparison_metrics_resize_scottkress_halloween_dl.csv")
comp_resize_scott_dl_1fps_df = pd.read_csv("comparison_metrics_resize_scottkress_halloween_dl_1fps.csv")
comp_resize_scott_dl_allv1_df = pd.read_csv("comparison_metrics_resize_allv1_scottkress_halloween_dl.csv")

comp_resize_time = comp_resize_scott_dl_df['comparison_seconds'].sum()
comp_resize_time_1fps = comp_resize_scott_dl_1fps_df['comparison_seconds'].sum()
comp_resize_time_allv1 = comp_resize_scott_dl_allv1_df['comparison_seconds'].sum()
all_resize_hash_time = all_resize_hashes_df.groupby('video')['processing_seconds'].first().sum()
all_resize_hash_1fps_time = all_resize_hashes_1fps_df.groupby('video')['processing_seconds'].first().sum()

print(f"Total comparison time for Scott's Halloween DL: {comp_scott_time:.2f} seconds")
print(f"Total comparison time for Scott's Halloween DL 1fps: {comp_scott_time_1fs:.2f} seconds")
print(f"Total comparison time for Scott's Halloween DL Allv1: {comp_scott_time_allv1:.2f} seconds")
print(f"Total hash time for all_hashes.csv: {all_hash_time:.2f} seconds")
print(f"Total hash time for all_hashes_1fps.csv: {all_hash_1fps_time:.2f} seconds")
print("--- Resized Hashes ---")
print(f"Total comparison time resized for Scott's Halloween DL: {comp_resize_time:.2f} seconds")
print(f"Total comparison time resized for Scott's Halloween DL 1fps: {comp_resize_time_1fps:.2f} seconds")
print(f"Total comparison time resized for Scott's Halloween DL Allv1: {comp_resize_time_allv1:.2f} seconds")
print(f"Total hash time for all_resize_hashes.csv: {all_resize_hash_time:.2f} seconds")
print(f"Total hash time for all_resize_hashes_1fps.csv: {all_resize_hash_1fps_time:.2f} seconds")