<?php

// This PHP file is retained outside the http-accessible 'www' directory
// so that users cannot obtain this file directly via wget etc. and gain
// access to database passwords or implementation details.

// Database configuration
$dbhost = 'localhost';
$dbuser = 'chaya';
$dbpass = 'db242313';
$dbname = 'aitutor';

// Create database connection
$db = new mysqli($dbhost, $dbuser, $dbpass, $dbname);
if ($db->connect_error) {
    die("Connection failed: " . $db->connect_error);
}

// Look up a user based on login username
function lookupUser($db, $username) {
    $sql = $db->prepare("SELECT * FROM users WHERE username = ?");
    $sql->bind_param('s', $username);
    $sql->execute();
    $res = $sql->get_result();
    if (mysqli_num_rows($res) == 0)
        return null;

    return $res->fetch_object();
}

// Look up a user based on user ID
function lookupUserId($db, $userid) {
    $sql = $db->prepare("SELECT * FROM users WHERE id = ?");
    $sql->bind_param('i', $userid);
    $sql->execute();
    $res = $sql->get_result();
    if (mysqli_num_rows($res) == 0)
        return null;

    return $res->fetch_object();
}

// Update the current user's last login time in the database
function updateLastLogin($db, $userid) {
    $sql = "UPDATE users SET lastlogin = CURRENT_TIMESTAMP() WHERE id = " . $userid;
    $db->query($sql);
}

// Return a list of defined topics in the database. We group
// the ordering of the list by parent, so that the subtopics
// within a chapter follow the chapter topic in the returned
// list. This makes the topic listing on the user's dashboard
// intuitive and easy to render.
function lookupTopics($db) {
    try {
        $res = $db->query("SELECT * FROM topics ORDER BY COALESCE(if(parent=0,NULL,parent), id), parent IS NOT NULL, id");
    } catch (Exception $e) {
        return $e->getMessage();
    }
    if (mysqli_num_rows($res) == 0)
        return 'No topics in database.';

    return $res->fetch_all(MYSQLI_ASSOC);
}

// Look up a specific topic in the database and return both
// the topic information and the user's progress with this
// topic (if any)
function lookupTopic($db, $tid, $uid) {
    try {
        $sql = $db->prepare("SELECT * FROM topics t LEFT JOIN progress p ON p.topic_id = ? AND p.uid = ? WHERE t.id = ?");
        $sql->bind_param('iii', $tid, $uid, $tid);
        $sql->execute();
    } catch (Exception $e) {
        return $e->getMessage();
    }
    $res = $sql->get_result();
    if (mysqli_num_rows($res) == 0)
        return null;

    return $res->fetch_object();
}

// Update the user's progress with a specific topic in the database.
function updateTopicProgress($db, $uid, $tid, $status) {
    try {
        $sql = $db->prepare("SELECT * FROM progress WHERE uid=? AND topic_id=? AND status=?");
        $sql->bind_param('iii', $uid, $tid, $status);
        $sql->execute();
    } catch (Exception $e) {
        $err = $e->getMessage();
        echo "<!-- error: {$err} //-->\n";
        return false;
    }

    $res = $sql->get_result();
    if (mysqli_num_rows($res) == 0) {
        $sql = $db->prepare("INSERT INTO progress (uid, topic_id, status) VALUES (?, ?, ?)");
        $sql->bind_param('iii', $uid, $tid, $status);
    } else {
        $sql = $db->prepare("UPDATE progress SET status=? WHERE uid=? and topic_id=?"); 
        $sql->bind_param('iii', $status, $uid, $tid);
    }

    try {
        $sql->execute();
    } catch (Exception $e) {
        $err = $e->getMessage();
        echo "<!-- error: {$err} //-->\n";
        return false;
    }

    return true;
}

// Get the user's progress with all the topics they've started so far
function getUserProgress($db, $userid) {
    $sql = $db->prepare("SELECT * FROM progress WHERE uid = ?");
    $sql->bind_param('i', $userid);
    $sql->execute();
    $res = $sql->get_result();
    if (mysqli_num_rows($res) == 0)
        return null;

    return $res->fetch_all(MYSQLI_ASSOC);
}

// Get the test questions for the specified topic form the database
function getTopicTests($db, $tid) {
    $sql = $db->prepare("SELECT * FROM tests WHERE topic = ? ORDER BY id");
    $sql->bind_param('i', $tid);
    $sql->execute();
    $res = $sql->get_result();
    if (mysqli_num_rows($res) == 0)
        return null;

    return $res->fetch_all(MYSQLI_ASSOC);
}

// Get the test questions for a given user and topic. This is used
// to build the test page when the user wants to qualify for a topic.
function getUserTopicTests($db, $uid, $tid) {
    $sql = $db->prepare("SELECT user_tests.*,tests.question,tests.answer FROM user_tests LEFT JOIN tests ON user_tests.qid = tests.id WHERE uid = ? AND tid = ? ORDER BY qid");
    $sql->bind_param('ii', $uid, $tid);
    $sql->execute();
    $res = $sql->get_result();
    if (mysqli_num_rows($res) == 0)
        return null;

    return $res->fetch_all(MYSQLI_ASSOC);
}

// Assign a test question to a user
function addUserTest($db, $uid, $test) {
    $sql = $db->prepare("INSERT IGNORE INTO user_tests VALUES (?, ?, ?, 0)");
    $sql->bind_param('iii', $uid, $test['id'], $test['topic']);

    try {
        $sql->execute();
    } catch (Exception $e) {
        $err = $e->getMessage();
        echo "<!-- error: {$err} //-->\n";
        return false;
    }

    return true;
}

?>
