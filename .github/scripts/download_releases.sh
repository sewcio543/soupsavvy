releases=()

for tag in $(gh release list --json tagName | jq -r '.[].tagName'); do
    name=$(echo "$tag" | tr -d '\r')
    release_info=$(gh release view "$name" --json tagName,body)
    release_data+=("$release_info")
done

echo "${release_data[@]}" | jq -s '.' > releases.json
