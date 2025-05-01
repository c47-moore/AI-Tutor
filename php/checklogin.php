<?php
// Check to see if the user has an active login cookie and
// if so, check the user ID is valid. If there is a valid
// user and cookie, we update the 'last login' time in the
// database - otherwise, redirect to the login page.
//
if (isset($_COOKIE['aituser'])) {
    $user = lookupUserId($db, $_COOKIE['aituser']);
    if (is_null($user)) {
        header('Location: /login.php');
        exit(0);
    } else {
	updateLastLogin($db, $user->id);
    }
} else {
    header('Location: /login.php');
    exit(0);
}
?>
