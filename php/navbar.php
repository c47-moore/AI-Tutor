<div id="nav" class="navbar">
<div style="float:left"><a href="/index.php"><span>Chaya's AI Math Tutor</span></a></div>
<?php
    if (isset($user)) {
        echo "Hello {$user->firstname}! <a class=\"button\" href=\"/logout.php\">Sign out</a>";
    } else {
        echo "<a href=\"/login.php\">Sign in </a>";
    }
?>
</div>
