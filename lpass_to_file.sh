rm "lpass_show_file"
for id in `lpass ls | sed -n "s/^.*\s\[id:\s*\([0-9]*\)\]$/\1/p"`; do
	lpass show ${id} >> "lpass_show_file"
	# 区切り線。Notesの中に同じ文字列があるとバグる
	echo +=-_ +=-_+=-_+=-_+=-_+=-_+=-_+=-_+=-_+=-_ >> "lpass_show_file"
done

