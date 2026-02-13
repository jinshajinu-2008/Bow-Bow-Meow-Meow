<?php
include 'matchdb.php';

$stmt = $conn->prepare("INSERT INTO pets (name, age, breed, color, gender, location)
VALUES (?, ?, ?, ?, ?, ?)");

$stmt->bind_param("sissss",
  $_POST['name'],
  $_POST['age'],
  $_POST['breed'],
  $_POST['color'],
  $_POST['gender'],
  $_POST['location']
);

$stmt->execute();

header("Location: match.php?id=" . $stmt->insert_id);
exit();
?>
