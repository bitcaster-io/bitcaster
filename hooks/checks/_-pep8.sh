if git diff-index --quiet HEAD --; then
    # no changes between index and working copy; just run tests
    OUT=`pep8 src`
    RET=$?
else
    # Test the version that's about to be committed,
    # stashing all unindexed changes
    git stash -q --keep-index
#    FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -e '\.py$')
    FILES=$(gitflow_commit_files py)
    OUT=`pep8 $FILES`
    RET=$?
    git stash pop -q
fi

if [ $RET -eq 0 ];then
    gitflow_ok "Pep8 ok"
else
    gitflow_fail "Pep8 found dome issues."
    echo "$OUT"
    exit $RET
fi
