M=`find src -type d -name migrations -exec git clean -n {} \;`
if [ -n "$M" ]; then
    gitflow_fail "Found untracked migrations $M"
    exit 1
fi

gitflow_ok "No untracked migrations found"
