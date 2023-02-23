#!/usr/bin/env bash
# The bootstrap script is meant to be run once for a new repository. It will do the following:
#   - Remove .git history
#   - Initialize a new git repository with git init
#   - Replace all pyclient, PYCLIENT, client strings with the desired client name

echo "Removing skeleton repo git history"
rm -rf .git

echo "Initialize new git repo"
git init

echo "Adding initial git content"
git add ./* .github/* .gitignore

read -r -p "Base name? [client] > " client_name
client_name=${client_name:-client}
client_name=${client_name}-tools
echo "Using name: [$client_name]"

read -r -p "Package name? [pyclient] > " package_name
package_name=${package_name:-pyclient}
echo "Using name: [$package_name]"

echo "Adding initial git commit"
git commit -m "Initial commit"

echo "Replacing all 'pyclient' and 'PYCLIENT' instances with '${package_name}' and '${package_name^^}'"
find src -type f -exec sed -i -e "s/pyclient/${package_name}/g" {} \;
find ci -type f -exec sed -i -e "s/pyclient/${package_name}/g" {} \;
find src -type f -exec sed -i -e "s/PYCLIENT/${package_name^^}/g" {} \;
sed -i -e "s/pyclient/${package_name}/g" pyproject.toml
sed -i -e "s/pyclient/${package_name}/g" README.md

echo "Replacing all 'client-tools' instances with '${client_name}-tools"
find src -type f -exec sed -i -e "s/client-tools/${client_name}/g" {} \;
sed -i -e "s/client-tools/${client_name}/g" README.md

git mv src/python/pyclient src/python/"${package_name}"

echo "Committing name changes"
git add ./* .github/* .gitignore
git commit -m "Renamed pyclient to $package_name"