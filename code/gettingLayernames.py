import fiona


def list_layers_in_geopackage(filepath):
    """Prints the layer names in a GeoPackage file using Fiona."""
    # Open the GeoPackage file
    with fiona.Env():
        # List all layers in the GeoPackage
        layers = fiona.listlayers(filepath)

        print("Layers in GeoPackage:")
        for layer in layers:
            print(f"Layer: {layer}")

            # Open the layer and print some metadata
            with fiona.open(filepath, layer=layer) as src:
                print("Columns:", src.schema['properties'].keys())
                print("First 5 rows:")
                for i, feature in enumerate(src):
                    if i < 5:
                        print(feature)
                    else:
                        break
                print()  # Newline for readability


# Example usage
geopackage_path = 'CA_Wetlands_Geopackage.gpkg'
list_layers_in_geopackage(geopackage_path)
