import yaml

with open('manifest.yaml', 'r') as file:
    try:
        manifest = yaml.safe_load(file)
        print("YAML content:")
        print(manifest)
        if 'version' in manifest:
            print(f"Version: {manifest['version']}")
        else:
            print("Error: 'version' field not found")
    except yaml.YAMLError as exc:
        print(f"YAML Error: {exc}")
