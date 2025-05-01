<?php
session_start();
include '../php/dbase.php';
include '../php/checklogin.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <?php include '../php/title.php'; ?>
    <link rel="icon" type="image/png" href="/images/favicon.png" />
    <link rel="stylesheet" href="css/styles.css" />
    <script src="js/script.js"></script>
</head>
<body>
<?php include '../php/navbar.php'; ?>
<?php include '../php/progress.php'; ?>

<div class="tutor-container" style="overflow:hidden">
<h2>Instructions</h2>
<img src="/images/aitutor.webp" style="float:left;margin-right:10px" /><p>
Your Key Stage 2 Mathematics journey consists of a number of chapters, with each chapter
focusing on a different part of the syllabus.</p><p>
Explore each chapter above and study its topics. Expand each chapter area using the '+'
button. You don't have to do each topic in turn, and its okay to spend a little time
on one topic, then do something else, and come back to it later.
</p><p>
Your progress is shown next to each topic, which will be one of:
</p>
<table width="100%">
<tr>
  <td class="not-started" style="width:33%;line-height:24px">Topic not started</td>
  <td>You have not yet started this topic. Click 'Begin' to start studying.</td>
</tr>
<tr>
  <td class="started" style="width:33%;line-height:24px">Studying ...</td>
  <td>You have been studying this topic. Click 'Continue' to resume your studies.</td>
</tr>
<tr>
  <td class="mastered" style="width:33%;line-height:24px">Mastered!</td>
  <td>You have passed the mastery test for this topic.</td>
</tr>
</table>
<p>
Your AI tutor will explain the topic and test your understanding with some example problems.
When you feel confident, you can take a test to verify if you have mastered the topic!
</p>
</div>

</body>
</html>
