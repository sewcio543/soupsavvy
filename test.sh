TAG_ARG="--no-tag"
COMMIT_ARG="--no-commit"

if [ "${{ inputs.tag }}" = "true" ]; then
    TAG_ARG="--tag"
fi

if [ "${{ inputs.commit }}" = "true" ]; then
    COMMIT_ARG="--commit"
fi

echo "${TAG_ARG} ${COMMIT_ARG}"
bump2version ${{ inputs.type }} --verbose $TAG_ARG $COMMIT_ARG --dry-run
