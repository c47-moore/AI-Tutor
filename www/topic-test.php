<?php
session_start();
include '../php/dbase.php';
include '../php/checklogin.php';

if (isset($_COOKIE['aitid'])) {
    $topic_id = $_COOKIE['aitid'];
    $topic = lookupTopic($db, $topic_id, $user->id);
    if (is_null($topic)) {
        header('Location: /index.php');
        exit(0);
    } else {
        $topic_title = $topic->name;
	switch ($topic->status) {
	case 0:
	    $test_notice = "<p>You haven't yet studied this topic.</p><p><a href=\"/tutor.php\">Click here</a> if you want to study with your AI tutor.</p>"; 
	    break;

	case 2:
	    $test_notice = "<p>You have already passed this test!</p><p><a href=\"/index.php\">Click here</a> to return to the dashboard.</p>";
	    break;

	default:
	    $test_notice = null;
	}
    }
} else {
    header('Location: /index.php');
    exit(0);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <?php include '../php/title.php'; ?>
    <link rel="icon" type="image/png" href="/images/favicon.png" />
    <link rel="stylesheet" href="css/styles.css">
    <script id="MathJax-script" async
        src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
    </script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="js/script.js"></script>
</head>
<body class="calign">
<?php include '../php/navbar.php'; ?>

    <div class="modal" id="model-modal" style="display:none"></div>
    <div class="modal-response" id="modal-popup" style="display:none">
        <span class="close" onClick="toggleResponseModal()">X</span>
        <div id="tutorResponse" class="tutorResponse">
        </div>
        <button id="modalButton" onClick="toggleResponseModal()">Okay</button>
    </div>

<input type="hidden" id="uid" value="<?php echo $user->id ?>">
<?php
    if ($test_notice !== null) {
        echo "<div class=\"errDiv info\">{$test_notice}</div>\n";
    }

    $tests = getTopicTests($db, $topic_id);
    if ($tests == null) {
        echo "<p>Unable to find any tests for {$topic_title}!</p></body></html>\n";
        exit(0);
    }

    /* Ensure these tests are added to the user test table
       so that we can keep track of their test results */
    foreach ($tests as $test) {
	addUserTest($db, $user->id, $test);
    }

    echo "<div class=\"accordion\"><h2>Test: {$topic_title}</h2>\n";
    $qnum = 0;
    $first = 0;

    /* retrieve the user's tests on this topic */
    $tests = getUserTopicTests($db, $user->id, $topic_id);
    foreach ($tests as $test) {

        $qnum = $qnum + 1;
	$row_class = "test-row";
        if ($test['score'] == 0) {
	    $img = '/images/edit.webp';
	} elseif ($test['score'] == 1) {
	    $img = '/images/incorrect.webp';
	} else {
	    $row_class .= " tick";
	    $img = null;
	}

	echo "<div class=\"{$row_class}\">\n<div class=\"qnum\">{$qnum}.</div>\n";
	echo "<div class=\"qtext\">{$test['question']}</div>\n";
	if (is_null($img)) {
	    echo "<span class=\"correct\"></span>\n";
	} else {
	    echo "<button id=\"b{$qnum}\" onClick=\"accordionToggle('{$qnum}')\" class=\"accordion-item-button\"><img src=\"{$img}\" /></button>\n";
	}
	echo "</div>\n";

	if ($test['score'] < 2) {
	    if ($first == 0) {
		$first = $qnum;
		$class = "accordion-item-body active";
		$tinput = "<input autofocus ";
	    } else {
		$class = "accordion-item-body";
		$tinput = "<input autofocus ";
	    }
	    echo "<div id=\"q{$qnum}\" class=\"{$class}\">" .
	      "<div class=\"loadContainer\" id=\"l{$qnum}\"></div>\n" .
	      "<div id=\"i{$qnum}\" class=\"accordion-item-body-content\">\n" .
	      "<button style=\"float:right\" onclick=\"testAnswer({$qnum}, {$test['qid']})\">Send</button>" .
	      "<span>{$tinput} onkeydown=\"answerKeyPress(event, {$qnum}, {$test['qid']})\" " .
	      "class=\"answer\" id=\"a{$qnum}\" type=\"text\" placeholder=\"Write your answer here ...\"></span>\n</div></div>\n";
	}

    }
    echo "</div>\n";
?>
    <script src="js/accordion.js"></script>
    <audio id="correctAudio"><source src="/sounds/correct.mp3" type="audio/mpeg"></audio>
    <audio id="incorrectAudio"><source src="/sounds/incorrect.mp3" type="audio/mpeg"></audio>
</body>
</html>
