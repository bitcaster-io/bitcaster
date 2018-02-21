ERROR=0
for file in $(gitflow_commit_files py); do
    if grep -Erls "(pdb\.|print 111)" $file >/dev/null ; then
    	gitflow_fail "Found pdb call in <$file>"
    	exit 1
    fi
done

gitflow_ok "Pdb check ok"
