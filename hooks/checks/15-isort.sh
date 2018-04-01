
if git diff-index --quiet HEAD --; then
    # no changes between index and working copy; just run tests
    OUT=`isort -c -rc src/ tests/`
    RET=$?
else
    # Test the version that's about to be committed,
    # stashing all unindexed changes
    stash;
    FILES=$(gitflow_python_files)
    if [ -n "$FILES" ]; then
        OUT=`isort -c $FILES`
        RET=$?
    else
        gitflow_ok "iSort skipped (no .py file in commit)"
        RET=-1
    fi
    unstash;
fi

if [ $RET -eq 0 ];then
    gitflow_ok "iSort ok"
elif [ $RET -gt 0 ];then
    gitflow_fail "iSort found some issues."
    echo "$OUT"
    exit $RET

fi
