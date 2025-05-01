<?php
session_start();
session_destroy();
setcookie("aituser", "", time() - 3600);
header('Location: /login.php');
?>
