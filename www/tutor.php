<?php
session_start();
include '../php/dbase.php';
include '../php/checklogin.php';

if (isset($_COOKIE['aitid'])) {
    $topic_id = $_COOKIE['aitid'];
    $topic = lookupTopic($db, $topic_id, $user->id);
    if (is_null($topic)) {
        $topic_title = "Topic {$topic_id} not in database!";
    } else {
        $topic_title = $topic->name;
        if ($topic->status == null) {
            updateTopicProgress($db, $user->id, $topic_id, 1);
            updateTopicProgress($db, $user->id, $topic->parent, 1);
            $topic_begin = true;
        } else {
            $topic_begin = false;
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
    <div class="chat-container">
        <div class="topic"> <?php echo $topic_title; ?> </div>
        <div class="chat-box" id="chatBox"></div>
        <div class="input-area">
            <input type="hidden" id="uid" value="<?php echo $user->id ?>">
            <textarea autofocus cols="120" style="font-size: 16px;max-width: 100%" rows="4" id="message"
	     placeholder="Type a message... (SHIFT+ENTER for new line, ENTER to send)"
	     onKeyDown="handleKeyPress(event)"></textarea>
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <div class="tutor-container test">
      Feel confident that you have mastered this topic?
      <a href="/topic-test.php" class="take-test">
	<span>Take Test</span></a>
    </div>

<?php if ($topic_begin === true): ?>
  <div id="startModal" class="modal" style="display: block">
    <div class="modal-content">
       <h2>Ready to learn how to <?php echo strtolower($topic_title); ?>?</h2>
       Your AI tutor will help you learn how to <?php echo strtolower($topic->description); ?>
       <p>When you feel confident with the topic, use the 'Take Test' button.
          Pass the test and this topic will be marked as 'mastered'.</p>
       <p>When you're ready to begin, click the button below...</p>
<?php
    echo "<button onClick=\"hideModal('startModal');tutorBegin('new:{$topic->id}')\">Let's go!</button>\n";
?>
        </div>
    </div>
<?php else: ?>
<script type="text/javascript">
    window.onload = tutorContinue('resume:<?php echo $topic->id; ?>');
</script>
<?php endif ?>
</body>
</html>
