import json

path = "/Users/Shared/old-laptop-c/D$/Purdue/Sem 6/Catapult/ml_pipeline/Model_2_Building_Detection.ipynb"
with open(path, "r") as f:
    nb = json.load(f)

for i, cell in enumerate(nb["cells"]):
    if cell["cell_type"] == "code":
        source = "".join(cell["source"])
        if "def display_predictions(dataset, model" in source:
            new_source = """def display_predictions(dataset, model, num_samples=3, image_paths=None):
    # Take a batch from the dataset
    for images, masks in dataset.take(1):
        preds = model.predict(images)
        # Threshold the prediction to create a binary mask
        preds_binary = (preds > 0.1).astype(np.float32)

        for i in range(min(num_samples, len(images))):
            # Extract filename if available
            filename_str = ""
            if image_paths is not None and i < len(image_paths):
                import os
                filename = os.path.basename(image_paths[i])
                filename_str = f"\\n({filename})"
                print(f"Checking image: {filename}")
                
            plt.figure(figsize=(15, 5))
            
            # 1. Original Image
            plt.subplot(1, 3, 1)
            plt.imshow(images[i].numpy().astype("uint8"))
            plt.title(f"Sample {i+1}: Original Image{filename_str}")
            plt.axis("off")
            
            # 2. Actual Label (Ground Truth)
            plt.subplot(1, 3, 2)
            plt.imshow(masks[i].numpy().squeeze(), cmap='gray')
            plt.title("Actual Building Mask")
            plt.axis("off")
            
            # 3. Model Output (Prediction)
            plt.subplot(1, 3, 3)
            plt.imshow(preds_binary[i].squeeze(), cmap='magma')
            plt.title("Predicted Building Mask")
            plt.axis("off")
            
            plt.tight_layout()
            plt.show()

print("Visualization function defined.")"""
            lines = new_source.split("\n")
            nb["cells"][i]["source"] = [line + "\n" if j < len(lines)-1 else line for j, line in enumerate(lines)]
            
        elif "display_predictions(test_ds, unet_model, num_samples=4)" in source:
            new_source = source.replace(
                "display_predictions(test_ds, unet_model, num_samples=4)",
                "display_predictions(test_ds, unet_model, num_samples=4, image_paths=test_paths)"
            )
            lines = new_source.split("\n")
            nb["cells"][i]["source"] = [line + "\n" if j < len(lines)-1 else line for j, line in enumerate(lines)]

with open(path, "w") as f:
    json.dump(nb, f, indent=1)

print("Notebook modified successfully.")
