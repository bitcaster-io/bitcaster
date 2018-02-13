ERROR=0
for file in $(gitflow_commit_files); do
    if grep -Erls "^<<<<<<< |^>>>>>>>" $file >/dev/null ; then
    	gitflow_fail "Markers found in $file"
    	exit 1
    fi
done

gitflow_ok "No merge markers found"
