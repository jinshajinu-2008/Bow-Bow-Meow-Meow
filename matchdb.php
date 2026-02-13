<?php
$conn = new mysqli("localhost", "root", "", "animal_match");

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
?>
