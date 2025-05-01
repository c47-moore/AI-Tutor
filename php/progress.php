
<?php
$topics = lookupTopics($db);
$progress = getUserProgress($db, $user->id);
?>
<div class="tutor-container">
<h1>Your tuition progress ...</h1>
<?php
if (is_string($topics)) {
    echo '<div class="errDiv">' . $topics . '</div>';
} else {
    $in_child = 0;
    $children = 0;
    foreach ($topics as $row) {
        $has_parent = ($row['parent'] != 0);
        if ($progress == null) {
            $status = '0';
        } else {
            $progress_key = array_search($row['id'], array_column($progress, 'topic_id'));
            if ($progress_key === false)
                $status = '0';
            else
                $status = $progress[$progress_key]['status'];
        }

        $button = "<button class=\"study-button\" onClick=\"launchTopic({$row['id']})\">";
        if ($status == '0') {
            $topic_status = 'not-started';
	    if ($has_parent)
                $stext = 'Topic not started';
	    else
		$stext = 'Chapter not started';
            $button .= 'Begin</button>';
        } elseif ($status == '1') {
            $topic_status = 'started';
	    if ($has_parent)
		$stext = 'Studying ...';
	    else
                $stext = 'Chapter in progress';
	    $button = "<button onClick=\"takeTest({$row['id']})\" class=\"study-button\">Take test</button>" .
		$button . 'Continue ...</button>';
        } elseif ($status == '2') {
            $topic_status = 'mastered';
            $stext = 'Mastered!';
            $button = '';
        } else {
            $topic_status = 'unknown';
            $stext = 'Unknown progress status.';
        }

        $class = 'progress-topic-name';
        $row_html = $row['name'];
        if ($row['parent'] != 0) {
            $class .= ' topic-child';
            $stext .= $button;
            if ($in_child == 0) {
                $in_child = 1;
                echo "<div id=\"expand-container\">\n<div id=\"expand-contract{$children}\" class=\"collapsed\">\n";
                $children = $children + 1;
            }
        } else {
            if ($in_child == 1) {
                $in_child = 0;
                echo "</div></div>";
            }
            $row_html = "<button class=\"expand-button\" onClick=\"expandContract(this, 'expand-contract{$children}')\">+</button>" . $row_html;
        }

        echo "<div class=\"progress-row\">\n";
        echo "<div class=\"{$class}\">{$row_html}</div>\n";
        echo "<div class=\"progress-topic-status {$topic_status}\">{$stext}</div>\n</div>\n";
    }
}
?>
    </div></div> <!-- end last row expander //-->
</div> <!-- end progress container //-->
