#!/bin/bash
OWNER="pratyay360"


# gh api users/$OWNER/packages?package_type=$TYPE --paginate -q '.[].name' | while read -r PACKAGE; do
#     # if [[ "$PACKAGE" == *"$REPO"* ]]; then
#         echo "Deleting package: $PACKAGE"
#         gh api --method DELETE "users/$OWNER/packages/$TYPE/$PACKAGE"
#     # fi
# done
PACKAGE_NAMES=$(gh api "/users/pratyay360/packages?package_type=container" --paginate --jq '.[].name')
for PACKAGE in $PACKAGE_NAMES; do
    echo "Deleting package: $PACKAGE"

    gh api "/users/pratyay360/packages/container/$PACKAGE/versions" --paginate --jq '.[].id' |
    while read -r ID; do
        gh api -X DELETE "/users/pratyay360/packages/container/$PACKAGE/versions/$ID"
    done

    gh api -X DELETE "/users/pratyay360/packages/container/$PACKAGE"
done
