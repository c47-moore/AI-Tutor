<?php
session_start();
include '../php/dbase.php';

$class = 'errDiv';

// Check if this is a form submission and, if so, evaluate it
// for a login or registration attempt
if (!empty($_POST)) {
    if (isset($_POST['action'])) {
        if ($_POST['action'] == 'login') {
            $user = lookupUser($db, $_POST['username']);
            if (is_null($user)) {
                $msg = "No user '" . $_POST['username'] . "' registered.";
            } else {
                if (password_verify($_POST['password'], $user->pwhash)) {
		    setcookie("aituser", $user->id, time() + (86400 * 30), "/");
                    $_SESSION['aituser'] = $user->id;
		    $sql = "UPDATE users SET lastlogin = CURRENT_TIMESTAMP() WHERE username = '{$_POST['username']}'";
		    $db->query($sql);
		    header('Location: /index.php');
		    exit(0);
		} else
		    $msg = 'Incorrect user name or password.';
            }
        } else
        if ($_POST['action'] == 'register') {
            $pw = $_POST['password'];
            if ($pw != $_POST['conf-password']) {
		$msg = 'Chosen and confirmed passwords do not match.';
	    } else {
		$user = lookupUser($db, $_POST['username']);
		if (!is_null($user)) {
		    $msg = 'An account with that username already exists.';
		} else {
		    $hash = password_hash($pw, PASSWORD_DEFAULT);
                    $sql = $db->prepare("INSERT INTO users (username, pwhash, firstname, lastname, lastlogin) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP())");
		    $sql->bind_param('ssss', $_POST['username'], $hash, $_POST['firstname'], $_POST['lastname']);
		    $sql->execute();
		    $msg = 'Account created. You can now sign in!';
		    $class .= ' info';
		}
            }
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login to Chaya's AI Math Tutor</title>
    <link rel="icon" type="image/png" href="/images/favicon.png" />
    <link rel="stylesheet" href="css/styles.css">
    <script src="js/script.js"></script>
</head>
<body class="calign">
<div id="log" class="logdiv">
<h1>Please sign in to use Chaya's AI Maths Tutor!</h1>
<form id="logform" action="" method="post">
    <input type="hidden" name="action" value="login">
    <?php
        if (isset($msg)) {
            echo '<div id="err" class="{$class}">' . $msg . '</div>';
        }
    ?>
    <input type="text" name="username" placeholder="Enter your username" required>
    <input type="password" name="password" placeholder="Enter your password" required>
    <button>Login</button>
</form>
<p style="text-align:center">No account? <a class="toggle" href="#" onClick="return swapLogRegDisplay()">Click here to register.</a></p>
</div>
<div id="reg" class="regdiv">
<h1>Create an account with Chaya's AI Maths Tutor!</h1>
<p style="text-align:center">Already have an account? <a class="toggle" href="#" onClick="return swapLogRegDisplay()">Click here to sign in.</a></p>
<form id="regform" action="" method="post">
  <input type="hidden" name="action" value="register">
  <div class="formrow">
    <input type="text" name="firstname" placeholder="Enter your first name" required>
    <input type="text" name="lastname" placeholder="Enter your last name" required>
  </div>
  <div class="formrow">
    <input type="password" name="password" placeholder="Choose a password" required>
    <input type="password" name="conf-password" placeholder="Confirm your password" required>
  </div>
  <div class="formrow">
    <input type="text" name="username" placeholder="Choose a user name" required>
    <button>Register</button>
  </div>
</form>
</div>
</body>
</html>
