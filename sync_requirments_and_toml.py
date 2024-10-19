import tomlkit

# Read the requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Sort the requirements alphabetically
requirements.sort()

# Read the existing pyproject.toml
with open('pyproject.toml', 'r') as f:
    pyproject = tomlkit.parse(f.read())

# Inject the dependencies into the pyproject.toml
pyproject['project']['dependencies'] = tomlkit.array().multiline(True)
for req in requirements:
    pyproject['project']['dependencies'].append(req)

# Write the updated pyproject.toml back to the file
with open('pyproject.toml', 'w') as f:
    f.write(tomlkit.dumps(pyproject))

print("Dependencies from requirements.txt have been added to pyproject.toml")